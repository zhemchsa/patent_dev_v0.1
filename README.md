# Patent Development Platform v0.1

A full-stack application for patent search and analysis, featuring AI-powered patent research capabilities.

## Project Structure

```
patent_dev_v0.1/
├── backend/           # Python FastAPI backend
│   ├── app.py        # Main FastAPI application
│   ├── ingest.py     # Data ingestion utilities
│   ├── requirements.txt
│   ├── models/       # Data models
│   └── utils/        # Utility functions
│       └── chunker.py
├── frontend/         # React frontend with Vite
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── components/
│   │       └── SearchBox.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Technologies Used

### Backend

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11.6** - Core programming language
- **OpenAI** - AI integration for patent analysis
- **Pinecone** - Vector database for semantic search
- **Google Cloud BigQuery** - Data warehouse integration
- **Uvicorn** - ASGI server for FastAPI

### Frontend

- **React** - UI library
- **Vite** - Build tool and development server
- **JavaScript/JSX** - Frontend programming

## Setup Instructions

### Prerequisites

- Python 3.11.6
- Node.js (for frontend development)
- Git

### Backend Setup

1. **Create and activate virtual environment:**

   ```bash
   python3.11 -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file in the backend directory
   cp backend/.env.example backend/.env  # If example exists
   # Add your API keys and configuration
   ```

### Frontend Setup

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## Development

### Running the Backend

```bash
# Activate virtual environment
source myenv/bin/activate

# Run the FastAPI server
cd backend
uvicorn app:app --reload
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

## API Endpoints

The backend provides RESTful API endpoints for:

- Patent search and retrieval
- AI-powered patent analysis
- Vector similarity search
- Data ingestion and processing

## Features

- 🔍 **Patent Search** - Search through patent databases
- 🤖 **AI Analysis** - AI-powered patent analysis and insights
- 🎯 **Semantic Search** - Vector-based similarity search
- 📊 **Data Visualization** - Interactive patent data visualization
- ⚡ **Fast Performance** - Optimized for speed and efficiency

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact the development team.
