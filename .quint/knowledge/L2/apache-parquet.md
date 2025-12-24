---
scope: SpeedData pivot storage. 2-100 channels per export (one file per channel). Time windows 30-60 seconds typical. Python 3.x environment. Linux/Raspberry Pi deployment. File sizes 5KB-50MB estimated (compressed).
kind: system
content_hash: e41683823f4b7c45d289227c6691fd35
---

# Hypothesis: Apache Parquet

Use Apache Parquet as disk serialization format for pivot storage. Implementation: Python pyarrow or fastparquet library. Structure: Each channel becomes a Parquet file with columnar layout (signal per column). Time-range queries via row group pruning on timestamp column. Multi-channel aggregation via multiple Parquet files referenced in manifest/metadata file. Column-oriented storage native to Parquet format. Integration with Roelle DataSet via pandas.read_parquet() or pyarrow.parquet.read_table(). Compression (snappy, gzip, zstd) reduces file size significantly vs uncompressed formats.

## Rationale
{"anomaly": "Need disk format for time-range exports with multi-channel aggregation", "approach": "Parquet is industry-standard columnar format with excellent compression, wide ecosystem support (Spark, Pandas, Arrow), efficient time-range filtering via row groups", "alternatives_rejected": []}