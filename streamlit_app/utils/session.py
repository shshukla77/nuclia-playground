"""
Session state management utilities for Streamlit.

Provides consistent session state initialization and access patterns
for chat history, search results, and user preferences.
"""
import streamlit as st
from typing import List, Dict, Any, Optional


def init_session_state() -> None:
    """
    Initialize all session state variables with default values.
    
    Should be called at the start of each page to ensure
    consistent session state structure.
    
    Example:
        >>> init_session_state()
        >>> st.write(len(st.session_state.messages))
        0
    """
    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Current search strategy
    if "current_strategy" not in st.session_state:
        st.session_state.current_strategy = "merged"
    
    # Last search query
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    
    # Comparison results cache
    if "comparison_results" not in st.session_state:
        st.session_state.comparison_results = {}
    
    # API client cache
    if "api_client" not in st.session_state:
        from utils.api_client import get_default_client
        st.session_state.api_client = get_default_client()


def add_message(role: str, content: str, metadata: Dict[str, Any] = None) -> None:
    """
    Add a message to the chat history.
    
    Args:
        role: Message role ("user" or "assistant")
        content: Message content
        metadata: Optional metadata (strategy, results, etc.)
        
    Example:
        >>> add_message("user", "What is RAG?")
        >>> add_message(
        ...     "assistant",
        ...     "RAG is...",
        ...     metadata={"strategy": "semantic", "result_count": 5}
        ... )
    """
    message = {
        "role": role,
        "content": content,
        "metadata": metadata or {}
    }
    st.session_state.messages.append(message)


def get_messages() -> List[Dict[str, Any]]:
    """
    Get all chat messages.
    
    Returns:
        List of message dictionaries
        
    Example:
        >>> messages = get_messages()
        >>> for msg in messages:
        ...     print(f"{msg['role']}: {msg['content'][:50]}")
        user: What is RAG?
        assistant: RAG is a technique that combines retrieval...
    """
    if "messages" not in st.session_state:
        init_session_state()
    return st.session_state.messages


def clear_messages() -> None:
    """
    Clear all chat messages.
    
    Example:
        >>> clear_messages()
        >>> len(get_messages())
        0
    """
    st.session_state.messages = []


def set_strategy(strategy: str) -> None:
    """
    Set the current search strategy.
    
    Args:
        strategy: Strategy name ("semantic", "hybrid", or "merged")
        
    Example:
        >>> set_strategy("semantic")
        >>> get_strategy()
        'semantic'
    """
    st.session_state.current_strategy = strategy


def get_strategy() -> str:
    """
    Get the current search strategy.
    
    Returns:
        Current strategy name
        
    Example:
        >>> get_strategy()
        'merged'
    """
    if "current_strategy" not in st.session_state:
        init_session_state()
    return st.session_state.current_strategy


def set_last_query(query: str) -> None:
    """
    Store the last executed query.
    
    Args:
        query: Search query string
        
    Example:
        >>> set_last_query("What is RAG?")
    """
    st.session_state.last_query = query


def get_last_query() -> str:
    """
    Get the last executed query.
    
    Returns:
        Last query string (empty if none)
        
    Example:
        >>> get_last_query()
        'What is RAG?'
    """
    if "last_query" not in st.session_state:
        init_session_state()
    return st.session_state.last_query


def cache_comparison_results(
    query: str,
    results: Dict[str, List[Dict[str, Any]]]
) -> None:
    """
    Cache comparison results for a query with LRU eviction.
    
    Maintains a maximum of 20 cached queries. When limit is reached,
    removes the oldest cached entry.
    
    Args:
        query: The search query
        results: Dictionary mapping strategy to results list
        
    Example:
        >>> results = {
        ...     "semantic": [...],
        ...     "hybrid": [...],
        ...     "merged": [...]
        ... }
        >>> cache_comparison_results("RAG", results)
    """
    MAX_CACHE_SIZE = 20
    
    # Remove oldest entry if at capacity
    if len(st.session_state.comparison_results) >= MAX_CACHE_SIZE:
        if query not in st.session_state.comparison_results:
            # Remove first (oldest) key
            oldest_key = next(iter(st.session_state.comparison_results))
            del st.session_state.comparison_results[oldest_key]
    
    st.session_state.comparison_results[query] = results


def get_cached_comparison_results(query: str) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    Get cached comparison results for a query.
    
    Args:
        query: The search query
        
    Returns:
        Cached results dictionary or None if not cached
        
    Example:
        >>> results = get_cached_comparison_results("RAG")
        >>> if results:
        ...     print("Using cached results")
        Using cached results
    """
    if "comparison_results" not in st.session_state:
        init_session_state()
    return st.session_state.comparison_results.get(query)


def clear_cache() -> None:
    """
    Clear all cached comparison results.
    
    Example:
        >>> clear_cache()
    """
    st.session_state.comparison_results = {}


def get_api_client():
    """
    Get the shared API client instance.
    
    Returns:
        SearchAPIClient instance
        
    Example:
        >>> client = get_api_client()
        >>> results = client.search("test query")
    """
    if "api_client" not in st.session_state:
        init_session_state()
    return st.session_state.api_client


def get_message_count() -> int:
    """
    Get the total number of messages in chat history.
    
    Returns:
        Number of messages
        
    Example:
        >>> get_message_count()
        12
    """
    return len(get_messages())


def get_last_assistant_message() -> Optional[Dict[str, Any]]:
    """
    Get the most recent assistant message.
    
    Returns:
        Last assistant message dict or None if no assistant messages
        
    Example:
        >>> last_msg = get_last_assistant_message()
        >>> if last_msg:
        ...     print(last_msg['content'])
        RAG is a technique...
    """
    messages = get_messages()
    for message in reversed(messages):
        if message["role"] == "assistant":
            return message
    return None
