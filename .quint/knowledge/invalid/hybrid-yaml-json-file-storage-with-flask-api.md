---
scope: Small deployments (&lt;20 channels). Requires Python 3.8+, Flask. Linux-only (fcntl).
kind: system
content_hash: 8f6bfc1013be4bad6a9fcfe43cf13f42
---

# Hypothesis: Hybrid: YAML + JSON File Storage with Flask API

Embedded Flask API in orchestrator using file-based storage (JSON) instead of SQLite for simplicity.

**Architecture:**
- Flask embedded in orchestrator.py
- Storage: config/relay.yaml (static) + data/registry.json (dynamic, file-locked)
- File locking via fcntl on Linux, atomic writes via write-temp-rename pattern
- In-memory cache (dict) for fast reads, flush to disk on writes

**Data Flow:**
- Startup: Load relay.yaml + registry.json → Merge → In-memory dict → Spawn fleet
- POST /channels → Update in-memory dict → Write registry.json → Spawn relay
- Registry format: {"channels": [{"name": "...", "port": ..., "schema": "...", "pid": ...}]}

**Trade-offs:**
- Simpler than SQLite (no schema migrations, no DB tooling)
- Human-readable/editable (JSON)
- Concurrent write protection via file locking
- No query optimization (linear scan for port conflicts)
- Risk of corruption on unclean shutdown

## Rationale
{"anomaly": "Need REST API + persistent state", "approach": "Use JSON files for simplicity, avoid SQL complexity", "alternatives_rejected": ["Pure in-memory (no persistence)", "Pickle (binary, not human-readable)"]}