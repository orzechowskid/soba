# Project Vision Step

The vision step is a project-level pre-step that runs at fresh pipeline start, before the first phase. It ensures the project has a living `docs/vision.md` — an anchor for where the project is heading — so feature interviews stop re-deriving the boundary between today's scope and the eventual picture.

The vision step is **not a phase**: it has no entry in the phase list, no gate, and no state-machine entry. It is a documented convention, not machine-enforced. Nothing about it is recorded in `sdlc-state.json`, and session resume does not need to know about it.

## When It Runs

- **Detection.** At fresh pipeline start (a new `begin_sdlc`), before entering the first phase — Enhancement on brownfield projects, Requirements on greenfield — check for `docs/vision.md` in the project.
  - **Present:** load it as project context and proceed. No exchange, no user interaction.
  - **Missing:** run the vision exchange below before entering the first phase.
- **Fresh start only.** A project already mid-pipeline (in Requirements or later) is not interrupted to run the exchange; the document is created on the next feature's fresh start.
- On brownfield projects the exchange runs **before** the Enhancement phase: understanding where the project is heading comes before scoping changes to the existing system.

## The Exchange

A short structured exchange in which the user expresses the project's overall picture, covering four dimensions:

1. What the project is.
2. Where it is heading.
3. What is on the horizon.
4. What is deliberately deferred.

Rules:

- The agent asks a small number of questions covering the four dimensions, following the memory-model output rules (self-contained messages, one decision per message, no internal coordinates).
- The agent then drafts `docs/vision.md` and **writes it only after the user's explicit confirmation**. The agent never writes vision content the user did not confirm.
- The user may **decline** the exchange for a given feature ("no vision yet — just scope this"). The agent proceeds with the feature. The deferral is not persisted anywhere; it ends with the session. At the next fresh start the agent offers the exchange again — briefly, once.

## The Document

- A single project-level `docs/vision.md`; git history is the revision record. No template file — each project's document is unique; the four dimensions above define its structure.
- The document is a **living, project-level artifact**: it is not a per-feature deliverable and is not frozen at any phase approval.
- The document has four sections mirroring the four dimensions (what it is / where it's heading / horizon / deliberate deferrals).

## Amendment

- The **human** may amend `docs/vision.md` at any time, without a pipeline gate.
- The **agent** may propose amendments — for example, when an interview surfaces a new aspiration — but writes them only after explicit human confirmation.

## Role in Feature Work

- Loaded as interview context at pipeline start.
- **Scope classifier.** During a feature interview, "is this in the vision?" classifies out-of-scope items. In the feature's requirements document, each out-of-scope item is either:
  - **not vision** — a regular out-of-scope entry with its own justification, or
  - **vision — deferred** — a pointer to `docs/vision.md` (a named deferral), instead of re-explaining the aspiration.
- When no vision doc exists (the exchange was declined), items stay regular out-of-scope entries.

## Authority

Writing `docs/vision.md` at pipeline start is a permitted agent action as the confirmed output of the vision exchange (see the authority exception in `00-bootstrap.md`). It is not a phase deliverable.

## What Stays Unchanged

- The per-feature pipeline and its gates.
- The phase list, phase lock, and human-approval gates.
- `sdlc-state.json` and state inference.
