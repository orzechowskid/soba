# Review Phase Playbook

This phase of the AI-SDLC pipeline is where a feature implementation undergoes a rigorous review to ensure correctness and completeness.  This phase is purely mechanical, suitable to be performed by an autonomous review or coding agent.

The source code under review during this phase will be deployed to production environments in later phases of this pipeline, so it is _absolutely critical_ that the implementation is proven to be correct, complete, and in accordance with requirements and technical-design documents.

It is appropriate to delegate this phase of the pipeline to a reviewer or architect sub-agent if one is available.

## Phase Guidelines

- **DO**: review the feature implementation based on the contents of the requirements and technical-design documents to complete the checklist in the next section ("Self-Review Checklist")
- **DO NOT**: review the entire codebase unless specifically indicated by the requirements or technical-design documents
- **DO NOT**: offer to fix any implementation issues discovered during the review.  This explicitly violates the Phase Lock directive forbidding the production of deliverables belonging to other phases.

## Self-Review Checklist

Perform a thorough review of all implementation artifacts based on the criteria in this checklist.

### Correctness
- [ ] Implementation matches requirements in `docs/requirements/<sequential number>-<feature name>.md`
- [ ] Every acceptance criterion is either covered by a passing implementation-phase test or explicitly deferred with a valid reason in the implementation summary's AC→test mapping
- [ ] No contradictions between implementation and technical-design document

### Completeness
- [ ] All functional requirements are implemented
- [ ] All edge cases identified in requirements are handled
- [ ] Error paths are implemented, not just happy paths

### Code Quality
- [ ] Implementation follows conventions (`09-coding-standards.md`)
- [ ] Complexity is justified (no over-engineering)

### Security
- [ ] Input parsing, validation, and normalization at system and layer boundaries (where the feature parses or accepts structured input)
- [ ] No hardcoded secrets, tokens, or credentials
- [ ] Authentication/authorization checks are present (where the feature has an authentication surface)
- [ ] Sensitive data is not logged

## Validation of AI-Generated Code

The implementation under review was written by an autonomous coding agent.  Common issues in AI-generated code that require explicit review:

### Hallucinated APIs
- [ ] All newly created or imported functions and methods actually exist

### Stale Patterns
- [ ] No deprecated features, tooling, dependencies, idioms, or patterns are used

### Missing Error Handling
- [ ] Try/catch constructs or error returns for every fallible operation

### Incomplete Implementations
- [ ] No new placeholder comments (e.g. `TODO`, `FIXME`) and no new placeholder return values

### Over-Engineering
- [ ] No unnecessary abstraction layers were added

## Severity Classification Examples

These are illustrative examples to help define severity levels, not a full list of possibilities for each level.

| Severity | Definition | Required Action |
|---|---|---|
| Critical | Security vulnerability, data loss, system crash | Must fix |
| Major | Feature broken under normal use, major performance issue | Must fix |
| Minor | Edge case not handled, suboptimal performance | Fix or document with justification |
| Cosmetic | Naming, formatting, comment clarity | Fix or defer |

## Output

### Deliverable

a review-results document at `docs/review/<sequential number>-<feature name>.md`.  If a document with this name already exists then append a new section to it; do **not** overwrite and replace the existing document.

### Required Sections

1. Checklist results (pass/fail per item)
2. AI-generated code results (pass/fail per item)
3. Issues found (classified by severity)
4. Summary and recommendation

## Phase Exit

After producing the review report:

1. Verify all critical and major issues are resolved.
2. Run `check_gate(project_path=<project>, from_phase="review", to_phase="testing")` to verify deliverables.
3. Report completion to the human.
4. Branch point:
   - If the review report contains critical- or major-severity issues then inform the user and **immediately** re-enter the implementation phase.
   - If the review report does not contain critical- or major-severity issues then **STOP.** Await human approval before proceeding to testing phase.
