---
scope: Full SpeedData system explicitly designed for tiered deployment (embedded streaming + optional analysis server)
kind: system
content_hash: 8aab8e065b127819b081c1b85d36f184
---

# Hypothesis: Two-Tier Architecture: Streaming Core + Analysis Layer

Separate the architecture into two tiers with different design priorities:

Tier 1 - Streaming Core (latency-critical):
- Relay+Stripchart as single optimized binary (Rust/C++)
- UDP → shared memory cache → WebSocket, no disk writes in hot path
- Minimal dependencies, optimized for Pi deployment

Tier 2 - Analysis Layer (throughput-oriented):
- Separate service cluster for cache persistence, pivot, and export (Python/Polars)
- Reads from shared memory cache (or memory-mapped files)
- Can run on different machine (NFS/network filesystem)
- Includes REST API, Jupyter integration, dataset loading

Deployment: Core runs on Pi/embedded, Analysis layer optional on separate hardware.
Repository: Two repos (speeddata-core, speeddata-analysis) with shared wire protocol spec.

## Rationale
{"anomaly": "Current architecture treats real-time streaming and batch analysis as equal concerns, but they have opposing optimization goals (latency vs throughput)", "approach": "Separate into performance-critical streaming tier (minimal, fast) and analysis tier (feature-rich, flexible), allowing independent deployment and scaling", "alternatives_rejected": ["Single binary trying to optimize for both (complexity explosion)", "Microservices (too granular for clear tier separation)"]}