from flask import Flask, request, redirect, send_from_directory, url_for, render_template, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import PyPDF2
from PIL import Image
import os
from flask_cors import CORS
import re
import pytesseract
import cv2
import csv

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'
app.config['UPLOAD_FOLDER'] = '/Users/bensecor/Desktop/Form2Sql/health-form-app/static/uploads'



# Enable CORS with specific origin and credentials support
CORS(app, resources={r"/visualize_boxes": {"origins": "http://localhost:3000"},r"/upload_filled": {"origins": "http://localhost:3000"}, r"/upload_blank": {"origins": "http://localhost:3000"}}, supports_credentials=True)
#CORS(app)
db = SQLAlchemy(app)


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
if os.path.exists(app.config['UPLOAD_FOLDER']):
    # Drop all tables in the database
    with app.app_context():
        db.drop_all()

import json

# Modify database schema creation to store bounding boxes
def create_dynamic_table_with_boxes(columns):
    class FormData(db.Model):
        __tablename__ = 'form_data'
        id = db.Column(db.Integer, primary_key=True)
        for column in columns:
            locals()[column] = db.Column(db.String(255))  # Data storage
    db.create_all()
    return FormData

# Store bounding boxes in JSON format
@app.route('/upload_blank', methods=['POST'])
def upload_blank():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blank_form.png')
    uploaded_file.save(file_path)

    # Use OCR to extract text and bounding boxes
    fields_with_boxes = extract_fields_with_boxes(file_path)

    # Save bounding boxes to a file or database
    bounding_boxes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bounding_boxes.json')
    with open(bounding_boxes_path, 'w') as f:
        json.dump(fields_with_boxes, f)

    # Extract field names
    fields = [field['name'] for field in fields_with_boxes]

    # Reset database schema with new fields
    try:
        db.drop_all()
        global FormData
        FormData = create_dynamic_table_with_boxes(fields)
        db.create_all()
    except Exception as e:
        return jsonify({"error": f"Failed to reset database: {e}"}), 500

    return jsonify({"message": "Blank form processed and schema created.", "fields": fields})


@app.route('/upload_filled', methods=['POST'])
def upload_filled():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'filled_form.png')
    uploaded_file.save(file_path)

    # Load bounding boxes
    bounding_boxes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bounding_boxes.json')
    with open(bounding_boxes_path, 'r') as f:
        fields_with_boxes = json.load(f)

    # Extract data using bounding boxes
    extracted_data = extract_data_with_boxes(file_path, fields_with_boxes)

    # Save data to the database
    valid_columns = {column.name for column in FormData.__table__.columns}
    filtered_data = {key: value for key, value in extracted_data.items() if key in valid_columns}
    try:
        record = FormData(**filtered_data)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": f"Failed to save data to database: {e}"}), 500

    return jsonify({"message": "Filled form processed and data saved.", "data": filtered_data})

def extract_fields_with_boxes(file_path):
    # Load the image
    image = cv2.imread(file_path)

    # Get OCR data
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config="--psm 11")

    # Collect bounding boxes and their corresponding text
    text_boxes = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text:  # Include only non-empty text
            bbox = {
                'text': text,
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i],
                'right': data['left'][i] + data['width'][i],
                'bottom': data['top'][i] + data['height'][i]
            }
            text_boxes.append(bbox)

    # Sort text_boxes by top, then left position for consistency
    text_boxes = sorted(text_boxes, key=lambda b: (b['top'], b['left']))

    # Initialize final field boxes
    field_boxes = []

    # Process text boxes to group them into logical fields based on geography
    used_boxes = set()

    for i, box in enumerate(text_boxes):
        if i in used_boxes:
            continue

        # Initialize a new field bounding box
        x1, y1 = box['left'], box['top']
        x2, y2 = box['right'], box['bottom']
        field_text = [box['text']]

        # Group nearby text into the same field based on geographic proximity
        for j, other_box in enumerate(text_boxes[i + 1:], start=i + 1):
            if j in used_boxes:
                continue

            # Define proximity thresholds (can be adjusted based on the form)
            horizontal_proximity = 50  # Max horizontal distance to group
            vertical_proximity = 10    # Max vertical distance to group

            # Check if the other box is close enough to be part of the same field
            if (abs(other_box['top'] - y1) <= vertical_proximity and
                other_box['left'] >= x2 and
                abs(other_box['left'] - x2) <= horizontal_proximity):
                # Extend the current bounding box
                x2 = max(x2, other_box['right'])
                y1 = min(y1, other_box['top'])
                y2 = max(y2, other_box['bottom'])
                field_text.append(other_box['text'])
                used_boxes.add(j)

        # Save the final field as a single bounding box with combined text
        field_boxes.append({
            'name': ' '.join(field_text).strip(),
            'bbox': (x1, y1, x2 - x1, y2 - y1)  # (x, y, width, height)
        })
        used_boxes.add(i)

    return field_boxes


def extract_data_with_boxes(file_path, fields_with_boxes):
    """
    Extracts data from the filled form using precomputed bounding boxes.

    Args:
        file_path (str): Path to the filled form image.
        fields_with_boxes (list): List of field metadata with bounding boxes.

    Returns:
        dict: A dictionary mapping field names to extracted values.
    """
    # Load the filled form image
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binarization for better OCR accuracy
    _, binarized = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    extracted_data = {}

    for field in fields_with_boxes:
        field_name = field['name']
        x, y, w, h = field['bbox']

        # Crop the region defined by the bounding box
        cropped_region = binarized[y:y + h, x:x + w]

        # Debugging: Save the cropped region as an image (optional)
        debug_path = f"static/cropped_{field_name}.png"
        cv2.imwrite(debug_path, cropped_region)

        # Extract text from the cropped region using Tesseract OCR
        extracted_text = pytesseract.image_to_string(cropped_region, config="--psm 6").strip()

        # Store the extracted text in the result dictionary
        extracted_data[field_name] = extracted_text

    return extracted_data



@app.route('/visualize_boxes', methods=['GET'])
def visualize_boxes():
    """
    Visualize bounding boxes on the blank form and serve the annotated image.
    """
    bounding_boxes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bounding_boxes.json')
    form_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'blank_form.png')
    annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'annotated_form.png')

    # Load bounding boxes
    try:
        with open(bounding_boxes_path, 'r') as f:
            fields_with_boxes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Bounding boxes not found"}), 404

    # Load the blank form image
    image = cv2.imread(form_image_path)

    # Draw bounding boxes on the image
    for field in fields_with_boxes:
        name = field['name']
        x, y, w, h = field['bbox']
        color = (0, 255, 0)  # Green box
        thickness = 2
        cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)
        cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

    # Save the annotated image
    cv2.imwrite(annotated_image_path, image)

    return send_file(annotated_image_path, mimetype='image/png')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)