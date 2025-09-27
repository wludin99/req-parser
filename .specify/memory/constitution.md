<!--
Sync Impact Report
- Version change: v1.0.0 → v1.1.0
- Modified principles: none
- Added sections: Principle 4 (Evaluation & Validation)
- Removed sections: none
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md
  ✅ .specify/templates/spec-template.md
  ✅ .specify/templates/tasks-template.md
  ✅ .specify/templates/commands/*.md
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Original adoption date unknown
-->

# Document Parser Constitution

## Metadata

- **Project Name**: Document Parser for Criteria Extraction  
- **Constitution Version**: v1.1.0  
- **Ratification Date**: TODO(RATIFICATION_DATE)  
- **Last Amended Date**: 2025-09-27  

---

## Principles

### Principle 1 — Production-Ready Code
All code MUST be suitable for commercial deployment: no unlicensed snippets,
no copy-paste boilerplate without provenance, and no experimental hacks that
would block integration into production.  

**Rationale**: This ensures the MVP is a credible baseline that could ship with
minor polishing.

---

### Principle 2 — Transparency of Choices
All architectural and implementation decisions MUST be documented (e.g., model
selection, chunking strategy, JSON validation approach).  

**Rationale**: This allows reviewers to understand trade-offs, replicate results,
and maintain the system beyond the original author.

---

### Principle 3 — Robust LLM Integration
The extraction pipeline MUST guarantee valid structured outputs:
- Enforce JSON schema compliance (retry, correction loops).
- Handle errors gracefully (malformed JSON, missing fields).
- Avoid dependence on a single provider without fallback strategy.  

**Rationale**: Document parsing is high-stakes; downstream systems cannot tolerate
hallucinations or format errors.

---

### Principle 4 — Evaluation & Validation
The project MUST include a mechanism to validate extracted data against
ground truth or reference rules:
- Automated checks (assertions, comparison scripts).  
- Clear metrics for accuracy and completeness.  

**Rationale**: Business users require evidence that extraction is reliable before
using outputs in decision-making processes.

---

### Principle 5 — Time-Boxed Delivery
All deliverables MUST fit within the agreed timeframe (e.g., 3-hour coding test).
Prioritize a functional vertical slice (ingestion → extraction → validation) over
completeness.  

**Rationale**: Demonstrates ability to scope and execute under pressure, a key
constraint of the interview format.

---

## Governance

- **Amendments**: Any contributor MAY propose amendments. Changes require review
  and acceptance by maintainers.  
- **Versioning**: Semantic versioning applies:
  - MAJOR: Principle removed or fundamentally redefined.  
  - MINOR: New principle added or significantly expanded.  
  - PATCH: Clarification or non-semantic fixes.  
- **Compliance Reviews**: At each milestone, the codebase MUST be reviewed
  against this constitution. Non-compliance MUST be documented with remediation
  tasks in the backlog.  


**Version**: v1.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-09-27