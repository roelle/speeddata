---
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-apache-arrow-ipc.md
type: external
target: apache-arrow-ipc
verdict: pass
assurance_level: L2
carrier_ref: test-runner
content_hash: 69e642589dc93ece460c7203ed99adfd
---

Apache Arrow IPC Integration Analysis:

**NumPy Arrays**: pyarrow.ipc.open_file() → table.column('signal').to_numpy(). Direct zero-copy conversion for compatible dtypes. Memory-mapped reads possible: `source = pa.memory_map('data.arrow')`.

**Pandas**: pyarrow.ipc.open_file() → table.to_pandas(). Example: `df = pa.ipc.open_file('data.arrow').read_all().to_pandas()`. Zero-copy for compatible types, fallback copy for others.

**Polars**: Native Arrow support via pl.read_ipc(). Example: `df = pl.read_ipc('data.arrow')`. Polars uses Arrow as internal memory format - true zero-copy integration.

**Roelle DataSet**: Arrow → numpy → DataSet via table.to_pandas() or column-wise to_numpy(). Requires custom wrapper (~15-30 LOC) but Arrow's columnar layout aligns perfectly with DataSet expectations.

**Evidence**: pyarrow.ipc documentation confirms memory-mapped reads and zero-copy numpy conversion (https://arrow.apache.org/docs/python/ipc.html). Polars documentation states Arrow IPC as native format (https://pola-rs.github.io/polars/py-polars/html/reference/io.html). to_pandas() performance analysis shows zero-copy for numeric types.

**Deserialization Code Requirement**: Minimal. Arrow IPC → NumPy/Pandas/Polars all have direct pathways. Memory mapping enables efficient random access. DataSet wrapper straightforward due to columnar alignment.

**Conclusion**: All 4 target formats supported with excellent zero-copy characteristics. Polars integration is optimal (Arrow-native). NumPy/Pandas trivial. DataSet requires thin wrapper but columnar alignment is clean.