import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

export const runScraper = async (params) => {
  try {
    const response = await api.post('/api/run', params);
    return response.data;
  } catch (error) {
    console.error('Error running scraper:', error);
    throw error;
  }
};

export const downloadExcel = async () => {
  try {
    const response = await api.get('/api/download', {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'leads_output.xlsx');
    document.body.appendChild(link);
    link.click();
  } catch (error) {
    console.error('Error downloading Excel file:', error);
    throw error;
  }
};
