import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import DataDisplay from "./components/DataDisplay";
import BoundingBoxVisualizer from "./components/BoundingBoxVisualizer";
import FieldsSelector from "./components/FieldsSelector";
import "./App.css";

function App() {
  const [fields, setFields] = useState([]);
  const [formData, setFormData] = useState(null);
  
  const handleFieldSubmission = async (selectedFields) => {
    console.log("Selected fields:", selectedFields);
    try {
      const response = await fetch("http://127.0.0.1:5000/submit_fields", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ "fields": selectedFields }),
        credentials: "include",
      });

      if (!response.ok) {
        console.log("Failed to submit fields:", response);
      }

      console.log("Fields submitted successfully:", selectedFields);
    } catch (error) {
      console.error("Error submitting fields:", error);
    }
  };

  return (
    <div className="App">
      <h1>Form Processor</h1>
      <UploadForm setFormData={setFormData} setFields={setFields} />
      <BoundingBoxVisualizer />
      {fields && fields.length >0 && <FieldsSelector availableFields={fields} onSubmit={handleFieldSubmission}/>}
      {formData && <DataDisplay data={formData} />}
    </div>
  );
}

export default App;
