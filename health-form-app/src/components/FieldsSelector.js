import React, { useState } from "react";
import "../App.css";

function FieldsSelector({ availableFields, onSubmit }) {
  const [selectedFields, setSelectedFields] = useState(availableFields); // Pre-select all fields

  const toggleField = (field) => {
    const isSelected = selectedFields.includes(field);
    if (isSelected) {
      setSelectedFields(selectedFields.filter((f) => f !== field)); // Remove field
    } else {
      setSelectedFields([...selectedFields, field]); // Add field
    }
  };

  const handleSubmit = () => {
    onSubmit(selectedFields); // Pass selected fields to parent on submit
  };

  // Helper function to insert line breaks after 50 characters
  const formatFieldText = (text) => {
    return text.replace(/(.{50})/g, "$1\n"); // Add newline after every 50 characters
  };

  return (
    <div className="container">
      <ul className="field-list">
        {availableFields.map((field) => (
          <li key={field} className="field-item">
            <label>
              <input
                type="checkbox"
                checked={selectedFields.includes(field)}
                onChange={() => toggleField(field)}
              />
              <span className="field-text">
                {formatFieldText(field)}
              </span>
            </label>
          </li>
        ))}
      </ul>
      <button onClick={handleSubmit} className="btn custom-btn">Submit</button>
    </div>
  );
}

export default FieldsSelector;
