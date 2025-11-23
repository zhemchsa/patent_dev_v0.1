import React, { useState } from 'react'

function SearchBox({ onSearch }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  return (
    <div className="search-box">
      <form onSubmit={handleSubmit}>
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search patents by keywords, technology, or patent number..."
            className="search-input"
            aria-label="Patent search query"
          />
          <button type="submit" className="search-button">
            Search Patents
          </button>
        </div>
      </form>
      
      <div className="search-suggestions">
        <p>Try searching for:</p>
        <span className="suggestion" onClick={() => setQuery('machine learning')}>
          machine learning
        </span>
        <span className="suggestion" onClick={() => setQuery('renewable energy')}>
          renewable energy
        </span>
        <span className="suggestion" onClick={() => setQuery('artificial intelligence')}>
          artificial intelligence
        </span>
      </div>
    </div>
  )
}

export default SearchBox