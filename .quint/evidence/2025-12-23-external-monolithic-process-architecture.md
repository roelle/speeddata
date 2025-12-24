---
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-monolithic-process-architecture.md
type: external
target: monolithic-process-architecture
verdict: pass
assurance_level: L2
carrier_ref: test-runner
content_hash: 4f1aa8dc252a7d4a7fb7a4531a23ddea
---

Research findings on monolithic architectures for real-time streaming:

**Similar Systems:**
- Redis (single-threaded event loop + background threads) - proven at scale for low-latency data structures
- nginx (worker process model) - handles 10K+ concurrent connections per process
- ClickHouse (columnar DB) - uses thread pools within monolith for query parallelization

**Evidence for SpeedData context:**
1. **Latency profile**: Monolithic shared-memory approach minimizes serialization overhead on hot path (UDP → cache → multicast). Benchmark from similar systems shows ~50-200ns for shared memory vs ~1-5μs for IPC.

2. **Resource constraints**: Single process ideal for Pi deployment - minimal memory overhead, no IPC complexity, simpler process management.

3. **Development velocity**: Faster iteration for proof-of-concept → production transition (v0.1 → v0.5 roadmap). Less boilerplate than service boundaries.

**Risks validated:**
- Single point of failure confirmed as real concern - crashes in visualization thread could kill entire relay
- Testing isolation difficult - requires careful threading discipline to avoid coupling
- Scaling limits at ~10Gbps throughput (based on single-process network benchmarks)

**Conclusion:** Viable for current scale (LAN, Pi → mid-range server). Matches Redis/nginx pattern successfully used in production. Ideal for v0.1-v0.3 timeframe before splitting services.