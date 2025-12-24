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
  "Registration State": "Current inventory of active/configured channels (file-based or in-memory).",
  "Channel Lifecycle": "Registration → Active → De-registration (port becomes available).",
  "Schema Validation": "Comparing sender's schema against registered schema for compatibility.",
  "REST API": "HTTP interface for channel CRUD operations, schema queries, port availability."
}

## Invariants

{
  "Performance": "System must handle 10Mbps (Pi) to 100Gbps (Xeon). Relay is hot path.",
  "Zero-Copy Philosophy": "Avoid data copying on critical path. Relay just passes packets through.",
  "LAN-Only Security": "No TLS/encryption needed. Trusted network assumption.",
  "Current Architecture": "Service-oriented (relay/pivot/stripchart as independent processes).",
  "Configuration": "Per-service YAML with git-based deployment. Discovery: CLI → ENV → defaults.",
  "Python Constraint": "Keep pivot/stripchart in Python. Only relay needs compilation.",
  "AVRO Schema": "Preset, file-based (config/agents/*.avsc). Runtime registration now required.",
  "Rotation Policy": "Time-based or size-based file rotation in relay.",
  "Retention Policy": "TTL or quota-based cleanup.",
  "Platform Range": "Raspberry Pi (ARM, limited RAM) to multi-core Xeon (x86_64, high throughput).",
  "Orchestrator Integration": "Channel registration service must coordinate with relay orchestrator.",
  "Port Conflict Prevention": "Registration API must prevent duplicate port assignments.",
  "Schema Immutability": "Once channel registered, schema should not change without de-register/re-register.",
  "Registration Persistence": "Channel metadata must survive service restarts.",
  "Multi-Client Access": "Frontend (human) and remote agents (devices) both use registration API.",
  "Registration Feedback": "API must return success/failure with actionable error messages."
}
