---
scope: Node.js for bridge service, modern browsers, Python 3.8+. Modular architecture, separate concerns.
kind: system
content_hash: 4933cfa287d60beab2e2cd74e3aab42c
---

# Hypothesis: Hybrid: Vanilla JS Frontend with Node.js Multicast Bridge + Rich Python Package

Split responsibilities for optimal performance.

**Frontend (Vanilla JS + Node Bridge):**
- registration.html: vanilla JS for API calls
- Separate Node.js service: multicast-bridge.js
  - Subscribes to UDP multicast
  - Deserializes AVRO packets
  - Forwards to browser via WebSocket
  - Runs alongside orchestrator
- No build step for frontend

**Python Package (speeddata):**
- Structured package with submodules:
  - speeddata.client: REST API wrapper
  - speeddata.schema: AVRO utilities
  - speeddata.dataset: DataSet integration
- Schema extraction from HDF5 files
- Batch operations: register_many()
- Configuration file support (~/.speeddata.yaml)
- ~600 lines

**Architecture:**
```
Browser → Fetch → Orchestrator REST API
Browser → WebSocket → multicast-bridge.js → UDP multicast

JupyterLab → speeddata package → REST API
JupyterLab → DataSet → schema extract → auto-register
```

**Schema Handling:**
- Schema compression (zlib before JSON)
- Deduplication: hash-based schema registry
- Reference by hash: avoid re-uploading identical schemas
- Streaming upload for 10MB+ schemas

## Rationale
{"anomaly": "Need UI + library for registration API + efficient multicast bridge", "approach": "Node.js for AVRO/multicast, vanilla JS frontend, rich Python", "alternatives_rejected": ["Python for multicast bridge (slower AVRO parsing)"]}