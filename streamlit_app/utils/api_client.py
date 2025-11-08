"""
API client for interacting with the FastAPI search service.

This module provides the SearchAPIClient class for executing search queries
against the backend API with comprehensive error handling and validation.
"""
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


# Load environment configuration
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


class SearchAPIClient:
    """
    Client for interacting with the search API.
    
    This client handles all communication with the FastAPI backend,
    including search requests and health checks.
    
    Example:
        >>> client = SearchAPIClient("http://localhost:8000")
        >>> results = client.search("What is RAG?", "semantic")
        >>> print(len(results))
        5
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    def search(
        self, 
        query: str, 
        search_type: str = "merged"
    ) -> List[Dict[str, Any]]:
        """
        Execute a search query against the API.
        
        Args:
            query: Search query string (non-empty)
            search_type: Search strategy - one of "semantic", "hybrid", or "merged"
            
        Returns:
            List of search results, each containing:
                - text (str): Result text content
                - score (float): Relevance score (0.0-1.0)
                - source (str): Source identifier
            
        Raises:
            ValueError: If query is empty or search_type is invalid
            requests.ConnectionError: If API server is unreachable
            requests.Timeout: If request exceeds timeout limit
            requests.HTTPError: If API returns error status (4xx, 5xx)
            
        Example:
            >>> results = client.search("machine learning", "semantic")
            >>> for result in results[:3]:
            ...     print(f"{result['score']:.2f}: {result['text'][:50]}")
            0.89: Machine learning is a subset of artificial...
            0.85: Deep learning uses neural networks with...
            0.82: Supervised learning requires labeled data...
        """
        # Validate query
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Validate search_type
        valid_types = ["semantic", "hybrid", "merged"]
        if search_type not in valid_types:
            raise ValueError(
                f"Invalid search_type: {search_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
        
        # Prepare request payload
        payload = {
            "query": query.strip(),
            "search_type": search_type
        }
        
        # Execute request
        response = requests.post(
            f"{self.base_url}/search",
            json=payload,
            timeout=self.timeout
        )
        
        # Raise exception for error status codes
        response.raise_for_status()
        
        # Return results
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check if the API server is reachable and responding.
        
        This performs a lightweight check by hitting the /docs endpoint
        with a short timeout (5 seconds).
        
        Returns:
            True if server responds with 200 status, False otherwise
            
        Example:
            >>> if client.health_check():
            ...     print("API is healthy")
            ... else:
            ...     print("API is unavailable")
            API is healthy
        """
        try:
            response = requests.get(
                f"{self.base_url}/docs",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            # Any exception means server is not healthy
            return False


def get_default_client() -> SearchAPIClient:
    """
    Create a SearchAPIClient with default configuration from environment.
    
    Loads API_BASE_URL and API_TIMEOUT from .env file.
    
    Returns:
        Configured SearchAPIClient instance
        
    Example:
        >>> client = get_default_client()
        >>> results = client.search("test query")
    """
    return SearchAPIClient(API_BASE_URL, API_TIMEOUT)


def safe_search(
    client: SearchAPIClient,
    query: str,
    strategy: str = "merged"
) -> Dict[str, Any]:
    """
    Execute search with comprehensive error handling.
    
    This is a convenience function that wraps client.search() with
    error handling, returning a structured response dictionary.
    
    Args:
        client: SearchAPIClient instance
        query: Search query string
        strategy: Search strategy (semantic/hybrid/merged)
        
    Returns:
        Dictionary with keys:
            - success (bool): Whether search succeeded
            - results (list): Search results (empty on error)
            - error (str|None): Error message if failed, None if successful
            
    Example:
        >>> client = get_default_client()
        >>> response = safe_search(client, "RAG architecture", "semantic")
        >>> if response["success"]:
        ...     print(f"Found {len(response['results'])} results")
        ... else:
        ...     print(f"Error: {response['error']}")
        Found 5 results
    """
    try:
        results = client.search(query, strategy)
        return {
            "success": True,
            "results": results,
            "error": None
        }
    except ValueError as e:
        # Validation error (empty query, invalid strategy)
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
            "error": (
                f"Unable to connect to search API. "
                f"Please ensure the API server is running at {client.base_url}."
            )
        }
    except requests.Timeout:
        # Request timed out
        return {
            "success": False,
            "results": [],
            "error": "Search request timed out. Please try again."
        }
    except requests.HTTPError as e:
        # API returned error status (4xx, 5xx)
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)
        
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
