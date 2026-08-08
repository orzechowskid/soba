# Quality Gates

## General Directive

- All gates are advisory. The human user can always override and proceed.
- Document any gate override in the deliverable for the phase being entered.

---

## Gate: Requirements → Design

- Requirements are structured and numbered.
- Acceptance criteria are defined per requirement.
- Constraints are documented.
- Open questions are resolved or accepted as documented assumptions.

---

## Gate: Design → Implementation

- ADR is written and stored in `docs/adr/` (target project root).
- Technology stack is selected.
- Dependencies are identified.
- Scope is clear and bounded.

---

## Gate: Implementation → Review

- Code compiles/runs without errors.
- Inline documentation is present.
- Implementation summary is written.
- API documentation is generated (if applicable).

---

## Gate: Review → Testing

- Self-review checklist is passed.
- Critical and major issues are resolved.
- **Requires explicit human confirmation that peer review is complete.** The agent cannot self-validate this gate and must wait for human signal before proceeding.

---

## Gate: Testing → Deployment

- Test suite passes.
- Coverage meets defined threshold.
- Test report is generated.
- Regressions are resolved.

---

## Gate: Deployment → Monitoring

- Deployment is successful.
- Post-deployment verification passes.
- Rollback procedure is documented.

---

## Failure

Gate failure triggers backtracking per `01-lifecycle-overview.md` rules.
