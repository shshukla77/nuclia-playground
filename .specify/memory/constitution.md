<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Added Principles:
  - I. Modular & Testable Code
  - II. Configuration-Driven
  - III. Idempotent Indexing
  - IV. Multi-Strategy Search
  - V. Test-Driven Development
- Added Sections:
  - Technology Stack & Dependencies
  - Development Workflow
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (to align with new principles)
  - ✅ .specify/templates/tasks-template.md (to reflect TDD)
- Follow-up TODOs: None
-->
# Nuclia RAG Kit Constitution

## Core Principles

### I. Modular & Testable Code
All new functionality MUST be organized into separate modules with clear responsibilities (e.g., `indexing.py`, `search.py`, `utils.py`). Every module MUST be independently testable, and core business logic MUST have corresponding unit or integration tests.

### II. Configuration-Driven
Application settings, especially secrets and environment-specific values (like KB URL and API keys), MUST be managed via environment variables and loaded through a central `config.py` module. No hardcoded credentials or URLs are permitted in the source code.

### III. Idempotent Indexing
Data ingestion MUST be idempotent. The system MUST detect whether a file has changed before re-indexing it to prevent redundant processing and ensure data consistency. This is achieved by hashing file content/metadata and storing it as a version identifier.

### IV. Multi-Strategy Search
The system MUST support multiple search strategies to address different use cases. This includes, but is not limited to, semantic, full-text (BM25), and hybrid/rank-fused search. New search functionalities should be implemented as distinct functions.

### V. Test-Driven Development (NON-NEGOTIABLE)
All new features or bug fixes MUST follow a Test-Driven Development (TDD) approach. Tests that replicate the bug or define the new feature MUST be written first and confirmed to fail before implementation begins. The Red-Green-Refactor cycle is mandatory.

## Technology Stack & Dependencies

The project relies on the following core technologies:
- **Language**: Python 3.10+
- **Primary SDK**: `nuclia-sdk`
- **Configuration**: `python-dotenv` for managing environment variables.
- **Testing**: `pytest` (assumed, to be formalized).

## Development Workflow

1.  **Configuration**: Set up a `.env` file with the required `KB_URL` and `KB_API_KEY`.
2.  **Data Preparation**: Place documents to be indexed into the `data/` directory.
3.  **Indexing**: Run `python main.py` to execute the indexing workflow.
4.  **Testing & Verification**: Use `python main.py [test|semantic|hybrid|compare]` to run predefined search tests and verify the results.
5.  **Adding Features**: For any new functionality, first add a corresponding test in `tests.py` or a new test file, ensure it fails, and then implement the feature.

## Governance

This constitution is the source of truth for all development practices within this project. Any deviation requires a formal amendment.

- **Amendments**: To change this constitution, a developer must open a pull request with the proposed changes, a justification, and an updated Sync Impact Report. The change must be approved by the project maintainer.
- **Compliance**: All code reviews MUST verify that the changes comply with the principles outlined in this constitution.
- **Versioning**: The constitution's version MUST be incremented on every change according to Semantic Versioning (MAJOR for breaking changes, MINOR for new principles, PATCH for clarifications).

**Version**: 1.0.0 | **Ratified**: 2025-11-07 | **Last Amended**: 2025-11-07
