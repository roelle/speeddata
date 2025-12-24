---
type: DRR
winner_id: service-oriented-architecture-with-process-isolation
created: 2025-12-23T09:15:16-08:00
content_hash: a39974a2ab27d181325e9e995c695035
---

# Service-Oriented Architecture for SpeedData v0.2+

## Context
SpeedData requires an architectural approach for v0.2+ that supports evolution from single-user proof-of-concept to multi-user production scenarios. Domain experience from similar tools shows multiple concurrent users viewing real-time data during experiments, plus multiple requesters tagging data sets. Architecture must support independent component improvement without monolith coupling.

## Decision
**Selected Option:** service-oriented-architecture-with-process-isolation

Adopt service-oriented architecture with process isolation: relay, stripchart, and pivot as independent processes communicating via defined protocols.

## Rationale
Domain knowledge indicates multi-user concurrent access patterns will emerge (viewers during experiments, multiple data tag requesters). Service boundaries enable independent component evolution without monolith refactoring risk. Clear interfaces force protocol discipline, reducing cognitive complexity despite coordination overhead. Modern deployment tooling (systemd, containers) makes process management tractable even on constrained hardware. User principle: smaller well-defined components < equivalent LOC in monolith. R_eff: 1.00 (equal to alternatives in formal analysis, but domain context provides unmodeled evidence).

### Characteristic Space (C.16)
Modularity: High. Simplicity: Medium (protocol overhead). Performance: TBD (depends on IPC choice). Maintainability: High (isolated components). Deployment complexity: Medium-High.

## Consequences
Immediate: Define inter-process protocols (UDP multicast exists for data plane, need REST/gRPC for control). Deployment complexity increases (process lifecycle, health checks, log aggregation). Benefits: Each service optimized/replaced independently. Future cloud migration path preserved (processes → containers). Risks: Resource overhead on Pi (mitigate by running subset of services). Protocol overhead could bottleneck hot paths (monitor relay → stripchart throughput).
