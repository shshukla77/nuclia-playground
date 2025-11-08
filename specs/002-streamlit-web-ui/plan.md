# Implementation Plan: Streamlit Web UI for Chat and API Access

**Branch**: `002-streamlit-web-ui` | **Date**: November 7, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-streamlit-web-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Streamlit web application that provides two primary interfaces: (1) an interactive chat interface for conversational search with selectable search strategies (semantic, hybrid, merged), and (2) a comparison tool that displays side-by-side results from all three search strategies for quality assessment. The application integrates with the existing FastAPI `/search` endpoint and maintains session-based conversation history.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: streamlit, requests, python-dotenv (existing: fastapi, uvicorn, nuclia)  
**Storage**: In-memory session state (Streamlit st.session_state) - no persistent storage  
**Testing**: pytest with streamlit testing utilities  
**Target Platform**: Local development environment (localhost web browser)  
**Project Type**: Single web application (Streamlit app)  
**Performance Goals**: Response time <10 seconds for search queries, support 10+ message conversation history  
**Constraints**: Single-user local development, must connect to existing FastAPI API on localhost:8000  
**Scale/Scope**: 2 pages (chat + comparison), ~300-400 lines of code total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Modular & Testable Code | ✅ PASS | Streamlit app will be organized into separate page modules (chat.py, comparison.py) with reusable utility functions. Each component will be testable. |
| II. Configuration-Driven | ✅ PASS | API endpoint URL will be configurable via environment variables (API_BASE_URL) using python-dotenv. |
| III. Idempotent Indexing | N/A | This feature does not involve data indexing - it only queries existing indexed data. |
| IV. Multi-Strategy Search | ✅ PASS | Core feature requirement - supports all three search strategies (semantic, hybrid, merged) with comparison capability. |
| V. Test-Driven Development | ✅ PASS | Will follow TDD approach - tests for API integration and UI components will be written first. |

**Initial Status (Pre-Phase 0)**: ✅ All applicable principles pass. No violations to justify.

**Re-check After Phase 1 Design**: 

| Principle | Post-Design Compliance | Implementation Details |
|-----------|----------------------|------------------------|
| I. Modular & Testable Code | ✅ CONFIRMED | Design includes: `utils/api_client.py`, `utils/session.py`, `utils/display.py`, `pages/1_💬_Chat.py`, `pages/2_🔍_Compare.py`. Each module has dedicated test file. |
| II. Configuration-Driven | ✅ CONFIRMED | `.env` file with `API_BASE_URL`, `API_TIMEOUT`. All config loaded via `python-dotenv`. See contracts/api-integration.md. |
| III. Idempotent Indexing | N/A | No change - feature does not index data. |
| IV. Multi-Strategy Search | ✅ CONFIRMED | Both chat and comparison interfaces support all three strategies. API client implements all strategy calls. See data-model.md. |
| V. Test-Driven Development | ✅ CONFIRMED | Test structure defined: `tests/test_api_client.py`, `tests/test_chat_page.py`, `tests/test_compare_page.py`. Tests use pytest + Streamlit AppTest. |

**Final Status**: ✅ All principles pass. Design is constitution-compliant. Ready for implementation.

## Project Structure

### Documentation (this feature)

```text
specs/002-streamlit-web-ui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-integration.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Single project structure - Streamlit app at root level
app.py                   # Main Streamlit application entry point
pages/
├── 1_💬_Chat.py         # Chat interface page
└── 2_🔍_Compare.py      # Search comparison page
utils/
├── api_client.py        # API integration utilities
├── session.py           # Session state management
└── display.py           # Display formatting utilities
tests/
├── test_api_client.py   # API client unit tests
├── test_chat_page.py    # Chat page tests
└── test_compare_page.py # Comparison page tests
.env.example             # Example environment configuration
requirements.txt         # Updated with Streamlit dependencies
```

**Structure Decision**: Single project structure selected because this is a straightforward Streamlit application that integrates with an existing API. Streamlit's multi-page app structure (using the `pages/` directory) naturally supports the two required interfaces (chat and comparison). The app will be launched from the root `app.py` file which serves as the landing page and navigation hub.

## Complexity Tracking

> **No violations - this section intentionally left empty**

This feature complies with all applicable constitution principles. No complexity justification required.
