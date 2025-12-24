---
scope: SpeedData v0.4 relay service rewrite. Applies to UDP receive → AVRO disk write → multicast relay hot path. Does not affect pivot or stripchart services.
kind: system
content_hash: 1012da219d15f5dcf67b70146e4060bc
---

# Hypothesis: v0.4 Relay Architecture Decision

Parent decision node grouping alternative approaches for porting SpeedData relay (rowdog) to a compiled language for v0.4.

Key design dimensions:
1. Process model (monolithic vs per-channel vs hybrid)
2. I/O strategy (buffered writes vs io_uring)
3. Language choice (Rust/Zig/C++/C)
4. Multi-channel handling

Goal: 10-100x performance improvement while maintaining zero-copy philosophy and supporting platform range (Raspberry Pi to multi-core Xeon).

## Rationale
{
  "anomaly": "Python relay (rowdog.py) is performance bottleneck. GIL limits multi-core scaling, interpreted overhead adds latency, cannot achieve 100Gbps target on Xeon.",
  "approach": "Systematic exploration of compiled language rewrites with different architectural patterns",
  "alternatives_rejected": ["Keep Python with PyPy JIT (still GIL-bound)", "Cython wrapper (complexity without full performance gain)"]
}