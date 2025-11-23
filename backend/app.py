from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Patent Development API",
    description="AI-powered patent search and analysis platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PatentSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class PatentResult(BaseModel):
    id: str
    title: str
    abstract: str
    inventors: List[str] = []
    assignee: Optional[str] = None
    publication_date: Optional[str] = None
    patent_number: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[PatentResult]
    total_count: int
    query: str

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Patent Development API",
        "version": "0.1.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "patent-api"}

@app.get("/search", response_model=SearchResponse)
async def search_patents(
    q: str = Query(..., description="Search query for patents"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    """
    Search for patents based on keywords, technology areas, or patent numbers
    
    - **q**: Search query string
    - **limit**: Maximum number of results to return (1-100)
    """
    try:
        # TODO: Implement actual patent search logic
        # This is a placeholder implementation
        
        # For now, return mock data
        mock_results = [
            PatentResult(
                id="US10123456",
                title=f"Advanced Patent Technology Related to: {q}",
                abstract=f"This patent describes innovative approaches to {q} with applications in various technological domains.",
                inventors=["John Doe", "Jane Smith"],
                assignee="Tech Corp Inc.",
                publication_date="2023-01-15",
                patent_number="US10123456B2"
            ),
            PatentResult(
                id="US10234567",
                title=f"System and Method for {q} Processing",
                abstract=f"A comprehensive system for implementing {q} with enhanced performance characteristics.",
                inventors=["Alice Johnson"],
                assignee="Innovation Labs",
                publication_date="2023-02-20",
                patent_number="US10234567B1"
            )
        ]
        
        # Limit results based on the limit parameter
        limited_results = mock_results[:limit]
        
        return SearchResponse(
            results=limited_results,
            total_count=len(limited_results),
            query=q
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_patents_post(request: PatentSearchRequest):
    """
    Search for patents using POST method with request body
    """
    return await search_patents(q=request.query, limit=request.limit)

@app.get("/patent/{patent_id}")
async def get_patent_details(patent_id: str):
    """
    Get detailed information about a specific patent
    """
    # TODO: Implement patent detail retrieval
    return {
        "patent_id": patent_id,
        "title": f"Patent {patent_id} Details",
        "status": "placeholder - not yet implemented"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)