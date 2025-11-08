# Data Model

## Entities

### SearchQuery

Represents a search query from a user.

-   **Fields**:
    -   `query`: `string` (The text to search for)
    -   `search_type`: `string` (Optional. One of `semantic`, `hybrid`, or `merged`. Defaults to `merged`.)
-   **Validation**:
    -   `query` must not be empty.
    -   `search_type` must be one of the allowed values if provided.

### SearchResult

Represents a single search result.

-   **Fields**:
    -   `text`: `string` (The content of the result)
    -   `score`: `float` (The relevance score of the result)
    -   `source`: `string` (The source of the result, e.g., a filename)
-   **Validation**: None.
