import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [scrapers, setScrapers] = useState([]);
  const [query, setQuery] = useState('');
  const [selectedScrapers, setSelectedScrapers] = useState([]);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/scrapers')
      .then(response => response.json())
      .then(data => setScrapers(data))
      .catch(error => console.error('Error fetching scrapers:', error));
  }, []);

  const handleScraperChange = (event) => {
    const { value, checked } = event.target;
    setSelectedScrapers(prev => {
      if (checked) {
        return [...prev, value];
      } else {
        return prev.filter(scraper => scraper !== value);
      }
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setResults([]); // Clear previous results

    const requestBody = {
      query: query,
      selected_scrapers: selectedScrapers,
      confidence_threshold: parseFloat(confidenceThreshold)
    };

    fetch('/api/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })
    .then(response => response.json())
    .then(data => {
      setResults(data.leads);
    })
    .catch(error => {
      console.error('Error running scraper:', error);
    })
    .finally(() => {
      setLoading(false);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Lead Discovery & Scraper Agent</h1>
      </header>
      <main>
        <div className="form-container">
          <h2>Configuration</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="query">Query:</label>
              <input
                type="text"
                id="query"
                name="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Hotels in England that may need POS"
                required
              />
            </div>
            <div className="form-group">
              <label>Select Scrapers:</label>
              <div className="checkbox-group">
                {scrapers.map(scraper => (
                  <label key={scraper}>
                    <input
                      type="checkbox"
                      name="scraper"
                      value={scraper}
                      onChange={handleScraperChange}
                    /> {scraper}
                  </label>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="threshold">Confidence Threshold: {confidenceThreshold}</label>
              <input
                type="range"
                id="threshold"
                name="threshold"
                min="0"
                max="1"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(e.target.value)}
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Running...' : 'Run Scraper'}
            </button>
          </form>
        </div>
        <div className="results-container">
          <h2>Results</h2>
          <a href="/api/download" download="leads_output.xlsx">
            <button>Download Results</button>
          </a>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Company</th>
                <th>City</th>
                <th>Title</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Website</th>
                <th>Source</th>
                <th>LinkedIn</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {results.map((lead, index) => (
                <tr key={index}>
                  <td>{lead.name}</td>
                  <td>{lead.company}</td>
                  <td>{lead.city || 'N/A'}</td>
                  <td>{lead.title || 'N/A'}</td>
                  <td>{lead.email || 'N/A'}</td>
                  <td>{lead.phone || 'N/A'}</td>
                  <td>
                    {lead.website ?
                      <a href={lead.website} target="_blank" rel="noopener noreferrer">{lead.website}</a> : 'N/A'}
                  </td>
                  <td>{lead.source || 'N/A'}</td>
                  <td>
                    {lead.linkedin_profile ?
                      <a href={lead.linkedin_profile} target="_blank" rel="noopener noreferrer">Profile</a> : 'N/A'}
                  </td>
                  <td>{lead.confidence_score ? lead.confidence_score.toFixed(2) : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

export default App;
