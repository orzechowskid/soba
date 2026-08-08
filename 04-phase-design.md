# Phase 4: Design

## 1. PRIOR DECISION DISCOVERY

**Purpose:** Avoid reinventing or contradicting architectural decisions that were already made.

**Process:**
1. **Scan** — List files in `docs/adr/`. Read only the title line (`# <title>`) and `Status:` field of each file. Do not read full content yet.
2. **Filter** — Read only ADRs whose title relates to your current domain (e.g., reading auth-related ADRs when designing authentication). Skip any ADR marked `superseded` or `deprecated` unless you are intentionally revisiting that decision.
3. **Cross-check** — Before finalizing your decision, verify it does not contradict any active ADR you read. If it does, note the conflict explicitly and either reconcile or write a new ADR that supersedes the prior one.
4. **Document** — In your new ADR, reference any prior ADRs that informed your decision (by filename). This creates a traceable decision graph.

**Rule:** You are not required to read every ADR. You are required to read every ADR that *could affect your current decision*. When in doubt, scan the title.

---

## 2. DECISION FRAMEWORK

**Purpose:** Systematize architectural choices. Eliminate guesswork.

**Process:**
1. List viable options
2. Evaluate against criteria:
   - Complexity
   - Maintainability
   - Performance
   - Security
3. Select option with highest weighted score
4. Document rationale in ADR

**Rules:**
- No "gut feel" decisions
- Every choice requires documented reasoning
- Revisit decisions when criteria shift

---

## 3. ADR STRUCTURE & STORAGE

**Location:** `docs/adr/` (relative to the **target project root**)
**Naming:** `001-<title>.md`, `002-<title>.md` (sequential)
**Format:** Nygard ADR

**Required Fields:**
- Title
- Context (problem statement)
- Options Considered
- Decision (chosen option)
- Consequences (positive and negative)
- Status (proposed | accepted | deprecated | superseded)

**Rules:**
- One ADR per decision
- Multiple decisions → multiple ADRs
- ADRs are immutable once accepted; supersede with new ADR

---

## 4. SIMPLICITY DEFAULT

**Principle:** Choose simplest design satisfying requirements.

**When to increase complexity:**
- Explicit justification required
- Document tradeoff in ADR
- Complexity must demonstrate measurable benefit

**Selection heuristic:**
When options meet requirements:
1. Fewer moving parts
2. Lower coupling
3. Easier onboarding

---

## 5. TRADEOFF ANALYSIS

**Dimensions:** cost | speed | reliability | maintainability | security

**Process:**
1. Identify relevant dimensions
2. Score each option per dimension
3. Document what is sacrificed
4. State tradeoff explicitly in ADR

**Rule:** No decision is free. Record what you give up.

---

## 6. TECH STACK SELECTION

**Principle:** Prefer well-supported, widely adopted tools.

**Justification required for:**
- Non-standard technologies
- Niche libraries
- New dependencies

**Rule:** Document rationale when deviating from convention.

---

## 7. OUTPUT

**Deliverables:**
- `docs/adr/<number>-<title>.md` (relative to the **target project root**) per significant decision
- Implementation summary referencing ADRs

**Checklist:**
- [ ] `docs/adr/` directory exists in the **target project root**
- [ ] ADRs follow Nygard format
- [ ] All decisions documented
- [ ] Tradeoffs stated
- [ ] Simplicity justified
- [ ] Tech stack choices explained

---

## 8. PHASE EXIT

After producing ADR(s) in `docs/adr/`:

1. Verify all significant architectural decisions are documented with tradeoffs.
2. Verify each ADR follows Nygard format: Title, Context, Options Considered, Decision, Consequences, Status.
3. Run `check_gate(project_path=<project>, from_phase="design", to_phase="implementation")` to verify deliverables.
4. Report completion to the human. List all ADRs produced.
5. **STOP.** Await human approval before proceeding to implementation phase.
6. Do NOT write code. Do NOT create source files. Do NOT produce deliverables for future phases.
