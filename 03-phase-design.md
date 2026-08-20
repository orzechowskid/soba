# Design Phase Playbook

This phase of the AI-SDLC pipeline is where an existing product-requirements document is turned into a technical-design document containing detailed technical specifications.  The shape of this phase is an **extremely** thorough, in-depth, wide-ranging, and exhaustive interview of the user to ensure technical requirements are created which contain absolutely no ambiguity.  Repeatedly ask for more information on _how_ each product requirement is to be implemented, in order to achieve the best possible technical design.

The technical-design document generated at the end of this phase will be handed off to autonomous coding agents, so it is _absolutely critical_ that it is complete and well-written.

It is appropriate to delegate this phase of the pipeline to an architect or planner sub-agent if one is available.

## Phase Protocol (Mandatory)

This phase proceeds in five sequential steps.
Do not skip, combine, or reorder steps. Do not proceed past a step until its
waiting condition is met.

The step and area structure is agent-internal state, not something the human
tracks. Apply the Memory Model from the bootstrap document (Output
Expectations) to every message in this interview: no step or area coordinates
in human-facing text, references restated rather than labeled, and every
message self-contained.

Two interview disciplines apply on top of the Memory Model:
- One decision per message: if deleting a sentence would not change a decision
  the human makes, delete it.
- Decoration reserved for decisions: bold and headers only for questions,
  decisions, and deliverables. An orientation line, if present, is plain text,
  one line, and appears only when something actually changes.

**Step 1 — Preparation and quantification.**
- Perform the Interview Prep for this feature (see below).
- Quantify every goal in the requirements document marked "to be quantified
  in the design phase": propose a concrete, testable target for each, with a
  one-line reason for the proposed value.
- Present the proposed targets and ask: "Do you accept these targets, or do
  you want to change any of them?"
- If the requirements document defers no goals, state that in one line.
- Wait for explicit confirmation of every proposed target. Do not proceed
  until the user confirms.

**Step 2 — Scope and areas.**
- Propose: (a) the areas of technical design the interview will cover,
  (b) existing systems or subsystems this feature does not modify, which are
  out of interview scope.
- Area count scales with feature size: 2–3 areas for a narrow change, 5–8
  for a new service.
- Ask the user to confirm or edit the area list. Wait for confirmation.

**Step 3 — Drill areas.**
- Work one area at a time, in list order. When you start an area, lead with
  one plain line stating, in content terms, what is being decided. Do not
  print area indices or the agent's internal area names as a label.
- Per turn: at most 5 questions, all within the current area.
- When the user's answers are in, summarize that area's decisions in 3–6
  bullets and ask: "Is that right?" Move to the next area only after
  confirmation.
- Summary length and question count scale with how much is genuinely open: an
  area with no open questions is summarized in one line and confirmed as such.
  The confirmation wait is unchanged.
- Every question must pass the Question Rules below. The Broad Interview
  Guide governs how options and tradeoffs are presented during this step.
- If the user skips questions: on your next turn name the skipped ones and ask
  "Do you want to answer these, or should I record them as Open Questions?"
  If skipped again, record them as Open Questions. Never treat a skipped
  question as settled, and never end the interview because some questions
  went unanswered.

**Step 4 — Close the interview.**
- Present: the confirmed scope, one-line summary of each area, the Open
  Questions list, and the significant decisions with their tradeoffs.
- Ask: "Anything else before I write the technical-design document?"
- Do not write the document until the user explicitly confirms the interview
  is complete. You may only *ask* "Shall I draft?"; you may not announce that
  you will draft.

**Step 5 — Write the document.**
- You may only enter this step after the user explicitly confirmed in Step 4
  that the interview is complete.
- Run the Pre-Output self-review. If any ambiguity or gap remains, return to
  the user with more questions (back to Step 3).
- Write the document per Output Structure, then follow Phase Exit.

## Question Rules

A question is allowed only if its answer changes one of: what the code must
do, how it must be built, or how it must be verified.

Allowed:
- Architecture and component design: services, modules, boundaries, processes
- Technology stack and dependencies, each with a reason for the choice
- Data models, storage, and their lifecycles
- APIs, endpoints, request/response shapes, and protocols
- Configuration surface: what is configured, formats, and defaults
- Failure behavior and edge cases: timeouts, retries, limits, error paths
- Concrete numbers that govern behavior (ports, timeouts, sizes, rates)

Forbidden:
- Re-litigating a functional requirement or a scope decision confirmed in the
  requirements phase. If a confirmed requirement turns out to be wrong, stop
  and send the feature back to requirements per the backtracking rules in
  `01-lifecycle-overview.md`
- Deciding out-of-scope items

Where a decision requires a number, never ask an open qualitative question
("how fast should it be?"). Propose a concrete value with a one-line reason
and ask the user to confirm or adjust it.

Example of a forbidden question and its correct form:
- Forbidden: "How fast should the hot path be?"
- Correct: "Requests on the hot path must complete within 100 ms — does that
  target match your expectation?"

## Interview Prep

Performed during Step 1 (Preparation and quantification) of the Phase Protocol.

- **DO**: Check if `docs/enhancement/` contains a context brief for this feature. If so, read it for architectural context and change scope before proceeding.
- **DO**: analyze the requirements document for the current feature which was generated in the previous step of the AI-SDLC pipeline.
- **DO**: Quantify every goal in the requirements document marked "to be quantified in the design phase" — turn each into a testable target and confirm it with the user.
- **DO**: analyse the current state of the codebase to discover tools, patterns, and processes already in use.  Prefer the re-use of these things over inventing or importing something new.
- **DO**: analyse existing technical-design documents which may apply to the current problem domain, to avoid contradicting architectural decisions which were already made.
- **DO NOT**: bulk-read every existing technical-design document. Search the `docs/design/` directory via MCP tool (or `grep`/`rg`/etc) for documents which may contain relevant keywords or other information, and limit yourself to reading only those technical-design docs.
- **DO NOT**: generate a set of initial questions to ask the user then jump straight to writing a technical-design document.
- **DO**: ask additional follow-up questions based on the answers to your initial questions.  This interview process is deliberately designed to be long and detailed.
- **DO NOT**: make assumptions, fill in any gaps yourself, or tolerate **any** ambiguity in requirements.  When ambiguity or uncertainty are detected, **STOP IMMEDIATELY** and ask additional questions to the user.

## Broad Interview Guide

Governs how questions and options are presented during Step 3 (Drill areas) of the Phase Protocol.

- **DO**: Suggest initial approaches and options and make recommendations, but confirm all of them with the user.
- **DO NOT**: make "gut feel" decisions.  Decisions must be come with reasons.
- **DO**: Enumerate tradeoffs of each proposed approach or available option (e.g. performance, security, cost).
- **DO**: Identify and ask about edge cases.  This is the phase of the pipeline where system behavior must be made crystal clear.
- **DO**: Push back (respectfully!) when users suggest options or approaches which may contradict existing system design or architecture.  Users are allowed to override decisions made in previous technical-design documentss, but these overrides **must** be recorded.
- **DO NOT**: make assumptions, fill in any gaps yourself, or tolerate **any** ambiguity in technical design.  When ambiguity or uncertainty are detected, **STOP IMMEDIATELY** and ask additional questions to the user.
- **DO**: Recognize that some features are going to be very narrow in scope and small in blast radius.  If the user **explicitly** indicates this then it is acceptable to trim down the technical-design document.
- **DO NOT**: unilaterally decide that a feature is small enough to not warrant a fully fleshed-out technical-design document. That is done solely at the user's discretion.
- **DO**: wait for the user's approval before drafting the technical-design document. Explicit, not implicit, acceptance is required.

## Pre-Output

Before deciding that enough information has been recorded to create the technical-design document, perform a critical self-review to ensure enough information really has been recorded.  If ambiguities or gaps are detected, and the technical-design document can not be executed with confidence that the product requirements will be met, then continue the user-interview process.

## Output

Adhere to the following guidelines to ensure a clear, concise, and informative technical design:

- Write numbered technical requirements (TR-001, TR-002, etc)
- Technical requirements should be logically sequenced such that a coding agent can implement them in order with a minimum of confusion or errors.
- Each technical requirement should come with its own acceptance criteria (AC-TR-001-1, AC-TR-001-2, AC-TR-002-1, etc) describing the assertions required for a unit, integration, visual, end-to-end, or manual test to validate the technical requirement.
- Do not give examples or suggestions ("a flag controlling the location of the config file named '--config-file' or similar").  Give specifications.  Be clear, specific, and deliberate ("a flag named '--config-file' which when set must contain an absolute path to the config file").

## Output Structure

The deliverable must contain, in this order:

1. **Numbered Technical Requirements**: TR-001, TR-002, etc.
2. **Acceptance Criteria**: per requirement, binary and testable.  Every AC must be covered by a named test in the implementation or testing phase — ownership recorded in the implementation summary's AC→test mapping and closed in the test report's traceability table; the cumulative test suite is the definition of done.
3. **Constraints**: regulatory, performance, security, availability.
4. **Assumptions**: documented with impact level (high / medium / low).
5. **References**: references to previous technical-design documents which contain more context.
6. **Self-Review**: the agent's recorded self-review of the finished document for deficiencies, performed per the Pre-Output step.

The deliverable **MUST NOT** contain any other sections.

## Phase Exit

After producing `docs/design/<sequential number>-<feature name>.md`:

1. Verify all significant architectural decisions are documented with tradeoffs.
2. Run `check_gate(project_path=<project>, from_phase="design", to_phase="implementation")` to verify deliverables.
3. Report completion to the human. List all deliverables produced.
4. **STOP.** Await human approval before proceeding to implementation phase.
5. Do NOT write code. Do NOT create source files. Do NOT produce deliverables for future phases.
