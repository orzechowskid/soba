# Monitoring Phase Playbook

## 1. ASSESS MONITORING NEEDS

Examine the feature and identify what needs to be monitored. Evaluate each category below; if a category does not apply, state that explicitly. Do not include boilerplate items that are irrelevant.

- **New/modified APIs** — latency, error rates, throughput
- **Database interactions** — query performance, connection pool health
- **Async/background jobs** — job success rate, queue depth, retry rates
- **External service calls** — upstream latency, failure rates, circuit breaker status
- **UI changes** — frontend error rates, load times

## 2. PROPOSE METRICS

Based on the assessment, select relevant metrics only. For each metric document:

- **What** to measure
- **Why** it matters for this feature

## 3. PROPOSE ALERTING THRESHOLDS

Define alerting thresholds per metric. Distinguish:

- **Warning** — investigate during business hours
- **Critical** — page on-call, act immediately

For each threshold document the value and rationale.

## 4. LOG STRUCTURE

All logs must be structured (JSON or equivalent). Required fields:

- `timestamp`
- `level`
- `service`
- `request_id` or `correlation_id`
- Relevant contextual fields for the operation

Never log sensitive data: secrets, tokens, or PII.

## 5. PERFORMANCE BASELINE

After deployment, capture baseline metrics. Document expected ranges for key metrics. Baselines enable future regression detection.

## 6. USER APPROVAL

Present the monitoring plan (metrics, alerts, log config, baselines) to the user. **STOP. Wait for explicit approval before finalizing.**

## 7. OUTPUT

Write the approved plan to:

```
docs/monitoring/<number>-<feature>.md (relative to the **target project root**)
```

The filename must align with the technical-design document and implementation numbering scheme.

---

## 8. PHASE EXIT

After producing `monitoring-spec.md`:

1. Verify all metrics, alerts, and baselines are documented.
2. Run `check_gate(project_path=<project>, from_phase="deployment", to_phase="monitoring")` to verify deliverables.
3. Report completion to the human.
4. **STOP.** SDLC pipeline is complete for this feature.
