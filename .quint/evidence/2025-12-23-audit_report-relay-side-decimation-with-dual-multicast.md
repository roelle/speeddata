---
type: audit_report
target: relay-side-decimation-with-dual-multicast
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-audit_report-relay-side-decimation-with-dual-multicast.md
content_hash: 6762a03aa88a17c041f46163a330590f
---

**R_eff: 1.00** (Internal testing, CL3 - same context)

**Weakest Link Analysis:**
- Evidence: Internal performance benchmark (0.4% CPU overhead)
- Congruence Level: CL3 (same codebase, same context)
- No dependencies, no WLNK penalty applied

**Network Bottleneck Risk (CRITICAL NEW FINDING):**

**Single-Machine Deployment:**
- NIC load: 80.8 MB/sec (40 MB/sec in + 40.8 MB/sec out)
- Doubles multicast bandwidth (full-rate + decimated streams)
- At 10 channels: ~800 Mbps (10% of 1 Gbps NIC) - MODERATE RISK
- At 100 channels: ~8 Gbps - EXCEEDS 1 Gbps NIC CAPACITY - HIGH RISK

**Multi-Machine Deployment:**
- Relay becomes NIC bottleneck (80.8 MB/sec)
- Server receives 40.8 MB/sec (dual streams)

**IPC Mitigation:**
- If relay/server co-located with Unix domain sockets: eliminates multicast bandwidth penalty
- Single-machine IPC: 40.8 MB/sec total NIC load (same as server-side)

**Rust Migration Impact:**
- Decimation CPU overhead becomes negligible (0.004% - 0.04%)
- Network bandwidth becomes PRIMARY bottleneck, not CPU
- Makes dual multicast bandwidth penalty MORE significant

**Architectural Risks:**
1. **Schema/Config Coupling:** Decimation params in AVRO schema couples data definition with processing config
2. **v0.4 Migration:** Decimation logic must be ported to Rust/compiled language
3. **Hot Loop Risk:** Mitigated by benchmark (0.4% CPU), but Rust will make this irrelevant

**Bias Check:**
- No pet idea bias detected
- Performance data is empirical (benchmark-driven)
- Network risk was initially underestimated - corrected by user input

**Updated Risk Assessment:**
- Single-machine multicast: MODERATE-HIGH (NIC bottleneck at scale)
- Multi-machine multicast: HIGH (relay NIC bottleneck)
- Single-machine IPC: LOW (mitigates bandwidth issue)

**Decision Factor:** Network architecture (multicast vs IPC) is more critical than decimation location for relay-side approach.