---
scope: Modern browsers with Web Components support, Python 3.8+. No build tools, modular architecture.
kind: system
content_hash: 8f90a43985ca03e5184f378621495733
---

# Hypothesis: Web Components Frontend + Python Library with Schema Validation

Standards-based approach with enhanced schema handling.

**Frontend (Web Components):**
- Custom elements: <channel-list>, <registration-form>, <live-data-widget>
- Vanilla JS with Shadow DOM for encapsulation
- Lit library for templating (tiny, 5KB)
- Progressive enhancement: works without JS (server-side fallback)
- No build required (ES modules)

**Python Library (speeddata.py + speeddata.avro module):**
- Main module: REST API wrapper
- avro module: schema validation using fastavro
- Schema registry: HTTP caching (ETag support)
- Jupyter magic: `%speeddata register channel1 --port 26001`
- ~400 lines total

**Architecture:**
```
Browser → Web Components → Fetch API → REST
Browser → WebSocket → Live data

JupyterLab → speeddata module → requests
JupyterLab → %speeddata magic → interactive registration
```

**Schema Handling:**
- Schema validation before upload (catch errors early)
- Compression for large schemas (gzip, handled by HTTP)
- Server-side schema cache (ETag/If-None-Match)
- Reference existing schemas by name

## Rationale
{"anomaly": "Need UI + library for registration API", "approach": "Standards-based components with schema validation", "alternatives_rejected": ["Angular (too heavy)", "Polymer (deprecated)"]}