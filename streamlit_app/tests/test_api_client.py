"""
Tests for SearchAPIClient.

Following TDD approach - tests written before implementation.
Tests cover all requirements from API Integration Contract:
- Successful searches (all strategies)
- Validation errors
- Connection errors
- Timeout handling
- HTTP error responses
- Empty results
- Health check
"""
import pytest
from unittest.mock import Mock, patch
import requests


class TestSearchAPIClient:
    """Test suite for SearchAPIClient class."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        from utils.api_client import SearchAPIClient
        return SearchAPIClient("http://localhost:8000", timeout=30)
    
    # T008: Test successful search with semantic strategy
    @patch('requests.post')
    def test_search_semantic_success(self, mock_post, client):
        """Test successful semantic search returns results."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "text": "RAG combines retrieval with generation",
                "score": 0.89,
                "source": "a/intro/overview"
            },
            {
                "text": "RAG systems use vector search",
                "score": 0.85,
                "source": "a/arch/components"
            }
        ]
        mock_post.return_value = mock_response
        
        # Act
        results = client.search("What is RAG?", "semantic")
        
        # Assert
        assert len(results) == 2
        assert results[0]["text"] == "RAG combines retrieval with generation"
        assert results[0]["score"] == 0.89
        assert results[0]["source"] == "a/intro/overview"
        
        mock_post.assert_called_once_with(
            "http://localhost:8000/search",
            json={"query": "What is RAG?", "search_type": "semantic"},
            timeout=30
        )
    
    # T009: Test successful search with hybrid strategy
    @patch('requests.post')
    def test_search_hybrid_success(self, mock_post, client):
        """Test successful hybrid search returns results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"text": "Hybrid result", "score": 0.75, "source": "doc1"}
        ]
        mock_post.return_value = mock_response
        
        results = client.search("machine learning", "hybrid")
        
        assert len(results) == 1
        assert results[0]["score"] == 0.75
        mock_post.assert_called_with(
            "http://localhost:8000/search",
            json={"query": "machine learning", "search_type": "hybrid"},
            timeout=30
        )
    
    # T010: Test successful search with merged strategy (default)
    @patch('requests.post')
    def test_search_merged_success(self, mock_post, client):
        """Test successful merged search (default strategy)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"text": "Merged result", "score": 0.92, "source": "doc2"}
        ]
        mock_post.return_value = mock_response
        
        results = client.search("neural networks", "merged")
        
        assert len(results) == 1
        mock_post.assert_called_with(
            "http://localhost:8000/search",
            json={"query": "neural networks", "search_type": "merged"},
            timeout=30
        )
    
    # T011: Test empty query validation
    def test_search_empty_query_error(self, client):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            client.search("", "semantic")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            client.search("   ", "semantic")
    
    # T012: Test invalid search_type validation
    def test_search_invalid_type_error(self, client):
        """Test that invalid search_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid search_type"):
            client.search("test query", "invalid_strategy")
        
        with pytest.raises(ValueError, match="Must be one of: semantic, hybrid, merged"):
            client.search("test query", "keyword")
    
    # T013: Test connection error handling
    @patch('requests.post')
    def test_search_connection_error(self, mock_post, client):
        """Test connection error when API server unavailable."""
        mock_post.side_effect = requests.ConnectionError("Connection refused")
        
        with pytest.raises(requests.ConnectionError):
            client.search("test query", "semantic")
    
    # T014: Test timeout handling
    @patch('requests.post')
    def test_search_timeout_error(self, mock_post, client):
        """Test timeout error when request exceeds timeout limit."""
        mock_post.side_effect = requests.Timeout("Request timed out")
        
        with pytest.raises(requests.Timeout):
            client.search("test query", "semantic")
    
    # Additional tests for comprehensive coverage
    
    @patch('requests.post')
    def test_search_http_422_error(self, mock_post, client):
        """Test HTTP 422 error (validation error from API)."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": "Invalid search_type. Must be one of: semantic, hybrid, merged"
        }
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            client.search("test", "semantic")
    
    @patch('requests.post')
    def test_search_http_500_error(self, mock_post, client):
        """Test HTTP 500 error (internal server error)."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "detail": "Search operation failed: database error"
        }
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            client.search("test", "semantic")
    
    @patch('requests.post')
    def test_search_empty_results(self, mock_post, client):
        """Test empty results array when no matches found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response
        
        results = client.search("nonexistent query", "semantic")
        
        assert results == []
        assert isinstance(results, list)
    
    @patch('requests.post')
    def test_search_strips_whitespace(self, mock_post, client):
        """Test that query whitespace is stripped before sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response
        
        client.search("  query with spaces  ", "semantic")
        
        # Verify stripped query was sent
        call_args = mock_post.call_args
        assert call_args[1]["json"]["query"] == "query with spaces"
    
    @patch('requests.post')
    def test_search_strips_trailing_slash_from_base_url(self, mock_post):
        """Test that trailing slash is removed from base_url."""
        from utils.api_client import SearchAPIClient
        
        client = SearchAPIClient("http://localhost:8000/", timeout=30)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_post.return_value = mock_response
        
        client.search("test", "semantic")
        
        # Should call without double slash
        mock_post.assert_called_with(
            "http://localhost:8000/search",
            json={"query": "test", "search_type": "semantic"},
            timeout=30
        )
    
    # Health check tests
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get, client):
        """Test health check returns True when server responds."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        is_healthy = client.health_check()
        
        assert is_healthy is True
        mock_get.assert_called_once_with(
            "http://localhost:8000/docs",
            timeout=5
        )
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get, client):
        """Test health check returns False when server unreachable."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")
        
        is_healthy = client.health_check()
        
        assert is_healthy is False
    
    @patch('requests.get')
    def test_health_check_non_200_status(self, mock_get, client):
        """Test health check returns False on non-200 status."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response
        
        is_healthy = client.health_check()
        
        assert is_healthy is False


class TestSearchAPIClientInitialization:
    """Test SearchAPIClient initialization."""
    
    def test_init_with_defaults(self):
        """Test client initialization with default timeout."""
        from utils.api_client import SearchAPIClient
        
        client = SearchAPIClient("http://localhost:8000")
        
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30
    
    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        from utils.api_client import SearchAPIClient
        
        client = SearchAPIClient("http://localhost:8000", timeout=60)
        
        assert client.timeout == 60
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped during init."""
        from utils.api_client import SearchAPIClient
        
        client = SearchAPIClient("http://localhost:8000/")
        
        assert client.base_url == "http://localhost:8000"
