---
winner_id: simple-synchronous-rest-api-with-query-parameters
created: 2025-12-23T13:47:45-08:00
type: DRR
content_hash: 12d9c2c7af7cfeb12da97426b1c7fe2b
---

# Simple Synchronous REST API with Query Parameters for SpeedData v0.3 Pivot

## Context
SpeedData v0.3 requires a REST API for the Pivot service to transform AVRO relay storage into HDF5 format for analysis. The API must support:

- **Users:** Data analysts working in JupyterLab, Python scripts, ad-hoc exploration
- **Workload:** Low traffic (~1 request/minute average), occasional bursts (multiple within 1 second)
- **Deployment:** Multi-user LAN environment, trusted network (no authentication required for v0.3)
- **Integration:** Must work with Roelle DataSet HDF5 loader, support web frontend
- **Time ranges:** Typical queries from 30 seconds to multi-hour ranges
- **Channel scale:** 2-100 channels per request

Key constraint: Need "easy frontend for people" (web UI), which eliminated file-path-based alternatives and favored RESTful design.

## Decision
**Selected Option:** simple-synchronous-rest-api-with-query-parameters

**Adopt Simple Synchronous REST API with Query Parameters**

Single GET endpoint with query parameters for time specification, channel/signal selection, and direct HDF5 file response.

**API Design:**
- Endpoint: `GET /api/v1/pivot/export`
- Time spec: `start` (ISO 8601, required), `end` or `duration` (ISO 8601 duration like PT30S)
- Selection: `channels` (comma-separated), `signals` (comma-separated, optional)
- Response: Direct HDF5 file (Content-Type: application/x-hdf5)
- Limits: Max 20 channels, max 5 minute range per request
- Timeout: 60 seconds, returns 408 if exceeded
- No authentication (v0.3), no job queue

**Implementation:**
- Flask-based server with `threaded=True` for concurrent request handling
- Server-side temporary file generation with send_file cleanup
- ISO 8601 parsing for timestamps and durations
- Query parameter validation with 413 responses for limit violations

## Rationale
**Why this approach won:**

1. **Workload fit:** Synchronous design handles stated workload (~1 req/min, occasional bursts) without over-engineering. Burst testing validated Flask handles 3+ concurrent requests in parallel (0.02-0.03s each).

2. **Simplicity:** Single endpoint, no job tracking, no state management. JupyterLab users get immediate results for interactive exploration.

3. **Web-friendly:** Query parameters work seamlessly with browser fetch() and curl, enabling "easy frontend" requirement. File-path API would be incompatible with web UI.

4. **Standard patterns:** ISO 8601 for time, comma-separated lists for selection, REST conventions throughout. Low learning curve for users.

5. **Validated performance:** Prototype responds in <0.3s for typical queries, well within 1-second guideline for synchronous APIs.

**Weakest link:** Mock data testing - real AVRO→HDF5 transformation not yet benchmarked. Will retest when catcol integration complete.

**Alternatives rejected:**
- **Async job queue API:** Over-engineered for low traffic. Adds complexity (job tracking, polling, cleanup) with no benefit at ~1 req/min.
- **POST with JSON body:** Unnecessary complexity. Query params are idiomatic for GET requests with filtering.
- **File-path API:** Incompatible with web frontend (client can't access server filesystem). Only works for localhost scripts.
- **WebSocket streaming:** Pattern mismatch - HDF5 requires random access during write, can't stream chunks.

### Characteristic Space (C.16)
- REST API pattern with synchronous execution
- Query parameter-based filtering and time specification  
- ISO 8601 standard for temporal queries
- Direct file response (no intermediate storage)
- Stateless server design
- Flask threading for concurrent request handling
- No authentication (v0.3 trusted network)
- Hard limits enforced (20 channels, 5 minutes, 60s timeout)

## Consequences
**Immediate actions:**
1. Integrate real AVRO→HDF5 transformation (catcol) into api_server.py
2. Replace mock h5py generation with actual relay storage reads
3. Add error handling for missing AVRO files, corrupted data
4. Create simple web frontend (HTML/JS) for non-technical users
5. Document API in README with curl/Python examples

**Architectural impact:**
- Pivot service becomes stateless HTTP server (can scale horizontally if needed)
- No persistent job storage or queue infrastructure required
- Frontend development simplified (standard REST fetch patterns)

**Future evolution (v0.4+):**
- Add API key authentication header when moving beyond trusted LAN
- Consider async pattern if workload changes (e.g., >10 req/sec sustained)
- May add batch endpoint if users request multi-query optimization
- Potential GraphQL layer if query complexity increases significantly

**Technical debt incurred:**
- Temporary file cleanup relies on Flask send_file behavior - should add explicit cleanup tests
- No rate limiting yet (acceptable for trusted LAN, needed for public deployment)
- Client must implement own retry logic (no server-side retry/queue)

**Constraints accepted:**
- 20 channel / 5 minute limits may need tuning based on real-world usage patterns
- 60-second timeout is arbitrary - should profile actual AVRO reads to calibrate
- No parallel query optimization (each request reads AVRO independently)
