---
scope: Modern browsers (ES6+), Python 3.8+. Single-page application. No build tools required.
kind: system
content_hash: f65dd35036c3c0be0098e7ecabd4b4be
---

# Hypothesis: Vanilla JS Frontend + Thin Python Wrapper

Conservative approach matching existing stripchart style.

**Frontend:**
- Single HTML page (registration.html) with vanilla JavaScript
- Fetch API for REST calls to orchestrator:8080/api/v1
- WebSocket connection to stripchart server for live data preview
- CSS matching existing monospace style
- No build step, no dependencies

**Python Library (speeddata_client.py):**
- Thin wrapper around requests library
- Methods: register_channel(), deregister_channel(), list_channels(), upload_schema()
- Schema upload: POST full JSON to /api/v1/channels (HTTP handles size)
- Returns parsed JSON responses
- ~200 lines, single file

**Architecture:**
```
Browser → Fetch API → Orchestrator REST API
Browser → WebSocket → Stripchart Server → Multicast (live data)

JupyterLab → speeddata_client.py → requests → Orchestrator REST API
```

**Schema Handling:**
- Direct JSON POST (REST/HTTP has no MTU limit)
- For huge schemas: optional file upload endpoint
- Python can read from DataSet or local .avsc files

## Rationale
{"anomaly": "Need UI + library for registration API", "approach": "Match existing simplicity, no frameworks", "alternatives_rejected": ["CLI-only (not user-friendly)", "Manual curl (no UI)"]}