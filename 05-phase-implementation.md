# Implementation Phase Playbook

## 1. FILE & STRUCTURE CONVENTIONS

- Follow existing project conventions. Inspect `tree`, `Makefile`, `package.json`, or equivalent before creating anything.
- When creating from scratch: group by domain/feature, separate concerns, keep related code together.
- Mirror the architecture defined in the corresponding ADR. Do not invent new layers.
- One concern per file. Split when a file exceeds ~300 lines without structural justification.

## 2. NAMING PATTERNS

- Use consistent, descriptive naming for files, functions, variables, and types.
- Match the language's idiomatic conventions:
  - JS/TS: `camelCase` for variables/functions, `PascalCase` for classes/types.
  - Python: `snake_case` for variables/functions, `PascalCase` for classes.
  - Rust: `snake_case` for everything except `PascalCase` for types/traits.
  - Go: `PascalCase` for exported symbols, `camelCase` for unexported.
- No abbreviations unless universally recognized (`id`, `url`, `http`).
- Files follow language conventions (e.g., `auth_service.ts`, `authService.go`).
- Tests live adjacent to source (`*.test.ts`, `*_test.go`) or in a sibling `tests/` directory matching project structure.

## 3. ERROR HANDLING

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

## 4. API DESIGN & PAYLOAD VALIDATION

- Consistent response shapes across all endpoints.
- Proper HTTP status codes per HTTP semantics. Never return `200` for errors.
- Versioning strategy: URI path (`/v1/`) or header — match existing convention.
- Pagination for all collection endpoints (cursor or offset-based, per project standard).
- Clear error responses with `code`, `message`, and optional `details`.
- **CRITICAL: Validate all API payloads at the network boundary, in both directions.**
  - Incoming: validate type, structure, range, format before any business logic runs.
  - Outgoing: sanitize and validate responses before they leave the service.
  - Trust nothing from the client. Reject malformed input immediately.

## 5. UI COMPLIANCE

- **All UI work must meet WCAG AA standards.**
- Color contrast minimum 4.5:1 for normal text, 3:1 for large text.
- Keyboard navigation: all interactive elements reachable and operable without a mouse.
- Screen reader compatibility: semantic HTML, `aria-*` attributes where semantic HTML is insufficient.
- Focus management: visible focus indicator on all focusable elements. Logical tab order.
- Accessible labels on all interactive elements (`aria-label`, `aria-labelledby`, or visible text).
- Do not treat accessibility as an afterthought — bake it into each component as you build it.

## 6. INCREMENTAL DELIVERY

- Build in small, verifiable increments. Each increment must compile and pass its tests before the next.
- Do not generate an entire module in one pass.
- Order of implementation:
  1. Core happy-path logic
  2. Edge cases
  3. Error handling and validation
  4. Integration with existing systems
- Verify each step compiles/runs before proceeding. Stop and confirm if a step fails.

## 7. DEPENDENCY MANAGEMENT

- Add dependencies only when necessary. Prefer standard library solutions.
- Document rationale for every third-party dependency in the code comment or ADR summary.
- Version strategy:
  - **Applications**: Pin exact versions (`"express": "4.18.2"`) for reproducibility.
  - **Shared libraries**: Use semver ranges (`"^4.18.0"`) for maximum compatibility.
- Run the existing dependency-audit or security-check tool before adding anything new.

## 8. OUTPUT

Every feature produces:

- **Source code files** — matching the conventions above.
- **Implementation summary**: `docs/implementation/<number>-<feature>-summary.md` (relative to the **target project root**)
  - `<number>` aligns with the corresponding ADR. If the ADR is `docs/adr/01-auth.md`, the summary is `docs/implementation/01-auth-summary.md`. **All paths above are relative to the target project root.**
  - Must document: tradeoffs made during coding, deviations from the ADR, open questions.
- **API documentation** — auto-generated, conditional:
  - Required only when APIs are exposed or modified.
  - Select the appropriate tool for your stack (e.g., OpenAPI/Swagger for REST, TSDoc + `typedoc` for TS, `go doc` for Go).
  - Not required for UI-only changes, internal refactoring, or non-API work.

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
