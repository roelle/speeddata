---
date: 2025-12-23
id: 2025-12-23-audit_report-stripchart-server-decimation-with-configurable-pipeline.md
type: audit_report
target: stripchart-server-decimation-with-configurable-pipeline
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-23
content_hash: cbf350bedca3aa5bfd81e2d74435c127
---

**R_eff: 1.00** (Internal testing, CL3 - same context)

**Weakest Link Analysis:**
- Evidence: Internal Node.js benchmark (6.0% CPU overhead at heavy load)
- Congruence Level: CL3 (same codebase, same context)
- No dependencies, no WLNK penalty applied

**Network Bottleneck Risk (CRITICAL NEW FINDING):**

**Single-Machine Deployment:**
- NIC load: 40.8 MB/sec (40 MB/sec in + 0.8 MB/sec out)
- Single multicast stream (full-rate relay → server)
- At 10 channels: ~320 Mbps (3.2% of 1 Gbps NIC) - LOW RISK
- At 100 channels: ~3.2 Gbps - EXCEEDS 1 Gbps NIC CAPACITY - MODERATE RISK
- **Saves 40 MB/sec vs relay-side decimation** (no decimated multicast stream)

**Multi-Machine Deployment:**
- Relay NIC: 80 MB/sec (40 in + 40 out)
- Server NIC: 40.8 MB/sec (40 in + 0.8 out)
- Relay still bottleneck, but 0.8 MB/sec better than relay-side

**IPC Mitigation:**
- If relay/server co-located with Unix domain sockets: 40.8 MB/sec total NIC load (optimal)
- Eliminates 40 MB/sec multicast overhead entirely

**Rust Migration Impact:**
- Relay becomes MUCH faster at I/O (compiled language)
- Server decimation remains in Node.js (no change)
- Network bandwidth remains bottleneck for relay
- **Key insight:** Server-side approach means relay CPU optimization (Rust) doesn't compete with decimation CPU cost

**Architectural Strengths:**
1. **Separation of Concerns:** Clean boundary - relay does ingestion, server does visualization preprocessing
2. **v0.4 Migration:** Relay Rust port is independent of decimation logic (stays in Node.js server)
3. **Hot-Reload Config:** Server can reload decimation config without restarting relay
4. **Service Isolation:** Server crash doesn't affect archival data path

**Architectural Risks:**
1. **Network Bandwidth Waste:** Full-rate multicast when only decimated stream needed
   - Mitigated: Single-machine IPC eliminates this
   - Acceptable: Multi-machine deployments likely have dedicated network segments
2. **Server CPU:** 6.0% overhead at 100 channels - could limit scalability
   - Mitigated: Node.js scales horizontally (multiple server instances)

**Bias Check:**
- No pet idea bias detected
- Performance data is empirical (benchmark-driven)
- Architectural pattern (layered architecture, separation of concerns) is industry-standard

**Updated Risk Assessment:**
- Single-machine multicast: LOW-MODERATE (better than relay-side)
- Multi-machine multicast: MODERATE (relay still bottleneck, but better than relay-side)
- Single-machine IPC: LOW (optimal - no bandwidth waste)

**Decision Factor:** Better network efficiency than relay-side in all deployment scenarios. Separation of concerns is stronger. Rust migration path is cleaner.