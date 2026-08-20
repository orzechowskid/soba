# Enhancement Phase Playbook

This phase of the AI-SDLC pipeline is the **customer/product intake** phase. A vague feature request — which may come from a field engineer, a salesperson, an end user, or anyone without a well-articulated product vision — is received. Before formalizing requirements, the agent must understand the existing system so it can properly scope where the new change fits.

This phase runs **only on brownfield projects** (existing applications with prior features already built). Greenfield projects skip this phase entirely and begin at Requirements.

## Ingestion Guidelines

Before interviewing the user, ingest the following from the existing project:

### Prior Feature Documentation
- **DO**: Read `docs/vision.md` if present — the project's intended trajectory; the anchor for where the change fits.
- **DO**: Read `docs/requirements/` files to understand what features have been built.
- **DO**: Read `docs/design/` files to understand architectural decisions and the technology stack.
- **DO**: Read `docs/decisions/` approval logs to understand what was approved, rejected, or caveated.
- **DO**: Read `docs/risks/` if present to understand known risk acceptances.
- **DO NOT**: Bulk-read every document. Search for documents relevant to the domain the new feature will touch, and limit reading to those.

### Codebase Structure
- **DO**: Scan the source code directory structure (top-level modules/packages) to understand the current shape of the application.
- **DO**: Note existing patterns, conventions, and architectural layers.
- **DO NOT**: Ingest the entire codebase. A high-level organizational overview is sufficient.

### Build and Deployment
- **DO**: Check for CI/CD pipeline files (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, etc.) to understand the build/deploy process.
- **DO**: Note existing dependency management (e.g., `package.json`, `pyproject.toml`, `go.mod`).
- **DO**: Check for existing `sdlc-state.json` to understand where the project left off.

## Interview Guidelines

After ingesting the existing system:

- **DO**: Ask the user clarifying questions about the vague feature request.
- **DO**: Identify the user's core goal for the change.
- **DO**: Understand how the change relates to existing features and capabilities.
- **DO NOT**: Discuss technical implementation details — those belong in the Design phase.
- **DO NOT**: Make assumptions about what the existing system does or how the change should work.
- **DO**: Surface any tensions between the requested change and existing system constraints.

## Pre-Output

Before producing the context brief, verify:
- You have read the relevant prior documentation.
- You understand the current system architecture at a high level.
- You can articulate where the new change fits within the existing system.

## Output

### Deliverable

Write `docs/enhancement/<number>-<feature>.md` (relative to the **target project root**).

The deliverable must contain, in this order:

1. **Current System Overview** — concise summary of what the existing application does, its architecture, and technology stack.
2. **Prior Features** — which features have been built, referencing prior requirements and design documents by filename.
3. **Relevant Design References** — which prior architectural decisions affect this new change.
4. **Change Context** — where the new feature request fits within the existing system, what it will touch, and any known tensions or constraints from prior decisions.

The filename number must align with the numbering scheme used for subsequent requirements and design documents for this feature. If this is the second feature, use `02-`. If it's the third, use `03-`, etc.

---

## Phase Exit

After producing `docs/enhancement/<number>-<feature>.md`:

1. Verify all four sections are present: Current System Overview, Prior Features, Relevant Design References, Change Context.
2. Run `check_gate(project_path=<project>, from_phase="enhancement", to_phase="requirements")` to verify deliverables.
3. Report completion to the human. List all deliverables produced.
4. **STOP.** Await human approval before proceeding to Requirements phase.
5. Do NOT begin requirements work. Do NOT write requirements documents. Do NOT produce deliverables for future phases.

---

## Examples

> Examples in this document are illustrative, not prescriptive. Follow the stated rules, not the example content. Do not reproduce example naming, structure, or domain specifics.
