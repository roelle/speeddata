---
scope: Multi-service deployments. Requires Python 3.8+, FastAPI, uvicorn. IPC overhead acceptable (non-critical path).
kind: system
content_hash: 5e8eb98650ebcc9ca78d00136522c416
---

# Hypothesis: Standalone FastAPI Service with SQLite

Separate registration service (registration-service.py) using FastAPI + SQLite, communicating with orchestrator via IPC.

**Architecture:**
- Standalone FastAPI service on port 8080
- SQLite backend: data/registry.db
- IPC: Unix domain socket (/tmp/speeddata-orchestrator.sock) or HTTP to orchestrator management API
- Orchestrator exposes internal API: POST /internal/relay/start, POST /internal/relay/stop

**Workflow:**
- Registration service: POST /channels → Validate → Insert DB → HTTP POST to orchestrator:8081/internal/relay/start
- Orchestrator: Receives IPC → Spawns relay → Returns PID
- Registration service: Updates DB with PID, returns to client

**Benefits:**
- Clean separation of concerns
- Independent scaling (registration API can be lightweight async)
- Testable in isolation
- OpenAPI auto-docs via FastAPI

## Rationale
{"anomaly": "Need REST API + orchestrator coordination", "approach": "Separate service with IPC for clean architecture", "alternatives_rejected": ["Embedded (tight coupling)", "Microservices with message queue (over-engineered)"]}