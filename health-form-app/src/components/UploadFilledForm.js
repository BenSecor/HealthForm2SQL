import React, { useState } from "react";
import '../App.css';

function UploadFilledForm({ setFormData, setFields }) {
  const [filledFiles, setFilledFiles] = useState([]); // Updated to hold multiple files
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false); // Loading state

  const handleFilledUpload = async (e) => { 
    e.preventDefault();
    if (filledFiles.length === 0) { //makes sure you've selected files before hitting upload
      setError("Please select filled forms to upload.");
      return;
    }
    setIsLoading(true); // Show the spinner
    const formData = new FormData();
    filledFiles.forEach((file) => {
      formData.append("files", file); // Append all files
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/upload_filled", { //try updating the database
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await response.json();
      setFormData(data.data);
      setError(""); // Clear errors
    } catch (err) {
      setError("Failed to upload filled forms."); //throw this if you cant updatea the database
    } finally {
      setIsLoading(false); // Hide the spinner
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleFilledUpload}>
        <div className="mb-3">
          <div className="input-group">
            <input
              type="file"
              class="form-control bg-dark text-light border-secondary"
              id="formFile" 
              multiple
              onChange={(e) => setFilledFiles(Array.from(e.target.files))}
            />
          </div>
        </div>
        <button type="submit" class="btn custom-btn">Upload Filled Forms</button>
        {/* Show spinner when isLoading is true */}
        {isLoading && (
          <div className="d-flex justify-content-center mt-3">
            <div className="spinner-border text-success" role="status"></div>
          </div>
        )}

        {/* Show error message */}
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
    </div>
  );
}

export default UploadFilledForm;
