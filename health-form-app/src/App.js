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
    console.log("Selected fields:", selectedFields); //use this to check off fields from empty form you want to use when updating your dataset. all boxes are checked off initially
    try {
      const response = await fetch("http://127.0.0.1:5000/submit_fields", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ fields: selectedFields }), //make string and populate when prompted
        credentials: "include",
      });

      if (!response.ok) {
        console.log("Failed to submit fields:", response); //couldn't submit the fields of interest for some reason
      }

      console.log("Fields submitted successfully:", selectedFields); //field submission worked
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
    
    <div className="d-flex justify-content-center align-items-center">
      <div className="container text-center">
        <img
          src='healthicon.png'
          alt="Health Icon"
          style={{ width: "80px", height: "80px", marginBottom: "10px" }}
        />
        <h1 className="mb-4 custom-font-merriweather">Form Reader
        </h1>
        
        {/* Upload Blank Form */}
        <div class="instruction crimson-text-regular" style={{ marginTop: "70px", marginBottom: "0px", padding: "0" }}>
          <p style={{ fontSize: "16px"}}>
            Welcome to Form Reader! Begin by uploading a blank copy of your form as a PNG or JPEG.
          </p>
        </div>
        <div className="mb-1">
          <UploadBlankForm
            setFields={(fields) => {
              setFields(fields);
              openModal();
            }}
          />
        </div>

        {/* Upload Filled Form */}
        <div class="instruction crimson-text-regular" style={{ marginTop: "70px", marginBottom: "0px", padding: "0" }}>
          <p style={{ fontSize: "16px", margin: "0px 0" }}>
            Finally upload one or more filled copies of your form (PNGs or JPEGs). You can upload as many files as many times as you want. 
          </p>
        </div>

        <div className="mb-1">
          <UploadFilledForm setFormData={setFormData} />
        </div>

        {/* Buttons Section */}
        <div class="instruction crimson-text-regular" style={{ marginTop: "70px", marginBottom: "0px", padding: "0" }}>
          <p style={{ fontSize: "16px", margin: "0px 0" }}>
            To export your data as a CSV use the "Download CSV" button below.
          </p>
          <p style={{ fontSize: "16px", margin: "0px 0" }}>
            If you want to start fresh with a new form, use the "Reset Database" button to clear all existing data and begin the process again.
          </p>
        </div>

        <div className="row justify-content-center g-2">
          <div className="col-auto">
            <DownloadCSVButton />
          </div>
          <div className="col-auto">
            <ResetDatabaseButton />
          </div>
        </div>

        {/* Data Display */}
        <div class="instruction crimson-text-regular" style={{ marginTop: "70px", marginBottom: "0px", padding: "0" }}>
          <p style={{ fontSize: "16px", margin: "0px 0" }}>
            The extracted data from your forms will appear below. Review the data for accuracy and completeness.
          </p>
        </div>

        {formData && (
          <div className="mt-4">
            <DataDisplay data={formData} />
          </div>
        )}

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
                <div className="modal-header py-0">
                  <div className="w-100 text-center">
                    <h5 className="modal-title custom-font-merriweather mb-0 mt-0" style={{ fontSize: "2.5rem", margin: "0" }}>
                      Select Fields
                    </h5>
                    <div class="instruction crimson-text-regular" style={{ margin: "0", padding: "0" }}>
                      <p style={{ fontSize: "16px", margin: "0px 0" }}>
                        Use the bounding box visualization below to review the detected fields on your blank form. These bounding boxes represent the areas the system will extract data from on your filled forms.
                      </p>
                    </div>
                  </div>
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
      </div>
    </div>
  );
}

export default App;