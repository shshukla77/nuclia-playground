# Quickstart

## API

1.  **Install dependencies**:
    ```bash
    pip install fastapi uvicorn python-dotenv nuclia-sdk
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
    pip install click python-dotenv nuclia-sdk
    ```

2.  **Create a `.env` file** (if you haven't already).

3.  **Run a simple query**:
    ```bash
    python cli.py ask "your question"
    ```

4.  **Start an interactive chat session**:
    ```bash
    python cli.py chat
    ```
