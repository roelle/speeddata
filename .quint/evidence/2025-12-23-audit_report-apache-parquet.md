---
date: 2025-12-23
id: 2025-12-23-audit_report-apache-parquet.md
type: audit_report
target: apache-parquet
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-23
content_hash: 2d671f80758f9b82185fa7d3ea58a48f
---

**Context Match Risk**: External evidence from big data ecosystem (Spark, Dask, cloud analytics). SpeedData's small-file regime (8KB-80MB) differs significantly from Parquet's typical multi-GB datasets. Row group overhead may be disproportionate for small files. Congruence Level: CL1 (different context - industrial big data vs embedded telemetry).

**Write Performance Risk**: Parquet optimizes for read performance via compression, encoding, statistics. Write path is complex (buffering, row group assembly, footer generation). May not suit real-time pivot conversion if latency matters.

**Dependency Risk**: Requires pyarrow library (larger dependency than h5py). Potential binary compatibility issues on Raspberry Pi ARM architecture. PyArrow has native C++ components that may complicate deployment.

**DataSet Integration Risk**: Requires wrapper layer (~20-40 LOC). No existing proof-of-concept. Integration complexity unknown until implemented. Pandas intermediate step may negate Parquet's memory efficiency.

**Overkill Risk**: Features like predicate pushdown, nested types, schema evolution are unused in SpeedData's simple columnar layout. Complexity cost without benefit.