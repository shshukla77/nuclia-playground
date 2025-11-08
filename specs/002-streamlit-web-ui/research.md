# Research & Design Decisions: Streamlit Web UI

**Feature**: 002-streamlit-web-ui  
**Date**: November 7, 2025  
**Phase**: 0 (Research & Resolution)

## Overview

This document captures research findings and design decisions for implementing a Streamlit-based web UI that provides chat and search comparison interfaces for the Nuclia RAG system.

## Research Tasks & Findings

### 1. Streamlit Multi-Page Application Architecture

**Research Question**: How to structure a Streamlit app with multiple pages (chat and comparison)?

**Decision**: Use Streamlit's native multi-page app structure with `pages/` directory

**Rationale**:
- Streamlit (v1.0+) natively supports multi-page apps through the `pages/` directory convention
- Each page is a separate Python file with automatic navigation in the sidebar
- Pages are numbered/named using the format: `1_💬_Chat.py`, `2_🔍_Compare.py`
- Shared state persists across pages using `st.session_state`
- Simple, no additional routing libraries required

**Alternatives Considered**:
- Single-page app with tabs: Rejected because it doesn't provide clean URL separation and makes bookmarking/sharing specific views difficult
- Custom routing with streamlit-option-menu: Rejected as unnecessarily complex for just 2 pages

**References**:
- Streamlit Multi-Page Apps: https://docs.streamlit.io/library/get-started/multipage-apps

---

### 2. Session State Management for Chat History

**Research Question**: How to maintain conversation history across user interactions in Streamlit?

**Decision**: Use `st.session_state` with a list of message dictionaries

**Rationale**:
- `st.session_state` persists data across reruns within the same browser session
- Stores messages as `[{"role": "user", "content": "...", "strategy": "..."}, ...]`
- Built-in to Streamlit, no external state management needed
- Automatically cleared when browser session ends (meets requirement for session-only persistence)
- Thread-safe for single-user local development

**Alternatives Considered**:
- Browser local storage via JavaScript: Rejected as overly complex and requires st.components integration
- File-based persistence: Rejected as specification explicitly states "session duration only"
- Database storage: Rejected as overkill for local single-user development

**Implementation Pattern**:
```python
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add message
st.session_state.messages.append({
    "role": "user", 
    "content": query,
    "strategy": selected_strategy
})

# Clear history
st.session_state.messages = []
```

---

### 3. API Integration with Existing FastAPI Endpoint

**Research Question**: How to integrate Streamlit app with existing FastAPI `/search` endpoint?

**Decision**: Use Python `requests` library with configurable base URL from environment variables

**Rationale**:
- Simple, synchronous HTTP client (adequate for local single-user use)
- No need for async/await complexity in Streamlit (Streamlit is inherently synchronous)
- Base URL configurable via `.env` file: `API_BASE_URL=http://localhost:8000`
- Matches existing API contract from `api.py`

**Alternatives Considered**:
- httpx (async): Rejected as Streamlit doesn't benefit from async in this context
- Direct import of search functions: Rejected to maintain separation of concerns and allow independent API/UI deployment

**Implementation Pattern**:
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def call_search_api(query: str, search_type: str = "merged"):
    response = requests.post(
        f"{API_BASE_URL}/search",
        json={"query": query, "search_type": search_type}
    )
    response.raise_for_status()
    return response.json()
```

---

### 4. Error Handling Strategy

**Research Question**: How to handle API errors, network failures, and validation errors?

**Decision**: Use try-except blocks with Streamlit's `st.error()` for user-friendly error display

**Rationale**:
- `st.error()` provides clear, red-highlighted error messages
- Catches common errors: connection errors, API errors (404, 500), timeout errors
- Simple validation for empty queries before API call
- Graceful degradation in comparison mode (show errors for failed strategies, display successful ones)

**Error Categories**:
1. **Validation errors**: Empty query → `st.warning("Please enter a search query")`
2. **Connection errors**: API unavailable → `st.error("Unable to connect to search API. Please ensure the API server is running.")`
3. **API errors**: 422, 500 → `st.error(f"Search failed: {error_message}")`
4. **Timeout errors**: Request timeout → `st.error("Search request timed out. Please try again.")`

**Implementation Pattern**:
```python
try:
    results = call_search_api(query, strategy)
except requests.ConnectionError:
    st.error("Unable to connect to search API...")
except requests.HTTPError as e:
    st.error(f"Search failed: {e.response.text}")
except requests.Timeout:
    st.error("Search request timed out...")
```

---

### 5. UI Layout and Visual Design

**Research Question**: How to create visually distinct messages and clear result displays?

**Decision**: Use Streamlit's `st.chat_message()` for chat UI and custom containers for comparison view

**Rationale**:
- `st.chat_message()` (Streamlit 1.23+) provides built-in chat UI with avatar support
- Built-in roles: "user" and "assistant" with default styling
- For comparison: Use `st.columns()` for side-by-side layout
- `st.expander()` for collapsible result details
- Minimal custom CSS needed

**Chat Interface Layout**:
```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
```

**Comparison Interface Layout**:
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🔤 Semantic")
    # Display results
with col2:
    st.subheader("🔀 Hybrid")
    # Display results
with col3:
    st.subheader("🎯 Merged")
    # Display results
```

---

### 6. Testing Strategy for Streamlit Apps

**Research Question**: How to write tests for Streamlit applications?

**Decision**: Use pytest with Streamlit AppTest (available in Streamlit 1.28+)

**Rationale**:
- `streamlit.testing.v1.AppTest` allows testing Streamlit apps without browser
- Can simulate user interactions and verify outputs
- Follows TDD principle from constitution
- For API client: Standard pytest with mocked requests

**Test Structure**:
```python
from streamlit.testing.v1 import AppTest

def test_chat_page():
    at = AppTest.from_file("pages/1_💬_Chat.py")
    at.run()
    # Verify elements exist
    assert at.text_input[0].value == ""
    
def test_api_client():
    # Mock requests and test API integration
    pass
```

**Alternatives Considered**:
- Selenium/Playwright: Rejected as too heavyweight for unit testing
- Manual testing only: Rejected as violates TDD constitution principle

---

### 7. Deployment and Launch Strategy

**Research Question**: How should users launch the application?

**Decision**: Single command `streamlit run app.py` with clear documentation

**Rationale**:
- Standard Streamlit convention
- `app.py` serves as landing/home page with navigation instructions
- Streamlit automatically displays URL in terminal and opens browser
- Simple, no custom scripts needed

**Launch Flow**:
1. Start FastAPI backend: `uvicorn api:app --reload` (existing)
2. Start Streamlit UI: `streamlit run app.py` (new)
3. Browser opens to `http://localhost:8501`

---

## Technology Decisions Summary

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| Streamlit | >=1.28 | Web UI framework | Built-in multi-page, chat UI, session state |
| requests | >=2.31 | HTTP client | Simple, synchronous API integration |
| python-dotenv | >=1.0 | Config management | Environment variable loading (existing) |
| pytest | >=7.0 | Testing | TDD support with Streamlit AppTest |

---

## Implementation Priorities

**Phase 1 (P1 - MVP)**:
1. Chat interface with single strategy selection
2. API integration with error handling
3. Session state management
4. Basic navigation

**Phase 2 (P2 - Comparison)**:
1. Comparison page with all three strategies
2. Side-by-side result display
3. Enhanced error handling for partial failures

---

## Open Questions Resolved

All technical unknowns from the plan have been resolved:
- ✅ Multi-page structure: Native Streamlit pages/
- ✅ Session management: st.session_state
- ✅ API integration: requests library
- ✅ Error handling: st.error() with try-except
- ✅ Testing: Streamlit AppTest + pytest
- ✅ Launch command: `streamlit run app.py`

**Ready to proceed to Phase 1 (Design & Contracts)**
