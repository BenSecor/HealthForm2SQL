import React from "react";
import '../App.css'; 

function DataDisplay({ data }) {
  return (
    <div>
      <h2>Extracted Data</h2>
      <table border="1">
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
