---
scope: SpeedData v0.3 relay, stripchart, and pivot services. Load-time configuration only (changes require restart). Must support service-oriented architecture with independent processes. Applies to both Python (v0.3) and future compiled implementations.
kind: episteme
content_hash: bd924b0d9c9650da9eeca64ea47594f3
---

# Hypothesis: SpeedData v0.3 Configuration System Decision

Parent decision node grouping competing configuration system approaches for SpeedData v0.3. Must determine file format (YAML, JSON, TOML, etc.), file organization (monolithic vs per-service), discovery mechanism (CLI args, env vars, default paths), and validation strategy for load-time service configuration.

Scope includes:
- Channel-port mappings for relay
- Multicast endpoints for relay→stripchart/pivot
- AVRO rotation thresholds (time or size)
- Data retention policies (TTL or storage quota)
- Storage paths for AVRO files

## Rationale
{"anomaly": "Services need channel-port mappings, multicast endpoints, AVRO rotation/retention policies, but no config system exists. User distinguishes config (static, file-based) from reg (dynamic, database).", "approach": "Systematically evaluate file formats, organization patterns, and discovery mechanisms for load-time service configuration", "alternatives_rejected": ["Runtime hot-reload (explicitly out of scope for v0.3)", "Database-backed config (user said config feels like JSON/YAML, not database)", "Hardcoded values (not maintainable)"]}