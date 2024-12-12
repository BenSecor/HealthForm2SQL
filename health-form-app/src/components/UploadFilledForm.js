import React, { useState } from "react";
import '../App.css';

function UploadFilledForm({ setFormData, setFields }) {
  const [filledFiles, setFilledFiles] = useState([]); // Updated to hold multiple files
  const [error, setError] = useState("");

  const handleFilledUpload = async (e) => {
    e.preventDefault();
    if (filledFiles.length === 0) {
      setError("Please select filled forms to upload.");
      return;
    }
    const formData = new FormData();
    filledFiles.forEach((file) => {
      formData.append("files", file); // Append all files
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_filled", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await response.json();
      setFormData(data.data);
    } catch (err) {
      setError("Failed to upload filled forms.");
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleFilledUpload}>
        <label>Upload Filled Forms:</label>
        <input type="file" class="file-input" multiple onChange={(e) => setFilledFiles(Array.from(e.target.files))} />
        <button type="submit">Upload Filled Forms</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default UploadFilledForm;
