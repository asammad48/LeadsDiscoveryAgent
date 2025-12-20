import React from 'react';
import * as XLSX from 'xlsx';

const DownloadButton = ({ results }) => {
  const handleDownload = () => {
    const worksheet = XLSX.utils.json_to_sheet(results);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Leads');
    XLSX.writeFile(workbook, 'leads.xlsx');
  };

  return (
    <button onClick={handleDownload} disabled={!results || results.length === 0}>
      Download as Excel
    </button>
  );
};

export default DownloadButton;
