# Quality Gates

## General Directive

- Gates are split into **Verifiable** (agent checks via `check_gate` MCP tool) and **Human Judgment** (requires explicit human confirmation).
- All verifiable gates must pass before the agent requests human approval.
- Human judgment gates require explicit human confirmation. Document all gate decisions in the phase deliverable.
- The human user can override and proceed. Document any gate override in the deliverable for the phase being entered.

---

## Gate: Enhancement → Requirements

### Verifiable
- `docs/enhancement/` directory exists with a file named `<sequential number>-<feature name>.md`
- File contains Current System Overview section
- File contains Prior Features section
- File contains Relevant Design References section
- File contains Change Context section

### Human Judgment
- System understanding is adequate for the proposed change
- Prior architectural decisions have been properly considered
- The change context accurately describes where the new feature fits

---

## Gate: Requirements → Technical Design

### Verifiable
- `docs/requirements/` directory exists with a file named `<sequential number>-<feature name>.md`
- File contains numbered functional requirements (FR-001, FR-002, …)
- File contains acceptance criteria per requirement (AC-*)
- File contains constraints section
- File contains assumptions section
- File contains open questions section
- File contains a Self-Review section.  Is this requirements doc ready to be handed off to a technical architect?

### Human Judgment
- Requirements completeness and correctness
- Business priority and stakeholder alignment
- No critical ambiguities remain unresolved

---

## Gate: Technical Design → Implementation

### Verifiable
- `docs/design/` directory exists with a file named `<sequential number>-<feature name>.md`
- Technical-design document contains: Numbered Technical Requirements (TR-*), Acceptance Criteria (AC-*), Constraints, Assumptions, References
- Technology stack is identified in technical-design documents
- Dependencies are identified in technical-design documents
- File contains a Self-Review section.  Is this technical-design doc ready to be handed off to an autonomous coding agent?

### Human Judgment
- Architecture is sound and appropriate for the problem
- Tradeoff analysis is acceptable
- Scope is appropriately bounded

---

## Gate: Implementation → Review

### Verifiable
- Source code files exist and match technical-design document architecture
- `docs/implementation/` directory contains implementation summary
- Inline documentation is present in source files
- The implementation summary's AC→test mapping accounts for 100% of the technical-design document's acceptance criteria (each mapped to a named test or an explicit deferral to the testing phase)
- The project's test suite runs and exits successfully (exit code 0)
- API documentation exists, or the implementation summary records a documented skip with reason (documentation is required only when the feature exposes or modifies an API of its own, and the tooling used must not violate the design document's dependency constraints)

### Human Judgment
- Code quality meets team standards
- Implementation matches architectural intent
- No unexpected technical debt introduced

---

## Gate: Review → Testing

### Verifiable
- `docs/review/` directory exists with a file named `<sequential number>-<feature name>.md`
- Self-review checklist is present in review report

### Human Judgment
- **Requires explicit human confirmation that peer review is complete.** The agent cannot self-validate this gate and must wait for human signal before proceeding.
- Critical and major issues are resolved

---

## Gate: Testing → Deployment

### Verifiable
- Test files exist alongside source or in `tests/` directory
- `docs/testing/` directory exists with a file named `<sequential number>-<feature name>-test-report.md`
- Test suite passes (exit code 0)
- Coverage meets defined threshold (documented in test report)
- The test report's AC→test traceability table covers 100% of the technical-design document's acceptance criteria, each with a passing test

### Human Judgment
- Test coverage is sufficient
- Regression risk is acceptable
- Edge cases are adequately tested

---

## Gate: Deployment → Monitoring

### Verifiable
- `docs/deploy/` directory exists with a file named `<sequential number>-<feature name>.md`
- Rollback procedure is documented
- CI/CD pipeline files exist

### Human Judgment
- Deployment is successful (post-deployment verification)
- System is stable in production

---

## Failure

Gate failure triggers backtracking per `01-lifecycle-overview.md` rules.
