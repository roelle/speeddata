---
scope: Git-managed deployments with infrequent registration changes. Requires Python 3.8+, Flask, PyYAML, watchdog.
kind: system
content_hash: fb513b15d1cb3a6d62e1b80e1cd10f98
---

# Hypothesis: Conservative: YAML-Only with File Watcher

Minimal REST API that only reads/writes config/relay.yaml, using file watcher for hot-reload.

**Architecture:**
- Lightweight Flask API embedded in orchestrator
- Single source of truth: config/relay.yaml (git-trackable)
- POST /channels → Append to relay.yaml → Trigger orchestrator reload
- DELETE /channels → Remove from relay.yaml → Reload
- File watcher (watchdog library) detects changes → Orchestrator diffs config → Start/stop relays accordingly

**Workflow:**
- POST /channels {"name": "sensor1", "port": 26001, "schema": "..."}
- API: Load relay.yaml → Validate → Append new channel → Save relay.yaml
- Watchdog: Detects file change → Orchestrator reloads config → Compares with running state → Spawns new relay

**Trade-offs:**
- Simplest implementation (no DB, no JSON, just YAML)
- Git-friendly (all config in version control)
- Slower writes (YAML serialization)
- Potential race conditions (file writes during git pull)
- No audit trail (git log only)

## Rationale
{"anomaly": "Need REST API for channel registration", "approach": "Keep git-based config workflow, add API as thin wrapper", "alternatives_rejected": ["Manual YAML editing (no remote device support)", "Database (over-engineered)"]}