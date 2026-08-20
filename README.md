# AI-SDLC Document Set

LLM-consumable instruction artifacts for autonomous AI-driven software development. Documents serve as system prompts and playbooks, not human-readable guides.

## Installation

Clone this repo and store it somewhere reachable by your agent harness or IDE, then install the provided MCP server.

The last step is optional but recommended: append the contents of `prompts/instruction-orchestrator.md` to the prompt you provide to your architect/orchestrator/etc. agent.

### Client Configuration

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "ai-sdlc": {
      "command": "python",
      "args": ["/absolute/path/to/sdlc/mcp-server/server.py"]
    }
  }
}
```

**Other MCP Clients**: Point to `server.py` using stdio transport.

## Usage

You should just be able to tell your agent to kick off (or resume) the AI-SDLC process in your project directory.

### Building a new feature

Building a new feature means entering the pipeline at the requirements phase, where you will be asked to define the scope of this new functionality from an end-user's perspective.

#### Beginning a new project

One special case of building a new feature is when you're building your _first_ feature.  If that's the case then you'll be asked to help draft a vision document for the overall goals (and non-goals) of your project.  From there you'll enter the pipeline as described above.

### Resuming a feature in progress

If something happens (you restarted your harness or IDE; you ran out of LLM context and had to compact or restart your session) then you should be able to pick up more or less where you left off.  The pipeline looks for a `sdlc-state.json` file in the root of your repo, and uses it to track state:
```json
{
  "schema_version": 2,
  "current_phase": "implementation",
  "feature": "sso-auth",
  "last_gate": "design",
  "timestamp": "2026-08-02T18:24:47.892384",
  "project_mode": "greenfield",
  "phase_progress": {
    "step": 2,
    "areas": [
      {"name": "auth-flow", "status": "confirmed"},
      {"name": "session-handling", "status": "in_progress"}
    ]
  }
}
```
(tip: add `sdlc-state.json` to your `.gitignore`)

### Changing an approved aspect mid-pipeline

You can change your mind about anything already agreed and approved. Just tell the agent. If the change reaches back into a phase whose gate has already been approved, the agent halts and presents an impact map: which prior decisions and deliverables it touches, and the earliest phase that must be revisited. You confirm the rewind; the agent re-executes the affected phases in order, appending addenda to affected deliverables instead of rewriting them. Every gate at or after the rewind point asks for your approval again — including phases whose documents are unchanged. Changes that stay inside the current phase are handled by that phase's normal workflow. See `01-lifecycle-overview.md` §7 for the full protocol.

## Artifact Directories

Deliverables for each phase of this pipeline are written to disk in the target project's root directory under the following subdirectories:

- `docs/enhancement/` — System context briefs (brownfield projects)
- `docs/requirements/` — Requirements documents
- `docs/design/` — Technical design documents
- `docs/implementation/` — Implementation summaries
- `docs/review/` — Review reports
- `docs/testing/` — Test reports
- `docs/deploy/` — Deployment plans
- `docs/monitoring/` — Monitoring plans
- `docs/decisions/` — Approval logs written by `record_approval`
- `docs/risks/` — Risk descriptions and acceptances
- `docs/vision.md` — project-level vision document, created by the vision step

All documents apart from the vision document use sequential numbering which tracks across phases.  If you're building the "sso-auth" feature and you have a `123-sso-auth.md` file in your `docs/requirements` directory, then (eventually) as you complete each stage of the pipeline you'll also have `123-sso-auth.md` in `docs/design`, `docs/implementation`, and so on.

## Document Index

| Filename | Loading Tier | Purpose |
|---|---|---|
| `00-bootstrap.md` | 1 (always) | System prompt: role, authority, context-loading, conflict resolution, output expectations, failure behavior |
| `01-lifecycle-overview.md` | 1 (always) | Phase map, gates, deliverables, backtracking rules, handoff protocols, in-flight change control |
| `02-phase-requirements.md` | 2 (on-demand) | Requirements elicitation, acceptance criteria, clarification protocol, output structure |
| `03-phase-design.md` | 2 (on-demand) | Technical-design format, simplicity default, tradeoff analysis, tech stack selection |
| `04-phase-implementation.md` | 2 (on-demand) | Coding conventions, API validation, UI compliance (WCAG AA), incremental delivery, dependency management |
| `05-phase-review.md` | 2 (on-demand) | Self-review checklist, AI code validation, severity classification, human peer review gate |
| `06-phase-testing.md` | 2 (on-demand) | Test strategy, coverage targets, test generation, regression protocol |
| `07-phase-deployment.md` | 2 (on-demand) | Deployment assessment, strategy selection, CI/CD changes, rollback procedures |
| `08-phase-monitoring.md` | 2 (on-demand) | Metrics proposal, alerting thresholds, log structure, performance baselines |
| `09-phase-enhancement.md` | 2 (on-demand) | Brownfield intake: system context brief, prior-feature awareness, change context |
| `09-coding-standards.md` | 3 (reference) | Language-agnostic naming, structure, error handling, state management |
| `10-architecture-principles.md` | 3 (reference) | Design principles, dependency direction, interface stability, anti-patterns |
| `11-quality-gates.md` | 3 (reference) | Pass/fail criteria at each lifecycle gate, override policy |
| `12-risk-and-governance.md` | 3 (reference) | Risk taxonomy, severity classification, mitigation patterns, data handling, accountability |
| `13-vision-step.md` | 3 (reference) | Project-level vision step: detection at pipeline start, the vision exchange, and the docs/vision.md lifecycle |

## MCP Server

This framework is distributed as an MCP server for LLM consumption. Configure your MCP client to point to the `mcp-server/` directory.

### Tools

| Tool | Purpose |
|---|---|
| `list_documents` | List available SDL docs with tier and purpose |
| `get_document(doc_name)` | Retrieve a specific document by filename |
| `get_pipeline_state(project_path)` | Read project pipeline state from `sdlc-state.json`. Requires `project_path` parameter. |
| `begin_sdlc(project_path, feature)` | Initialize pipeline state for a new feature (auto-detects greenfield vs brownfield). Fails if `sdlc-state.json` already exists. |
| `set_pipeline_state(project_path, current_phase, feature, last_gate, override_reason)` | Update pipeline state. Phase advancement is a human action; skipping phases forward requires `override_reason`. |
| `check_gate(project_path, from_phase, to_phase)` | Verify deliverables exist and are properly formatted before requesting human approval. Returns verifiable gate results and lists human judgment gates. |
| `record_approval(project_path, phase, decision, caveats, risk_acceptances)` | Record a human approval decision for a phase transition. Logs to `docs/decisions/<feature>-approval.md`. |

### Prompts

| Prompt | Purpose |
|---|---|
| `sdlc_bootstrap` | Load Tier 1 documents (bootstrap + lifecycle overview) as session context |
| `sdlc_phase(phase_name)` | Load the relevant Tier 2 playbook for a given phase |
| `sdlc_resume(project_path)` | Restore context after loss/compaction: loads Tier 1 + current phase playbook + pipeline state |

### Usage Workflow

1. Start a new pipeline → `begin_sdlc(project_path, feature)`
2. Bootstrap context → use `sdlc_bootstrap` prompt
3. Enter a phase → use `sdlc_phase("<phase>")` prompt
4. Agent produces deliverables, then **halts**
5. Agent runs `check_gate(project_path, from_phase, to_phase)` to verify deliverables
6. Human reviews deliverables and records decision → `record_approval(project_path, phase, decision, caveats)`
7. Human advances phase → `set_pipeline_state(project_path, current_phase="<next_phase>")`
   - Skipping phases requires an `override_reason` parameter
8. Repeat from step 3 for the new phase
9. Context lost → use `sdlc_resume("<project_path>")` prompt

**Phase Lock:** The agent MUST NOT advance phases autonomously. Each phase transition requires explicit human action through `set_pipeline_state`.
