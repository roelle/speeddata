---
scope: Node.js build environment, modern browsers, Python 3.8+ with async support. Requires npm/build step.
kind: system
content_hash: 43ea4f4eddc1132d67487097de3dbbb2
---

# Hypothesis: React SPA + Rich Python SDK with DataSet Integration

Modern framework approach with rich Python integration.

**Frontend (React SPA):**
- Create React App with TypeScript
- Component library: channel list, registration form, live data cards
- React Query for API state management
- WebSocket hooks for live data
- Real-time updates without page reload
- Build output: static bundle served by Flask

**Python SDK (speeddata package):**
- Class-based API: SpeedDataClient with context manager
- DataSet integration: extract schemas from RoelleDataSet objects
- Schema repository: local cache (.speeddata/schemas/)
- Async support: httpx for async operations
- Rich CLI: `speeddata register --from-dataset mydata.h5`
- ~1000 lines, structured package

**Architecture:**
```
Browser → React → REST API
Browser → WebSocket (react-use-websocket) → Live data

JupyterLab → SpeedDataClient class → httpx → REST API
JupyterLab → DataSet.schema → auto-extract → upload
```

**Schema Handling:**
- Chunked upload for huge schemas (multipart/form-data)
- Progress callbacks
- Schema diffing (detect changes before re-register)

## Rationale
{"anomaly": "Need UI + library for registration API", "approach": "Modern framework for rich UX and DataSet integration", "alternatives_rejected": ["jQuery (outdated)", "Vue (less ecosystem)"]}