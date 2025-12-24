---
date: 2025-12-24
type: audit
target: standalone-fastapi-service-with-sqlite
r_eff: 0.72
content_hash: manual-audit
---

# Audit Report: Standalone FastAPI Service with SQLite

**R_eff: 0.72** (Medium-High Confidence)

## Weakest Link Analysis

- **Evidence:** External research (CL2, similar context)
- **CL2 Penalty:** 10% reduction (general REST APIs → SpeedData specific)
- **No dependencies:** No WLNK penalty
- **WLNK = Self R × CL2 penalty = 0.80 × 0.90 = 0.72**

## Risk Factors

1. **Deployment Risk: MEDIUM** - Additional service to manage (systemd, monitoring)
2. **Integration Risk: MEDIUM** - IPC failure modes (socket errors, orchestrator unavailable)
3. **Operational Risk: MEDIUM** - Pi footprint (+50-100MB RAM), process count
4. **Complexity Risk: MEDIUM** - Two-phase commit (API DB → IPC → orchestrator)
5. **Performance Risk: LOW** - FastAPI validated 5-10x faster, but not needed for use case

## Bias Check

- ⚠ Possible "shiny object" bias - FastAPI performance attractive but not required
- ✓ Evidence shows benefits don't justify costs for low-traffic registration API
- ✓ Properly evaluated despite appeal of async/performance features

## Evidence Quality

- 2025 benchmarks from reputable sources (Strapi, Medium)
- IPC research from Linux-specific sources (Baeldung)
- Good coverage of performance + operational trade-offs

## Confidence Penalty

R_eff reduced by CL2 penalty because:
- Benchmarks for high-traffic APIs (15k req/s) not applicable to <1 req/s registration
- IPC research general-purpose, not SpeedData-specific
- No prototype validation in target environment

## Trade-off Analysis

- Superior performance (5-10x) wasted on non-hot-path
- Clean architecture offset by operational overhead
- Benefits accrue in multi-team/microservices context (not applicable here)
