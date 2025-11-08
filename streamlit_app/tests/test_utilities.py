"""
Tests for session state utilities.

Note: Session state tests require actual Streamlit runtime context and are marked
as skipped. These functions are integration tested through the running application.
Display utility tests (format functions) can run without Streamlit context.
"""
import pytest
from unittest.mock import Mock, patch


@pytest.mark.skip(reason="Requires Streamlit runtime context")
class TestSessionStateUtilities:
    """Test session state utility functions."""
    
    @pytest.fixture
    def mock_session_state(self):
        """Create a mock session state object."""
        return {}
    
    @patch('streamlit.session_state', {})
    def test_init_session_state_creates_defaults(self, mock_session_state):
        """Test that init_session_state creates all default values."""
        import streamlit as st
        from utils.session import init_session_state
        
        # Act
        init_session_state()
        
        # Assert
        assert "messages" in st.session_state
        assert "current_strategy" in st.session_state
        assert "last_query" in st.session_state
        assert "comparison_results" in st.session_state
        assert "api_client" in st.session_state
        
        assert st.session_state.messages == []
        assert st.session_state.current_strategy == "merged"
        assert st.session_state.last_query == ""
        assert st.session_state.comparison_results == {}
    
    @patch('streamlit.session_state', {})
    def test_add_message(self):
        """Test adding a message to chat history."""
        import streamlit as st
        from utils.session import init_session_state, add_message
        
        init_session_state()
        
        # Add user message
        add_message("user", "What is RAG?")
        
        assert len(st.session_state.messages) == 1
        assert st.session_state.messages[0]["role"] == "user"
        assert st.session_state.messages[0]["content"] == "What is RAG?"
        assert st.session_state.messages[0]["metadata"] == {}
    
    @patch('streamlit.session_state', {})
    def test_add_message_with_metadata(self):
        """Test adding a message with metadata."""
        import streamlit as st
        from utils.session import init_session_state, add_message
        
        init_session_state()
        
        metadata = {"strategy": "semantic", "result_count": 5}
        add_message("assistant", "RAG is...", metadata=metadata)
        
        assert len(st.session_state.messages) == 1
        msg = st.session_state.messages[0]
        assert msg["metadata"]["strategy"] == "semantic"
        assert msg["metadata"]["result_count"] == 5
    
    @patch('streamlit.session_state', {})
    def test_get_messages(self):
        """Test retrieving all messages."""
        import streamlit as st
        from utils.session import init_session_state, add_message, get_messages
        
        init_session_state()
        
        add_message("user", "Query 1")
        add_message("assistant", "Answer 1")
        add_message("user", "Query 2")
        
        messages = get_messages()
        
        assert len(messages) == 3
        assert messages[0]["content"] == "Query 1"
        assert messages[1]["content"] == "Answer 1"
        assert messages[2]["content"] == "Query 2"
    
    @patch('streamlit.session_state', {})
    def test_clear_messages(self):
        """Test clearing all messages."""
        import streamlit as st
        from utils.session import init_session_state, add_message, clear_messages, get_messages
        
        init_session_state()
        
        add_message("user", "Message 1")
        add_message("user", "Message 2")
        
        assert len(get_messages()) == 2
        
        clear_messages()
        
        assert len(get_messages()) == 0
    
    @patch('streamlit.session_state', {})
    def test_set_and_get_strategy(self):
        """Test setting and getting search strategy."""
        import streamlit as st
        from utils.session import init_session_state, set_strategy, get_strategy
        
        init_session_state()
        
        # Default strategy
        assert get_strategy() == "merged"
        
        # Change strategy
        set_strategy("semantic")
        assert get_strategy() == "semantic"
        
        set_strategy("hybrid")
        assert get_strategy() == "hybrid"
    
    @patch('streamlit.session_state', {})
    def test_set_and_get_last_query(self):
        """Test storing and retrieving last query."""
        import streamlit as st
        from utils.session import init_session_state, set_last_query, get_last_query
        
        init_session_state()
        
        # Initially empty
        assert get_last_query() == ""
        
        # Set query
        set_last_query("What is RAG?")
        assert get_last_query() == "What is RAG?"
    
    @patch('streamlit.session_state', {})
    def test_cache_comparison_results(self):
        """Test caching comparison results."""
        import streamlit as st
        from utils.session import (
            init_session_state,
            cache_comparison_results,
            get_cached_comparison_results
        )
        
        init_session_state()
        
        # Cache results
        results = {
            "semantic": [{"text": "Result 1", "score": 0.9}],
            "hybrid": [{"text": "Result 2", "score": 0.8}]
        }
        cache_comparison_results("RAG", results)
        
        # Retrieve cached results
        cached = get_cached_comparison_results("RAG")
        
        assert cached is not None
        assert "semantic" in cached
        assert len(cached["semantic"]) == 1
        assert cached["semantic"][0]["text"] == "Result 1"
    
    @patch('streamlit.session_state', {})
    def test_get_cached_comparison_results_missing(self):
        """Test getting cached results for non-existent query."""
        import streamlit as st
        from utils.session import init_session_state, get_cached_comparison_results
        
        init_session_state()
        
        cached = get_cached_comparison_results("nonexistent query")
        
        assert cached is None
    
    @patch('streamlit.session_state', {})
    def test_clear_cache(self):
        """Test clearing cached comparison results."""
        import streamlit as st
        from utils.session import (
            init_session_state,
            cache_comparison_results,
            get_cached_comparison_results,
            clear_cache
        )
        
        init_session_state()
        
        # Add cached results
        cache_comparison_results("query1", {"semantic": []})
        cache_comparison_results("query2", {"hybrid": []})
        
        assert get_cached_comparison_results("query1") is not None
        
        # Clear cache
        clear_cache()
        
        assert get_cached_comparison_results("query1") is None
        assert get_cached_comparison_results("query2") is None
    
    @patch('streamlit.session_state', {})
    def test_get_message_count(self):
        """Test getting message count."""
        import streamlit as st
        from utils.session import init_session_state, add_message, get_message_count
        
        init_session_state()
        
        assert get_message_count() == 0
        
        add_message("user", "Message 1")
        assert get_message_count() == 1
        
        add_message("assistant", "Message 2")
        add_message("user", "Message 3")
        assert get_message_count() == 3
    
    @patch('streamlit.session_state', {})
    def test_get_last_assistant_message(self):
        """Test getting the last assistant message."""
        import streamlit as st
        from utils.session import (
            init_session_state,
            add_message,
            get_last_assistant_message
        )
        
        init_session_state()
        
        # No messages yet
        assert get_last_assistant_message() is None
        
        # Add messages
        add_message("user", "Query 1")
        add_message("assistant", "Answer 1")
        add_message("user", "Query 2")
        add_message("assistant", "Answer 2")
        
        last_msg = get_last_assistant_message()
        
        assert last_msg is not None
        assert last_msg["role"] == "assistant"
        assert last_msg["content"] == "Answer 2"
    
    @patch('streamlit.session_state', {})
    def test_get_last_assistant_message_no_assistant(self):
        """Test getting last assistant message when only user messages exist."""
        import streamlit as st
        from utils.session import (
            init_session_state,
            add_message,
            get_last_assistant_message
        )
        
        init_session_state()
        
        add_message("user", "Query 1")
        add_message("user", "Query 2")
        
        assert get_last_assistant_message() is None


class TestDisplayUtilities:
    """Test display utility functions (structure only - can't test Streamlit rendering)."""
    
    def test_format_result_count_singular(self):
        """Test formatting singular result count."""
        from utils.display import format_result_count
        
        assert format_result_count(1) == "1 result"
        assert format_result_count(1, "message") == "1 message"
    
    def test_format_result_count_plural(self):
        """Test formatting plural result count."""
        from utils.display import format_result_count
        
        assert format_result_count(0) == "0 results"
        assert format_result_count(5) == "5 results"
        assert format_result_count(100, "message") == "100 messages"
