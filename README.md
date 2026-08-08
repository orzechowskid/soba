# AI-SDLC Document Set

LLM-consumable instruction artifacts for autonomous AI-driven software development. Documents serve as system prompts and playbooks, not human-readable guides.

## Document Index

| Filename | Tier | Purpose |
|---|---|---|
| `00-bootstrap.md` | 1 (always) | System prompt: role, authority, context-loading, conflict resolution, output expectations, failure behavior |
| `01-lifecycle-overview.md` | 1 (always) | Phase map, gates, deliverables, backtracking rules, handoff protocols |
| `03-phase-requirements.md` | 2 (on-demand) | Requirements elicitation, acceptance criteria, clarification protocol, output structure |
| `04-phase-design.md` | 2 (on-demand) | Decision framework, ADR format, simplicity default, tradeoff analysis, tech stack selection |
| `05-phase-implementation.md` | 2 (on-demand) | Coding conventions, API validation, UI compliance (WCAG AA), incremental delivery, dependency management |
| `06-phase-review.md` | 2 (on-demand) | Self-review checklist, AI code validation, severity classification, human peer review gate |
| `07-phase-testing.md` | 2 (on-demand) | Test strategy, coverage targets, test generation, regression protocol |
| `08-phase-deployment.md` | 2 (on-demand) | Deployment assessment, strategy selection, CI/CD changes, rollback procedures |
| `09-phase-monitoring.md` | 2 (on-demand) | Metrics proposal, alerting thresholds, log structure, performance baselines |
| `10-coding-standards.md` | 3 (reference) | Language-agnostic naming, structure, error handling, state management |
| `11-architecture-principles.md` | 3 (reference) | Design principles, dependency direction, interface stability, anti-patterns |
| `12-quality-gates.md` | 3 (reference) | Pass/fail criteria at each lifecycle gate, override policy |
| `13-risk-and-governance.md` | 3 (reference) | Risk taxonomy, severity classification, mitigation patterns, data handling, accountability |

## Loading Protocol

- **Tier 1**: Always loaded into agent context at session start.
- **Tier 2**: Loaded on-demand for the active lifecycle phase.
- **Tier 3**: Loaded on-demand when specific reference is needed.

## Artifact Directories

Phase deliverables are written to disk in the **target project's** root directory, under the following subdirectories (using sequential numbering aligned with the project's ADR sequence):

- `docs/adr/` — Architecture Decision Records
- `docs/implementation/` — Implementation summaries
- `docs/review/` — Review reports
- `docs/deploy/` — Deployment plans
- `docs/monitoring/` — Monitoring plans
- `docs/risks/` — Risk descriptions and acceptances

## MCP Server

This framework is distributed as an MCP server for LLM consumption. Configure your MCP client to point to the `mcp-server/` directory.

### Tools

| Tool | Purpose |
|---|---|
| `list_documents` | List available SDL docs with tier and purpose |
| `get_document(doc_name)` | Retrieve a specific document by filename |
| `get_pipeline_state(project_path)` | Read project pipeline state from `sdlc-state.json`. Requires `project_path` parameter. |
| `check_gate(project_path, from_phase, to_phase)` | Verify deliverables exist and are properly formatted before requesting human approval. Returns verifiable gate results and lists human judgment gates. |
| `record_approval(project_path, phase, decision, caveats, risk_acceptances)` | Record a human approval decision for a phase transition. Logs to `docs/decisions/<feature>-approval.md`. |

### Prompts

| Prompt | Purpose |
|---|---|
| `sdlc_bootstrap` | Load Tier 1 documents (bootstrap + lifecycle overview) as session context |
| `sdlc_phase(phase_name)` | Load the relevant Tier 2 playbook for a given phase |
| `sdlc_resume(project_path)` | Restore context after loss/compaction: loads Tier 1 + current phase playbook + pipeline state |

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

### Usage

1. Start a new session → use `sdlc_bootstrap` prompt
2. Enter a phase → use `sdlc_phase("<phase>")` prompt
3. Context lost → use `sdlc_resume("<project_path>")` prompt
4. Reference docs → use `get_document("<filename>")` tool

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
