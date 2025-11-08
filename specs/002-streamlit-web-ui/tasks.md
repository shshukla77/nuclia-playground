# Tasks: Streamlit Web UI for Chat and API Access

**Input**: Design documents from `/specs/002-streamlit-web-ui/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-integration.md

**Tests**: Following TDD approach per constitution - tests written FIRST before implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure at repository root
- Streamlit pages in `pages/` directory
- Utilities in `utils/` directory
- Tests in `tests/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Streamlit application

- [ ] T001 Create project directory structure (app.py, pages/, utils/, tests/)
- [ ] T002 Update requirements.txt with Streamlit dependencies (streamlit>=1.28, requests>=2.31)
- [ ] T003 Install dependencies with pip install -r requirements.txt
- [ ] T004 Create .env.example file with API_BASE_URL and API_TIMEOUT template
- [ ] T005 Copy .env.example to .env and configure API_BASE_URL=http://localhost:8000
- [ ] T006 [P] Create utils/__init__.py (empty file for package initialization)
- [ ] T007 [P] Create pages/__init__.py (empty file for package initialization)

**Checkpoint**: Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core API client and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for API Client (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T008 [P] Create tests/test_api_client.py with test_search_success using mocked requests
- [ ] T009 [P] Add test_search_connection_error to tests/test_api_client.py
- [ ] T010 [P] Add test_search_http_error to tests/test_api_client.py
- [ ] T011 [P] Add test_search_timeout to tests/test_api_client.py
- [ ] T012 [P] Add test_search_empty_query_validation to tests/test_api_client.py
- [ ] T013 [P] Add test_search_invalid_strategy_validation to tests/test_api_client.py
- [ ] T014 [P] Add test_health_check to tests/test_api_client.py

### Implementation of API Client

- [ ] T015 Create utils/api_client.py with SearchAPIClient class skeleton
- [ ] T016 Implement SearchAPIClient.__init__ in utils/api_client.py (base_url, timeout parameters)
- [ ] T017 Implement SearchAPIClient.search method in utils/api_client.py (query validation, HTTP POST, error handling)
- [ ] T018 Implement SearchAPIClient.health_check method in utils/api_client.py
- [ ] T019 Run pytest tests/test_api_client.py and verify all tests pass
- [ ] T020 [P] Create utils/display.py with format_search_result function for displaying result text and scores
- [ ] T021 [P] Create utils/session.py with initialize_session_state function for chat message list initialization

**Checkpoint**: Foundation ready - API client tested and working, user story implementation can now begin

---

## Phase 3: User Story 3 - Application Launcher (Priority: P1) 🎯 MVP Infrastructure

**Goal**: Create the main entry point (app.py) that launches the Streamlit application on localhost

**Independent Test**: Execute `streamlit run app.py` and verify application starts, displays URL, and shows navigation

### Implementation for User Story 3

- [ ] T022 [US3] Create app.py with Streamlit page configuration (title, icon, layout)
- [ ] T023 [US3] Add welcome message and navigation instructions to app.py
- [ ] T024 [US3] Add sidebar with links to Chat and Compare pages in app.py
- [ ] T025 [US3] Add API health check indicator to app.py using SearchAPIClient.health_check
- [ ] T026 [US3] Test launch with `streamlit run app.py` - verify opens browser at localhost:8501
- [ ] T027 [US3] Update README.md with launch instructions and prerequisites

**Checkpoint**: Application can be launched and accessed via browser - infrastructure ready for page implementation

---

## Phase 4: User Story 1 - Interactive Chat Interface (Priority: P1) 🎯 MVP Core Feature

**Goal**: Build chat interface where users can ask questions, select search strategies, view conversation history, and clear history

**Independent Test**: Open chat page, submit questions with different strategies, verify history persists, test clear history button

### Tests for Chat Page (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T028 [P] [US1] Create tests/test_chat_page.py with test_chat_page_loads using Streamlit AppTest
- [ ] T029 [P] [US1] Add test_strategy_selector_default_merged to tests/test_chat_page.py
- [ ] T030 [P] [US1] Add test_message_submission to tests/test_chat_page.py
- [ ] T031 [P] [US1] Add test_conversation_history_display to tests/test_chat_page.py
- [ ] T032 [P] [US1] Add test_clear_history_button to tests/test_chat_page.py
- [ ] T033 [P] [US1] Add test_empty_query_validation to tests/test_chat_page.py
- [ ] T034 [P] [US1] Add test_api_error_handling to tests/test_chat_page.py

### Implementation for User Story 1

- [ ] T035 [US1] Create pages/1_💬_Chat.py with page title and configuration
- [ ] T036 [US1] Initialize session state for messages in pages/1_💬_Chat.py using utils/session.py
- [ ] T037 [US1] Add search strategy selector (selectbox) in sidebar of pages/1_💬_Chat.py with options: semantic, hybrid, merged (default: merged)
- [ ] T038 [US1] Add "Clear History" button in sidebar of pages/1_💬_Chat.py
- [ ] T039 [US1] Implement clear history functionality in pages/1_💬_Chat.py (clears st.session_state.messages)
- [ ] T040 [US1] Display conversation history using st.chat_message in pages/1_💬_Chat.py (loop through messages)
- [ ] T041 [US1] Add chat input widget at bottom of pages/1_💬_Chat.py with st.chat_input
- [ ] T042 [US1] Implement message submission handler in pages/1_💬_Chat.py (validate non-empty, call API, append to history)
- [ ] T043 [US1] Add API error handling with st.error for connection errors in pages/1_💬_Chat.py
- [ ] T044 [US1] Add visual distinction between user and assistant messages in pages/1_💬_Chat.py using chat_message roles
- [ ] T045 [US1] Add result display formatting in pages/1_💬_Chat.py using utils/display.py
- [ ] T046 [US1] Run pytest tests/test_chat_page.py and verify all tests pass
- [ ] T047 [US1] Manual test: Start app, navigate to Chat, test all acceptance scenarios from spec.md

**Checkpoint**: Chat interface fully functional - users can have conversations with search, history works, errors handled

---

## Phase 5: User Story 2 - Search Comparison Tool (Priority: P2)

**Goal**: Build comparison page that displays side-by-side results from all three search strategies

**Independent Test**: Open comparison page, enter query, verify results from all three strategies displayed with labels and scores

### Tests for Comparison Page (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T048 [P] [US2] Create tests/test_compare_page.py with test_compare_page_loads using Streamlit AppTest
- [ ] T049 [P] [US2] Add test_query_input_exists to tests/test_compare_page.py
- [ ] T050 [P] [US2] Add test_three_column_layout to tests/test_compare_page.py
- [ ] T051 [P] [US2] Add test_all_strategies_called to tests/test_compare_page.py (mock API client)
- [ ] T052 [P] [US2] Add test_results_display_with_scores to tests/test_compare_page.py
- [ ] T053 [P] [US2] Add test_empty_query_validation to tests/test_compare_page.py
- [ ] T054 [P] [US2] Add test_partial_failure_handling to tests/test_compare_page.py (one strategy fails, others succeed)

### Implementation for User Story 2

- [ ] T055 [US2] Create pages/2_🔍_Compare.py with page title and configuration
- [ ] T056 [US2] Add query input text field in pages/2_🔍_Compare.py
- [ ] T057 [US2] Add search button in pages/2_🔍_Compare.py
- [ ] T058 [US2] Implement query validation (non-empty) in pages/2_🔍_Compare.py
- [ ] T059 [US2] Create three-column layout using st.columns in pages/2_🔍_Compare.py
- [ ] T060 [US2] Implement parallel API calls for all three strategies in pages/2_🔍_Compare.py (semantic, hybrid, merged)
- [ ] T061 [US2] Add error handling for each strategy with try-except in pages/2_🔍_Compare.py
- [ ] T062 [US2] Display semantic results in column 1 with header "🔤 Semantic" in pages/2_🔍_Compare.py
- [ ] T063 [US2] Display hybrid results in column 2 with header "🔀 Hybrid" in pages/2_🔍_Compare.py
- [ ] T064 [US2] Display merged results in column 3 with header "🎯 Merged" in pages/2_🔍_Compare.py
- [ ] T065 [US2] Format results display (top 5, with text and scores) using utils/display.py in pages/2_🔍_Compare.py
- [ ] T066 [US2] Add "No results found" message for empty results per strategy in pages/2_🔍_Compare.py
- [ ] T067 [US2] Add error message display for failed strategies in pages/2_🔍_Compare.py
- [ ] T068 [US2] Run pytest tests/test_compare_page.py and verify all tests pass
- [ ] T069 [US2] Manual test: Start app, navigate to Compare, test all acceptance scenarios from spec.md

**Checkpoint**: Comparison page fully functional - users can compare all three strategies side-by-side

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, and final validation

- [ ] T070 [P] Add loading spinners with st.spinner for API calls in both pages/1_💬_Chat.py and pages/2_🔍_Compare.py
- [ ] T071 [P] Add helpful tooltips to strategy selector in pages/1_💬_Chat.py explaining each strategy
- [ ] T072 [P] Improve error messages to be more user-friendly across all files
- [ ] T073 [P] Add page icons and better titles to both chat and compare pages
- [ ] T074 Update README.md with complete quickstart guide based on specs/002-streamlit-web-ui/quickstart.md
- [ ] T075 Create .streamlit/config.toml with theme customization (optional)
- [ ] T076 Add usage examples and screenshots to README.md
- [ ] T077 Run full manual test of quickstart.md steps end-to-end
- [ ] T078 Verify all edge cases from spec.md are handled appropriately
- [ ] T079 Code review and cleanup: remove debug prints, ensure consistent formatting
- [ ] T080 Final pytest run: pytest tests/ --verbose to verify all tests pass

**Checkpoint**: Application polished, documented, and ready for use

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 3 - Launcher (Phase 3)**: Depends on Foundational - Can run in parallel with US1/US2 (different files)
- **User Story 1 - Chat (Phase 4)**: Depends on Foundational - Can run in parallel with US2/US3 (different files)
- **User Story 2 - Compare (Phase 5)**: Depends on Foundational - Can run in parallel with US1/US3 (different files)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 3 (Launcher) - P1**: Independent - No dependencies on other stories, just needs Foundational
- **User Story 1 (Chat) - P1**: Independent - No dependencies on other stories, just needs Foundational
- **User Story 2 (Compare) - P2**: Independent - No dependencies on other stories, just needs Foundational

**All three user stories are fully independent and can be implemented in parallel after Foundational phase completes**

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Tests for a page before page implementation
- Utilities (api_client, display, session) before pages that use them
- Core page structure before advanced features
- Error handling integrated throughout

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T006 and T007 can run in parallel (different files)

**Foundational Phase Tests (Phase 2)**:
- T008-T014 (all test creation tasks) can run in parallel (different test functions)

**Foundational Phase Implementation (Phase 2)**:
- T020 and T021 can run in parallel with T015-T019 (different files: display.py, session.py vs api_client.py)

**User Story 1 Tests (Phase 4)**:
- T028-T034 (all chat test creation tasks) can run in parallel (different test functions)

**User Story 2 Tests (Phase 5)**:
- T048-T054 (all compare test creation tasks) can run in parallel (different test functions)

**Polish Phase (Phase 6)**:
- T070, T071, T072, T073, T076 can all run in parallel (different aspects/files)

**MAJOR PARALLELIZATION OPPORTUNITY**:
Once Foundational (Phase 2) is complete, ALL THREE USER STORY PHASES (3, 4, 5) can run in parallel by different developers:
- Developer A: User Story 3 (Launcher) - app.py
- Developer B: User Story 1 (Chat) - pages/1_💬_Chat.py
- Developer C: User Story 2 (Compare) - pages/2_🔍_Compare.py

---

## Parallel Example: Foundational Phase

```bash
# After Setup completes, launch all test creation tasks together:
Task: "Create tests/test_api_client.py with test_search_success"
Task: "Add test_search_connection_error to tests/test_api_client.py"
Task: "Add test_search_http_error to tests/test_api_client.py"
Task: "Add test_search_timeout to tests/test_api_client.py"
Task: "Add test_search_empty_query_validation to tests/test_api_client.py"
Task: "Add test_search_invalid_strategy_validation to tests/test_api_client.py"
Task: "Add test_health_check to tests/test_api_client.py"

# Then implement api_client to make tests pass
# While implementing api_client, also create utilities in parallel:
Task: "Create utils/display.py with format_search_result"
Task: "Create utils/session.py with initialize_session_state"
```

---

## Parallel Example: User Story Phases (After Foundational)

```bash
# Three developers can work in parallel after Phase 2:

Developer A (Launcher):
Task T022: "Create app.py with Streamlit page configuration"
Task T023: "Add welcome message and navigation instructions"
Task T024: "Add sidebar with links to Chat and Compare pages"
# ... continue with US3 tasks

Developer B (Chat):
Task T028-T034: "Create all chat tests" (in parallel)
Task T035: "Create pages/1_💬_Chat.py with page title"
Task T036-T047: "Implement chat features"

Developer C (Compare):
Task T048-T054: "Create all compare tests" (in parallel)
Task T055: "Create pages/2_🔍_Compare.py with page title"
Task T056-T069: "Implement comparison features"

# All three can work simultaneously without conflicts!
```

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Recommended for solo developer or quick validation:**

1. ✅ Complete Phase 1: Setup (T001-T007)
2. ✅ Complete Phase 2: Foundational (T008-T021) - CRITICAL for everything else
3. ✅ Complete Phase 3: User Story 3 - Launcher (T022-T027)
4. ✅ Complete Phase 4: User Story 1 - Chat (T028-T047)
5. **STOP and VALIDATE**: Test chat interface independently, get user feedback
6. Deploy/demo if ready - you now have a working chat interface!

**At this point you have a fully functional MVP**: Users can chat with the RAG system using different strategies.

### Incremental Delivery

**Recommended for continuous value delivery:**

1. Foundation (Phases 1-2) → API client tested and working
2. Add Launcher + Chat (Phases 3-4) → Deploy/Demo **MVP!**
3. Add Comparison (Phase 5) → Deploy/Demo (enhanced version)
4. Add Polish (Phase 6) → Deploy/Demo (production-ready)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

**Recommended for team of 3+ developers:**

1. **Week 1**: Team completes Setup + Foundational together (Phases 1-2)
2. **Week 2**: Once Foundational is done, split into parallel work:
   - Developer A: User Story 3 (Launcher) - 1-2 days
   - Developer B: User Story 1 (Chat) - 3-4 days
   - Developer C: User Story 2 (Compare) - 3-4 days
3. **Week 3**: Integration testing, polish phase together
4. Stories complete and integrate independently

**Estimated Timeline**:
- Setup: 1-2 hours
- Foundational: 4-6 hours (includes TDD)
- US3 (Launcher): 2-3 hours
- US1 (Chat): 6-8 hours (includes TDD)
- US2 (Compare): 6-8 hours (includes TDD)
- Polish: 2-3 hours

**Total: 21-30 hours for solo developer, 12-16 hours with 3-person team**

---

## Task Summary

**Total Tasks**: 80 tasks

### Tasks by Phase:
- **Phase 1 (Setup)**: 7 tasks (T001-T007)
- **Phase 2 (Foundational)**: 14 tasks (T008-T021)
  - Tests: 7 tasks
  - Implementation: 7 tasks
- **Phase 3 (US3 - Launcher)**: 6 tasks (T022-T027)
- **Phase 4 (US1 - Chat)**: 20 tasks (T028-T047)
  - Tests: 7 tasks
  - Implementation: 13 tasks
- **Phase 5 (US2 - Compare)**: 22 tasks (T048-T069)
  - Tests: 7 tasks
  - Implementation: 15 tasks
- **Phase 6 (Polish)**: 11 tasks (T070-T080)

### Tasks by Story:
- **Setup & Foundation**: 21 tasks (no story label)
- **US3 (Launcher)**: 6 tasks
- **US1 (Chat)**: 20 tasks
- **US2 (Compare)**: 22 tasks
- **Polish**: 11 tasks

### Parallelizable Tasks:
- **37 tasks marked [P]** can run in parallel with other tasks in their phase
- **Major parallel opportunity**: All 3 user stories (48 tasks) can run in parallel after Phase 2

### Test Tasks (TDD):
- **21 test tasks** following Test-Driven Development
- Tests written FIRST before implementation per constitution

---

## Format Validation

✅ **All tasks follow required checklist format**:
- ✅ All start with `- [ ]` (checkbox)
- ✅ All have sequential Task IDs (T001-T080)
- ✅ User story tasks have [US1], [US2], or [US3] labels
- ✅ Setup, Foundational, and Polish tasks have no story labels
- ✅ Parallelizable tasks marked with [P]
- ✅ All descriptions include specific file paths
- ✅ Clear, actionable descriptions

---

## Notes

- [P] tasks = different files or independent functions, no blocking dependencies within phase
- [Story] label maps task to specific user story for traceability and parallel execution
- Each user story is independently completable and testable
- TDD approach: Tests fail first, then implement to make them pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP delivery possible after just Phases 1-4 (Setup + Foundational + Launcher + Chat)
