---
id: 2025-12-23-audit_report-per-service-yaml-files-with-shared-globals.md
type: audit_report
target: per-service-yaml-files-with-shared-globals
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-23
date: 2025-12-23
content_hash: f230412e213653464a939676e83d6464
---

**R_eff: 1.00** (No dependencies, external validation only)

**Weakest Link Analysis:**
- Single evidence source: External research (CL1 - different context)
- Docker Compose multiple files + extends pattern validated
- Distributed deployment pattern proven in container orchestration
- No internal testing yet (prototype not implemented)

**Risks:**
1. **CONFIG DRIFT - HIGHEST RISK:** If global.yaml not synchronized across machines, relay publishes to multicast X while stripchart subscribes to multicast Y. Services fail silently or emit warnings but don't prevent deployment.
2. **Deployment Discipline Required:** Needs config management tool (Ansible, rsync, git hooks) or manual sync. Risk: High without tooling, Low with proper deployment automation.
3. **Complexity vs Monolithic:** More files to manage, merge logic to understand. Risk: Medium (developer onboarding overhead).

**Bias Check:**
- No "pet idea" bias - Docker Compose pattern widely adopted
- No NIH syndrome - using established split-config pattern
- Matches user scenario: "multi-user" LAN suggests potential multi-machine deployment

**Congruence Analysis:**
- External evidence from Docker Compose (CL1)
- Pattern transferable but requires deployment infrastructure
- Runtime detection possible (services can warn on endpoint mismatch) but prevention requires tooling

**Trade-off vs Monolithic:**
- Better for: Multi-machine deployments where services on different hosts
- Worse for: Single-machine (unnecessary complexity)
- Requires: Config management tooling to prevent drift

**Overall Assessment:** High confidence for multi-machine deployments WITH config management tooling (Ansible/Chef/Puppet). Medium confidence without tooling (manual drift risk).