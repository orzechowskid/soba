## 1. SDLC Pipeline Enforcement

When working on features within a project that uses the AI-SDLC framework (MCP tools: `begin_sdlc`, `sdlc_bootstrap`, `sdlc_phase`, `check_gate`, `set_pipeline_state`, `record_approval`), you **MUST** follow this protocol. This is not optional.  If previous guidelines conflict with AI-SDLC rules then the AI-SDLC wins.  This is not optional.

### 1.1 Session Initialization

At the start of every SDLC pipeline:
1. Call the `sdlc_bootstrap` MCP prompt to load framework reference documents.
2. Call `begin_sdlc(project_path=<absolute_path>, feature="<name>")` to initialize the pipeline state.
3. Check for `docs/vision.md`: if present, load it as project context; if absent, follow the vision exchange in `13-vision-step.md` before entering the phase.
4. Call `sdlc_phase("<current_phase>")` to load the phase playbook before doing any work.

### 1.2 Phase Protocol

For every phase:
1. Load the phase playbook via `sdlc_phase("<current_phase>")`.
2. Read the playbook instructions fully before producing any deliverables.
3. Produce **only** deliverables belonging to your current phase.
4. After completing deliverables, run `check_gate(project_path=<path>, from_phase="<current>", to_phase="<next>")` to verify.
5. Report completion to the human, list all deliverables produced, and **STOP**.
6. **Await human approval** before proceeding. Do NOT advance phases autonomously.

### 1.3 Phase Lock (Mandatory)

- You **MUST NOT** advance to the next SDLC phase without explicit human approval.
- You **MUST NOT** produce deliverables belonging to a future phase.
- You **MUST NOT** write code, or spawn sub-agents to write code, during the requirements phase.
- You **MUST NOT** write code, or spawn sub-agents to write code, during the design phase.
- You **MUST NOT** write technical-design documents, or spawn sub-agents to write technical-design documents, during the requirements phase.
- You may *propose* advancing ("I recommend proceeding to the design phase"), but you **MUST NOT** execute the advancement yourself unless a phase gate _specifically and explicitly_ allows for it.
- If the human sends you back to a prior phase, re-execute from the backtracking rules in `01-lifecycle-overview.md`.
- If you find yourself about to perform work outside your current phase, **STOP** and report the phase violation.

### 1.4 Worker Delegation Rules

- You may spawn `coder` subagents **ONLY** during the **implementation** phase.
- During requirements, design, review, testing, deployment, and monitoring phases, you produce deliverables **directly** — do not delegate to Workers.
- Workers are execution tools; they do not manage phases. Phase responsibility is entirely yours.

### 1.5 Change Requests (In-Flight)

A user message that alters content in a deliverable of a phase strictly earlier than the current phase is a **cross-phase change request**. Local changes (anything inside the current phase, including at its exit gate) follow the phase's normal workflow — no protocol.

When a cross-phase change request arrives:

1. **Halt** current work immediately. A pending approval request is voided — do not record an approval for it.
2. **Impact map:** quote each affected prior section (file + heading), list affected FR/AC/TR items and the phase of each touched deliverable, and derive the **earliest affected phase** as the proposed rewind target. If the request adds net-new scope rather than modifying agreed scope, it is a **new feature** — say so and stop.
3. **Batch:** if another change request arrives before the rewind completes (the feature returns to the phase it was in when the change was first requested), merge it: union impact map, earliest affected phase across all pending changes, one human decision.
4. **The human confirms the target, then invokes `set_pipeline_state`** to the rewind target. You MUST NOT rewind autonomously.
5. Re-execute per the backtracking rules in `01-lifecycle-overview.md` §2, with reuse:
   - **Affected deliverables:** keep the existing document and append an `## Addendum` marking superseded sections. The sequential number does not change.
   - **Unaffected phases:** fast-reconfirm — re-verify the deliverable (for implementation, the actual code and tests) against the current upstream deliverables, state why it is unaffected, and re-present the existing deliverable. A phase that fails verification is affected and receives real work.
   - The phase's own playbook still applies on re-entry, scoped to the affected areas. If the change adds a new area, the scope step re-confirms the area list including the new area.
   - Never delete partial work from an interrupted phase; report its state in the impact map and reconcile it when the phase is re-executed.
6. **Every gate at or after the rewind target requires a fresh `record_approval` — including fast-reconfirmed, unchanged deliverables. Never skip a gate halt.**
7. No change log file exists. Change history lives in the addenda and in each deliverable's Decisions Log.
8. Changes to `docs/vision.md` are out of scope for this protocol.

## 2. Phase-Aware Planning Protocol

Your planning behavior changes depending on the current SDLC phase:

| Phase | Your Role | Worker Delegation |
|---|---|---|
| **Vision (pre-step)** | At pipeline start, if docs/vision.md is missing, run the vision exchange per 13-vision-step.md | Prohibited (agent runs it directly; conversational) |
| **Requirements** | Produce requirements documents in `docs/requirements/` directly | Prohibited |
| **Design** | Produce technical-design documents in `docs/design/` directly | Prohibited |
| **Implementation** | Create implementation plan, delegate steps to Workers | Required |
| **Review** | Produce `docs/review/<n>-<feature>.md` directly | Prohibited |
| **Testing** | Produce test files, plus a report in `docs/testing/` | Required |
| **Deployment** | Produce deploy configs directly | Required |
| **Monitoring** | Produce monitoring specs directly | Required |

## 3. Context Recovery

If a session is restarted, context is lost, or you receive a signal to resume:
1. Call `sdlc_resume(project_path=<absolute_path>)` to restore framework context and pipeline state.
2. Check `sdlc-state.json` via `get_pipeline_state(project_path=<path>)` to verify your current phase.
3. Call `sdlc_phase("<current_phase>")` to reload the phase playbook.
4. **Do not begin work** until you have confirmed your current phase and loaded the relevant playbook.
