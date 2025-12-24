---
scope: SpeedData v0.3 relay and stripchart services. Applies to all channels requiring visualization at lower rates than acquisition (e.g., 5000 Hz → 100 Hz). Affects relay multicast architecture, stripchart server processing, and frontend rendering.
kind: episteme
content_hash: 5d31f3ae9ef3c8f906f8fc3afb967e4d
---

# Hypothesis: Decimation Architecture Decision

Parent decision node grouping competing decimation architecture approaches for SpeedData v0.3. Must determine where decimation occurs (relay/server/frontend), algorithm selection, configuration granularity, and dual-output strategy for visualization vs archival streams.

## Rationale
{"anomaly": "Visualization cannot render 5000 Hz data streams without decimation. Current architecture has no decimation strategy.", "approach": "Systematically evaluate decimation placement options and create decision framework", "alternatives_rejected": ["No decimation (infeasible - browsers cannot render 5000 Hz)", "Ad-hoc decimation in random locations (unmaintainable)"]}