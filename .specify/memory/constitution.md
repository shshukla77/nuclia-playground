<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified Principles:
  - I. Modular & Testable Code (updated with streamlit_app structure)
- Added Principles:
  - VI. User Interface Components
- Modified Sections:
  - Technology Stack & Dependencies (added FastAPI, Streamlit, Click, requests)
  - Development Workflow (updated to reflect current structure, added UI workflow)
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (already aligned)
  - ✅ .specify/templates/tasks-template.md (already aligned)
- Follow-up TODOs: None
-->
# Nuclia RAG Kit Constitution

## Core Principles

### I. Modular & Testable Code
All new functionality MUST be organized into separate modules with clear responsibilities. The project follows a modular architecture:
- **Core Backend**: `indexing.py`, `search.py`, `utils.py`, `api.py`, `cli.py`, `config.py`
- **Web UI**: Isolated in `streamlit_app/` with its own modules (`utils/`, `pages/`, `tests/`)

Every module MUST be independently testable, and core business logic MUST have corresponding unit or integration tests. The streamlit_app maintains 100% test coverage for its API client.

### II. Configuration-Driven
Application settings, especially secrets and environment-specific values (like KB URL and API keys), MUST be managed via environment variables and loaded through a central `config.py` module. No hardcoded credentials or URLs are permitted in the source code. The Streamlit UI has its own `.env.example` for UI-specific configuration.

### III. Idempotent Indexing
Data ingestion MUST be idempotent. The system MUST detect whether a file has changed before re-indexing it to prevent redundant processing and ensure data consistency. This is achieved by hashing file content/metadata and storing it as a version identifier.

### IV. Multi-Strategy Search
The system MUST support multiple search strategies to address different use cases. This includes, but is not limited to, semantic, full-text (BM25), and hybrid/rank-fused search. New search functionalities should be implemented as distinct functions. The Web UI MUST provide visual comparison tools for evaluating strategy quality.

### V. Test-Driven Development (NON-NEGOTIABLE)
All new features or bug fixes MUST follow a Test-Driven Development (TDD) approach. Tests that replicate the bug or define the new feature MUST be written first and confirmed to fail before implementation begins. The Red-Green-Refactor cycle is mandatory. The streamlit_app feature (002-streamlit-web-ui) exemplifies this with 18 passing unit tests written before implementation.

### VI. User Interface Components
User-facing components MUST be organized separately from core business logic. Web UI code resides in the `streamlit_app/` directory with its own:
- Entry point (`app.py`)
- Page modules (`pages/`)
- Utilities (`utils/api_client.py`, `utils/display.py`, `utils/session.py`)
- Tests (`tests/`)
- Documentation (`README.md`)

UI components MUST provide comprehensive error handling and clear user feedback. Session state MUST be managed consistently, and API errors MUST be presented in user-friendly formats.

## Technology Stack & Dependencies

The project relies on the following core technologies:
- **Language**: Python 3.10+
- **Primary SDK**: `nuclia` for knowledge base operations
- **Web Framework**: `fastapi` for REST API, `uvicorn` for ASGI server
- **CLI Framework**: `click` for command-line interface
- **UI Framework**: `streamlit` (≥1.28) for web interface
- **HTTP Client**: `requests` (≥2.31) for API communication
- **Configuration**: `python-dotenv` for managing environment variables
- **Testing**: `pytest` (≥7.0) with 33 total tests (20 passing, 13 skipped)

## Development Workflow

### Backend Development

1.  **Configuration**: Set up a `.env` file with the required `KB_URL` and `KB_API_KEY`.
2.  **Data Preparation**: Place documents to be indexed into the `data/` directory.
3.  **Indexing**: Run `python main.py upload` to execute the indexing workflow.
4.  **Testing & Verification**: Use `python main.py [test|test-semantic|test-hybrid|test-comparison]` to run predefined search tests.
5.  **API Server**: Run `uvicorn api:app --reload` to start the REST API at `localhost:8000`.

### Web UI Development

1.  **Prerequisites**: Ensure FastAPI backend is running at `localhost:8000`.
2.  **Configuration**: Copy `streamlit_app/.env.example` to `streamlit_app/.env` (or use defaults).
3.  **Launch UI**: Run `cd streamlit_app && streamlit run app.py` or use `./streamlit_app/run.sh`.
4.  **Testing**: Run `cd streamlit_app && pytest tests/ -v` (18 API client tests must pass).
5.  **Adding Features**: Follow TDD - write tests first in `streamlit_app/tests/`, verify they fail, then implement.

### CLI Development

1.  **Interactive Chat**: Run `python cli.py chat` for conversational interface.
2.  **Single Query**: Run `python cli.py ask "your question"` for one-off searches.

## Governance

This constitution is the source of truth for all development practices within this project. Any deviation requires a formal amendment.

- **Amendments**: To change this constitution, a developer must open a pull request with the proposed changes, a justification, and an updated Sync Impact Report. The change must be approved by the project maintainer.
- **Compliance**: All code reviews MUST verify that the changes comply with the principles outlined in this constitution.
- **Versioning**: The constitution's version MUST be incremented on every change according to Semantic Versioning (MAJOR for breaking changes, MINOR for new principles, PATCH for clarifications).

**Version**: 1.1.0 | **Ratified**: 2025-11-07 | **Last Amended**: 2025-11-07
