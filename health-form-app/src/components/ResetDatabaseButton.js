import React, { useState } from "react";
import "../App.css";

const ResetDatabaseButton = () => {
  const handleReset = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/reset_database", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to reset the database.");
      }

      const data = await response.json();
      alert(data.message); // Notify the user on success
    } catch (error) {
      console.error("Error resetting database:", error);
      alert("Error resetting the database. Check console for details.");
    }
  };

  return (
    <button onClick={handleReset} className="btn btn-danger">
      Reset Database
    </button>
  );
};

export default ResetDatabaseButton;
