# Review Phase Playbook

## 1. SELF-REVIEW CHECKLIST

Before requesting human approval, perform a thorough self-review of all implementation artifacts.

### Correctness
- [ ] Implementation matches requirements in `requirements.md`
- [ ] All acceptance criteria can be satisfied by the implementation
- [ ] No contradictions between implementation and ADR

### Completeness
- [ ] All functional requirements are implemented
- [ ] All edge cases identified in requirements are handled
- [ ] Error paths are implemented, not just happy paths

### Code Quality
- [ ] Naming follows conventions (`10-coding-standards.md`)
- [ ] Functions/methods are single-purpose and reasonably sized
- [ ] No dead code, unused imports, or commented-out blocks
- [ ] Complexity is justified (no over-engineering)

### Security
- [ ] Input validation at all boundaries
- [ ] No hardcoded secrets, tokens, or credentials
- [ ] Authentication/authorization checks are present
- [ ] Sensitive data is not logged

## 2. AI-GENERATED CODE VALIDATION

Common issues in AI-generated code that require explicit checking:

- **Hallucinated APIs** — verify all imported functions and methods actually exist
- **Stale patterns** — check that deprecated patterns aren't used
- **Missing error handling** — verify try/catch or error returns at every fallible operation
- **Incomplete implementations** — check for TODO, FIXME, placeholder returns
- **Over-engineering** — verify no unnecessary abstraction layers were added

## 3. SEVERITY CLASSIFICATION

| Severity | Definition | Required Action |
|---|---|---|
| Critical | Security vulnerability, data loss, system crash | Must fix before approval |
| Major | Feature broken under normal use, major performance issue | Must fix before approval |
| Minor | Edge case not handled, suboptimal performance | Fix or document with justification |
| Cosmetic | Naming, formatting, comment clarity | Fix or defer |

## 4. OUTPUT

**Deliverable:** `docs/review/<number>-<feature>-review.md` (relative to target project root)

**Required sections:**
1. Checklist results (pass/fail per item from §1)
2. Issues found (classified by severity from §3)
3. AI validation results (§2 checks)
4. Summary and recommendation

## 5. PHASE EXIT

After producing the review report:

1. Verify all critical and major issues are resolved.
2. Run `check_gate(project_path=<project>, from_phase="review", to_phase="testing")` to verify deliverables.
3. Report completion to the human.
4. **STOP.** Await human approval before proceeding to testing phase.
5. Note: The human judgment gate for this phase requires explicit human confirmation that peer review is complete.
