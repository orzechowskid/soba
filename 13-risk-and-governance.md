# Risk and Governance

## 1. Risk Taxonomy

**Security**

- Vulnerabilities: weaknesses exploitable by adversaries.
- Attack surfaces: any point where an unauthorized actor can interfere with the system.

**Reliability**

- Outages: loss of availability affecting users or downstream systems.
- Data loss: permanent or transient loss of data integrity or durability.

**Data**

- Privacy: unlawful or unauthorized processing of personal data.
- PII handling: collection, storage, transmission, or deletion of personally identifiable information.
- Retention: holding data beyond its lawful or necessary lifespan.

**Compliance**

- Regulatory: violation of applicable laws, standards, or directives.
- Licensing: non-compliance with software license obligations.
- Third-party: obligations imposed by vendors, contractors, or integrated services.

---

## 2. Severity Classification

**Critical**

- Immediate threat to users, systems, or legal standing.
- Must halt work until the risk is neutralized or explicitly accepted by the human user.

**High**

- Significant risk of material harm if unaddressed.
- Must mitigate before release to production.

**Medium**

- Manageable risk with controlled exposure.
- Must mitigate within the current sprint or iteration.

**Low**

- Acceptable risk within defined tolerances.
- Track and monitor; review at the next scheduled gate.

---

## 3. Mitigation Patterns

**Fail Closed**

- Deny by default. Explicitly grant access only when justified and verified.

**Defense in Depth**

- Layer multiple independent controls. No single point of failure in any security layer.

**Least Privilege Access**

- Grant the minimum permissions necessary for the task. Scope by identity, resource, and duration.

**Input Validation at All Boundaries**

- Validate at every external interface: APIs, queues, file systems, environment variables.
- Reject malformed input immediately; never propagate raw internals.

**Encrypt Sensitive Data at Rest and in Transit**

- Use approved algorithms and key management practices.
- Never implement custom cryptography.

**Maintain Audit Trails for Sensitive Operations**

- Log who acted, what was accessed or changed, when, and from where.
- Protect audit logs from tampering and unauthorized access.

---

## 4. Third-Party Dependency Risk

- Evaluate before adding: maintenance activity, license compatibility, known vulnerabilities, supply chain exposure.
- Document the rationale for inclusion in the ADR or implementation summary.
- Pin versions per `05-phase-implementation.md` rules.
- Re-audit on every major version bump and at each quarterly review.

---

## 5. Data Handling

- Classify data sensitivity before any processing begins.
- Encrypt sensitive data at rest and in transit.
- Never log secrets, tokens, API keys, passwords, or PII.
- Define retention periods and automated deletion policies for every data class.
- Honor data subject requests (access, correction, erasure) within defined SLAs.

---

## 6. Accountability

- Every decision, especially risk-accepting ones, must be documented.
- Architectural risks: record in an ADR stored in `docs/adr/` (in the **target project root**).
- Implementation risks: record in the review or implementation report.
- The human user owns final accountability for all risk acceptance. Agents may flag and recommend but cannot accept risk on their own authority.

---

## 7. Output

Create `docs/risks/<number>-<feature>.md` (relative to the **target project root**) aligned with ADR and implementation numbering.

Required fields:

- **Risk Classification** — one or more taxonomy categories from Section 1.
- **Severity Level** — Critical, High, Medium, or Low per Section 2.
- **Mitigation Strategy** — which pattern(s) from Section 3 apply.
- **Acceptance Status** — mitigated, accepted with justification, or deferred with date.
- **Accountability Assignment** — who owns the risk decision and mitigation.

---

## 8. RISK ACCEPTANCE LOGGING

When an agent flags a risk and the human user chooses to proceed despite it, the agent MUST record the acceptance.

### Location
`docs/risks/<number>-<feature>-acceptances.md` (relative to the target project root), aligned with ADR and implementation numbering.

### Required Fields
- **Risk Description** — what the risk is
- **Severity** — Critical, High, Medium, or Low per §2
- **Agent Recommendation** — what the agent recommended
- **Human Decision** — approve, approve with caveats, or proceed despite risk
- **Justification** — why the human decided to proceed
- **Timestamp** — ISO 8601

### Rules
- Records are immutable once created. Do not edit or delete.
- Use the `record_approval` MCP tool to append acceptance records.
- If the human ignores a Critical risk, the agent MUST re-flag it at the next phase transition.
