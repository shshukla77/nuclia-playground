# Streamlit Web UI

A modern web interface for the Nuclia search engine, providing interactive chat and strategy comparison tools.

## Quick Start

```bash
# From the streamlit_app directory
cd streamlit_app

# Run the application
streamlit run app.py
```

The UI will open at `http://localhost:8501`

**Prerequisites:**
- FastAPI backend running at `localhost:8000` (run `uvicorn api:app --reload` from project root)
- Python 3.10+
- Dependencies installed (see below)

## Project Structure

```
streamlit_app/
├── app.py                  # Main entry point
├── pages/                  # Streamlit pages
│   ├── 1_💬_Chat.py        # Chat interface
│   └── 2_🔍_Compare.py     # Strategy comparison
├── utils/                  # Utility modules
│   ├── api_client.py       # API client with error handling
│   ├── display.py          # UI rendering components
│   └── session.py          # Session state management
├── tests/                  # Unit tests
│   ├── test_api_client.py  # API client tests (18 tests)
│   └── test_utilities.py   # Utility tests
├── .env.example            # Example configuration
├── pytest.ini              # Test configuration
└── README.md               # This file
```

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings (default values work for local dev)
```

3. **Start the application**:
```bash
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

### Running the Backend

The Streamlit UI requires the FastAPI backend to be running:

```bash
# In a separate terminal
uvicorn api:app --reload
```

## Features

### Chat Interface (`pages/1_💬_Chat.py`)

Interactive chat with search-powered responses:

- **Strategy Selection**: Choose semantic, hybrid, or merged search
- **Message History**: Persistent chat history during session
- **Result Display**: Expandable search results with scores
- **Clear Chat**: Reset conversation at any time

**Usage**:
1. Select your preferred search strategy in the sidebar
2. Type a question in the chat input
3. View results inline with metadata
4. Expand result cards to see full details

### Compare Tool (`pages/2_🔍_Compare.py`)

Side-by-side strategy comparison:

- **Multi-Strategy Search**: Run query across selected strategies simultaneously
- **Visual Comparison**: Columns for each strategy with top results
- **Analysis Insights**: Automatic overlap detection and quality metrics
- **Result Caching**: Instant re-runs for the same query

**Usage**:
1. Select strategies to compare (1-3)
2. Enter your search query
3. Click "Compare" to execute
4. Review side-by-side results and insights

### Launcher (`app.py`)

Main entry point with system status:

- **API Health Check**: Real-time backend connectivity status
- **Navigation**: Links to all pages
- **Configuration Display**: Show current API endpoint and timeout

## Architecture

### Project Structure

```
.
├── app.py                      # Main entry point
├── pages/
│   ├── __init__.py
│   ├── 1_💬_Chat.py            # Chat interface
│   └── 2_🔍_Compare.py         # Comparison tool
├── utils/
│   ├── __init__.py
│   ├── api_client.py           # API client with error handling
│   ├── display.py              # UI rendering utilities
│   └── session.py              # Session state management
├── tests/
│   ├── test_api_client.py      # API client tests (18 tests)
│   └── test_utilities.py       # Utility tests
├── .env                        # Environment configuration
├── .env.example                # Example configuration
└── requirements.txt            # Python dependencies
```

### Key Components

#### API Client (`utils/api_client.py`)

Handles all communication with the FastAPI backend:

- **SearchAPIClient**: Main client class
  - `search(query, search_type)`: Execute search
  - `health_check()`: Verify API availability
- **safe_search()**: Wrapper with comprehensive error handling
- **get_default_client()**: Factory for configured client

**Error Handling**:
- Connection errors (API not running)
- Timeout errors (slow responses)
- HTTP errors (4xx, 5xx)
- Validation errors (empty queries)

#### Session Management (`utils/session.py`)

Manages Streamlit session state:

- **Chat History**: Messages with metadata
- **Strategy Selection**: Current search strategy
- **Result Caching**: Comparison results cache
- **API Client**: Shared client instance

**Key Functions**:
- `init_session_state()`: Initialize defaults
- `add_message()`: Add chat message
- `cache_comparison_results()`: Cache search results
- `get_api_client()`: Get shared client

#### Display Utilities (`utils/display.py`)

Reusable UI components:

- `render_search_results()`: Display result list
- `render_comparison_results()`: Side-by-side comparison
- `render_error()`: Consistent error display
- `show_api_health_indicator()`: Status indicator

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Streamlit Configuration  
STREAMLIT_SERVER_PORT=8501
```

### Streamlit Settings

Default settings work for most cases. To customize:

```bash
# Create .streamlit/config.toml
mkdir .streamlit
cat > .streamlit/config.toml << EOF
[server]
port = 8501
headless = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
EOF
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
# API client tests (18 tests)
pytest tests/test_api_client.py -v

# Utility tests
pytest tests/test_utilities.py -v
```

### Test Coverage

```bash
pytest --cov=utils --cov-report=html
```

Current test coverage:
- `api_client.py`: 100% (18 tests)
- `display.py`: Format functions tested
- `session.py`: Core logic tested (requires Streamlit context for full coverage)

## Development

### Adding a New Page

1. Create file in `pages/` with numeric prefix:
```python
# pages/3_📊_Analytics.py
import streamlit as st
from utils.session import init_session_state

st.set_page_config(page_title="Analytics", page_icon="📊")
init_session_state()

st.title("📊 Analytics")
# Your page content...
```

2. Page automatically appears in Streamlit sidebar

### Extending the API Client

Add new methods to `SearchAPIClient`:

```python
# utils/api_client.py
def get_stats(self) -> Dict[str, Any]:
    """Get search statistics from API."""
    response = requests.get(
        f"{self.base_url}/stats",
        timeout=self.timeout
    )
    response.raise_for_status()
    return response.json()
```

Add corresponding tests:

```python
# tests/test_api_client.py
@patch('requests.get')
def test_get_stats_success(self, mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"total_searches": 100}
    mock_get.return_value = mock_response
    
    stats = client.get_stats()
    
    assert stats["total_searches"] == 100
```

## Troubleshooting

### Common Issues

#### "Unable to connect to search API"

**Cause**: FastAPI backend not running

**Solution**:
```bash
# Start the backend
uvicorn api:app --reload

# Verify it's running
curl http://localhost:8000/docs
```

#### "Import Error: No module named 'streamlit'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

#### "Empty results for all strategies"

**Cause**: Knowledge base not indexed

**Solution**:
1. Check that FastAPI /search endpoint works:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "search_type": "semantic"}'
```

2. Verify knowledge base is populated
3. Try different query terms

#### "Session state not persisting"

**Cause**: Browser cached old version

**Solution**:
1. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Or click "Always rerun" in Streamlit UI
3. Or clear Streamlit cache: `streamlit cache clear`

### Debug Mode

Enable debug logging:

```python
# Add to top of app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View Streamlit logs:
```bash
streamlit run app.py --logger.level=debug
```

## Performance

### Optimization Tips

1. **Cache API Results**: Comparison tool caches results per query
2. **Limit Result Display**: Use max_results parameter to control rendering
3. **Lazy Loading**: Results load in expandable sections
4. **Session Persistence**: State preserved across reruns

### Monitoring

Track performance metrics:

```python
import time
from utils.session import add_message

start = time.time()
results = client.search(query, strategy)
duration = time.time() - start

add_message("assistant", f"Search completed in {duration:.2f}s")
```

## Security

### Local Development Only

This UI is designed for **local development only**:

- No authentication/authorization
- HTTP (not HTTPS)
- Single-user sessions
- No data encryption

**Do not deploy to production without adding**:
- User authentication
- HTTPS/TLS
- Rate limiting
- Input validation/sanitization
- Secrets management (not `.env` files)

### Safe Practices

Current safety measures:

- Input validation in API client
- Error handling prevents crashes
- No direct database access
- Query sanitization via API

## Contributing

### Code Style

Follow existing patterns:

- **Imports**: Group by standard lib, third-party, local
- **Docstrings**: Google style with examples
- **Type Hints**: Use for function signatures
- **Formatting**: Run `ruff format .`

### Testing Requirements

All new features must include:

1. Unit tests for logic
2. Integration tests for API calls
3. Documentation in docstrings
4. Update this README if needed

### Commit Messages

Use conventional commits:

```
feat: add export results button
fix: handle empty search results
docs: update troubleshooting guide
test: add tests for caching
```

## Roadmap

Future enhancements (not in current scope):

- [ ] Export results to CSV/JSON
- [ ] Advanced filtering options
- [ ] Query history with persistence
- [ ] Batch search mode
- [ ] Custom result rendering
- [ ] Analytics dashboard
- [ ] User preferences storage
- [ ] Dark mode theme

## License

See main project LICENSE file.

## Support

For issues or questions:

1. Check this README
2. Review existing issues in repository
3. Check Streamlit documentation: https://docs.streamlit.io
4. Create new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages
   - Environment details

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io) - Web framework
- [Requests](https://requests.readthedocs.io) - HTTP client
- [Pytest](https://pytest.org) - Testing framework
- [Nuclia](https://nuclia.com) - Search backend
