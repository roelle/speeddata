---
scope: SpeedData pivot storage. 2-100 channels per export. Time windows 30-60 seconds typical. Python 3.x environment. Linux/Raspberry Pi deployment. File sizes 8KB-80MB estimated (uncompressed, but memory-mappable). Assumes pyarrow available in deployment environment.
kind: system
content_hash: 03fe4f42cd1acb7b6e83d20aebcdc615
---

# Hypothesis: Apache Arrow IPC

Use Apache Arrow IPC (Inter-Process Communication) format as disk serialization format for pivot storage. Implementation: Python pyarrow library with arrow.ipc.RecordBatchFileWriter. Structure: Each channel becomes an Arrow table with columnar layout (signal per column). Time-range queries via direct memory mapping and timestamp column filtering. Multi-channel aggregation via multiple IPC files or single IPC file with metadata indicating channel boundaries. Column-oriented storage native to Arrow format. Zero-copy reads enable fast integration with Roelle DataSet via pyarrow.ipc.open_file(). Memory-mappable format allows efficient random access without full deserialization. Cross-language compatibility (C++, Java, R, JavaScript) future-proofs architecture.

## Rationale
{"anomaly": "Need disk format for time-range exports with multi-channel aggregation", "approach": "Arrow IPC provides zero-copy columnar format optimized for analytics workloads, memory mapping enables fast random access, cross-language support future-proofs integration", "alternatives_rejected": []}