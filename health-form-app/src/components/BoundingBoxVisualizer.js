import React, { useState } from "react";
import '../App.css'; 

const BoundingBoxVisualizer = () => {
  const [imageUrl, setImageUrl] = useState(null);
  const [error, setError] = useState(null);

  const fetchAnnotatedImage = async () => {
    try {
      setError(null); // Clear previous errors
      const response = await fetch("http://127.0.0.1:5000/visualize_boxes", {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error("Failed to fetch annotated image");
      }
      setImageUrl("http://127.0.0.1:5000/visualize_boxes"); // Set the image URL directly
    } catch (err) {
      console.error(err);
      setError("Could not load the annotated image.");
    }
  };

  return (
    <div style={{ textAlign: "center", margin: "20px" }}>
      <h1>Bounding Box Visualization</h1>
      <button onClick={fetchAnnotatedImage} style={{ padding: "10px 20px", fontSize: "16px" }}>
        Visualize
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {imageUrl && (
        <div style={{ marginTop: "20px" }}>
          <img
            src={imageUrl}
            alt="Annotated Form"
            style={{ maxWidth: "100%", border: "1px solid #ccc" }}
          />
        </div>
      )}
    </div>
  );
};

export default BoundingBoxVisualizer;
