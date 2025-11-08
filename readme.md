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

# Quickstart

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

6.  **Run tests**:
    ```bash
    python main.py test
    ```

