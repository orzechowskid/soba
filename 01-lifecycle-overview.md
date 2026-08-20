# Lifecycle Overview

## 1. LIFECYCLE OVERVIEW

You operate through 8 phases. Load the relevant Tier 2 playbook (`02-` through `09-`) for your current phase.

| Phase | Entry | Exit (soft gates) | Deliverables | Human Gate |
|---|---|---|---|---|
| Enhancement | Vague feature request on an existing project | System context brief written, prior features and architecture understood, change context documented | `docs/enhancement/*.md` | Required — agent halts and awaits approval. |
| Requirements | Vague request or user prompt | Requirements structured, acceptance criteria defined, constraints identified | `docs/requirements/*.md` | Required — agent halts and awaits approval. |
| Design | Approved requirements | Architecture decided, technical-design document written, tech stack selected | `docs/design/*.md` | Required — agent halts and awaits approval. |
| Implementation | Approved design | Code written, files created, inline docs complete | Source files + `docs/implementation/*.md` summary + API documentation (conditional — see directive) | Not required |
| Review | Completed implementation | Self-review checklist passed, issues resolved | `docs/review/*.md` | Situational.  Not required if critical- or major-severity issues are uncovered (pipeline reverts to Implementation phase); agent halts and awaits approval if minor-, cosmetic-, or no issues are uncovered. |
| Testing | Approved review | Test suite written and passing, coverage met | Test files + `docs/testing/*.md` | Required — agent halts and awaits approval. |
| Deployment | Approved tests | Deployment config written, CI/CD gates defined, rollback plan ready | `docs/deploy/*.md` + CI/CD pipeline files | Required — agent halts and awaits approval. |
| Monitoring | Successful deployment | Metrics instrumented, alerts configured, baselines established | `docs/monitoring/*.md` | Required — agent halts and awaits approval. |

## 2. BACKTRACKING RULE

- If you revisit phase N, you must re-execute all phases N+1 through your current phase in order. No skipping.
- Adjacent backward movement (e.g., Testing → Review) does not require re-execution of intervening phases (there are none).
- Non-adjacent backward movement (e.g., Testing → Requirements) triggers full retrace.
- **Requirements is the floor.** You cannot backtrack from Requirements to Enhancement. If requirements are fundamentally wrong, restart the feature from Requirements (do not re-run Enhancement).

## 3. GATE POLICY

All gates are **advisory** (soft). A human developer may override and proceed without satisfying all exit criteria.

When overriding, document the justification in the phase's deliverable file.

## 4. AGILE SUPPORT

Iteration loops are valid. Phases may be re-entered from their immediate predecessor without requiring full retrace.

Full retrace is only required when jumping backward non-adjacently.

## 5. HANDOFF PROTOCOL

Each phase's deliverable is input to the next phase. Verify deliverables exist and are current before proceeding.

If a deliverable is missing or stale, request it or regenerate it before continuing.

## 6. STATE TRACKING & RECOVERY

- Write `sdlc-state.json` to the project root — on phase completion, and (in interactive phases) as work proceeds. Current format (schema v2):
  ```json
  {
    "schema_version": 2,
    "current_phase": "<phase_name>",
    "feature": "<feature_name>",
    "last_gate": "<gate_name>",
    "timestamp": "<iso_8601>",
    "phase_progress": {
      "step": <int>,
      "areas": [
        {"name": "<area name>", "status": "open | in_progress | confirmed"}
      ]
    }
  }
  ```
- `schema_version` and `phase_progress` are **optional** for backward compatibility. Readers (including the `get_pipeline_state` MCP tool) MUST tolerate their absence and fall back to schema v1 behavior (phase-level state only). New writers SHOULD emit both so that mid-phase work is recoverable.
- **Mid-phase updates.** In an interactive phase (e.g. the requirements interview), update `phase_progress` as the work proceeds: advance `step` and set each area's `status` as it is confirmed. Goal: a compaction or restart mid-interview restores the current step and per-area status, not just the phase.
- If context is lost, compacted, or the session restarts, call the `get_pipeline_state(project_path=<your_working_dir>)` MCP tool to re-orient yourself.
- Use `sdlc_resume` to restore Tier 1 context and the relevant phase playbook.
- If `sdlc-state.json` is missing, infer state by scanning the project directory for the following subdirectories and finding the document with the largest numerical prefix:
  - `docs/enhancement/` exists → Enhancement complete
  - `docs/requirements/` exists → Requirements complete
  - `docs/design/` exists → Design complete
  - `docs/implementation/` exists → Implementation complete
  - `docs/review/` exists → Review complete
  - `docs/testing/` exists → Testing complete
  - `docs/deploy/` exists → Deployment complete
  - `docs/monitoring/` exists → Monitoring complete
- Trust explicit state (`sdlc-state.json`) over inferred state.

## 8. PHASE TRANSITION PROTOCOL

Phase transitions follow a strict propose-approve cycle:

1. **Agent completes phase** — produces all deliverables listed in the lifecycle table
2. **Agent halts** — stops work, reports completion, and awaits human approval
3. **Human reviews deliverables** — approves, approves with caveats, or sends agent back
4. **Human advances phase** — invokes `set_pipeline_state` to move to next phase
5. **Agent resumes** — checks state via `get_pipeline_state`, loads phase playbook via `sdlc_phase`

The agent MUST NOT advance phases autonomously unless explicitly directed to do so by the "Phase Exit" section of a phase document. Otherwise, phase advancement requires explicit human action through `set_pipeline_state`.
