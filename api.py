from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status, Security, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import logging
import os

from search import search_semantic, search_hybrid, search_merged
from config import get_kb_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown."""
    # Startup: Initialize KB client
    try:
        get_kb_client()
        logger.info("API startup complete")
    except ValueError as e:
        logger.error(f"Failed to initialize KB client: {e}")
        raise
    
    yield
    
    # Shutdown: cleanup if needed
    logger.info("API shutdown")


app = FastAPI(lifespan=lifespan)

# API Key authentication (optional, for production deployment)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key if API_KEY environment variable is set.
    
    If API_KEY is not set, authentication is disabled (for local development).
    For production deployment, always set API_KEY environment variable.
    """
    required_api_key = os.getenv("API_KEY")
    
    # If no API_KEY is configured, allow access (local development mode)
    if not required_api_key:
        logger.debug("API authentication disabled - no API_KEY configured")
        return None
    
    # If API_KEY is configured, require valid key
    if not api_key or api_key != required_api_key:
        logger.warning("Invalid or missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    return api_key

# Generic error handler to prevent information leakage
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with generic error response."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred"}
    )

class SearchQuery(BaseModel):
    query: str
    search_type: Optional[str] = "merged"

class SearchResult(BaseModel):
    text: str
    score: float
    source: str

@app.post("/search", response_model=List[SearchResult])
async def search(query: SearchQuery, api_key: str = Depends(get_api_key)):
    if query.search_type == "semantic":
        results = await search_semantic(query.query)
    elif query.search_type == "hybrid":
        results = await search_hybrid(query.query)
    elif query.search_type == "merged":
        results = await search_merged(query.query)
    else:
        raise HTTPException(status_code=422, detail="Invalid search_type")
    
    return [SearchResult(text=r.get('text', ''), score=r.get('score', 0.0), source=r.get('field', '')) for r in results]
