import React, { useState } from "react";
import UploadBlankForm from "./components/UploadBlankForm";
import UploadFilledForm from "./components/UploadFilledForm";
import DataDisplay from "./components/DataDisplay";
import DownloadCSVButton from "./components/DownloadCSVButton";
import BoundingBoxVisualizer from "./components/BoundingBoxVisualizer";
import FieldsSelector from "./components/FieldsSelector";
import ResetDatabaseButton from "./components/ResetDatabaseButton";
import "./App.css";

function App() {
  const [fields, setFields] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false); // Modal visibility state
  const [formData, setFormData] = useState(null);

  const handleFieldSubmission = async (selectedFields) => {
    console.log("Selected fields:", selectedFields);
    try {
      const response = await fetch("http://127.0.0.1:5000/submit_fields", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ fields: selectedFields }),
        credentials: "include",
      });

      if (!response.ok) {
        console.log("Failed to submit fields:", response);
      }

      console.log("Fields submitted successfully:", selectedFields);
    } catch (error) {
      console.error("Error submitting fields:", error);
    }
    setIsModalOpen(false); // Close modal after submission
  };

  const openModal = () => {
    setIsModalOpen(true); // Open modal handler
  };

  const closeModal = () => {
    setIsModalOpen(false); // Close modal handler
  };

  return (
    <div className="App">
      <h1>Form Processor</h1>
      <UploadBlankForm
        setFields={(fields) => {
          setFields(fields);
          openModal(); // Open modal after fetching fields
        }}
      />

      {/* Modal */}
      {isModalOpen && (
        <div
          className={`modal fade ${isModalOpen ? "show d-block" : ""}`}
          tabIndex="-1"
          role="dialog"
          style={{ background: "rgba(0, 0, 0, 0.5)" }}
        >
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Select Fields</h5>
                <button
                  type="button"
                  className="btn-close"
                  aria-label="Close"
                  onClick={closeModal}
                ></button>
              </div>
              <div className="modal-body">
                <BoundingBoxVisualizer fields={fields} />
                <FieldsSelector
                  availableFields={fields}
                  onSubmit={handleFieldSubmission}
                />
              </div>
            </div>
          </div>
        </div>
      )}
      <UploadFilledForm setFormData={setFormData}/>
            <div className="container mt-4 p-2">
              <div className="row g-2">
                <div className="col text-center">
                  <DownloadCSVButton />
                </div>
                <div className="col text-center">
                  <ResetDatabaseButton />
                </div>
              </div>
            </div>
      {formData && <DataDisplay data={formData} />}
    </div>
  );
}

export default App;
