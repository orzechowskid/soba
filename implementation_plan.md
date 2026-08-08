# Implementation Plan — AI-SDLC Phase Enforcement & Human Approval Protocol

## Problem Statement

The AI-SDLC framework is purely advisory. Agents skip phases because:
1. No **phase-lock** — nothing prevents jumping from requirements → implementation
2. No **HALT/STOP** at phase boundaries — agent keeps running
3. No **human approval protocol** — no structured way to record approvals, caveats, or risk acceptances
4. Gates that *can* be verified are treated the same as ones that can't
5. MCP server tools don't enforce phase progression
6. Three phase playbooks (06, 07, 08) are missing entirely

## 1. Architecture & Patterns

### Core Principle
**Agent proposes, human disposes.** The agent produces deliverables and halts. The human approves (with optional caveats) or sends the agent back. The MCP server enforces adjacent-only phase transitions.

### Key Files Modified
| File | Change |
|------|--------|
| `00-bootstrap.md` | Add phase-lock directive, human approval protocol, phase-restricted authority |
| `01-lifecycle-overview.md` | Add approval workflow, tighten gate definitions |
| `03-phase-requirements.md` | Add STOP/HALT block at end |
| `04-phase-design.md` | Add STOP/HALT block at end |
| `05-phase-implementation.md` | Add STOP/HALT block at end |
| `06-phase-review.md` | **Create** — with STOP/HALT block |
| `07-phase-testing.md` | **Create** — with STOP/HALT block |
| `08-phase-deployment.md` | **Create** — with STOP/HALT block |
| `09-phase-monitoring.md` | Add STOP/HALT block at end |
| `12-quality-gates.md` | Split gates into verifiable vs human-required |
| `13-risk-and-governance.md` | Add risk acceptance logging protocol |
| `mcp-server/server.py` | Add `check_gate` tool, restrict `set_pipeline_state` to adjacent transitions |

### New Artifacts
- `docs/decisions/<feature>-approval.md` — per-phase human approval records (caveats, risk acceptances, go-backs)

---

## 2. Step-by-Step Implementation Strategy

### Phase 1: Document Changes — Authority & Protocol (Bootstrap)

- [ ] **Step 1: Add phase-lock directive to `00-bootstrap.md`**
    - *Context*: The agent needs an explicit rule that it cannot advance phases on its own.
    - *Instruction*: Add a new section **§8. PHASE LOCK** to `00-bootstrap.md` with these rules:
      - You MUST NOT advance to the next phase without explicit human approval.
      - At the end of each phase, produce your deliverable, then STOP and wait for the human to invoke `set_pipeline_state`.
      - You MAY propose advancing, but you MUST NOT execute the advancement yourself.
      - If the human sends you back to a prior phase, re-execute from the backtracking rules in `01-lifecycle-overview.md`.

- [ ] **Step 2: Restrict authority by phase in `00-bootstrap.md`**
    - *Context*: The authority matrix currently grants full autonomy regardless of phase. Code should only be written during implementation phase.
    - *Instruction*: Modify **§2. AUTHORITY MATRIX** to add:
      - **Phase-Restricted Authority**: Your autonomy is scoped to your current phase. During requirements, you may only write `requirements.md`. During design, you may only write ADRs. During implementation, you may write code. You MUST NOT produce deliverables belonging to a future phase.
      - Add a sub-table mapping phase → permitted file operations:
        - `requirements`: write `requirements.md`, read codebase for context only
        - `design`: write `docs/adr/*.md`, read codebase for context
        - `implementation`: write/modify source code, write `docs/implementation/*.md`
        - `review`: read code, write `docs/review/*.md`
        - `testing`: write test files, write `docs/review/*.md` (test reports)
        - `deployment`: write config files, write `docs/deploy/*.md`
        - `monitoring`: write monitoring config, write `docs/monitoring/*.md`

- [ ] **Step 3: Add human approval protocol to `00-bootstrap.md`**
    - *Context*: When the human approves, the decision needs to be recorded — especially caveats and risk acceptances.
    - *Instruction*: Add **§9. HUMAN APPROVAL PROTOCOL** to `00-bootstrap.md`:
      - Each phase ends with a human approval gate. The agent produces deliverables and halts.
      - The human may respond with one of three decisions:
        1. **Approve** — proceed to next phase. No further action.
        2. **Approve with caveats** — proceed, but caveats are documented in the phase's deliverable file under a `## Human Caveats` section.
        3. **Send back to [phase]** — agent backtracks per lifecycle rules.
      - When the human accepts a risk that the agent flagged, the agent MUST record this in `docs/risks/` with: risk description, agent recommendation, human decision, timestamp.
      - Approval records are stored in `docs/decisions/<feature>-approval.md` with one entry per phase: phase, decision type, caveats (if any), timestamp.

### Phase 2: Document Changes — Lifecycle & Gates

- [ ] **Step 4: Add approval workflow to `01-lifecycle-overview.md`**
    - *Context*: The lifecycle table should reference the approval protocol.
    - *Instruction*: 
      - Add a column "Human Gate" to the lifecycle table, marking each phase with "Required — agent halts and awaits approval."
      - Add **§8. PHASE TRANSITION PROTOCOL**:
        - Agent completes phase deliverables → agent halts
        - Human reviews deliverables → human invokes `set_pipeline_state` to advance
        - Agent checks state on next session start via `get_pipeline_state`
      - Update **§4. GATE POLICY**: "Advisory gates that can be verified by the agent (deliverable existence, format compliance) should be checked via the `check_gate` MCP tool. Gates requiring human judgment (manual testing, third-party review) require explicit human confirmation. Document all gate decisions in the phase deliverable."

- [ ] **Step 5: Tighten `12-quality-gates.md` — split into verifiable vs human-required**
    - *Context*: Some gates can be checked automatically, others need human judgment.
    - *Instruction*: Restructure each gate into two sub-sections:
      - **Verifiable** (agent can check via `check_gate`): deliverable exists, required sections present, format correct
      - **Human Judgment** (requires explicit human confirmation): manual testing, third-party review, business validation
      - Example for Requirements → Design gate:
        - Verifiable: `requirements.md` exists, contains numbered FRs, contains ACs, contains constraints
        - Human Judgment: requirements completeness, business priority, stakeholder alignment

- [ ] **Step 6: Add risk acceptance logging to `13-risk-and-governance.md`**
    - *Context*: When a human overrides a risk recommendation, it must be recorded.
    - *Instruction*: Add **§8. RISK ACCEPTANCE LOGGING** to `13-risk-and-governance.md`:
      - When an agent flags a risk and the human user chooses to proceed despite it, the agent MUST create or append to `docs/risks/<number>-<feature>-acceptances.md`.
      - Required fields: risk description, severity, agent recommendation, human decision, justification, timestamp.
      - These records are immutable once created.

### Phase 3: Document Changes — STOP/HALT Blocks in Phase Playbooks

- [ ] **Step 7: Add STOP/HALT block to `03-phase-requirements.md`**
    - *Context*: Agent must stop after producing requirements.md.
    - *Instruction*: Add a new section **§8. PHASE EXIT** to the end of `03-phase-requirements.md`:
      ```
      ## 8. PHASE EXIT
      After producing `requirements.md`:
      1. Verify all sections present (FRs, ACs, Constraints, Assumptions, Open Questions, Out-of-Scope).
      2. Write `sdlc-state.json` with `current_phase: requirements` (or request human to invoke `set_pipeline_state`).
      3. **STOP**. Await human approval before proceeding to design phase.
      4. Do NOT begin design work. Do NOT write ADRs. Do NOT write code.
      ```

- [ ] **Step 8: Add STOP/HALT block to `04-phase-design.md`**
    - *Instruction*: Add **§8. PHASE EXIT**:
      ```
      ## 8. PHASE EXIT
      After producing ADR(s) in `docs/adr/`:
      1. Verify all significant decisions are documented with tradeoffs.
      2. Request human approval of design artifacts.
      3. **STOP**. Await human approval before proceeding to implementation phase.
      4. Do NOT write code. Do NOT create source files.
      ```

- [ ] **Step 9: Add STOP/HALT block to `05-phase-implementation.md`**
    - *Instruction*: Add **§10. PHASE EXIT** (numbering continues from existing §9):
      ```
      ## 10. PHASE EXIT
      After producing source code, implementation summary, and API docs (if applicable):
      1. Verify code compiles/runs without errors.
      2. Verify inline documentation is present.
      3. Request human approval of implementation artifacts.
      4. **STOP**. Await human approval before proceeding to review phase.
      ```

- [ ] **Step 10: Add STOP/HALT block to `09-phase-monitoring.md`**
    - *Instruction*: Add a **PHASE EXIT** section to the end of `09-phase-monitoring.md`:
      ```
      ## PHASE EXIT
      After producing `monitoring-spec.md`:
      1. Verify all metrics, alerts, and baselines are documented.
      2. **STOP**. SDLC pipeline complete for this feature.
      ```

### Phase 4: Create Missing Phase Playbooks (06, 07, 08)

- [ ] **Step 11: Create `06-phase-review.md`**
    - *Context*: Missing — agent gets "Document not found" for review phase.
    - *Instruction*: Create `06-phase-review.md` with sections:
      1. Self-review checklist (correctness, completeness, code quality, security)
      2. AI code validation patterns (common AI-generated code issues to check)
      3. Severity classification (critical, major, minor, cosmetic)
      4. Output: `docs/review/<number>-<feature>-review.md`
      5. **PHASE EXIT** — STOP, await human approval

- [ ] **Step 12: Create `07-phase-testing.md`**
    - *Context*: Missing — agent gets "Document not found" for testing phase.
    - *Instruction*: Create `07-phase-testing.md` with sections:
      1. Test strategy (unit, integration, e2e)
      2. Coverage targets (define thresholds)
      3. Test generation guidelines
      4. Regression protocol
      5. Output: test files + `docs/testing/<number>-<feature>-test-report.md`
      6. **PHASE EXIT** — STOP, await human approval

- [ ] **Step 13: Create `08-phase-deployment.md`**
    - *Context*: Missing — agent gets "Document not found" for deployment phase.
    - *Instruction*: Create `08-phase-deployment.md` with sections:
      1. Deployment assessment (environment, strategy)
      2. CI/CD changes
      3. Rollback procedures
      4. Output: `deploy-config.md` + CI/CD files in `docs/deploy/`
      5. **PHASE EXIT** — STOP, await human approval

### Phase 5: MCP Server Hardening

- [ ] **Step 14: Restrict `set_pipeline_state` to adjacent transitions in `server.py`**
    - *Context*: Currently any phase can be set from any phase. This should require explicit intent.
    - *Instruction*: Modify the `set_pipeline_state` handler in `server.py`:
      - Define phase order: `["requirements", "design", "implementation", "review", "testing", "deployment", "monitoring"]`
      - When `current_phase` is provided, compare against the existing `current_phase` in state.
      - Allow transitions where `new_index <= old_index + 2` (forward: adjacent +1; backward: any, per backtracking rules).
      - If `new_index > old_index + 1`, return a warning (not error) listing the skipped phases: `"Warning: Skipping phases X, Y. Ensure deliverables for those phases are complete."`
      - Add an optional parameter `override_reason` (string) that must be provided when skipping phases. Store it in state.

- [ ] **Step 15: Add `check_gate` tool to `server.py`**
    - *Context*: Agent needs to verify its own deliverables before requesting approval.
    - *Instruction*: Add a new MCP tool `check_gate` with parameters:
      - `project_path` (required): absolute path to project root
      - `from_phase` (required): phase being exited (e.g., "requirements")
      - `to_phase` (required): phase being entered (e.g., "design")
      - Returns a structured result:
        - `verifiable_gates`: list of {gate, status: pass/fail, detail}
        - `human_gates`: list of {gate, requires: "human judgment", detail}
        - `overall`: "pass" (all verifiable gates pass), "fail" (verifiable gate failed), or "pending" (all verifiable pass, human gates remain)
      - Gate definitions embedded in tool:
        - requirements→design: check `requirements.md` exists with FR sections, AC sections, Constraints section
        - design→implementation: check `docs/adr/` exists with at least one `.md` file
        - implementation→review: check source files exist, check `docs/implementation/` exists
        - review→testing: check `docs/review/` exists (human judgment: peer review complete)
        - testing→deployment: check test files exist, check `docs/testing/` exists
        - deployment→monitoring: check `docs/deploy/` exists

- [ ] **Step 16: Add `record_approval` tool to `server.py`**
    - *Context*: When human approves, the decision and any caveats should be recorded.
    - *Instruction*: Add a new MCP tool `record_approval` with parameters:
      - `project_path` (required)
      - `phase` (required): the phase being approved
      - `decision` (required): "approve" | "approve_with_caveats" | "send_back_to_[phase]"
      - `caveats` (optional): text describing any caveats
      - `risk_acceptances` (optional): array of {risk, severity, agent_recommendation, human_decision, justification}
      - Appends a structured entry to `docs/decisions/<feature>-approval.md` in the project root.
      - Creates the file and directory if they don't exist.

### Phase 6: Integration & Verification

- [ ] **Step 17: Update `README.md` with new tools and workflows**
    - *Context*: README documents the MCP server interface and should reflect new tools.
    - *Instruction*: Update the Tools table to include `check_gate` and `record_approval`. Add a "Usage Workflow" section describing the approve/halt cycle.

- [ ] **Step 18: Manual verification**
    - *Context*: Confirm the full pipeline works end-to-end with enforcement.
    - *Instruction*: 
      1. Start a test SDLC pipeline with `begin_sdlc`
      2. Verify `sdlc_bootstrap` loads all Tier 1 docs
      3. Verify each `sdlc_phase` prompt loads correctly (including 06, 07, 08)
      4. Verify `check_gate` returns correct results for each gate
      5. Verify `set_pipeline_state` warns on skipped phases
      6. Verify `record_approval` creates proper approval records
      7. Verify each phase playbook ends with STOP/HALT directive

---

## 3. Dependency Order

Steps 1-3 (bootstrap changes) are independent of Steps 4-6 (lifecycle/gates/risk).
Steps 7-10 (STOP/HALT blocks) depend on Steps 1-3 completing (so the phase-lock context exists).
Step 11-13 (missing playbooks) are independent of each other.
Steps 14-16 (MCP server) are independent of document changes but should be deployed together.
Step 17 (README) should be last.
Step 18 (verification) is final.

## 4. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Existing agents using the MCP server break due to stricter `set_pipeline_state` | Medium | Warnings, not errors — allows override with reason |
| New `record_approval` tool adds friction | Low | Optional — agents can still use `set_pipeline_state` directly |
| STOP/HALT directives conflict with other system prompts | Medium | Phase-lock is scoped to AI-SDLC context; other directives take precedence per conflict resolution rules |
