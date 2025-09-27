# Tasks: Government Tender Extraction System

**Input**: Design documents from `/specs/002-mock-tech-test/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, API endpoints
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- Paths shown below assume full-stack structure

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize backend Python project with FastAPI dependencies
- [x] T003 Initialize frontend React project with TypeScript dependencies
- [x] T004 [P] Configure backend linting and formatting tools (black, flake8)
- [x] T005 [P] Configure frontend linting and formatting tools (ESLint, Prettier)
- [x] T006 [P] Create configuration files for LLM settings
- [x] T007 [P] Set up database schema and migrations

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T008 [P] Contract test POST /extract in backend/tests/contract/test_extract_api.py
- [x] T009 [P] Contract test POST /evaluate in backend/tests/contract/test_evaluate_api.py
- [x] T010 [P] Integration test document processing pipeline in backend/tests/integration/test_pipeline.py
- [x] T011 [P] Integration test ground truth evaluation in backend/tests/integration/test_ground_truth.py
- [x] T012 [P] Frontend component test DocumentUpload in frontend/src/__tests__/components/test_document_upload.tsx
- [x] T013 [P] Frontend component test ExtractionResults in frontend/src/__tests__/components/test_extraction_results.tsx
- [x] T014 [P] Frontend component test EvaluationMetrics in frontend/src/__tests__/components/test_evaluation_metrics.tsx
- [x] T015 [P] Frontend integration test API communication in frontend/src/__tests__/integration/test_api_integration.tsx

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T016 [P] TenderData model in backend/src/models/tender_data.py
- [x] T017 [P] ProcessingResult model in backend/src/models/processing_result.py
- [x] T018 [P] GroundTruthData model in backend/src/models/ground_truth_data.py
- [ ] T019 [P] Document processor service in backend/src/services/document_processor.py
- [ ] T020 [P] LLM extractor service in backend/src/services/llm_extractor.py
- [ ] T021 [P] Validator service in backend/src/services/validator.py
- [ ] T022 [P] DocumentUpload component in frontend/src/components/DocumentUpload.tsx
- [ ] T023 [P] ExtractionResults component in frontend/src/components/ExtractionResults.tsx
- [ ] T024 [P] EvaluationMetrics component in frontend/src/components/EvaluationMetrics.tsx
- [ ] T025 POST /extract endpoint in backend/src/api/routes.py
- [ ] T026 POST /evaluate endpoint in backend/src/api/routes.py
- [ ] T027 WebSocket connection for real-time updates in backend/src/api/routes.py
- [ ] T028 API service integration in frontend/src/services/api.ts
- [ ] T029 Home page component in frontend/src/pages/Home.tsx
- [ ] T030 Results page component in frontend/src/pages/Results.tsx

## Phase 3.4: Integration
- [ ] T031 Connect document processor to database
- [ ] T032 Connect LLM extractor to OpenAI and Hugging Face APIs
- [ ] T033 Connect validator to Pydantic models
- [ ] T034 Connect frontend to backend API
- [ ] T035 WebSocket connection for real-time processing updates
- [ ] T036 Error handling and logging middleware
- [ ] T037 CORS and security headers
- [ ] T038 File upload handling and validation

## Phase 3.5: Polish
- [ ] T039 [P] Unit tests for TenderData model validation in backend/tests/unit/test_tender_data.py
- [ ] T040 [P] Unit tests for ProcessingResult model validation in backend/tests/unit/test_processing_result.py
- [ ] T041 [P] Unit tests for document processor in backend/tests/unit/test_document_processor.py
- [ ] T042 [P] Unit tests for LLM extractor in backend/tests/unit/test_llm_extractor.py
- [ ] T043 [P] Unit tests for validator service in backend/tests/unit/test_validator.py
- [ ] T044 [P] Frontend unit tests for API service in frontend/tests/unit/test_api_service.tsx
- [ ] T045 Performance tests for document processing (<10s requirement)
- [ ] T046 [P] Update backend documentation in backend/README.md
- [ ] T047 [P] Update frontend documentation in frontend/README.md
- [ ] T048 [P] Create sample documents and ground truth data
- [ ] T049 [P] Style frontend components with TailwindCSS
- [ ] T050 [P] Add error boundaries and loading states
- [ ] T051 [P] Implement retry logic and exponential backoff
- [ ] T052 [P] Add comprehensive logging and monitoring

## Dependencies
- Tests (T008-T015) before implementation (T016-T030)
- T016-T018 (models) before T019-T021 (services)
- T019-T021 (services) before T025-T027 (endpoints)
- T022-T024 (components) before T028 (API integration)
- T025-T027 (endpoints) before T031-T038 (integration)
- Implementation before polish (T039-T052)

## Parallel Example
```
# Launch T008-T015 together:
Task: "Contract test POST /extract in backend/tests/contract/test_extract_api.py"
Task: "Contract test POST /evaluate in backend/tests/contract/test_evaluate_api.py"
Task: "Integration test document processing pipeline in backend/tests/integration/test_pipeline.py"
Task: "Integration test ground truth evaluation in backend/tests/integration/test_ground_truth.py"
Task: "Frontend component test DocumentUpload in frontend/tests/components/test_document_upload.tsx"
Task: "Frontend component test ExtractionResults in frontend/tests/components/test_extraction_results.tsx"
Task: "Frontend component test EvaluationMetrics in frontend/tests/components/test_evaluation_metrics.tsx"
Task: "Frontend integration test API communication in frontend/tests/integration/test_api_integration.tsx"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- Focus on TDD approach with failing tests first
- Ensure both frontend and backend components are properly integrated

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] Frontend and backend tasks are properly balanced
- [ ] Full-stack integration tasks are included
