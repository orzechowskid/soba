# Requirements Phase Playbook

This phase of the AI-SDLC pipeline is where a user's vague requests are transformed into a full-blown product requirements document containing numbered functional specifications. 

The shape of this phase is a structured interview that covers every confirmed in-scope item — and nothing beyond it. It is defined by the Phase Protocol below.

The requirements document generated at the end of this phase will be handed off to an autonomous technical architect agent, so it is _absolutely critical_ that it is complete and well-written.

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

**Step 1 — Goal.**
- If project context is unclear, ask at most 3 questions about the project as a whole.
- Restate the user's goal in one sentence and ask: "Is that right?"
- Derive the feature name: a short kebab-case identifier taken from the confirmed
  goal (e.g. goal "Add rate limiting to the public API" → `rate-limiting-public-api`).
  Never ask the user to choose a code name or reference name.
- Wait for explicit confirmation. Do not proceed until the user confirms.

**Step 2 — Scope.**
- Propose: (a) in-scope items, (b) out-of-scope items, (c) the list of interview
  areas you will cover.
- Area count scales with feature size: 2–3 areas for a narrow change, 5–8 for a
  new service.
- Ask the user to confirm or edit the scope and area list. Wait for confirmation.

**Step 3 — Drill areas.**
- Work one area at a time, in list order. When you start an area, lead with
  one plain line stating, in content terms, what is being decided. Do not print
  area indices or the agent's internal area names as a label.
- Per turn: at most 5 questions, all within the current area.
- When the user's answers are in, summarize that area's requirements in 3–6
  bullets and ask: "Is that right?" Move to the next area only after confirmation.
- Summary length and question count scale with how much is genuinely open: an
  area with no open questions is summarized in one line and confirmed as such.
  The confirmation wait is unchanged.
- Every question must pass the Question Rules below.
- If the user skips questions: on your next turn name the skipped ones and ask
  "Do you want to answer these, or should I record them as Open Questions?"
  If skipped again, record them as Open Questions. Never treat a skipped
  question as settled, and never end the interview because some questions
  went unanswered.

**Step 4 — Close the interview.**
- Present: the confirmed scope, one-line summary of each area, the Open
  Questions list, and the constraints and goals collected.
- Ask: "Anything else before I write the requirements document?"
- Do not write the document until the user explicitly confirms the interview is
  complete. You may only *ask* "Shall I draft?"; you may not announce that you
  will draft.

**Step 5 — Write the document.**
- You may only enter this step after the user explicitly confirmed in Step 4 that the interview is complete.
- Run the Pre-Output Checklist. If any answer is "no", return to the user with
  more questions (back to Step 3).
- Write the document per Output Structure, then follow Phase Exit.

## Question Rules

A question is allowed only if its answer changes one of: what the user
experiences, what the product does, or what the product is already obligated
to do.

Allowed:
- User needs, the problem being solved, what success looks like
- In-scope / out-of-scope items
- User-visible behavior, content, and flows
- Existing obligations: SLAs, contracts, regulations, customer promises —
  record these verbatim with their source
- Aspirations without numbers ("the dashboard feels slow") — record as goals

Forbidden:
- Implementation technology, architecture, data models, endpoints, APIs
- Inventing numbers. Do not ask the user for latency, throughput, or
  concurrency targets, and do not propose your own. If an aspiration has no
  existing number, record it as a goal marked "to be quantified in the
  design phase."
- Never ask the user to choose a code name or reference name for the feature

Example of a forbidden question and its correct form:
- Forbidden: "How many endpoints should be rate-limited?"
- Correct: "Does the product need to limit or prevent abusive usage? Are
  there existing limits we must honor?"

## Interview Checklist

- [ ] Check for `docs/vision.md`. If present, read it as project context and use it to classify out-of-scope items as "not vision" or "vision — deferred" (pointing at `docs/vision.md`); see `13-vision-step.md`.
- [ ] Check if `docs/enhancement/` contains a context brief for this feature. If so, read it for system understanding and change context before interviewing the user.
- [ ] Identify the user's core goal
- [ ] Ensure no questions are in violation of phase lock directives forbidding discussion of concerns belonging in other phases of the AI-SDLC pipeline
- [ ] Ensure no assumptions were made or gaps filled in on behalf of the user
- [ ] Ask follow-up questions to user answers
- [ ] Ask the user - and ask yourself - about what is in-scope and out-of-scope
- [ ] Ensure the requirements document is not produced in the same turn that the interview finishes.  Always pause and ask yourself "is there anything else I haven't asked the user about?"

## Pre-Output Checklist (Mandatory)

Before writing the requirements document, answer these questions honestly.
If the answer to ANY is "no," you MUST return to the user with more questions.

1. Does every functional requirement have at least one objective and testable acceptance criterion?
2. Are there any requirements I wrote that I inferred rather than the user explicitly confirming?
3. Did the user confirm the out-of-scope list, or did I assemble it myself?
4. Are there any "reasonable default" decisions I made that the user didn't explicitly approve?
5. Could another agent read this document and implement a technical-design document from it without ever asking the user a single additional question?
6. Did I ask any forbidden (technical) question, or invent any number? If so, remove it from the document and note it for the design phase.
7. Did the user explicitly confirm the interview was complete before I wrote this document?

## Output

Adhere to the following guidelines to ensure a clear, concise, and informative requirements document is created:

- Write numbered functional requirements (FR-001, FR-002, …).
- Include a section for in-scope requirements
- Include a section for out-of-scope items
- Include a Constraints & Goals section: (a) external obligations — SLAs, contracts, regulations, customer promises — recorded verbatim with their source; (b) goals without numbers, each marked "to be quantified in the design phase."

### Acceptance criteria

Write acceptance criteria for each numbered functional requirement. Criteria must be binary (pass/fail).

- Use imperative format.
- No qualitative language ("should be fast," "user-friendly," "robust").
- Every criterion must be testable as-is without guesswork or assumptions.
- Acceptance criteria describe user-observable behavior, not implementation.
- Quantitative performance or capacity targets appear in this document **only when externally mandated** (SLA, contract, regulation). Otherwise record the goal in Constraints & Goals, marked "to be quantified in the design phase."

**Format:**
```
AC-<req>-<n>: <imperative, testable condition>
```

**Bad:** "The system should respond quickly."
**Good:** "AC-FR-003-1: When the user clicks Export, a file download begins and the file contains exactly the rows currently displayed."
**Good (externally mandated target):** "AC-FR-001-1: The dashboard must load within 2 seconds, per the customer SLA."

## Output Structure (`docs/requirements/<sequential number>-<feature name>.md`)

The deliverable must contain, in this order:

1. **Numbered Functional Requirements** — FR-001, FR-002, …
2. **Acceptance Criteria** — per requirement, binary and testable.
3. **Constraints & Goals** — external obligations (regulatory, contractual, SLA) recorded verbatim with source; goals without numbers, each marked "to be quantified in the design phase."
4. **Assumptions** — documented with impact level (high / medium / low).
5. **Open Questions** — specific clarification asks with proposed options.
6. **Out-of-Scope Items** — explicit list with justification.
7. **Decisions Log** — compact record of what was decided during the interview, by whom, when, and which overrides or caveats were applied. This is the review interface for future readers, including the design-phase agent.
8. **Self-Review** — the agent's recorded self-review of the finished document for deficiencies (completeness, ambiguity, unconfirmed inferences), performed per the Pre-Output Checklist.

## Examples

> Examples in this document are illustrative, not prescriptive. Follow the stated rules, not the example content. Do not reproduce example naming, structure, or domain specifics.
>
> Example only — illustrates the principle above. Extract the underlying pattern, do not reproduce these specifics.

### Rule: Every requirement must be specific, testable, and free of qualitative language.

**Good requirement (example only):**
> FR-001: The system shall allow authenticated users to create, read, update, and delete resources within a namespace. Each operation must give the user a visible confirmation of success or failure.

**Vague requirement (example only):**
> FR-001: The system should handle resources well and be fast for users.

### Restate rule: Specific, testable, no qualitative language. Always.

## Phase Exit

After producing `docs/requirements/<sequential number>-<feature name>.md`:

1. Verify all sections are present: Functional Requirements (FR-*), Acceptance Criteria (AC-*), Constraints & Goals, Assumptions, Open Questions, Out-of-Scope Items, Decisions Log.
2. Run `check_gate(project_path=<project>, from_phase="requirements", to_phase="design")` to verify deliverables.
3. Report completion to the human. List all deliverables produced.
4. **STOP.** Await human approval before proceeding to design phase.
5. Do NOT begin design work. Do NOT write technical-design documents. Do NOT write code. Do NOT produce deliverables for future phases.
