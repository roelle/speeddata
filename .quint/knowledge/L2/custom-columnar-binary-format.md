---
scope: SpeedData pivot storage. 2-100 channels per export. Time windows 30-60 seconds typical. Python 3.x environment (struct in stdlib). Linux/Raspberry Pi deployment. File sizes 5KB-50MB estimated (compressed). Requires custom reader implementation (~50-100 LOC) for Roelle DataSet integration.
kind: system
content_hash: ec9c1e5fb5f8289bc1e1b2c2db81fd1c
---

# Hypothesis: Custom Columnar Binary Format

Design and implement custom columnar binary format tailored exactly to SpeedData pivot requirements. Implementation: Python struct module for encoding, minimal-dependency approach. Structure: File header (magic bytes, version, channel count, signal metadata), followed by signal blocks (timestamp array + per-signal value arrays). Time-range queries via binary search on timestamp array (requires sorted data). Multi-channel aggregation via concatenated signal blocks with channel delimiters in header. Column-oriented storage via separate contiguous arrays per signal. Integration with Roelle DataSet via custom reader module (50-100 LOC). Compression optional via zlib/lz4 on signal blocks. Format optimized for SpeedData's exact access patterns - no unnecessary features from general-purpose formats.

## Rationale
{"anomaly": "Need disk format for time-range exports with multi-channel aggregation", "approach": "Custom format eliminates all unnecessary complexity from general-purpose formats, maximum control over layout/compression/versioning, zero external dependencies beyond stdlib, optimized for SpeedData's exact access patterns", "alternatives_rejected": []}