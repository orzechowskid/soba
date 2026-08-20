# Lifecycle Overview

## 1. LIFECYCLE OVERVIEW

You operate through 8 phases. Load the relevant Tier 2 playbook (`02-` through `08-`, plus `09-phase-enhancement.md`) for your current phase.

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
- Re-execution following a cross-phase change request reuses prior deliverables per §7 (append an addendum to affected deliverables; fast-reconfirm unaffected phases). The re-execution order is unchanged.

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

## 7. IN-FLIGHT CHANGE CONTROL

The user may change their mind about any already-agreed aspect of the feature at any time. Most such changes are **local**: they touch only the currently active phase (including while sitting at that phase's exit gate). Local changes are handled by the phase's normal workflow — no protocol, no addendum, no record.

A change is **cross-phase** if and only if it alters content in a deliverable of a phase strictly earlier than the current phase. The operational test: can you name a section in a prior deliverable that the user's statement contradicts or modifies (file + heading)? If yes, it is cross-phase. If you cannot name one, it is local. When in doubt, treat it as cross-phase and present it as a change request — an over-trigger costs the human one "no, just do it"; an under-trigger silently corrupts an approved artifact with no gate in between.

Boundary with new features: a request that *adds* scope rather than modifying previously-agreed scope is a **new feature** (a new sequential number and a new pipeline entry), not a change. Say so and stop.

### Protocol

1. **Halt.** Stop current work immediately. A pending approval request is voided by the change — do not record an approval for it.
2. **Impact map (agent).** For every prior deliverable the change touches, quote the affected section(s) (file + heading) and list the affected FR/AC/TR items, code, tests, and configuration. Name the phase of each touched deliverable and derive the **earliest affected phase**. Present the map and propose the rewind target.
3. **Batch.** If another change request arrives before the rewind completes (the rewind completes when the feature returns to the phase it was in when the change was first requested), merge it into the same rewind: the impact map is the union of all pending changes, the rewind target is the earliest affected phase across all of them, and the human makes one decision on the combined map.
4. **Rewind (human).** The human confirms the target, then invokes `set_pipeline_state` to the earliest affected phase. The agent MUST NOT rewind autonomously. The agent then re-executes from that phase per §2 (Backtracking Rule), with reuse:
   - **Affected deliverables:** reuse the existing document; append an `## Addendum` section (original text is preserved, superseded sections are marked). The sequential number does not change.
   - **Unaffected phases:** **fast-reconfirm** — visit the phase in order, re-verify the deliverable against the current state of upstream deliverables (for implementation, against the actual code and tests), state why it is unaffected, and re-present the existing deliverable. A phase that fails verification is affected and receives real work.
   - The phase's own playbook still applies on re-entry, scoped to the affected areas (e.g., a requirements re-interview runs all five steps but drills only the affected areas). If the change adds a new area, the scope step re-confirms the area list including the new area.
   - Partial work from an interrupted phase is never deleted. Report its state in the impact map and reconcile it (keep, amend, or discard) when the phase is re-executed.
5. **Re-approval (human).** Every gate at or after the rewind target requires a fresh `record_approval` — including fast-reconfirmed phases whose deliverables are byte-for-byte unchanged. Fast-reconfirm MUST NOT skip the gate halt. Prior approval entries in `docs/decisions/` remain immutable history.

### Scope exclusions and relationships

- Local changes (current phase, including at its exit gate): no protocol, no addendum, no record.
- A gate-time `send_back_to_[phase]` decision is a special case of this protocol (origin at the gate).
- Changes to `docs/vision.md` are out of scope for this protocol.
- No separate change log exists. The history of a change lives in the addenda it produces and in the Decisions Log of each affected deliverable.

## 8. PHASE TRANSITION PROTOCOL

Phase transitions follow a strict propose-approve cycle:

1. **Agent completes phase** — produces all deliverables listed in the lifecycle table
2. **Agent halts** — stops work, reports completion, and awaits human approval
3. **Human reviews deliverables** — approves, approves with caveats, or sends agent back
4. **Human advances phase** — invokes `set_pipeline_state` to move to next phase
5. **Agent resumes** — checks state via `get_pipeline_state`, loads phase playbook via `sdlc_phase`

The agent MUST NOT advance phases autonomously unless explicitly directed to do so by the "Phase Exit" section of a phase document. Otherwise, phase advancement requires explicit human action through `set_pipeline_state`.
