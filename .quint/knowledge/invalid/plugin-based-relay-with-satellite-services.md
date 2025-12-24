---
scope: SpeedData relay component with extensibility for encoding formats, satellite services for visualization/export
kind: system
content_hash: ef84cafcae0099821fc8a5cbbf351a1c
---

# Hypothesis: Plugin-Based Relay with Satellite Services

Core relay as plugin host with hot-swappable modules:
- Relay Core: High-performance UDP/multicast engine (Rust/C++), plugin API for wire encodings
- Wire Encoding Plugins: Avro, MessagePack, Cap'n Proto as dynamically loaded libraries
- Archive Export Plugins: HDF5, Parquet writers as separate executables triggered via IPC
- Visualization: Standalone service consuming multicast (decoupled from relay)

Plugin contract: Wire plugins implement deserialize/multicast/cache interface, export plugins implement cache→file interface.
Deployment: Core binary + plugin directory + satellite services.
Repository: Core in one repo, plugins/satellites can be separate or monorepo subdirectories.

## Rationale
{"anomaly": "Tight coupling between relay and encoding formats makes experimentation expensive, violates 'unopinionated about formats' requirement", "approach": "Plugin architecture allows format experimentation without relay recompilation, supports gradual migration and user-specific encodings", "alternatives_rejected": ["Hardcoded multi-format support (maintenance burden)", "Separate relay per encoding (deployment nightmare)"]}