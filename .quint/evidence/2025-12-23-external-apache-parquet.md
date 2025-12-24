---
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-apache-parquet.md
type: external
target: apache-parquet
content_hash: e7cc01ca0ac79ff70a909520ae837b2f
---

Apache Parquet Integration Analysis:

**NumPy Arrays**: pyarrow.parquet.read_table().to_pandas() → df.to_numpy() OR pyarrow.parquet.read_table().column('signal').to_numpy(). Direct numpy conversion via Arrow → NumPy bridge.

**Pandas**: Native support via pandas.read_parquet(). Example: `df = pd.read_parquet('data.parquet')`. Supports row group filtering, column projection. Multiple backends: pyarrow (default), fastparquet.

**Polars**: Native Parquet reader via pl.read_parquet(). Example: `df = pl.read_parquet('data.parquet')`. Lazy evaluation for large files via pl.scan_parquet(). Predicate pushdown for time-range queries.

**Roelle DataSet**: Two pathways: (1) Parquet → Pandas → DataSet, or (2) Parquet → Arrow → numpy → DataSet. Both require custom integration module (~20-40 LOC wrapper).

**Evidence**: pyarrow documentation shows to_pandas() and to_numpy() methods (https://arrow.apache.org/docs/python/parquet.html). Pandas read_parquet() supports filters parameter for predicate pushdown. Polars scan_parquet() enables lazy columnar reads with time-range predicates.

**Deserialization Code Requirement**: Minimal for Pandas/Polars (native readers). NumPy requires 1-step conversion via Arrow or Pandas. DataSet integration needs wrapper module but standard Parquet ecosystem handles heavy lifting.

**Conclusion**: All 4 target formats supported with excellent ecosystem tooling. Pandas/Polars have best integration (native readers + predicate pushdown). NumPy trivial via Arrow bridge. DataSet requires thin wrapper.