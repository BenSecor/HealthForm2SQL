import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import DataDisplay from "./components/DataDisplay";
import BoundingBoxVisualizer from "./components/BoundingBoxVisualizer";
import "./App.css";

function App() {
  const [fields, setFields] = useState([]);
  const [formData, setFormData] = useState(null);

  return (
    <div className="App">
      <h1>Form Processor</h1>
      <UploadForm setFormData={setFormData} setFields={setFields} />
      <BoundingBoxVisualizer />
      {fields && fields.length > 0 && <h2>Database Fields: {fields.join(", ")}</h2>}
      {formData && <DataDisplay data={formData} />}
    </div>
  );
}

export default App;
