import React from "react";
import '../App.css';

function DataDisplay({ data }) {
  return (
    <div className="container">
      <h2>Extracted Data</h2>
      {data && data.length > 0 ? (
        data.map((dataset, index) => (
          // this is what appears when you display the data obtained from the filled out forms
          <div key={index} className="dataset-container"> 
            <h3>File {index + 1}</h3>
            <table>
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(dataset).map((key) => (
                  <tr key={key}>
                    <td><strong>{key}</strong></td>
                    <td>{dataset[key]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      ) : (
        <p>No data available</p>
      )}
    </div>
  );
}

export default DataDisplay;
