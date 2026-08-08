# Requirements Phase Playbook

## 1. DECOMPOSITION

Break vague requests into numbered functional specifications.

- Extract user goals from the request.
- Write numbered functional requirements (FR-001, FR-002, …).
- Surface constraints — fold non-functional requirements (performance, scalability, availability, security, regulatory) into the constraints section. Do not create a separate NFR section.
- List edge cases explicitly.

**Decomposition pattern:**
1. Identify the user's core goal.
2. Enumerate functional requirements that achieve it.
3. Surface technical, regulatory, performance, and security constraints.
4. List edge cases.

---

## 2. ACCEPTANCE CRITERIA

Write acceptance criteria per requirement. Criteria must be binary (pass/fail).

- Use imperative format.
- No qualitative language ("should be fast," "user-friendly," "robust").
- Every criterion must be testable as-is.

**Format:**
```
AC-<req>-<n>: <imperative, testable condition>
```

**Bad:** "The system should respond quickly."
**Good:** "AC-FR-001-1: The API must respond within 200ms at the 99th percentile under 1,000 concurrent requests."

---

## 3. CLARIFICATION & ASSUMPTION PROTOCOL

- Ask the user about ambiguities. Ask specifically ("Should this support multi-tenant isolation?"), not generically ("Can you clarify?").
- Limit clarification asks to high-impact unknowns. Do not stall on trivial details.
- For low-impact unknowns where the user does not know or does not care:
  - Make a documented assumption.
  - Flag it in the deliverable with an impact level (high / medium / low).
  - Proceed immediately.

---

## 4. EDGE CASE IDENTIFICATION

Surface edge cases using these patterns:

- **Boundary values:** minimum, maximum, overflow, off-by-one.
- **Empty / zero states:** empty collections, null inputs, zero-value defaults.
- **Error paths:** network failure, permission denied, partial success, retry exhaustion.
- **Concurrent access:** race conditions, deadlocks, idempotency under parallel calls.
- **Data migration:** schema changes, backward compatibility, data loss risk.
- **Backward compatibility:** API versioning, deprecated field handling, schema evolution.

Document each edge case with the requirement it affects and the proposed handling.

---

## 5. SCOPE CREEP DETECTION

- Flag requirements that belong in a different phase, different project, or represent feature bloat.
- Classify each requirement:
  - **Required** — necessary for this feature to function.
  - **Nice to have** — desirable but not blocking.
  - **Out of scope** — belongs elsewhere; log explicitly.
- Log all out-of-scope items in the deliverable with a one-line justification.

---

## 6. OUTPUT STRUCTURE (`requirements.md`)

The deliverable must contain, in this order:

1. **Numbered Functional Requirements** — FR-001, FR-002, …
2. **Acceptance Criteria** — per requirement, binary and testable.
3. **Constraints** — technical, regulatory, performance, security, availability.
4. **Assumptions** — documented with impact level (high / medium / low).
5. **Open Questions** — specific clarification asks with proposed options.
6. **Out-of-Scope Items** — explicit list with justification.

---

## 7. EXAMPLES

> Examples in this document are illustrative, not prescriptive. Follow the stated rules, not the example content. Do not reproduce example naming, structure, or domain specifics.
>
> Example only — illustrates the principle above. Extract the underlying pattern, do not reproduce these specifics.

### Rule: Every requirement must be specific, testable, and free of qualitative language.

**Good requirement (example only):**
> FR-001: The system shall allow authenticated users to create, read, update, and delete resources within a namespace. Each operation must complete within 200ms at the 99th percentile under 1,000 concurrent requests.

**Vague requirement (example only):**
> FR-001: The system should handle resources well and be fast for users.

### Restate rule: Specific, testable, no qualitative language. Always.
