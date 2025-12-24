---
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-internal-relay-side-decimation-with-dual-multicast.md
type: internal
target: relay-side-decimation-with-dual-multicast
verdict: pass
assurance_level: L2
carrier_ref: test-runner
content_hash: 657cd6e2a955ffebfaaa9a7fac7be842
---

**Performance Benchmark (tests/benchmark_decimation.py):**
- Downsample: 0.0% CPU overhead (negligible)
- Average: 0.2% CPU overhead
- Min-Max: 0.4% CPU overhead
- RMS: 0.3% CPU overhead

All algorithms well below 10% threshold. Hot loop performance risk is LOW.

**Implementation Feasibility:**
- Relay code is simple (93 lines), adding decimation requires:
  1. Import numpy for algorithms (~5 lines)
  2. Load decimation config from schema (~10 lines)
  3. Add decimation function calls (~15 lines)
  4. Create second multicast socket (~5 lines)
  5. Send to dual multicast groups (~3 lines)
- Estimated implementation: ~40 LOC addition

**Dual Multicast Validation:**
- Current relay uses single multicast (224.0.0.1:26001)
- Dual approach: full-rate (224.0.0.1:26001), decimated (224.0.0.2:26002)
- Multicast group consumption: 2 per channel (acceptable for <100 channels)

**Domain Research:**
- SCADA systems use multicast for PMU telemetry data with multiple rates
- Utility networks handle "explosion of data that PMUs generate" via selective multicast
- Industrial telemetry commonly separates high-rate archival from low-rate visualization

**Sources:**
- [IP multicast in SCADA](https://www.researchgate.net/publication/298078797_IP_multicast_and_its_application_in_SCADA_system)
- [Multicast in Utility Networks](https://www.ciscopress.com/articles/article.asp?p=2928192&seqNum=4)
- [SCADA Telemetry Guide](https://www.reverecontrol.com/scada-basics-what-are-scada-and-telemetry/)

**Conclusion:** Performance validated, implementation feasible, domain precedent exists.