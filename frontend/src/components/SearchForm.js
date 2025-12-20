import React from 'react';

const SearchForm = ({ onSearch, isLoading }) => {
  const [query, setQuery] = React.useState('');
  const [sources, setSources] = React.useState('');
  const [threshold, setThreshold] = React.useState(0.8);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ query, sources: sources.split(',').map(s => s.trim()), threshold });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="query">Query:</label>
        <input
          id="query"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="sources">Sources (comma-separated):</label>
        <input
          id="sources"
          type="text"
          value={sources}
          onChange={(e) => setSources(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="threshold">Similarity Threshold:</label>
        <input
          id="threshold"
          type="number"
          step="0.01"
          min="0"
          max="1"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          required
        />
      </div>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Running...' : 'Run'}
      </button>
    </form>
  );
};

export default SearchForm;
