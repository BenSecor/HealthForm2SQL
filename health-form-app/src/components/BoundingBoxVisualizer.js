import React, { useState } from "react";
import '../App.css'; 

const BoundingBoxVisualizer = () => { //creates the visualizer for the bounding boxes
  const [imageUrl, setImageUrl] = useState(null); 
  const [error, setError] = useState(null); 

  const fetchAnnotatedImage = async () => { //obtains the filled out form
    try {
      setError(null); // Clear previous errors
      const response = await fetch("http://127.0.0.1:5000/visualize_boxes", { 
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) { //error in obtaining filled out form
        throw new Error("Failed to fetch annotated image");
      }
      setImageUrl("http://127.0.0.1:5000/visualize_boxes"); // Set the image URL directly
    } catch (err) {
      console.error(err);
      setError("Could not load the annotated image.");
    }
  };

  const hideImage = () => { //hide the image 
    setImageUrl(null);
  };

  return (
    <div className="container" >
      <label className= "custom-font-merriweather" style={{ padding: "0px 20px", fontSize: "22px"}}>Bounding Box Visualization</label>
      {imageUrl ? ( //vizualizer image
        <button //hide visualizer button
          onClick={hideImage} 
          style={{ padding: "10px 20px", fontSize: "16px"}} className="btn custom-btn"
        >
          Hide
        </button>
      ) : (
        <button //show visualizer button
          onClick={fetchAnnotatedImage} 
          style={{ padding: "10px 20px", fontSize: "16px" }} className="btn custom-btn"
        >
          Visualize
        </button>
      )}
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
