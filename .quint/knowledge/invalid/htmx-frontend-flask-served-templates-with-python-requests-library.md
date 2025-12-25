---
scope: Any browser (degrades gracefully), Python 3.8+. Server-side rendering, minimal client JS.
kind: system
content_hash: ee78a2c50f6faa1542ebb7bd6f2bd7e2
---

# Hypothesis: HTMX Frontend + Flask-Served Templates with Python Requests Library

Server-driven hypermedia approach (minimal JavaScript).

**Frontend (HTMX + Jinja2):**
- Flask serves HTML templates (registration.html via Jinja2)
- HTMX for dynamic updates (hx-get, hx-post attributes)
- Server-side rendering (orchestrator serves UI pages)
- WebSocket via HTMX extensions for live data
- ~100 lines of JavaScript total
- Progressive enhancement: full functionality without JS

**Python Library (speeddata_client.py):**
- Simple requests wrapper
- Command-line interface: speeddata-cli
- Reads schemas from files or stdin
- JSON response parsing
- ~250 lines

**Architecture:**
```
Browser → HTMX → Flask templates → Orchestrator REST API (same service)
Browser → HTMX WebSocket extension → Live data

JupyterLab → speeddata_client → requests → REST API
CLI → speeddata-cli → same library
```

**Schema Handling:**
- File upload via multipart form
- Server validates and stores
- Large files handled by werkzeug (Flask's upload handler)
- No client-side size limits

## Rationale
{"anomaly": "Need UI + library for registration API", "approach": "Server-side rendering, hypermedia, minimal JS", "alternatives_rejected": ["Full SSR framework like Next.js (overkill)"]}