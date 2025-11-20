# Official Nuclia Developers Docs

## Data Ingestion

* Understanding Resources: https://docs.rag.progress.cloud/docs/ingestion/resource
* Indexing: https://docs.rag.progress.cloud/docs/ingestion/indexing
* Add Metadata: https://docs.rag.progress.cloud/docs/ingestion/metadata
* Best practices: https://docs.rag.progress.cloud/docs/ingestion/best-practices
* Split Strategies: https://docs.rag.progress.cloud/docs/ingestion/how-to/split-strategies

## Search & RAG

* Search Strategy: https://docs.rag.progress.cloud/docs/rag/search-strategy
* Search Endpoints: https://docs.rag.progress.cloud/docs/rag/search-strategy
* Search Filters: https://docs.rag.progress.cloud/docs/rag/advanced/search-filters
* Ask: https://docs.rag.progress.cloud/docs/rag/advanced/ask
* RAG Strategy: https://docs.rag.progress.cloud/docs/rag/rag-strategy


## How-to-code-examples

* Create a chatbot: https://docs.rag.progress.cloud/docs/rag/how-to/chatbot

# Security & Deployment

⚠️ **Important Security Notice**

This application is designed for **local development** and **trusted internal environments**. Before deploying to production or exposing to the internet, implement the following security measures:

## Security Best Practices

### 1. API Authentication
- **For Production**: Always set the `API_KEY` environment variable to enable authentication
  ```bash
  export API_KEY="your-secure-random-api-key"
  ```
- API clients must include the key in the `X-API-Key` header:
  ```bash
  curl -X POST "https://your-api.com/search" \
    -H "X-API-Key: your-secure-random-api-key" \
    -H "Content-Type: application/json" \
    -d '{"query": "your question"}'
  ```
- **For Local Development**: Authentication is disabled by default when `API_KEY` is not set

### 2. Use HTTPS/TLS
- **Never expose the API over HTTP in production**
- Use a reverse proxy (nginx, Apache, or cloud load balancer) with TLS certificates
- Example nginx configuration:
  ```nginx
  server {
      listen 443 ssl;
      ssl_certificate /path/to/cert.pem;
      ssl_certificate_key /path/to/key.pem;
      
      location / {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
  }
  ```

### 3. Network Restrictions
- **Do not expose the API directly to the public internet**
- Use firewall rules to restrict access to trusted IP ranges
- Consider running behind a VPN or private network
- Use cloud security groups or network policies to limit access

### 4. Reverse Proxy Authentication
- For additional security, use reverse proxy authentication:
  - HTTP Basic Auth (nginx, Apache)
  - OAuth2 Proxy for enterprise SSO integration
  - Cloud provider authentication (AWS ALB, GCP Load Balancer)

### 5. File Upload Security
- The application restricts file access to the `data/` directory only
- Never allow users to specify arbitrary file paths
- Validate uploaded files before processing
- Set appropriate file size limits

### 6. Environment Variables
- **Never commit `.env` files** with secrets to version control
- Use `.env-example` as a template
- Store secrets securely (e.g., AWS Secrets Manager, HashiCorp Vault)
- Rotate API keys regularly

### 7. Error Handling
- Production API returns generic error messages to clients
- Detailed errors are logged server-side only
- Monitor logs for security incidents

## Deployment Checklist

Before deploying to production:

- [ ] Set `API_KEY` environment variable
- [ ] Enable HTTPS/TLS with valid certificates
- [ ] Configure firewall/security groups
- [ ] Set up reverse proxy with authentication
- [ ] Enable logging and monitoring
- [ ] Verify `KB_API_KEY` is stored securely
- [ ] Test API authentication
- [ ] Review and minimize network exposure
- [ ] Set up automated security updates
- [ ] Document incident response procedures

## Local Development

For local development on `localhost`, the default configuration is safe:
- API authentication is optional (no `API_KEY` required)
- HTTP is acceptable for localhost
- Direct API access is convenient for testing

**Remember**: The security measures above are **required** before any production deployment or when handling sensitive data.

# Quickstart

## Streamlit Web UI 🎨

Interactive web interface for chat and search strategy comparison.

**Quick Start:**
```bash
# 1. Start the API server (required)
uvicorn api:app --reload

# 2. In another terminal, launch the web UI
cd streamlit_app
streamlit run app.py
# OR use the launch script:
./streamlit_app/run.sh
```

**Features:**
- 💬 **Chat Interface**: Interactive Q&A with search-powered responses
- 🔍 **Compare Tool**: Visual strategy comparison (semantic, hybrid, merged)
- 📊 **Analytics**: Result overlap and quality metrics

**Documentation:** See `streamlit_app/README.md` for detailed usage and configuration.

---

## API

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file** with your Nuclia credentials:
    ```
    KB_URL="<your-nuclia-kb-url>"
    KB_API_KEY="<your-nuclia-api-key>"
    ```

3.  **Run the API server**:
    ```bash
    uvicorn api:app --reload
    ```

4.  **Send a search request**:
    ```bash
    curl -X POST "http://127.0.0.1:8000/search" -H "Content-Type: application/json" -d '{"query": "your question"}'
    ```

## CLI

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file** (if you haven't already).

3.  **Run a simple query**:
    ```bash
    python main.py ask "your question"
    ```

4.  **Start an interactive chat session**:
    ```bash
    python main.py chat
    ```

5.  **Upload data**:
    ```bash
    python main.py upload
    ```

## Testing

Run all tests with pytest:

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_api.py
pytest tests/test_cli.py
pytest tests/test_search.py

# Run with verbose output
pytest -v

# Run tests in the streamlit app
cd streamlit_app
pytest tests/ -v
```

**Test Coverage:**
- `tests/test_api.py` - API endpoint tests
- `tests/test_cli.py` - CLI command tests
- `tests/test_search.py` - Search functionality tests (semantic, hybrid, merged)
- `streamlit_app/tests/` - Streamlit app component tests

