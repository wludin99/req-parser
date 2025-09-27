
# Implementation Plan: Government Tender Extraction System

**Branch**: `002-mock-tech-test` | **Date**: 2025-09-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-mock-tech-test/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Create a document processing pipeline for extracting structured data from government tender documents using LLM processing with robust JSON validation, error handling, and evaluation against ground truth data.

## Technical Context
**Language/Version**: Python 3.11, TypeScript 5.0, Node.js 18+  
**Primary Dependencies**: FastAPI, React, OpenAI API, Hugging Face API, PyPDF2, Pydantic, SQLAlchemy  
**Storage**: SQLite with SQLAlchemy ORM for processing logs and results  
**Testing**: pytest, Jest, React Testing Library for validation and accuracy testing  
**Target Platform**: Web browser, local development server  
**Project Type**: web (frontend + backend)  
**Performance Goals**: <10s document processing, >90% extraction accuracy, <200ms API response  
**Constraints**: 3-hour development window, MVP scope, PDF and text files only  
**Scale/Scope**: Single user, local processing, 10-50 documents for evaluation

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle 1 - Production-Ready Code**: ✅ PASS
- Using established frameworks (FastAPI, PyPDF2, Pydantic)
- No experimental hacks, all dependencies are production-ready
- SQLAlchemy for reliable data persistence

**Principle 2 - Transparency of Choices**: ✅ PASS  
- All architectural decisions will be documented in research.md
- LLM model selection, chunking strategy, and JSON validation approach documented
- Error handling and retry mechanisms clearly defined

**Principle 3 - Robust LLM Integration**: ✅ PASS
- JSON schema validation with Pydantic models
- Retry mechanisms for failed extractions
- Fallback strategy (OpenAI → Hugging Face)
- Error handling for malformed JSON responses

**Principle 4 - Evaluation & Validation**: ✅ PASS
- Ground truth comparison for accuracy measurement
- Automated validation of extracted data structure
- Clear metrics for extraction success/failure

**Principle 5 - Time-Boxed Delivery**: ✅ PASS
- 3-hour constraint respected with MVP scope
- Functional vertical slice prioritized (ingestion → extraction → validation)
- Focus on core extraction pipeline over completeness

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/
├── src/
│   ├── models/
│   │   ├── tender_data.py
│   │   └── processing_result.py
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── llm_extractor.py
│   │   └── validator.py
│   ├── api/
│   │   └── routes.py
│   └── main.py
├── tests/
│   ├── contract/
│   │   ├── test_extraction_api.py
│   │   └── test_validation.py
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   └── test_ground_truth.py
│   └── unit/
│       ├── test_models.py
│       └── test_services.py
├── data/
│   ├── sample_documents/
│   ├── ground_truth/
│   └── results/
├── config/
│   ├── extraction_config.yaml
│   └── llm_config.yaml
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── DocumentUpload.tsx
│   │   ├── ExtractionResults.tsx
│   │   └── EvaluationMetrics.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   └── Results.tsx
│   ├── services/
│   │   └── api.ts
│   └── App.tsx
├── tests/
│   ├── components/
│   └── integration/
└── package.json
```

**Structure Decision**: Full-stack web application with separate frontend and backend directories. Backend uses FastAPI with Python for document processing and API endpoints. Frontend uses React with TypeScript for user interface. Clear separation of concerns with dedicated API, models, and services layers. Data directory for sample documents and ground truth evaluation.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh cursor`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before CLI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

**Specific Task Categories for Tender Extraction**:
- **Setup**: Project initialization, dependencies, configuration files for both frontend and backend
- **Backend Tests**: Pydantic model validation tests, API contract tests, LLM integration tests
- **Frontend Tests**: Component tests, API integration tests, user interaction tests
- **Integration Tests**: End-to-end pipeline tests, ground truth evaluation tests, full-stack tests
- **Backend Implementation**: TenderData and ProcessingResult models, document processor, LLM extractor, API routes
- **Frontend Implementation**: React components, API integration, real-time updates, user interface
- **API Integration**: RESTful endpoints, WebSocket connections, error handling
- **Evaluation**: Ground truth comparison, accuracy metrics, performance testing
- **Polish**: Error handling, logging, documentation, styling, configuration management

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
