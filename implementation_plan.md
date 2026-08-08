# Implementation Plan - Add "Prior Decision Discovery" Guidance

## Goal
Insert instructions into two framework documents telling agents to selectively discover and read relevant ADRs before making architectural decisions.

## Files Modified
- `04-phase-design.md` — new section 1A before existing "1. DECISION FRAMEWORK"
- `00-bootstrap.md` — one bullet added to section 3, "CONTEXT LOADING PROTOCOL"

---

## Step-by-Step

### Step 1: Update `04-phase-design.md`

Insert a new section **before** the existing "1. DECISION FRAMEWORK" heading (line 4). Re-number the existing sections: old 1→2, old 2→3, old 3→4, old 4→5, old 5→6, old 6→7.

**New section to insert at the top:**

```markdown
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

```

### Step 2: Update `00-bootstrap.md`

In section 3 ("CONTEXT LOADING PROTOCOL"), after the existing four bullets (lines 37-40), add a fifth bullet:

```markdown
- **Prior Decisions:** Before making architectural choices, scan `docs/adr/` in the target project. Read only ADRs whose titles relate to your current domain. Skip `superseded`/`deprecated` entries unless revisiting.
```

### Phase 2: Verification

- Confirm `04-phase-design.md` has the new section 1 and all old sections re-numbered
- Confirm `00-bootstrap.md` has the new bullet in section 3
- Confirm no other content was altered