---
date: 2025-12-23
id: 2025-12-23-external-hdf5-hierarchical-data-format-5.md
type: external
target: hdf5-hierarchical-data-format-5
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
content_hash: e091b15a8b96da31640ca5480e3f6aa1
---

HDF5 Integration Analysis:

**NumPy Arrays**: h5py provides direct numpy array interface via dataset slicing. Example: `data = f['channel1/voltage'][:]` returns numpy.ndarray. Zero-copy possible with memory mapping via h5py.File(mode='r', driver='core').

**Pandas**: pandas.read_hdf() for HDFStore format (PyTables-based), or manual h5py read + pd.DataFrame() constructor. Example: `df = pd.DataFrame({'voltage': f['channel1/voltage'][:], 'timestamp': f['channel1/timestamp'][:]})`

**Polars**: pl.DataFrame() constructor accepts numpy arrays. Two-step: h5py → numpy → polars. Example: `pl.DataFrame({'voltage': f['channel1/voltage'][:]})`

**Roelle DataSet**: Custom integration via h5py read operations. User's catcol.py proof-of-concept demonstrates HDF5 → DataSet pathway exists (README line 69, 120).

**Evidence**: h5py documentation confirms numpy compatibility (https://docs.h5py.org/en/stable/quick.html). Pandas HDFStore uses PyTables backend (different from raw HDF5 but compatible). Polars lacks native HDF5 reader but numpy bridge is trivial.

**Deserialization Code Requirement**: Minimal. h5py handles HDF5 → numpy automatically. Pandas/Polars wrappers are 1-5 lines per signal. DataSet integration requires custom module but user has working prototype.

**Conclusion**: All 4 target formats supported with minimal deserialization overhead. NumPy/Pandas have mature pathways. Polars requires numpy intermediate step. DataSet integration proven via catcol.py.