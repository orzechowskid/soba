# Quality Gates

## General Directive

- Gates are split into **Verifiable** (agent checks via `check_gate` MCP tool) and **Human Judgment** (requires explicit human confirmation).
- All verifiable gates must pass before the agent requests human approval.
- Human judgment gates require explicit human confirmation. Document all gate decisions in the phase deliverable.
- The human user can override and proceed. Document any gate override in the deliverable for the phase being entered.

---

## Gate: Requirements → Design

### Verifiable
- `requirements.md` exists in project root
- File contains numbered functional requirements (FR-001, FR-002, …)
- File contains acceptance criteria per requirement (AC-*)
- File contains constraints section
- File contains assumptions section
- File contains open questions section

### Human Judgment
- Requirements completeness and correctness
- Business priority and stakeholder alignment
- No critical ambiguities remain unresolved

---

## Gate: Design → Implementation

### Verifiable
- `docs/adr/` directory exists with at least one `.md` file
- Each ADR contains: Title, Context, Options Considered, Decision, Consequences, Status
- Technology stack is identified in ADRs
- Dependencies are identified in ADRs

### Human Judgment
- Architecture is sound and appropriate for the problem
- Tradeoff analysis is acceptable
- Scope is appropriately bounded

---

## Gate: Implementation → Review

### Verifiable
- Source code files exist and match ADR architecture
- `docs/implementation/` directory contains implementation summary
- Inline documentation is present in source files
- API documentation exists (if APIs are exposed or modified)

### Human Judgment
- Code quality meets team standards
- Implementation matches architectural intent
- No unexpected technical debt introduced

---

## Gate: Review → Testing

### Verifiable
- `docs/review/` directory contains review report
- Self-review checklist is present in review report

### Human Judgment
- **Requires explicit human confirmation that peer review is complete.** The agent cannot self-validate this gate and must wait for human signal before proceeding.
- Critical and major issues are resolved

---

## Gate: Testing → Deployment

### Verifiable
- Test files exist alongside source or in `tests/` directory
- `docs/testing/` directory contains test report
- Test suite passes (exit code 0)
- Coverage meets defined threshold (documented in test report)

### Human Judgment
- Test coverage is sufficient
- Regression risk is acceptable
- Edge cases are adequately tested

---

## Gate: Deployment → Monitoring

### Verifiable
- `docs/deploy/` directory contains deployment configuration
- Rollback procedure is documented
- CI/CD pipeline files exist

### Human Judgment
- Deployment is successful (post-deployment verification)
- System is stable in production

---

## Failure

Gate failure triggers backtracking per `01-lifecycle-overview.md` rules.
