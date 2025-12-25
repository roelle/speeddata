# Bounded Context

## Vocabulary

- **SpeedData**: High-performance telemetry system for UDP multicast data streaming.
- **Relay**: C99 per-channel process receiving UDP, writing AVRO, multicasting data.
- **Orchestrator**: Python fleet manager with embedded REST API for dynamic channel registration.
- **Channel**: Collection of signals with common time axis, one AVRO schema.
- **Signal**: Single data entity (e.g. voltage, temperature). Registration
- **Frontend**: Vanilla JS web UI for channel management with live data preview. Python
- **Client**: Thin requests wrapper for programmatic channel registration.
- **Stripchart**: WebSocket server + Canvas frontend for real-time visualization.
- **Pivot**: AVRO→HDF5 transformer for columnar analysis.

## Invariants

No GPL license (user explicitly stated preference). Must be open source. Tech stack: C99 relay, Python orchestrator/pivot, Node.js stripchart, vanilla JS frontend. Performance constraint: 5Gbps per-channel relay throughput. Platform range: Raspberry Pi to 16-core Xeon. Current status: v0.6.0 tagged, production-ready features complete. README states 'TBD - Subject to change (will be open, not GPL)'. Project has multiple contributors expected (mentions 'reach out to maintainer'). Multi-language codebase (C, Python, JavaScript). Integration with external tools (JupyterLab, web browsers).
