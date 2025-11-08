"""
Display utilities for Streamlit UI.

Provides reusable components for rendering search results, messages,
and other UI elements consistently across pages.
"""
import streamlit as st
from typing import List, Dict, Any


def render_search_results(
    results: List[Dict[str, Any]],
    max_results: int = 10,
    show_scores: bool = True
) -> None:
    """
    Render search results in a consistent format.
    
    Args:
        results: List of result dictionaries with text, score, source
        max_results: Maximum number of results to display
        show_scores: Whether to show relevance scores
        
    Example:
        >>> results = client.search("RAG", "semantic")
        >>> render_search_results(results, max_results=5)
    """
    if not results:
        st.info("No results found.")
        return
    
    # Display result count
    total = len(results)
    showing = min(max_results, total)
    
    if total > showing:
        st.caption(f"Showing top {showing} of {total} results")
    else:
        st.caption(f"{total} result{'s' if total != 1 else ''} found")
    
    # Render each result
    for i, result in enumerate(results[:max_results], 1):
        with st.container():
            # Header with score
            if show_scores:
                score = result.get("score", 0.0)
                st.markdown(f"**Result {i}** • Score: {score:.3f}")
            else:
                st.markdown(f"**Result {i}**")
            
            # Result text
            text = result.get("text", "")
            st.write(text)
            
            # Source
            source = result.get("source", "Unknown")
            st.caption(f"Source: `{source}`")
            
            # Divider between results
            if i < showing:
                st.divider()


def render_comparison_results(
    results_by_strategy: Dict[str, List[Dict[str, Any]]],
    max_per_strategy: int = 5
) -> None:
    """
    Render search results in vertical stacked format by strategy.
    
    Args:
        results_by_strategy: Dictionary mapping strategy name to results
        max_per_strategy: Maximum results to show per strategy
        
    Example:
        >>> results = {
        ...     "semantic": client.search("RAG", "semantic"),
        ...     "hybrid": client.search("RAG", "hybrid"),
        ...     "merged": client.search("RAG", "merged")
        ... }
        >>> render_comparison_results(results)
    """
    strategies = list(results_by_strategy.keys())
    num_strategies = len(strategies)
    
    if num_strategies == 0:
        st.warning("No results to compare.")
        return
    
    # Render each strategy's results vertically
    for strategy_idx, strategy in enumerate(strategies):
        # Strategy header with visual separation
        st.markdown(f"### 🔍 {strategy.title()} Strategy")
        
        results = results_by_strategy[strategy]
        
        if not results:
            st.info("No results found")
        else:
            # Show result count
            total = len(results)
            showing = min(max_per_strategy, total)
            if total > showing:
                st.caption(f"Showing top {showing} of {total} results")
            else:
                st.caption(f"{total} result{'s' if total != 1 else ''} found")
            
            # Render results in a clean list format
            for i, result in enumerate(results[:max_per_strategy], 1):
                score = result.get("score", 0.0)
                text = result.get("text", "")
                source = result.get("source", "Unknown")
                
                # Result container with clear hierarchy
                with st.container():
                    col1, col2 = st.columns([1, 10])
                    
                    with col1:
                        # Rank indicator
                        st.markdown(f"**#{i}**")
                    
                    with col2:
                        # Score badge
                        st.markdown(f"**Score:** `{score:.3f}`")
                        
                        # Result text
                        st.write(text)
                        
                        # Source
                        st.caption(f"📄 Source: `{source}`")
                    
                    # Divider between results
                    if i < showing:
                        st.divider()
        
        # Divider between strategies (not after the last one)
        if strategy_idx < num_strategies - 1:
            st.markdown("---")
            st.write("")  # Extra spacing


def render_error(error_message: str, title: str = "Error") -> None:
    """
    Render error message in consistent format.
    
    Args:
        error_message: Error message to display
        title: Optional title for the error
        
    Example:
        >>> render_error("Unable to connect to API", "Connection Error")
    """
    st.error(f"**{title}**: {error_message}")


def format_result_count(count: int, context: str = "result") -> str:
    """
    Format result count with proper pluralization.
    
    Args:
        count: Number of results
        context: Context word (e.g., "result", "message")
        
    Returns:
        Formatted string like "5 results" or "1 result"
        
    Example:
        >>> format_result_count(5)
        '5 results'
        >>> format_result_count(1)
        '1 result'
    """
    plural = f"{context}s" if count != 1 else context
    return f"{count} {plural}"


def show_api_health_indicator(is_healthy: bool) -> None:
    """
    Display API health status indicator.
    
    Args:
        is_healthy: Whether API is healthy
        
    Example:
        >>> client = get_default_client()
        >>> show_api_health_indicator(client.health_check())
    """
    if is_healthy:
        st.success("🟢 API Connected")
    else:
        st.error("🔴 API Unavailable")
        st.caption("Ensure FastAPI server is running at localhost:8000")
