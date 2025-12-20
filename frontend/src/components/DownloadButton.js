import React from 'react';
import { downloadExcel } from '../services/api';

const DownloadButton = ({ filename }) => {
  const handleDownload = () => {
    if (filename) {
      downloadExcel(filename);
    }
  };

  return (
    <button onClick={handleDownload} disabled={!filename}>
      Download as Excel
    </button>
  );
};

export default DownloadButton;
