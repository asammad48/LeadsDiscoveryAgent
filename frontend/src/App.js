import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import ResultsTable from './components/ResultsTable';
import DownloadButton from './components/DownloadButton';
import { runScraper } from './services/api';

function App() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filename, setFilename] = useState(null);

  const handleSearch = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await runScraper(params);
      setResults(response.results);
      setFilename(response.filename);
    } catch (err) {
      setError('An error occurred while running the scraper. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Lead Discovery & Scraper Agent</h1>
      </header>
      <main>
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        {error && <p className="error">{error}</p>}
        <ResultsTable results={results} />
        <DownloadButton filename={filename} />
      </main>
    </div>
  );
}

export default App;
