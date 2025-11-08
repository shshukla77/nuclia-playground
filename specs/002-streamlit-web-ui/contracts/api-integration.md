# API Integration Contract

**Feature**: 002-streamlit-web-ui  
**Date**: November 7, 2025  
**Version**: 1.0

## Overview

This document defines the contract between the Streamlit web UI and the existing FastAPI search service. The UI acts as a client consuming the `/search` endpoint.

---

## Base Configuration

**Environment Variables**:
```bash
# Required
API_BASE_URL=http://localhost:8000  # Base URL of the FastAPI service

# Optional
API_TIMEOUT=30  # Request timeout in seconds (default: 30)
```

**Configuration Loading**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
```

---

## Endpoint: Search

### Request

**Method**: `POST`  
**Path**: `/search`  
**Full URL**: `{API_BASE_URL}/search`  
**Content-Type**: `application/json`

**Request Body Schema**:
```json
{
    "query": "string (required, min_length=1)",
    "search_type": "string (optional, enum: [semantic, hybrid, merged], default: merged)"
}
```

**Request Examples**:

*Semantic search*:
```json
{
    "query": "What is retrieval-augmented generation?",
    "search_type": "semantic"
}
```

*Hybrid search*:
```json
{
    "query": "machine learning techniques",
    "search_type": "hybrid"
}
```

*Merged search (default)*:
```json
{
    "query": "explain RAG architecture"
}
```

---

### Response

#### Success Response (200 OK)

**Content-Type**: `application/json`

**Response Body Schema**:
```json
[
    {
        "text": "string (required)",
        "score": "float (required, range: 0.0-1.0)",
        "source": "string (required)"
    }
]
```

**Response Example**:
```json
[
    {
        "text": "Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with language generation...",
        "score": 0.89,
        "source": "a/introduction/overview"
    },
    {
        "text": "RAG systems typically consist of two main components: a retriever and a generator...",
        "score": 0.85,
        "source": "a/architecture/components"
    },
    {
        "text": "The retrieval phase uses vector similarity search to find relevant documents...",
        "score": 0.82,
        "source": "a/retrieval/vector-search"
    }
]
```

**Notes**:
- Results are ordered by descending score (highest relevance first)
- Result count varies based on available matches
- Empty array `[]` returned when no results found
- Score interpretation: Higher values indicate better relevance (typically 0.0-1.0 range)

---

#### Error Responses

**422 Unprocessable Entity** - Invalid request parameters

```json
{
    "detail": "Invalid search_type. Must be one of: semantic, hybrid, merged"
}
```

*Causes*:
- Invalid `search_type` value
- Missing required `query` field
- Empty query string

---

**500 Internal Server Error** - Search execution failed

```json
{
    "detail": "Search operation failed: [error details]"
}
```

*Causes*:
- Backend search service unavailable
- Knowledge base access error
- Internal processing error

---

**503 Service Unavailable** - API server not responding

*Causes*:
- FastAPI server not running
- Network connectivity issue
- Server overloaded

---

## Client Implementation

### Python Client (for Streamlit)

```python
import requests
from typing import List, Dict, Optional

class SearchAPIClient:
    """Client for interacting with the search API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def search(
        self, 
        query: str, 
        search_type: str = "merged"
    ) -> List[Dict[str, any]]:
        """
        Execute a search query.
        
        Args:
            query: Search query string
            search_type: Strategy to use (semantic/hybrid/merged)
            
        Returns:
            List of search results with text, score, and source
            
        Raises:
            requests.ConnectionError: API server unavailable
            requests.HTTPError: API returned error status
            requests.Timeout: Request timed out
            ValueError: Invalid parameters
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if search_type not in ["semantic", "hybrid", "merged"]:
            raise ValueError(
                f"Invalid search_type: {search_type}. "
                "Must be one of: semantic, hybrid, merged"
            )
        
        payload = {
            "query": query.strip(),
            "search_type": search_type
        }
        
        response = requests.post(
            f"{self.base_url}/search",
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check if API server is reachable.
        
        Returns:
            True if server responds, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/docs",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

---

### Error Handling Pattern

```python
def safe_search(client, query, strategy):
    """Execute search with comprehensive error handling."""
    try:
        results = client.search(query, strategy)
        return {
            "success": True,
            "results": results,
            "error": None
        }
    except ValueError as e:
        # Validation error
        return {
            "success": False,
            "results": [],
            "error": f"Validation error: {str(e)}"
        }
    except requests.ConnectionError:
        # API server not reachable
        return {
            "success": False,
            "results": [],
            "error": "Unable to connect to search API. Please ensure the API server is running at {API_BASE_URL}."
        }
    except requests.Timeout:
        # Request timed out
        return {
            "success": False,
            "results": [],
            "error": "Search request timed out. Please try again."
        }
    except requests.HTTPError as e:
        # API returned error status
        error_detail = e.response.json().get("detail", str(e))
        return {
            "success": False,
            "results": [],
            "error": f"Search failed: {error_detail}"
        }
    except Exception as e:
        # Unexpected error
        return {
            "success": False,
            "results": [],
            "error": f"Unexpected error: {str(e)}"
        }
```

---

## Testing Contract

### Unit Tests

**Test Coverage Requirements**:
- ✅ Successful search request (all three strategies)
- ✅ Empty query validation
- ✅ Invalid search_type validation
- ✅ Connection error handling
- ✅ Timeout handling
- ✅ HTTP error handling (422, 500)
- ✅ Empty results handling

**Mock Example**:
```python
import pytest
from unittest.mock import Mock, patch

@patch('requests.post')
def test_search_success(mock_post):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"text": "Result 1", "score": 0.9, "source": "doc1"}
    ]
    mock_post.return_value = mock_response
    
    client = SearchAPIClient("http://localhost:8000")
    
    # Act
    results = client.search("test query", "semantic")
    
    # Assert
    assert len(results) == 1
    assert results[0]["text"] == "Result 1"
    mock_post.assert_called_once_with(
        "http://localhost:8000/search",
        json={"query": "test query", "search_type": "semantic"},
        timeout=30
    )
```

---

### Integration Tests

**Prerequisites**:
- FastAPI server must be running
- Knowledge base must be indexed with test data

**Test Scenarios**:
```python
def test_integration_semantic_search():
    client = SearchAPIClient("http://localhost:8000")
    results = client.search("RAG architecture", "semantic")
    assert len(results) > 0
    assert all("text" in r and "score" in r for r in results)

def test_integration_comparison():
    client = SearchAPIClient("http://localhost:8000")
    query = "machine learning"
    
    semantic = client.search(query, "semantic")
    hybrid = client.search(query, "hybrid")
    merged = client.search(query, "merged")
    
    # All strategies should return results
    assert len(semantic) > 0
    assert len(hybrid) > 0
    assert len(merged) > 0
```

---

## Performance Requirements

**Response Time**:
- Target: <5 seconds for typical queries
- Maximum acceptable: 10 seconds
- Timeout: 30 seconds (configurable)

**Throughput**:
- Single-user local development: No specific requirements
- Expected load: 1-10 queries per minute

**Result Limits**:
- UI displays top 5 results in comparison mode
- UI displays top 10 results in chat mode
- API may return more (no hard limit enforced)

---

## Security Considerations

**Authentication**: None (local development only)  
**Authorization**: None (local development only)  
**Data Validation**: 
- Client-side: Empty query prevention
- Server-side: Pydantic validation in FastAPI

**Network**:
- Communication over HTTP (localhost only)
- HTTPS not required for local development
- CORS not applicable (same-origin)

---

## Versioning & Compatibility

**API Version**: 1.0 (implicit, no version in URL)  
**Breaking Changes**: None expected  
**Deprecation Policy**: Not applicable (local development)

**Compatibility Matrix**:
| UI Component | API Version | Status |
|--------------|-------------|--------|
| Streamlit Chat | 1.0 | ✅ Compatible |
| Streamlit Comparison | 1.0 | ✅ Compatible |

---

## Troubleshooting Guide

### Common Issues

**1. Connection Refused**
```
Error: Unable to connect to search API
Solution: Ensure FastAPI server is running with `uvicorn api:app --reload`
```

**2. Invalid Search Type**
```
Error: Invalid search_type. Must be one of: semantic, hybrid, merged
Solution: Use only supported strategy values
```

**3. Empty Results**
```
Results: []
Possible causes:
- Query doesn't match indexed content
- Knowledge base not populated
- Search strategy may not work well for this query type
```

**4. Timeout**
```
Error: Search request timed out
Solutions:
- Increase timeout in .env: API_TIMEOUT=60
- Check API server performance
- Verify knowledge base size is reasonable
```

---

## Monitoring & Logging

**Client-Side Logging** (recommended):
```python
import logging

logger = logging.getLogger(__name__)

def search_with_logging(client, query, strategy):
    logger.info(f"Executing {strategy} search: {query[:50]}...")
    try:
        results = client.search(query, strategy)
        logger.info(f"Search successful: {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise
```

**Metrics to Track**:
- Search query count per strategy
- Average response time
- Error rate by error type
- Empty result rate

---

## Future Enhancements

**Not in Current Scope**:
- Pagination support
- Result filtering/sorting options
- Bulk search operations
- Asynchronous search
- Result caching
- Authentication/API keys
- Rate limiting
- WebSocket support for streaming results
