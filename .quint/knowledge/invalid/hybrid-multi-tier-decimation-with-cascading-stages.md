---
scope: All services: relay, stripchart server, frontend. Applies to high-rate channels (>1000 Hz). Optimizes bandwidth, server CPU, and rendering performance independently.
kind: system
content_hash: 035a2a9c49c3b837c3553b971b065833
---

# Hypothesis: Hybrid Multi-Tier Decimation with Cascading Stages

Implement decimation at MULTIPLE stages with different purposes:

**Relay Stage (Coarse Decimation):**
- Apply aggressive downsample (e.g., 5000 Hz → 500 Hz) for bandwidth reduction
- Dual multicast: full-rate (archival) + coarse-decimated (network optimization)
- Config: global decimation.network_reduction_factor in relay config

**Server Stage (Algorithm Selection):**
- Subscribe to coarse-decimated multicast (500 Hz)
- Apply algorithm-specific decimation (average/min-max/RMS) for visualization quality
- Output target: 50-100 Hz for WebSocket transmission
- Config: per-channel algorithm in stripchart/config/decimation.json

**Frontend Stage (Adaptive Display):**
- Receive 50-100 Hz stream over WebSocket
- Apply final downsample based on chart zoom level and viewport
- Render only visible points (e.g., 10 Hz for zoomed-out view, 100 Hz for zoomed-in)
- Config: dynamic, based on user interaction

Cascading architecture: 5000 Hz → (relay) → 500 Hz → (server) → 100 Hz → (frontend) → 10-100 Hz display.

## Rationale
{"anomaly": "Single-stage decimation creates conflicting requirements (bandwidth vs quality vs rendering)", "approach": "Separate concerns: relay reduces bandwidth, server optimizes for visualization algorithm, frontend adapts to display context", "alternatives_rejected": ["Single-stage at any tier (cannot optimize all three concerns)", "No relay decimation (wastes network bandwidth for all consumers)"]}