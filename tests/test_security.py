"""Security feature tests for API authentication and file path validation."""
import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch
from api import app
from config import get_kb_client
from indexing import validate_file_path, DATA_DIR


class TestConfigSecurity:
    """Test config.py security features."""
    
    def test_get_kb_client_missing_url(self):
        """Test that get_kb_client raises error when KB_URL is missing."""
        env_vars = os.environ.copy()
        if 'KB_URL' in env_vars:
            del env_vars['KB_URL']
        env_vars['KB_API_KEY'] = 'test-key'
        
        with patch.dict(os.environ, env_vars, clear=True):
            # Need to reload config module to pick up new env vars
            from importlib import reload
            import config as config_module
            reload(config_module)
            with pytest.raises(ValueError, match="KB_URL"):
                config_module.get_kb_client()
    
    def test_get_kb_client_missing_api_key(self):
        """Test that get_kb_client raises error when KB_API_KEY is missing."""
        env_vars = os.environ.copy()
        env_vars['KB_URL'] = 'http://test.com'
        if 'KB_API_KEY' in env_vars:
            del env_vars['KB_API_KEY']
        
        with patch.dict(os.environ, env_vars, clear=True):
            # Need to reload config module to pick up new env vars
            from importlib import reload
            import config as config_module
            reload(config_module)
            with pytest.raises(ValueError, match="KB_API_KEY"):
                config_module.get_kb_client()


class TestFilePathValidation:
    """Test file path validation and constraints."""
    
    def test_validate_file_path_in_data_dir(self, tmp_path):
        """Test that files within DATA_DIR are accepted."""
        # Create a test file in a temporary data directory
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")
        
        with patch('indexing.DATA_DIR', tmp_path):
            validated = validate_file_path(str(test_file))
            assert validated == test_file.resolve()
    
    def test_validate_file_path_outside_data_dir(self, tmp_path):
        """Test that files outside DATA_DIR are rejected."""
        # Create a file outside the data directory
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "test.pdf"
        outside_file.write_text("test content")
        
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        with patch('indexing.DATA_DIR', data_dir):
            with pytest.raises(ValueError, match="must be within"):
                validate_file_path(str(outside_file))
    
    def test_validate_file_path_traversal_attempt(self, tmp_path):
        """Test that path traversal attempts are blocked."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create a file outside data dir
        outside_file = tmp_path / "secret.txt"
        outside_file.write_text("secret")
        
        # Try to access it using path traversal
        with patch('indexing.DATA_DIR', data_dir):
            with pytest.raises(ValueError):
                validate_file_path(str(data_dir / ".." / "secret.txt"))
    
    def test_validate_file_path_nonexistent(self, tmp_path):
        """Test that nonexistent files are rejected."""
        with patch('indexing.DATA_DIR', tmp_path):
            with pytest.raises(ValueError, match="does not exist"):
                validate_file_path(str(tmp_path / "nonexistent.pdf"))
    
    def test_validate_file_path_directory(self, tmp_path):
        """Test that directories are rejected."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        
        with patch('indexing.DATA_DIR', tmp_path):
            with pytest.raises(ValueError, match="not a file"):
                validate_file_path(str(test_dir))


class TestAPIAuthentication:
    """Test API authentication features."""
    
    @patch('api.search_merged')
    def test_search_without_api_key_when_not_required(self, mock_search):
        """Test that search works without API key when API_KEY env var is not set."""
        mock_search.return_value = []
        
        # Ensure API_KEY is not set
        with patch.dict(os.environ, {}, clear=False):
            if 'API_KEY' in os.environ:
                del os.environ['API_KEY']
            
            client = TestClient(app)
            response = client.post("/search", json={"query": "test"})
            # Should not be 401 Unauthorized
            assert response.status_code != 401
            # Should be 200 OK
            assert response.status_code == 200
    
    @patch('api.search_merged')
    def test_search_with_valid_api_key(self, mock_search):
        """Test that search works with valid API key when required."""
        mock_search.return_value = []
        test_api_key = "test-secret-key"
        
        with patch.dict(os.environ, {"API_KEY": test_api_key}):
            client = TestClient(app)
            response = client.post(
                "/search",
                json={"query": "test"},
                headers={"X-API-Key": test_api_key}
            )
            # Should not be 401 Unauthorized
            assert response.status_code != 401
            # Should be 200 OK
            assert response.status_code == 200
    
    def test_search_with_invalid_api_key(self):
        """Test that search rejects invalid API key when required."""
        with patch.dict(os.environ, {"API_KEY": "correct-key"}):
            client = TestClient(app)
            response = client.post(
                "/search",
                json={"query": "test"},
                headers={"X-API-Key": "wrong-key"}
            )
            assert response.status_code == 401
            assert "Invalid or missing API key" in response.json()["detail"]
    
    def test_search_without_api_key_when_required(self):
        """Test that search rejects request without API key when required."""
        with patch.dict(os.environ, {"API_KEY": "required-key"}):
            client = TestClient(app)
            response = client.post(
                "/search",
                json={"query": "test"}
                # No X-API-Key header
            )
            assert response.status_code == 401
            assert "Invalid or missing API key" in response.json()["detail"]


class TestErrorHandling:
    """Test generic error handling."""
    
    def test_generic_error_response(self):
        """Test that unhandled exceptions return generic error messages."""
        client = TestClient(app)
        
        # Trigger an error by using invalid search type
        response = client.post(
            "/search",
            json={"query": "test", "search_type": "invalid"}
        )
        
        # Should return an error but not leak stack traces
        json_response = response.json()
        assert "detail" in json_response
        # Should not contain sensitive implementation details
        assert "traceback" not in str(json_response).lower()
        assert "stack" not in str(json_response).lower()
