---
target: service-oriented-architecture-with-process-isolation
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-service-oriented-architecture-with-process-isolation.md
type: external
content_hash: 323cf27f7a1e491c4140c3bb70e5eb6d
---

Research findings on service-oriented architectures for data streaming:

**Similar Systems:**
- Kafka ecosystem (broker + consumers + producers as separate processes) - industry standard for distributed streaming
- Prometheus (server + exporters + pushgateway as services) - proven monitoring architecture
- Telegraf + InfluxDB + Grafana (TIG stack) - separated collection/storage/visualization

**Evidence for SpeedData context:**
1. **Service boundaries align with SpeedData components:**
   - Relay = data ingestion/relay (like Kafka broker)
   - Stripchart = visualization (like Grafana)
   - Pivot = batch processing (like Kafka Connect)

2. **IPC overhead measurement from similar systems:**
   - Unix domain sockets: ~2-10μs latency (acceptable for non-critical path)
   - Multicast already crosses process boundary - no additional overhead for Stripchart/Pivot
   - Hot path (UDP → multicast) remains within Relay service

3. **Operational benefits:**
   - Independent restarts (Pivot maintenance doesn't affect real-time streaming)
   - Clear upgrade path to Docker (roadmap v0.6)
   - Separate resource limits per service (cgroup isolation)

**Risks validated:**
- Deployment complexity increase confirmed - 3 systemd units vs 1
- Service discovery needed if multi-machine (solvable via static config for LAN)
- Memory overhead: ~30-50MB per process baseline (acceptable on modern systems)

**Conclusion:** Excellent fit for production deployments (v0.4+). Clean separation enables independent scaling and maintenance. IPC overhead negligible compared to UDP latency budget.