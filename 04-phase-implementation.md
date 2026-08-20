# Implementation Phase Playbook

This phase of the AI-SDLC pipeline is where a technical-design document is turned into real running code.  This phase is purely mechanical, suitable to be performed by an autonomous coding agent.

The source code changes and other artifacts generated at the end of this phase will be handed off to autonomous testing and validation agents, so it is _absolutely critical_ the the implementation is correct and time and effort is not wasted.

It is appropriate to delegate **individual units of work** in this phase of the pipeline to a worker or coder sub-agent if one is available.  It is also appropriate to delegate  **individual verification, validation, or research tasks** in this phase of the pipeline to a worker or researcher sub-agent if one is available.  It is **NOT** appropriate to delegate the _entire_ pipeline to any sub-agent or sub-agents; an architect or planner must be responsible.

## General Guidelines

- **DO**: examine the acceptance criteria in the associated requirements and technical-design document prior to writing code.
- **DO**: check for the existence of a review-report document (`docs/review/<sequential number>-<feature name>.md`) prior to writing code.  The existence of this document indicates that a previous attempt at implementation was partially successful, and any future implementation _must_ address the deficiencies from the review-report document.
- **DO**: examine the current state of the relevant parts of the codebase prior to writing code.
- **DO NOT**: ingest the entire codebase before beginning.  A high-level organizational overview is appropriate; "getting a complete picture" or "examining the full scope of the project" is not.  Use MCP tools (or tools such as `grep`/`rg`/etc.) to search for relevant keywords and concepts to give you a place to start your investigation.
- **DO**: write the tests this phase owns, per the Testing section below — AC-derived tests for every implementation-testable acceptance criterion, and unit tests for pure or idempotent internal units with non-trivial logic. Write each AC-derived test from the acceptance criterion _before_ writing the code it verifies.
- **DO NOT**: write tests that require a running instance of the system (live server, process, browser, external service, or OS signals), or any test beyond the two sources defined in the Testing section.  Integration, end-to-end, component, accessibility, visual-regression, and smoke tests belong to the testing phase.
- **DO**: follow existing project conventions and best practices (if documentation for these is present).
- **DO**: fall back to recognized industry-, community-, or language-standard conventions and idioms in the absence of project conventions or best practices.
- **PRECEDENCE**: where the technical-design or requirements document specifies behavior, format, order, or constraints, it supersedes every fallback convention in this playbook. Fallbacks apply only where those documents are silent.

## Testing

The implementation phase writes exactly two sources of tests:

1. **AC-derived tests.** For every acceptance criterion in the technical-design document that is implementation-testable (boundary below), write the test from the acceptance criterion _before_ writing the code it verifies, then make it pass.
2. **Unit tests for internal units.** For every pure or idempotent internal unit this feature introduces that contains non-trivial logic, write a unit test — even when no acceptance criterion names that unit. Non-trivial logic means branching or edge-case behavior, format or parsing rules, or non-obvious invariants. Units the technical-design document identifies as a test seam always qualify. Do not test trivial accessors or pass-throughs.

**Boundary — implementation-testable.** A test belongs to this phase when it is deterministic, runs under the project's standard test runner, requires no running instance of the system (no live server, process, browser, external service, or OS signals), and can be re-run without affecting other tests. This covers pure functions and idempotent operations exercised through design-defined seams (injected clocks, captured streams, in-process ports). Any test whose proof requires the built system running is deferred to the testing phase and recorded as such in the AC→test mapping (see Output).

**Naming.** AC-derived tests are named after the acceptance criterion they verify (e.g., `AC-TR-001-1: relative date is rendered, absolute date is not`). Unit tests for internal units are named after the unit and the behavior pinned (e.g., `formatRelativeDate: same-day input yields "today"`).

## File and Structure Conventions

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- When creating from scratch: group by domain/feature, separate concerns, keep related code together.
- Mirror the architecture defined in the corresponding technical-design document. Do not invent new layers.
- One concern per file. Split when a file exceeds ~300 lines without structural justification.

## Error Handling

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- Handle errors at the appropriate boundary. Don't swallow, don't propagate raw internals.
- Fail fast on invalid input — reject at the edge, never deep in a call stack.
- Use specific error types, not generic catch-all errors:

  ```typescript
  // BAD
  throw new Error("something went wrong");

  // GOOD
  throw new AuthenticationError("invalid token: expired");
  ```

- Log context, not just the error: include request ID, user ID, timestamp, and relevant state.

## API Design & Payload Validation

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- Consistent response shapes across all endpoints.
- Proper HTTP status codes per HTTP semantics. Never return `200` for errors.
- Versioning strategy: URI path (`/v1/`) or header — match existing convention.
- Pagination for all collection endpoints (cursor or offset-based, per project standard).
- Clear error responses with `code`, `message`, and optional `details`.
- Validate all API payloads at the network boundary, in both directions:
  - Incoming: validate type, structure, range, format before any business logic runs.
  - Outgoing: sanitize and validate responses before they leave the service.
  - Trust nothing from the client. Reject malformed input immediately.

## UI Compliance

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- **All UI work must meet WCAG AA standards.**
- Color contrast minimum 4.5:1 for normal text, 3:1 for large text.
- Keyboard navigation: all interactive elements reachable and operable without a mouse.
- Screen reader compatibility: semantic HTML, `aria-*` attributes where semantic HTML is insufficient.
- Focus management: visible focus indicator on all focusable elements. Logical tab order.
- Accessible labels on all interactive elements (`aria-label`, `aria-labelledby`, or visible text).
- Do not treat accessibility as an afterthought — bake it into each component as you build it.

## Incremental Delivery

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- Build in small, verifiable increments. Each increment must compile and pass its tests before the next.
- Do not generate an entire module in one pass.
- Order of implementation: follow the technical-design document's ordered technical requirements. Where the document defines no order:
  1. Core happy-path logic
  2. Edge cases
  3. Error handling and validation
  4. Integration with existing systems
- Verify each step compiles/runs before proceeding. Stop and confirm if a step fails.

## Dependency Management

in the absence of applicable coding standards or best practices for this project (which if present should always win):

- Add dependencies only when necessary. Prefer standard library solutions.
- Document rationale for every third-party dependency in the code comment or technical-design document.
- Version strategy:
  - when building **Applications**: Pin exact versions (`"express": "4.18.2"`) for reproducibility.
  - when building **Shared libraries**: Use semver ranges (`"^4.18.0"`) for maximum compatibility.
- Run the existing dependency-audit or security-check tool before adding anything new.

## Output

Every feature produces:

- **Source code files** — matching the conventions above.
- **Implementation summary**: `docs/implementation/<number>-<feature>.md`
  - `<number>` aligns with the corresponding product-requirement and technical-design documents. If the technical-design doc is `docs/design/01-auth.md`, the summary is `docs/implementation/01-auth.md`.
  - Must document: tradeoffs made during coding, deviations from the technical-design document or requirements document, open questions.
  - Must contain an **AC→test mapping** section: every acceptance criterion in the technical-design document, each mapped to a named test and its owning phase — "implementation" (test exists in this phase's suite) or "testing" (deferred; reason: requires a running instance of the system). The table must account for 100% of the design document's acceptance criteria.
  - Must contain an **Internal unit tests** section: each internal unit tested under the unit-derived rule, with the unit name and the behavior the test pins.
- **API documentation** — conditional:
  - Required only when the feature exposes or modifies an API of its own.
  - The chosen tooling must not violate the technical-design document's dependency constraints (e.g., no new dependencies of any kind for a zero-dependency project).
  - Select the appropriate tool for your stack (e.g., OpenAPI/Swagger for REST, TSDoc + `typedoc` for TS, `go doc` for Go).
  - When not required, or when dependency constraints prevent generation, record a skip and its reason in the implementation summary (e.g., "API documentation: not required — feature exposes no API of its own").

## 9. EXAMPLES

Examples in this document are illustrative, not prescriptive. Follow the stated rules, not the example content. Do not reproduce example naming, structure, or domain specifics.

Example only — illustrates the principle above. Extract the underlying pattern, do not reproduce these specifics.

**API Payload Validation:**

```typescript
import { z } from "zod";

const CreateUserSchema = z.object({
  email: z.string().email().max(254),
  password: z.string().min(12).max(128),
  role: z.enum(["admin", "editor", "viewer"]).optional().default("viewer"),
});

app.post("/v1/users", async (req, res) => {
  const parsed = CreateUserSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ code: "VALIDATION_ERROR", message: "Invalid payload", details: parsed.error.issues });
    return;
  }
  // parsed.data is typed and validated — proceed
});
```

**Error Handling:**

```typescript
class DomainError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

async function transferFunds(from: UserId, to: UserId, amount: Money) {
  if (amount.lte(Money.zero)) throw new DomainError("INVALID_AMOUNT", "amount must be positive");
  const fromAccount = await accountRepo.findById(from);
  if (!fromAccount) throw new DomainError("ACCOUNT_NOT_FOUND", `account ${from} does not exist`);
  if (fromAccount.balance.lt(amount)) throw new DomainError("INSUFFICIENT_FUNDS", "account balance too low");
  // proceed...
}
```

Rule: Validate at the boundary with explicit schemas and fail fast. Use typed domain errors with machine-readable codes, not generic exceptions.

Rule: All UI must be WCAG AA compliant — contrast, keyboard, screen reader, focus, and labels are mandatory, not optional.

---

## Phase Exit

After producing source code, implementation summary, and API docs (if applicable):

1. Verify code compiles/runs without errors.
2. Run the project's test suite; every test must pass (exit code 0).
3. Verify inline documentation is present.
4. Verify `docs/implementation/<number>-<feature>.md` is written and its AC→test mapping accounts for 100% of the technical-design document's acceptance criteria.
5. Verify API documentation is generated, or a documented skip with reason is recorded in the implementation summary.
6. Run `check_gate(project_path=<project>, from_phase="implementation", to_phase="review")` to verify deliverables.
7. Report completion to the human. List all files produced.
8. proceed **IMMEDIATELY** to the review phase without waiting for human acknowledgement
