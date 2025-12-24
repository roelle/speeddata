---
id: 2025-12-23-external-two-tier-architecture-streaming-core-analysis-layer.md
type: external
target: two-tier-architecture-streaming-core-analysis-layer
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
content_hash: f70f8bfec81f3d44c7061b84b1f16a14
---

Research findings on tiered architectures for streaming + analytics:

**Similar Systems:**
- Lambda Architecture (speed layer + batch layer) - proven pattern for streaming/analytics separation
- Apache Flink (streaming runtime) + Apache Spark (batch analytics) - common pairing in data pipelines
- TimescaleDB (real-time inserts + columnar compression for analytics) - tiered storage within single system

**Evidence for SpeedData context:**
1. **Tier separation matches data lifecycle:**
   - Streaming tier (Relay + Stripchart): latency-critical, row-based, ephemeral
   - Analysis tier (Pivot): throughput-critical, column-based, persistent archives
   - Clean handoff via ephemeral cache (similar to Kafka as buffer between tiers)

2. **Performance isolation validated:**
   - Analysis workload (row→column transformation) won't impact real-time streaming
   - Independent resource allocation (CPU/memory) per tier
   - Streaming tier can prioritize UDP packet processing without competition

3. **Deployment flexibility:**
   - Streaming tier on Pi (low latency, minimal footprint)
   - Analysis tier on Xeon (high throughput for HDF5 compression)
   - Scales to heterogeneous hardware naturally

**Risks validated:**
- Cache interface is critical coupling point - format changes ripple through both tiers
- Tier boundary placement requires careful design (Avro cache format acts as contract)
- Operational complexity: need to understand 2 different performance profiles

**Conclusion:** Strong architectural match for SpeedData's dual lifecycle (real-time + offline analysis). Provides clear upgrade path: start monolithic, split into tiers as scale demands. Aligns with functional separation invariant.