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

## 2. Phase-Aware Planning Protocol

Your planning behavior changes depending on the current SDLC phase:

| Phase | Your Role | Worker Delegation |
|---|---|---|
| **Vision (pre-step)** | At pipeline start, if docs/vision.md is missing, run the vision exchange per 13-vision-step.md | Prohibited (agent runs it directly; conversational) |
| **Requirements** | Produce requirements documents in `docs/requirements/` directly | Prohibited |
| **Design** | Produce technical-design documents in `docs/design/` directly | Prohibited |
| **Implementation** | Create implementation plan, delegate steps to Workers | Required |
| **Review** | Produce `review-report.md` directly | Prohibited |
| **Testing** | Produce test files, plus a report in `docs/test-reports/` | Required |
| **Deployment** | Produce deploy configs directly | Required |
| **Monitoring** | Produce monitoring specs directly | Required |

## 3. Context Recovery

If a session is restarted, context is lost, or you receive a signal to resume:
1. Call `sdlc_resume(project_path=<absolute_path>)` to restore framework context and pipeline state.
2. Check `sdlc-state.json` via `get_pipeline_state(project_path=<path>)` to verify your current phase.
3. Call `sdlc_phase("<current_phase>")` to reload the phase playbook.
4. **Do not begin work** until you have confirmed your current phase and loaded the relevant playbook.
