---
scope: SpeedData pivot storage. 2-100 channels per export (tables per database). Time windows 30-60 seconds typical. Python 3.x environment (sqlite3 in stdlib). Linux/Raspberry Pi deployment. File sizes 15KB-150MB estimated (uncompressed, but indexed). No external dependencies beyond Python stdlib.
kind: system
content_hash: c991cf5404677f5e47ca55b9f746d8b6
---

# Hypothesis: SQLite with Time-Series Extension

Use SQLite database as disk serialization format for pivot storage. Implementation: Python sqlite3 standard library with time-series optimized schema. Structure: Each Set becomes a database file with tables per channel (columns: timestamp, signal1, signal2, ...). Time-range queries via SQL WHERE clauses on indexed timestamp column. Multi-channel aggregation via JOIN operations across channel tables or UNION for same-schema channels. Column-oriented access via SELECT signal_name FROM channel_table. Integration with Roelle DataSet via pandas.read_sql() or direct sqlite3 cursor operations. Queryable without custom tools - standard SQL clients can inspect data. Single-file portability. VACUUM command for compaction.

## Rationale
{"anomaly": "Need disk format for time-range exports with multi-channel aggregation", "approach": "SQLite provides zero-dependency embedded database, SQL enables flexible time-range queries, universally queryable format improves observability and debugging, single-file portability", "alternatives_rejected": []}