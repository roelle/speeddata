---
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-24
date: 2025-12-24
id: 2025-12-24-external-standalone-fastapi-service-with-sqlite.md
type: external
target: standalone-fastapi-service-with-sqlite
content_hash: 82811bdf418396772e91334b0b17d41a
---

External research via web search (2025 sources):

**Performance Analysis:**
- FastAPI: 15,000-20,000 req/s vs Flask: 2,000-3,000 req/s (5-10x faster)
- Response latency: FastAPI 45ms vs Flask 142ms
- Memory: FastAPI 127MB vs Flask 156MB
- Architecture: async/await (FastAPI) vs synchronous WSGI (Flask)

Sources:
- [FastAPI vs Flask 2025 Performance](https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison)
- [Performance Showdown](https://medium.com/@krishtech/performance-showdown-fastapi-vs-flask-in-high-traffic-applications-1cb041d2ae51)

**IPC Overhead Analysis:**
- Unix domain sockets: 0.01-0.05ms latency (10-20x faster than TCP)
- HTTP localhost: 0.1-1ms latency (network stack overhead)
- Benchmark: 127,582 messages/sec for 1KB payloads (Unix sockets)

Sources:
- [IPC Performance Comparison](https://www.baeldung.com/linux/ipc-performance-comparison)
- [Unix Sockets for Microservices](https://medium.com/@sanathshetty444/beyond-http-unleashing-the-power-of-unix-domain-sockets-for-high-performance-microservices-252eee7b96ad)

**Operational Considerations:**
- Deployment complexity: +1 service to manage (systemd unit, health checks, restart policies)
- Pi footprint: +50-100MB RAM for FastAPI + uvicorn process
- IPC failure modes: Network errors, socket permission issues, orchestrator unavailable
- Error propagation: Two-phase commit needed (API DB write → orchestrator IPC → relay spawn)

**Verdict Rationale:**
While FastAPI is technically superior (performance, async, OpenAPI docs), the benefits don't justify costs for this use case:
- Channel registration is NOT hot path (< 1 req/s typical)
- Flask performance adequate for CRUD operations
- IPC adds complexity without performance benefit (registration latency tolerant)
- Extra service increases Pi deployment footprint
- Tight coupling (register → spawn relay) better served by embedded approach

**Congruence Level: CL2 (Similar Context)**
Evidence from web applies to general REST APIs, minor penalty for SpeedData-specific context (single-host, low-traffic registration)