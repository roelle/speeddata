---
scope: Single-host deployments (Pi to Xeon). Requires Python 3.8+, Flask, sqlite3 stdlib. Sub-100 channels expected.
kind: system
content_hash: 5a5077734082ec9b1729d73c87156470
---

# Hypothesis: Embedded Flask API in Orchestrator with SQLite

Extend relay/orchestrator.py to embed Flask REST API with SQLite backend (data/registry.db).

**Architecture:**
- Flask blueprint added to orchestrator.py
- SQLite schema: channels(name, port, schema_path, config_json, status, created_at)
- Startup: Load relay.yaml → Load registry.db → Merge (DB overrides) → Spawn fleet → Start Flask
- Endpoints: GET/POST/DELETE /channels, GET /channels/{name}/schema, POST /channels/{name}/validate-schema, GET /ports/available

**Integration:**
- POST /channels → Validate → Insert DB → orchestrator.spawn_relay(channel_config) → Return PID
- DELETE /channels → orchestrator.stop_relay() → Delete from DB → Release port
- Atomic operations via Python threading locks

**Storage:**
- Static baseline: config/relay.yaml (git-tracked)
- Runtime state: data/registry.db (SQLite, ACID transactions)
- Schema files: config/agents/*.avsc (referenced by path)

## Rationale
{"anomaly": "Need REST API + orchestrator coordination", "approach": "Embed API in orchestrator for tight coupling and atomic operations", "alternatives_rejected": ["gRPC (overkill for LAN)", "Config file only (no dynamic registration)"]}