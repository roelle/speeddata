---
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-audit_report-apache-arrow-ipc.md
type: audit_report
target: apache-arrow-ipc
verdict: pass
content_hash: 26239f4044e91ac7d995bcb76205f5d2
---

**Context Match Risk**: External evidence from in-memory analytics and cross-process communication domains. Arrow IPC designed for ephemeral data exchange, not long-term storage. Congruence Level: CL1 (different context - IPC/streaming vs disk archival).

**Persistence Risk**: Arrow IPC lacks built-in compression in format spec (application-layer concern). File sizes may be larger than compressed alternatives. Long-term storage cost vs memory-mapped read speed tradeoff unclear.

**Dependency Risk**: Requires pyarrow library (same concerns as Parquet regarding binary compatibility on Raspberry Pi ARM). Arrow ecosystem moves quickly - format stability for multi-year archives uncertain.

**DataSet Integration Risk**: Requires wrapper (~15-30 LOC). Zero-copy characteristics may not transfer through wrapper layer. Integration benefits (zero-copy) may be lost in DataSet's internal representation.

**Maturity Risk**: Arrow IPC less battle-tested for long-term archival compared to HDF5 (decades of scientific use) or Parquet (years in data warehouses). Tooling ecosystem for inspection/repair of corrupted files less mature.

**Schema Evolution Risk**: Adding new signals to existing files requires format version compatibility. Arrow's schema flexibility may complicate backward compatibility for old archives.