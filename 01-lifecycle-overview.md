# Lifecycle Overview

## 1. LIFECYCLE OVERVIEW

You operate through 7 phases. Load the relevant Tier 2 playbook (`03-` through `09-`) for your current phase.

| Phase | Entry | Exit (soft gates) | Deliverables |
|---|---|---|---|
| Requirements | Vague request or user prompt | Requirements structured, acceptance criteria defined, constraints identified | `requirements.md` |
| Design | Approved requirements | Architecture decided, ADR written, tech stack selected | `adr.md` |
| Implementation | Approved design | Code written, files created, inline docs complete | Source files + `implementation-summary.md` + API documentation (conditional — see directive) |
| Review | Completed implementation | Self-review checklist passed, issues resolved | `review-report.md` |
| Testing | Approved review | Test suite written and passing, coverage met | Test files + `test-report.md` |
| Deployment | Approved tests | Deployment config written, CI/CD gates defined, rollback plan ready | `deploy-config.md` + CI/CD pipeline files |
| Monitoring | Successful deployment | Metrics instrumented, alerts configured, baselines established | `monitoring-spec.md` |

## 2. API DOCUMENTATION DIRECTIVE

Auto-generated API documentation in a standard machine-readable format (e.g., OpenAPI/Swagger) is a **required** deliverable when the implementation exposes or modifies APIs.

- Tool and format are not prescriptive — select the appropriate tool for your technology stack.
- This deliverable does **NOT** apply to UI-only changes, internal refactoring, or other non-API work.

## 3. BACKTRACKING RULE

- If you revisit phase N, you must re-execute all phases N+1 through your current phase in order. No skipping.
- Adjacent backward movement (e.g., Testing → Review) does not require re-execution of intervening phases (there are none).
- Non-adjacent backward movement (e.g., Testing → Requirements) triggers full retrace.

## 4. GATE POLICY

All gates are **advisory** (soft). A human developer may override and proceed without satisfying all exit criteria.

When overriding, document the justification in the phase's deliverable file.

## 5. AGILE SUPPORT

Iteration loops are valid. Phases may be re-entered from their immediate predecessor without requiring full retrace.

Full retrace is only required when jumping backward non-adjacently.

## 6. HANDOFF PROTOCOL

Each phase's deliverable is input to the next phase. Verify deliverables exist and are current before proceeding.

If a deliverable is missing or stale, request it or regenerate it before continuing.

## 7. STATE TRACKING & RECOVERY

- Upon completing each phase, write `sdlc-state.json` to the project root. Format:
  ```json
  {"current_phase": "<phase_name>", "feature": "<feature_name>", "last_gate": "<gate_name>", "timestamp": "<iso_8601>"}
  ```
- If context is lost, compacted, or the session restarts, call the `get_pipeline_state(project_path=<your_working_dir>)` MCP tool to re-orient yourself.
- Use `sdlc_resume` to restore Tier 1 context and the relevant phase playbook.
- If `sdlc-state.json` is missing, infer state by scanning the **target project's** root directory for the following subdirectories:
  - `docs/adr/` exists → Design complete
  - `docs/implementation/` exists → Implementation complete
  - `docs/review/` exists → Review complete
  - `docs/deploy/` exists → Deployment complete
  - `docs/monitoring/` exists → Monitoring complete
- Trust explicit state (`sdlc-state.json`) over inferred state.
