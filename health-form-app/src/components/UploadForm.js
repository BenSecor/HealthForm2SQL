import React, { useState } from "react";
import '../App.css';


function UploadForm({ setFormData, setFields }) {
  const [blankFile, setBlankFile] = useState(null);
  const [filledFile, setFilledFile] = useState(null);
  const [error, setError] = useState("");

  const handleBlankUpload = async (e) => {
    e.preventDefault();
    if (!blankFile) {
      setError("Please select a blank form to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("file", blankFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_blank", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await response.json();
      setFields(data.fields);
    } catch (err) {
      setError("Failed to upload blank form.");
    }
  };

  const handleFilledUpload = async (e) => {
    e.preventDefault();
    if (!filledFile) {
      setError("Please select a filled form to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("file", filledFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_filled", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await response.json();
      setFormData(data.data);
    } catch (err) {
      setError("Failed to upload filled form.");
    }
  };

  return (
    <div>
      <form onSubmit={handleBlankUpload}>
        <label>Upload Blank Form:</label>
        <input type="file" classname='file-input' onChange={(e) => setBlankFile(e.target.files[0])} />
        <button type="submit">Upload Blank Form</button>
      </form>
      <form onSubmit={handleFilledUpload}>
        <label>Upload Filled Form:</label>
        <input type="file" classname='file-input' onChange={(e) => setFilledFile(e.target.files[0])} />
        <button type="submit">Upload Filled Form</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default UploadForm;
