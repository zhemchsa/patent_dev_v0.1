import React, { useState } from 'react'
import SearchBox from './components/SearchBox'
import './App.css'

function App() {
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async (query) => {
    setLoading(true)
    try {
      // TODO: Implement API call to backend
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`)
      const results = await response.json()
      setSearchResults(results)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Patent Development Platform</h1>
        <p>AI-Powered Patent Search and Analysis</p>
      </header>
      
      <main>
        <SearchBox onSearch={handleSearch} />
        
        {loading && (
          <div className="loading">
            <p>Searching patents...</p>
          </div>
        )}
        
        {searchResults.length > 0 && (
          <div className="results">
            <h2>Search Results</h2>
            {searchResults.map((result, index) => (
              <div key={index} className="result-item">
                <h3>{result.title}</h3>
                <p>{result.abstract}</p>
                <small>Patent ID: {result.id}</small>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App