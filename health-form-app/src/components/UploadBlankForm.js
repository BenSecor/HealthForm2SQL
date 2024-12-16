import React, { useState } from "react";
import "../App.css";

function UploadBlankForm({ setFields }) {
  const [blankFile, setBlankFile] = useState(null);
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
      setFields(data.fields); // Pass fetched fields to parent
    } catch (err) {
      setError("Failed to upload blank form.");
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleBlankUpload}>
        <label>Upload Blank Form:</label>
        <input
          type="file"
          className="file-input"
          onChange={(e) => setBlankFile(e.target.files[0])}
        />
        <button type="submit" className="btn btn-primary">
          Upload Blank Form
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default UploadBlankForm;
