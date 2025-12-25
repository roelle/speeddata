---
scope: SpeedData v0.6 registration frontend. Applies to human operators and JupyterLab users. Target platforms: modern browsers + Python 3.8+.
kind: episteme
content_hash: 8d061db61a0218dee330a21575b58ef4
---

# Hypothesis: Registration Frontend and Python Client Architecture Decision

Decision point for implementing registration frontend (web UI) and Python client library. Must provide:
- Web UI for channel management and live data preview
- Python library for JupyterLab/scripting use cases
- Large schema handling (schemas can exceed UDP MTU but REST/HTTP is fine)
- Multicast subscription for live data values
- Match existing stripchart simplicity

Key trade-offs: Framework complexity vs development speed, library richness vs simplicity, schema upload strategies.

## Rationale
{"anomaly": "REST API (v0.5) exists but no human-friendly UI or programmatic library for registration", "approach": "Build web frontend + Python client library", "alternatives_rejected": []}