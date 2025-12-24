---
scope: SpeedData core components, designed for independent scaling and language optimization per service
kind: system
content_hash: 9ee0077f8071fb5a3b5ae6fabba13988
---

# Hypothesis: Service-Oriented Architecture with Process Isolation

Three independent services communicating via well-defined interfaces:
1. Relay Service: UDP ingestion → disk cache → multicast relay (compiled: Rust/C++)
2. Stripchart Service: Multicast subscriber → WebSocket publisher (Node.js/compiled)
3. Pivot Service: On-demand REST API for cache → archive conversion (Python/compiled)

Inter-service communication: Multicast (Relay→Stripchart), REST (User→Pivot), filesystem (shared cache).
Deployment options: (a) separate processes on same host, (b) Docker Compose stack, (c) separate repos/containers.
Repository: monorepo with independent build targets OR separate repos with contract definitions.

## Rationale
{"anomaly": "Current architecture mixes concerns without clear boundaries, making optimization and maintenance difficult", "approach": "Separate services by responsibility (streaming, visualization, analysis) with stable interfaces, allowing per-service technology optimization", "alternatives_rejected": ["Keep Python for all (too slow for relay)", "Full microservices with service mesh (overkill for LAN-only system)"]}