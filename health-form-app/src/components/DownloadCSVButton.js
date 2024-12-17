import React from "react";
import "../App.css";

const DownloadCSVButton = () => {
    const handleDownload = () => {
        const url = "http://127.0.0.1:5000/download_csv"; //backend url for downloading the csv, prompted when button clicked
        console.log("Attempting to download CSV from:", url);
        window.open(url);
      };
  
    return (
      //button to download CSV
      <button onClick={handleDownload} className="btn btn-primary">
        Download CSV
      </button>
    );
  };
  
  export default DownloadCSVButton;
  