# Backend README

## Overview

This directory contains the backend API for the Patent Development Platform, built with FastAPI.

## Files

- `app.py` - Main FastAPI application with API endpoints
- `ingest.py` - Data ingestion utilities for patent data processing
- `requirements.txt` - Python dependencies
- `models/` - Data models and schemas
- `utils/` - Utility functions and helpers
  - `chunker.py` - Text chunking utilities for patent documents

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint  
- `GET /search` - Search for patents
- `POST /search` - Search for patents (POST method)
- `GET /patent/{patent_id}` - Get specific patent details

## Environment Variables

Create a `.env` file in this directory with:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
GOOGLE_CLOUD_PROJECT_ID=your_project_id
BIGQUERY_DATASET_ID=your_dataset_id
```

## Running the Server

```bash
# Make sure you're in the virtual environment
source ../myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API documentation will be available at http://localhost:8000/docs