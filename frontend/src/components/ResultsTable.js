import React from 'react';

const ResultsTable = ({ results }) => {
  if (!results || results.length === 0) {
    return <p>No results found.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Source</th>
          <th>Title</th>
          <th>URL</th>
        </tr>
      </thead>
      <tbody>
        {results.map((result, index) => (
          <tr key={index}>
            <td>{result.source}</td>
            <td>{result.title}</td>
            <td><a href={result.url} target="_blank" rel="noopener noreferrer">{result.url}</a></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ResultsTable;
