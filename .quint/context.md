# Bounded Context

## Vocabulary

{
  "Channel": "Collection of Signals with common time axis (abscissa). Each has own AVRO schema and UDP port.",
  "Signal": "Single data stream (e.g., voltage, current). AVRO field, HDF5 dataset.",
  "Relay (rowdog)": "Service receiving UDP packets, writing AVRO to disk, multicasting to subscribers.",
  "Decimation": "Downsampling strategy (downsample/average/minmax/rms) with configurable factor.",
  "Dual Multicast": "Full-rate stream (archival) + decimated stream (visualization) on separate multicast groups.",
  "AVRO": "Row-oriented wire encoding with preset schemas.",
  "HDF5": "Column-oriented disk format for pivot output.",
  "Pivot": "Row-to-column transformation service (AVRO → HDF5).",
  "io_uring": "Linux async I/O interface for zero-copy, kernel-managed operations.",
  "Compiled Language Target": "C/C++/Rust/Zig for relay rewrite (performance critical path).",
  "Channel Registration": "Dynamic discovery and management of channel metadata (port, schema, status).",
  "Registration State": "Current inventory of active/configured channels (SQLite database).",
  "Channel Lifecycle": "Registration → Active → De-registration (port becomes available).",
  "Schema Validation": "Comparing sender's schema against registered schema for compatibility.",
  "REST API": "HTTP interface for channel CRUD operations, schema queries, port availability (v0.5: Flask embedded in orchestrator).",
  "Registration Frontend": "Web UI for human operators to view/manage channels, see live data, monitor status.",
  "Python Client Library": "Programmatic API wrapper for JupyterLab/scripting use cases (schema upload, channel registration).",
  "Live Data Preview": "Frontend subscribes to multicast to show latest data values per channel.",
  "Data Rate Monitoring": "Tracking packet rate to verify channels are actively sending data.",
  "Schema Repository": "Storage for large/historical schemas (local files or server-side)."
}

## Invariants

{
  "Performance": "System must handle 10Mbps (Pi) to 100Gbps (Xeon). Relay is hot path.",
  "Zero-Copy Philosophy": "Avoid data copying on critical path. Relay just passes packets through.",
  "LAN-Only Security": "No TLS/encryption needed. Trusted network assumption.",
  "Current Architecture": "Service-oriented (relay/pivot/stripchart as independent processes).",
  "Configuration": "Per-service YAML with git-based deployment. Discovery: CLI → ENV → defaults.",
  "Python Constraint": "Keep pivot/stripchart in Python. Only relay needs compilation.",
  "AVRO Schema": "File-based (config/agents/*.avsc). Runtime registration via REST API (v0.5).",
  "Rotation Policy": "Time-based or size-based file rotation in relay.",
  "Retention Policy": "TTL or quota-based cleanup.",
  "Platform Range": "Raspberry Pi (ARM, limited RAM) to multi-core Xeon (x86_64, high throughput).",
  "Orchestrator Integration": "Channel registration service coordinates with relay orchestrator (v0.5: embedded Flask).",
  "Port Conflict Prevention": "Registration API prevents duplicate port assignments (SQLite UNIQUE constraint).",
  "Schema Immutability": "Once channel registered, schema should not change without de-register/re-register.",
  "Registration Persistence": "Channel metadata survives service restarts (SQLite at data/registry.db).",
  "Multi-Client Access": "Frontend (human) and remote agents (devices) both use registration API.",
  "Registration Feedback": "API must return success/failure with actionable error messages.",
  "Frontend Simplicity": "Prefer vanilla JS over frameworks unless complexity justified. Match existing stripchart style.",
  "Real-Time Not Critical": "Frontend data preview needs 'ok' latency, not sub-second updates.",
  "JupyterLab Use Case": "Python library must support schema upload from notebooks (large schemas, DataSet integration).",
  "Schema Size": "Some schemas are huge - need efficient upload/storage strategy.",
  "Multicast Subscribe": "Frontend should subscribe to decimated multicast to show live data (demonstration of multicast benefit).",
  "Existing Style": "Match monospace font, simple HTML/CSS from stripchart frontend."
}
