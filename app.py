from flask import Flask, request, redirect, send_from_directory, url_for, render_template, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
import pytesseract
import cv2
from googleapiclient.discovery import build
import base64
import numpy as np
import fitz

import csv
from io import StringIO
from flask import Response

# Your API key
api_key = "AIzaSyDzzPQFMV1agHwnABcSyaYJtqU4dvrMf0U"

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///form_data.db'
app.config['UPLOAD_FOLDER'] = '/Users/bensecor/Desktop/DeepLearning/HealthForm2SQL/health-form-app/static/uploads'


# Enable CORS with specific origin and credentials support
CORS(app, resources={r"\download_csv":{"origins":"http://localhost:3000"},r"/submit_fields": {"origins": "http://localhost:3000"},r"/visualize_boxes": {"origins": "http://localhost:3000"},r"/upload_filled": {"origins": "http://localhost:3000"}, r"/upload_blank": {"origins": "http://localhost:3000"}}, supports_credentials=True)
#CORS(app)
db = SQLAlchemy(app)


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
if os.path.exists(app.config['UPLOAD_FOLDER']):
    # Drop all tables in the database
    with app.app_context():
        db.drop_all()

import json

# Function to dynamically create a table with given columns
def create_dynamic_table_with_boxes(columns):
    metadata = db.Model.metadata
    table_name = 'form_data'

    if table_name in metadata.tables:
        # Remove existing table definition from metadata
        metadata.remove(metadata.tables[table_name])

    # Define dynamic table schema
    fields = {
        '__tablename__': table_name,
        'id': db.Column(db.Integer, primary_key=True)
    }

    for column in columns:
        fields[column] = db.Column(db.String(255))

    # Create a new dynamic model
    FormData = type('FormData', (db.Model,), fields)
    db.create_all()  # Apply schema changes to the database
    return FormData

@app.route('/reset_database', methods=['POST'])
def reset_database():
    try:
        db.drop_all()  # Drops all database tables
        db.create_all()  # Recreates the database schema
        print("Database reset successfully.")  # Debug log
        return jsonify({"message": "Database reset successfully."}), 200
    except Exception as e:
        print("Error resetting database:", str(e))  # Debug log
        return jsonify({"error": "Failed to reset database.", "details": str(e)}), 500

@app.route('/download_csv', methods=['GET'])
def download_csv():
    global FormData 
    try:
        # Step 1: Query the database
        records = FormData.query.all()
        print("Fetched records:", records)  # Log all records

        # Step 2: Get column names
        column_names = [column.name for column in FormData.__table__.columns]
        print("Column names:", column_names)  # Log column names

        # Step 3: Generate CSV content
        csv_output = StringIO()
        writer = csv.writer(csv_output)
        writer.writerow(column_names)  # Write header
        print("CSV Header written.")  # Log

        # Step 4: Write each record to CSV
        for record in records:
            row = [getattr(record, column) for column in column_names]
            print("Writing row to CSV:", row)  # Log row being written
            writer.writerow(row)
        
        # Step 5: Generate and return response
        csv_output.seek(0)
        response = Response(csv_output, mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=form_data.csv'
        print("CSV generated successfully.")  # Log success
        return response
    except Exception as e:
        # Log detailed error information
        print("Error generating CSV:", str(e))  # Log error message
        return jsonify({"error": "Failed to generate CSV", "details": str(e)}), 500

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

    # Save bounding boxes to a JSON file
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
    except Exception as e:
        return jsonify({"error": f"Failed to reset database: {e}"}), 500

    return jsonify({"message": "Blank form processed and schema created.", "fields": fields})

@app.route('/submit_fields', methods=['POST'])
def submit_fields():
    data = request.get_json()
    selected_fields = data.get('fields', [])
    try:
        db.drop_all()
        global FormData
        FormData = create_dynamic_table_with_boxes(selected_fields)
    except Exception as e:
        return jsonify({"error": f"Failed to submit fields: {e}"}), 500

    return jsonify({"success": True, "message": "Fields submitted successfully."}), 200

@app.route('/upload_filled', methods=['POST'])
def upload_filled():
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({"error": "No selected files"}), 400

    new_files = []

    print("Uploaded Files", uploaded_files)  # Log uploaded files
    # Process PDFs and convert them into images
    for uploaded_file in uploaded_files:
        if uploaded_file.filename.endswith('.pdf'):
            try:
                # Save the uploaded PDF to a temporary file
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(pdf_path)
                pdf_document = fitz.open(pdf_path)  # Open the PDF using PyMuPDF

                for page_number in range(len(pdf_document)):
                    page = pdf_document[page_number]  # Get a page
                    pix = page.get_pixmap(dpi=300)   # Convert page to an image with DPI=300
                    page_filename = f"{os.path.splitext(uploaded_file.filename)[0]}_page_{page_number}.png"
                    page_path = os.path.join(app.config['UPLOAD_FOLDER'], page_filename)
                    pix.save(page_path)  # Save the image as PNG
                    new_files.append(page_path)  # Append file path to list
                
                pdf_document.close()
                print("PDF processed successfully.")  # Log success
            except Exception as e:
                raise RuntimeError(f"Failed to process PDF {uploaded_file.filename}: {e}")

        elif uploaded_file.filename.endswith(('.png', '.jpg')):
            # Save the image files directly
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            new_files.append(file_path)
        else:
            return jsonify({"error": "Invalid file format. Please upload PDF, PNG, or JPG files only."}), 400

    # Process each file for bounding box extraction and database saving
    extracted_data_list = []
    try:
        bounding_boxes_path = os.path.join(app.config['UPLOAD_FOLDER'], 'bounding_boxes.json')
        with open(bounding_boxes_path, 'r') as f:
            fields_with_boxes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Bounding boxes JSON file not found."}), 500

    print("File Paths", new_files)  # Log bounding boxes
    for file_path in new_files:
        try:
            # Extract data using bounding boxes
            extracted_data = extract_data_with_boxes(file_path, fields_with_boxes)

            # Filter valid database columns
            valid_columns = {column.name for column in FormData.__table__.columns}
            filtered_data = {key: value for key, value in extracted_data.items() if key in valid_columns}

            # Save the data to the database
            record = FormData(**filtered_data)
            db.session.add(record)
            db.session.commit()
            extracted_data_list.append(filtered_data)
        except Exception as e:
            return jsonify({"error": f"Failed to process file {file_path}: {e}"}), 500

    # Retrieve all data from the database
    all_data = []
    try:
        records = FormData.query.all()
        for record in records:
            row = {column.name: getattr(record, column.name) for column in FormData.__table__.columns}
            all_data.append(row)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data from database: {e}"}), 500

    return jsonify({"message": "Filled forms processed and data saved.", "data": all_data})

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
            'name': '_'.join(field_text).strip(),
            'bbox': (x1, y1, x2 - x1, y2 - y1)  # (x, y, width, height)
        })
        used_boxes.add(i)

    # Extend bounding boxes to cover the entire field
    height, width, _ = image.shape
    new_field_boxes = extend_bboxes(field_boxes, width, height)

    return new_field_boxes


def extend_bboxes(field_boxes, width, height, max_iterations=100):
    """
    Gradually extends bounding boxes in both directions over multiple iterations.

    Args:
        field_boxes (list): List of field metadata with bounding boxes.
        width (int): Width of the image.
        height (int): Height of the image.
        max_iterations (int): Maximum number of iterations for extending boxes.

    Returns:
        list: List of updated field boxes with extended dimensions.
    """
    def intersects(box1, box2):
        """Checks if two bounding boxes intersect."""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    for _ in range(max_iterations):
        # Create a copy of field_boxes to process extensions iteratively
        new_field_boxes = []
        extended = False
        # Extend each bounding box to the right and downwards incrementally
        for box in field_boxes:
            x, y, w, h = box['bbox']

            # Try to extend to the right
            if (x + w+ 10) < width:
                extended_box = (x, y, w + 10, h)
                if not any(
                    intersects(extended_box, other_box['bbox'])
                    for other_box in field_boxes
                    if other_box['bbox'] != box['bbox']
                ):
                    w += 10
                    extended = True

            # Try to extend downwards
            if (y + h+2) < height:
                extended_box = (x, y, w, h + 1)
                if not any(
                    intersects(extended_box, other_box['bbox'])
                    for other_box in field_boxes
                    if other_box['bbox'] != box['bbox']
                ):
                    h += 1
                    extended = True
            
             # Try to extend upwards
            if (y + h+1) < height and y > 0:
                extended_box = (x, y-1, w, h + 2)
                if not any(
                    intersects(extended_box, other_box['bbox'])
                    for other_box in field_boxes
                    if other_box['bbox'] != box['bbox']
                ):
                    y -= 1
                    h += 1
                    extended = True

            # Update the box dimensions
            box['bbox'] = (x, y, w, h)
            new_field_boxes.append(box)
        
        # Update field_boxes for the next iteration
        field_boxes = new_field_boxes
        # If no extensions were made in this iteration, stop
        if not extended:
            break

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
        # Save the uploaded file
    def subtract_blank_form(filled_form, blank_form):
        """
        Subtracts the blank form from the filled form to isolate input text.

        Args:
            filled_form (ndarray): Image of the filled form.
            blank_form (ndarray): Image of the blank form.

        Returns:
            ndarray: Image containing only the input text and differences.
        """
        # Ensure both images are grayscale
        filled_gray = cv2.cvtColor(filled_form, cv2.COLOR_BGR2GRAY) if len(filled_form.shape) == 3 else filled_form
        blank_gray = cv2.cvtColor(blank_form, cv2.COLOR_BGR2GRAY) if len(blank_form.shape) == 3 else blank_form

        # Resize the blank form to match the filled form (if necessary)
        filled_gray = cv2.resize(filled_gray, (blank_gray.shape[1], blank_gray.shape[0]))

        # Subtract the blank form from the filled form
        difference = cv2.absdiff(filled_gray, blank_gray)

        # Apply a binary threshold to isolate the differences
        _, thresholded = cv2.threshold(difference, 50, 255, cv2.THRESH_BINARY)

        return thresholded

    binarized = subtract_blank_form(gray, cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], 'blank_form.png')))

    #Save Binarized Image
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'binarized.png'), binarized)
    # # Apply binarization for better OCR accuracy
    # _, binarized = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    extracted_data = {}

    service = build("vision", "v1", developerKey=api_key)

    for field in fields_with_boxes:
        field_name = field['name']
        x, y, w, h = field['bbox']

        # Crop the region defined by the bounding box
        cropped_region = binarized[y:y + h, x:x + w]

        extracted_data[field_name] = ""
        # Encode the cropped region in memory
        _, buffer = cv2.imencode(".png", cropped_region)
        content = base64.b64encode(buffer).decode("utf-8")
        # Prepare the request
        request = {
            "requests": [
                {
                    "image": {"content": content},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        # Make the API call
        response = service.images().annotate(body=request).execute()
        if "textAnnotations" in response["responses"][0]:
            text = response["responses"][0]["textAnnotations"][0]['description']
            extracted_data[field_name] += text
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