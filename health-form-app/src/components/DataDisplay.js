import React from "react";
import '../App.css';

function DataDisplay({ data }) {
  return (
    <div className="container">
      <h2>Extracted Data</h2>
      <table>
        <thead>
          <tr>
            <th>Field</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(data).map((key) => (
            <tr key={key}>
              <td><strong>{key}</strong></td>
              <td>{data[key]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataDisplay;
