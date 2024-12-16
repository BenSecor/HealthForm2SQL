import React, { useState } from "react";

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

  return (
    <div className="container">
      {/* <h2>Select Fields</h2> */}
      <ul>
        {availableFields.map((field) => (
          <li key={field}>
            <label>
              <input
                type="checkbox"
                checked={selectedFields.includes(field)}
                onChange={() => toggleField(field)}
              />
              {field}
            </label>
          </li>
        ))}
      </ul>
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default FieldsSelector;
