# Data Model: Streamlit Web UI

**Feature**: 002-streamlit-web-ui  
**Date**: November 7, 2025  
**Phase**: 1 (Design)

## Overview

This document defines the data structures used within the Streamlit web UI for managing chat sessions, search queries, and results. Note: This application does not use a persistent database - all data is stored in-memory using Streamlit's session state.

---

## Entity Definitions

### 1. Chat Message

**Purpose**: Represents a single message in a conversation (user question or system response)

**Fields**:
- `role` (string, required): Message sender - either "user" or "assistant"
- `content` (string, required): The message text (question or answer)
- `strategy` (string, optional): Search strategy used - "semantic", "hybrid", or "merged"
- `results` (list[SearchResult], optional): Search results associated with this message (for assistant messages)
- `timestamp` (datetime, optional): When the message was created

**Validation Rules**:
- `role` must be one of: ["user", "assistant"]
- `content` must not be empty or whitespace-only
- `strategy` must be one of: ["semantic", "hybrid", "merged"] or None
- `results` only present for assistant messages

**State Transitions**: 
- Created when user submits query (role="user") or system returns response (role="assistant")
- Immutable once created
- Deleted when "Clear History" is clicked

**Example**:
```python
{
    "role": "user",
    "content": "What is RAG?",
    "strategy": "merged",
    "timestamp": datetime.now()
}

{
    "role": "assistant", 
    "content": "Based on the search results...",
    "strategy": "merged",
    "results": [...],
    "timestamp": datetime.now()
}
```

---

### 2. Chat Session

**Purpose**: Container for all messages in a user's conversation during a browser session

**Fields**:
- `messages` (list[ChatMessage], required): Ordered list of chat messages
- `session_id` (string, auto-generated): Unique identifier for the session (Streamlit manages this)

**Validation Rules**:
- `messages` list can be empty (initial state)
- Maximum practical size: ~50 messages (to avoid performance degradation)
- Messages ordered chronologically

**State Transitions**:
- Initialized as empty list when user first accesses chat page
- Messages appended as conversation progresses
- Cleared when user clicks "Clear History"
- Destroyed when browser session ends

**Storage**: `st.session_state.messages` (Streamlit session state)

**Example**:
```python
st.session_state.messages = [
    {"role": "user", "content": "What is RAG?", ...},
    {"role": "assistant", "content": "RAG stands for...", ...},
    {"role": "user", "content": "How does it work?", ...},
    {"role": "assistant", "content": "It works by...", ...}
]
```

---

### 3. Search Result

**Purpose**: Individual search result from the API containing matched content and relevance

**Fields**:
- `text` (string, required): The matched text content
- `score` (float, required): Relevance score (0.0 to 1.0)
- `source` (string, required): Source field name from the knowledge base

**Validation Rules**:
- `text` must not be empty
- `score` must be between 0.0 and 1.0
- `source` must not be empty

**Example**:
```python
{
    "text": "Retrieval-Augmented Generation (RAG) is...",
    "score": 0.87,
    "source": "a/file/title"
}
```

---

### 4. Search Strategy

**Purpose**: Enum-like value representing the search algorithm to use

**Values**:
- `"semantic"`: Vector-based semantic search
- `"hybrid"`: Combined BM25 and semantic search  
- `"merged"`: Rank fusion of multiple strategies (default)

**Usage**: 
- Selected via dropdown/radio in chat interface
- All three used simultaneously in comparison interface
- Passed to API as `search_type` parameter

**Default**: `"merged"`

---

### 5. Comparison Result Set

**Purpose**: Collection of search results grouped by strategy for side-by-side comparison

**Fields**:
- `query` (string, required): The search query used
- `semantic_results` (list[SearchResult], optional): Results from semantic search
- `hybrid_results` (list[SearchResult], optional): Results from hybrid search
- `merged_results` (list[SearchResult], optional): Results from merged search
- `semantic_error` (string, optional): Error message if semantic search failed
- `hybrid_error` (string, optional): Error message if hybrid search failed
- `merged_error` (string, optional): Error message if merged search failed

**Validation Rules**:
- `query` must not be empty
- Each strategy has either results (list) or error (string), not both
- Results lists limited to top 5 items
- At least one strategy must succeed (not all can have errors)

**State Transitions**:
- Created when user submits comparison query
- Regenerated on each new query (not persisted)
- Not stored in session state (ephemeral)

**Example**:
```python
{
    "query": "What is RAG?",
    "semantic_results": [
        {"text": "...", "score": 0.9, "source": "..."},
        {"text": "...", "score": 0.8, "source": "..."}
    ],
    "hybrid_results": [
        {"text": "...", "score": 0.85, "source": "..."}
    ],
    "merged_results": [
        {"text": "...", "score": 0.95, "source": "..."}
    ],
    "semantic_error": None,
    "hybrid_error": None,
    "merged_error": None
}
```

---

## Data Flow Diagrams

### Chat Interface Flow

```
User Input (query) 
    → Validation (non-empty)
    → API Call (with selected strategy)
    → Response Processing
    → Update Session State (add user message + assistant response)
    → Re-render Chat UI
```

### Comparison Interface Flow

```
User Input (query)
    → Validation (non-empty)
    → Parallel API Calls (semantic, hybrid, merged)
    → Collect Results & Errors
    → Render Three Columns
    → Display Results or Error Messages
```

---

## Session State Schema

**Streamlit Session State Keys**:

```python
st.session_state = {
    # Chat page
    "messages": List[ChatMessage],           # Conversation history
    "selected_strategy": str,                # Current strategy selection
    
    # Comparison page (ephemeral - not stored)
    # Results rendered directly without state persistence
}
```

---

## API Contract Integration

**Existing API Endpoint**: `POST /search`

**Request Schema**:
```json
{
    "query": "string (required)",
    "search_type": "semantic | hybrid | merged (optional, default: merged)"
}
```

**Response Schema**:
```json
[
    {
        "text": "string",
        "score": float,
        "source": "string"
    }
]
```

**Error Responses**:
- `422 Unprocessable Entity`: Invalid search_type
- `500 Internal Server Error`: Search execution failed

---

## Validation Summary

| Entity | Key Validation Rules |
|--------|---------------------|
| Chat Message | Non-empty content, valid role, valid strategy |
| Chat Session | Message list size reasonable (<50), chronological order |
| Search Result | Score in [0.0, 1.0], non-empty text and source |
| Search Strategy | Must be one of three valid values |
| Comparison Result Set | At least one strategy succeeds, max 5 results per strategy |

---

## Storage Strategy

- **Primary Storage**: Streamlit `st.session_state` (in-memory)
- **Persistence**: Browser session duration only
- **Cleared On**: Browser close/refresh, explicit "Clear History" action
- **Backup**: None (per specification requirements)
- **Scalability**: Single-user, <50 messages per session

---

## Performance Considerations

- Message history limited to prevent DOM bloating (recommend max 50 messages)
- Comparison results not cached (regenerated on each query)
- API calls synchronous (acceptable for single-user local development)
- No pagination needed for current scope (top 5 results per strategy)

---

## Future Extensibility

**Potential Enhancements** (not in current scope):
- Export conversation history to JSON/Markdown
- Persist sessions to local file storage
- Add message metadata (timing, token count)
- Support message editing/deletion
- Conversation branching/threading

**Not Planned**:
- Multi-user support
- Real-time collaboration
- Cloud storage/sync
- Advanced analytics/metrics
