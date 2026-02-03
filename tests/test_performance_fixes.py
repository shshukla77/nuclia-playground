"""
Tests for performance improvements.

This module tests the performance fixes:
1. Parallel file processing in indexing.py
2. Exponential backoff in utils.py
3. LRU cache in streamlit_app/utils/session.py
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import time


# Test 1: Parallel File Processing
@pytest.mark.asyncio
async def test_upload_folder_processes_files_in_parallel():
    """Test that upload_folder processes files concurrently."""
    from indexing import upload_folder
    
    # Create temporary directory structure
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create mock PDF files
        for i in range(3):
            (tmp_path / f"test{i}.pdf").touch()
        
        # Mock upsert_file to track timing
        call_times = []
        
        async def mock_upsert_file(*args, **kwargs):
            call_times.append(time.time())
            await asyncio.sleep(0.1)  # Simulate processing time
            return f"rid_{len(call_times)}", True
        
        with patch('indexing.upsert_file', side_effect=mock_upsert_file):
            start_time = time.time()
            results = await upload_folder(tmp_path, wait=False)
            total_time = time.time() - start_time
            
            # Verify results
            assert len(results) == 3
            
            # Verify parallel execution (should take ~0.1s, not ~0.3s)
            # Allow some overhead for test execution
            assert total_time < 0.25, f"Expected parallel execution, but took {total_time}s"
            
            # Verify all calls started within a short window
            if len(call_times) >= 2:
                time_spread = max(call_times) - min(call_times)
                assert time_spread < 0.1, f"Calls should start concurrently, but spread was {time_spread}s"


@pytest.mark.asyncio
async def test_upload_folder_handles_errors_gracefully():
    """Test that upload_folder handles individual file errors."""
    from indexing import upload_folder
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create mock PDF files
        for i in range(3):
            (tmp_path / f"test{i}.pdf").touch()
        
        # Mock upsert_file to fail on second file
        call_count = [0]
        
        async def mock_upsert_file(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Simulated error")
            return f"rid_{call_count[0]}", True
        
        with patch('indexing.upsert_file', side_effect=mock_upsert_file):
            # Should raise exception due to asyncio.gather behavior
            with pytest.raises(Exception, match="Simulated error"):
                await upload_folder(tmp_path, wait=False)


# Test 2: Exponential Backoff
@pytest.mark.asyncio
async def test_wait_until_processed_uses_exponential_backoff():
    """Test that wait_until_processed uses exponential backoff."""
    from utils import wait_until_processed
    from nucliadb_models.metadata import ResourceProcessingStatus
    
    # Track sleep intervals
    sleep_intervals = []
    
    async def mock_sleep(duration):
        sleep_intervals.append(duration)
    
    # Mock resource API
    call_count = [0]
    mock_res = Mock()
    mock_res.metadata.status = ResourceProcessingStatus.PENDING
    
    async def mock_get(*args, **kwargs):
        call_count[0] += 1
        # Return PROCESSED on 5th call
        if call_count[0] >= 5:
            mock_res.metadata.status = ResourceProcessingStatus.PROCESSED
        return mock_res
    
    mock_api = AsyncMock()
    mock_api.get = mock_get
    
    with patch('utils.sdk.AsyncNucliaResource', return_value=mock_api):
        with patch('asyncio.sleep', side_effect=mock_sleep):
            result = await wait_until_processed("test_rid", interval=2, timeout=900)
            
            assert result == mock_res
            assert len(sleep_intervals) == 4  # 4 sleeps before 5th successful call
            
            # Verify exponential backoff (2, 3, 4.5, 6.75)
            assert sleep_intervals[0] == 2.0
            assert 2.9 < sleep_intervals[1] < 3.1  # ~3.0
            assert 4.4 < sleep_intervals[2] < 4.6  # ~4.5
            assert 6.6 < sleep_intervals[3] < 6.9  # ~6.75


@pytest.mark.asyncio
async def test_wait_until_processed_caps_at_max_interval():
    """Test that backoff interval is capped at 30 seconds."""
    from utils import wait_until_processed
    from nucliadb_models.metadata import ResourceProcessingStatus
    
    sleep_intervals = []
    
    async def mock_sleep(duration):
        sleep_intervals.append(duration)
    
    call_count = [0]
    mock_res = Mock()
    mock_res.metadata.status = ResourceProcessingStatus.PENDING
    
    async def mock_get(*args, **kwargs):
        call_count[0] += 1
        # Return PROCESSED after many calls
        if call_count[0] >= 20:
            mock_res.metadata.status = ResourceProcessingStatus.PROCESSED
        return mock_res
    
    mock_api = AsyncMock()
    mock_api.get = mock_get
    
    with patch('utils.sdk.AsyncNucliaResource', return_value=mock_api):
        with patch('asyncio.sleep', side_effect=mock_sleep):
            await wait_until_processed("test_rid", interval=2, timeout=900)
            
            # Verify that intervals are capped at 30
            for interval in sleep_intervals[10:]:  # After sufficient backoff
                assert interval <= 30.0, f"Interval {interval} exceeds max of 30"


@pytest.mark.asyncio
async def test_wait_until_processed_timeout():
    """Test that wait_until_processed raises TimeoutError."""
    from utils import wait_until_processed
    from nucliadb_models.metadata import ResourceProcessingStatus
    
    mock_res = Mock()
    mock_res.metadata.status = ResourceProcessingStatus.PENDING
    
    async def mock_get(*args, **kwargs):
        return mock_res
    
    mock_api = AsyncMock()
    mock_api.get = mock_get
    
    with patch('utils.sdk.AsyncNucliaResource', return_value=mock_api):
        with pytest.raises(TimeoutError, match="Timed out waiting for"):
            # Very short timeout to force error
            await wait_until_processed("test_rid", interval=2, timeout=0.1)


# Test 3: LRU Cache
def test_cache_comparison_results_respects_size_limit():
    """Test that cache_comparison_results maintains size limit."""
    from streamlit_app.utils.session import cache_comparison_results
    import streamlit as st
    
    # Initialize session state
    if "comparison_results" not in st.session_state:
        st.session_state.comparison_results = {}
    
    # Clear cache
    st.session_state.comparison_results = {}
    
    # Add 25 entries (exceeds limit of 20)
    for i in range(25):
        cache_comparison_results(
            f"query_{i}",
            {"semantic": [], "hybrid": [], "merged": []}
        )
    
    # Cache should contain only 20 entries
    assert len(st.session_state.comparison_results) == 20
    
    # First 5 entries should be evicted
    for i in range(5):
        assert f"query_{i}" not in st.session_state.comparison_results
    
    # Last 20 entries should be present
    for i in range(5, 25):
        assert f"query_{i}" in st.session_state.comparison_results


def test_cache_comparison_results_updates_existing_entry():
    """Test that updating an existing entry doesn't trigger eviction."""
    from streamlit_app.utils.session import cache_comparison_results
    import streamlit as st
    
    # Initialize and clear cache
    if "comparison_results" not in st.session_state:
        st.session_state.comparison_results = {}
    st.session_state.comparison_results = {}
    
    # Add 20 entries (at limit)
    for i in range(20):
        cache_comparison_results(
            f"query_{i}",
            {"semantic": [{"text": f"result_{i}"}]}
        )
    
    assert len(st.session_state.comparison_results) == 20
    
    # Update an existing entry
    cache_comparison_results(
        "query_10",
        {"semantic": [{"text": "updated_result"}]}
    )
    
    # Should still have 20 entries
    assert len(st.session_state.comparison_results) == 20
    
    # Verify update
    assert st.session_state.comparison_results["query_10"]["semantic"][0]["text"] == "updated_result"


def test_cache_comparison_results_evicts_oldest():
    """Test that oldest entry is evicted when adding new entry at capacity."""
    from streamlit_app.utils.session import cache_comparison_results
    import streamlit as st
    
    # Initialize and clear cache
    if "comparison_results" not in st.session_state:
        st.session_state.comparison_results = {}
    st.session_state.comparison_results = {}
    
    # Add 20 entries in order
    for i in range(20):
        cache_comparison_results(f"query_{i}", {"results": [i]})
    
    # Add one more (should evict query_0)
    cache_comparison_results("query_new", {"results": ["new"]})
    
    assert len(st.session_state.comparison_results) == 20
    assert "query_0" not in st.session_state.comparison_results
    assert "query_new" in st.session_state.comparison_results
    assert "query_1" in st.session_state.comparison_results


# Test 4: Async HTTP Client
@pytest.mark.asyncio
async def test_search_api_client_uses_async_http():
    """Test that SearchAPIClient uses async HTTP."""
    from streamlit_app.utils.api_client import SearchAPIClient
    
    client = SearchAPIClient("http://localhost:8000", timeout=30)
    
    # Mock httpx.AsyncClient
    mock_response = Mock()
    mock_response.json.return_value = [
        {"text": "result1", "score": 0.9, "source": "source1"}
    ]
    mock_response.raise_for_status = Mock()
    
    mock_async_client = AsyncMock()
    mock_async_client.post = AsyncMock(return_value=mock_response)
    
    with patch.object(client, '_get_client', return_value=mock_async_client):
        results = await client.search("test query", "semantic")
        
        # Verify async client was used
        mock_async_client.post.assert_called_once()
        assert results == [{"text": "result1", "score": 0.9, "source": "source1"}]


@pytest.mark.asyncio
async def test_search_api_client_handles_async_errors():
    """Test that SearchAPIClient handles async errors properly."""
    from streamlit_app.utils.api_client import SearchAPIClient
    import httpx
    
    client = SearchAPIClient("http://localhost:8000", timeout=30)
    
    # Mock connection error
    mock_async_client = AsyncMock()
    mock_async_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
    
    with patch.object(client, '_get_client', return_value=mock_async_client):
        with pytest.raises(httpx.ConnectError):
            await client.search("test query", "semantic")


@pytest.mark.asyncio
async def test_safe_search_async():
    """Test that safe_search works with async client."""
    from streamlit_app.utils.api_client import SearchAPIClient, safe_search
    
    client = SearchAPIClient("http://localhost:8000", timeout=30)
    
    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = [{"text": "result", "score": 0.8}]
    mock_response.raise_for_status = Mock()
    
    mock_async_client = AsyncMock()
    mock_async_client.post = AsyncMock(return_value=mock_response)
    
    with patch.object(client, '_get_client', return_value=mock_async_client):
        response = await safe_search(client, "test query", "semantic")
        
        assert response["success"] is True
        assert len(response["results"]) == 1
        assert response["error"] is None


@pytest.mark.asyncio
async def test_client_cleanup():
    """Test that SearchAPIClient properly cleans up resources."""
    from streamlit_app.utils.api_client import SearchAPIClient
    
    client = SearchAPIClient("http://localhost:8000")
    
    # Create a mock client
    mock_async_client = AsyncMock()
    client._client = mock_async_client
    
    # Close the client
    await client.close()
    
    # Verify cleanup
    mock_async_client.aclose.assert_called_once()
    assert client._client is None
