# Deployment Phase Playbook

## 1. DEPLOYMENT ASSESSMENT

Before writing deployment artifacts, assess:

- **Target environment** — cloud provider, container orchestrator, bare metal, serverless
- **Existing infrastructure** — what already exists, what needs to be created
- **Dependencies** — databases, message queues, external APIs, CDN
- **Data migration** — schema changes, data transformations, backward compatibility

## 2. DEPLOYMENT STRATEGY

Select the appropriate strategy based on risk and environment:

| Strategy | Use When | Risk |
|---|---|---|
| Big bang | Small changes, low-risk, single environment | High — all-or-nothing |
| Rolling | Stateless services, canary-safe | Medium — gradual rollout |
| Blue-green | Full environment duplication available | Low — instant rollback |
| Canary | High-traffic, need gradual validation | Low — limited blast radius |

Document the chosen strategy and justification in the deployment plan.

## 3. CI/CD CHANGES

- Define pipeline stages: build → test → stage → deploy → verify
- Include automated health checks after deployment
- Include automated rollback triggers (health check failure, error rate spike)
- Do not store secrets in CI/CD configs. Reference secret management systems.

## 4. ROLLBACK PROCEDURES

Every deployment MUST include a rollback plan:

- **Trigger conditions** — what metrics/events trigger rollback
- **Rollback steps** — ordered, specific commands or actions
- **Data rollback** — how to revert data changes (if applicable)
- **Communication** — who is notified, when
- **Verification** — how to confirm rollback succeeded

## 5. OUTPUT

**Deliverables:**
- `docs/deploy/<number>-<feature>.md` — deployment strategy, environment config, rollout plan, rollback procedures
- CI/CD pipeline files (e.g., `.github/workflows/`, `Jenkinsfile`, etc.)

## 6. PHASE EXIT

After producing deployment artifacts:

1. Verify deployment config is complete.
2. Verify rollback procedure is documented.
3. Verify CI/CD pipeline files are present.
4. Run `check_gate(project_path=<project>, from_phase="deployment", to_phase="monitoring")` to verify deliverables.
5. Report completion to the human.
6. **STOP.** Await human approval before proceeding to monitoring phase.
