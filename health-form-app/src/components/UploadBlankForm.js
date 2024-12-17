import React, { useState } from "react";
import "../App.css";

function UploadBlankForm({ setFields }) {
  const [blankFile, setBlankFile] = useState(null);
  const [error, setError] = useState("");

  const handleBlankUpload = async (e) => {
    e.preventDefault();
    if (!blankFile) { //makes sure you've attached a file before uploading
      setError("Please select a blank form to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("file", blankFile); //add the blank file to formData

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_blank", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await response.json();
      setFields(data.fields); // Store the fields in the database
    } catch (err) {
      setError("Failed to upload blank form."); //throw this error if you cant update the database
    }
  };

  return (
    <div className="container">
    <form onSubmit={handleBlankUpload} className="text-center">
      {/* Custom styled file input */}
      <div className="mb-3">
        <div className="input-group">
          <input
            type="file"
            className="form-control bg-dark text-light border-secondary"
            id="fileInput"
            onChange={(e) => setBlankFile(e.target.files[0])}
          />
        </div>
      </div>
        <button type="submit" className="btn custom-btn">
          Upload Blank Form
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default UploadBlankForm;
