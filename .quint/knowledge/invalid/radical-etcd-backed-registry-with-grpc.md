---
scope: Multi-host, high-availability deployments. Requires etcd cluster, Python 3.8+, grpcio. NOT suitable for Pi/embedded.
kind: system
content_hash: f706955d136cf988b62410bef69c8121
---

# Hypothesis: Radical: etcd-Backed Registry with gRPC

Distributed configuration store using etcd with gRPC API for high-availability and multi-host orchestration.

**Architecture:**
- etcd cluster stores channel registry (key: /speeddata/channels/{name})
- gRPC service (registration-service) with protobuf schema
- Orchestrators watch etcd for changes → Spawn/stop relays automatically
- Leader election via etcd for multi-orchestrator deployments

**Data Model:**
- etcd key-value: /speeddata/channels/sensor1 → {"port": 26001, "schema": "...", "host": "node1"}
- Schema storage: /speeddata/schemas/{name} → AVRO JSON
- Port locks: /speeddata/locks/ports/{port} → TTL-based lease

**Benefits:**
- Multi-host support (orchestrator per machine)
- Automatic failover (leader election)
- Atomic operations (etcd transactions)
- Watch API for real-time updates

**Trade-offs:**
- Complex deployment (etcd cluster)
- Overkill for single-host (Pi deployments impossible)
- Network dependency (etcd must be reachable)

## Rationale
{"anomaly": "Need distributed channel registry for multi-host orchestration", "approach": "Use etcd for consensus and gRPC for performance", "alternatives_rejected": ["Redis (no strong consistency)", "Consul (heavier than etcd)"]}