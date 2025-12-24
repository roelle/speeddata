---
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-custom-columnar-binary-format.md
type: external
target: custom-columnar-binary-format
content_hash: 955236ca7bb84df1775b463071df2bcc
---

Custom Columnar Binary Format Integration Analysis:

**NumPy Arrays**: Direct target. Custom reader unpacks struct-encoded binary arrays into numpy.ndarray. Example: `header = struct.unpack('...', f.read(header_size)); signal_data = np.frombuffer(f.read(signal_size), dtype=np.float64)`. np.frombuffer() enables zero-copy reads from memory-mapped files.

**Pandas**: Custom reader → numpy → pd.DataFrame(). Two-step process: binary → numpy arrays → DataFrame constructor. Example: `df = pd.DataFrame({'voltage': read_signal_array('voltage'), 'timestamp': read_signal_array('timestamp')})`.

**Polars**: Custom reader → numpy → pl.DataFrame() or direct pl.from_numpy(). Same two-step process as Pandas. Polars accepts dict of numpy arrays in constructor.

**Roelle DataSet**: Custom reader outputs numpy arrays directly consumable by DataSet. Integration requires implementing reader module (~50-100 LOC as noted in hypothesis) with functions: read_header(), read_signal_block(), get_channel_list(), read_time_range(). Once implemented, DataSet integration is clean.

**Evidence**: Python struct module documentation confirms binary unpacking capabilities (https://docs.python.org/3/library/struct.html). numpy.frombuffer() documentation shows zero-copy array creation from binary buffers (https://numpy.org/doc/stable/reference/generated/numpy.frombuffer.html). Custom format means no external documentation - reliance on implementation correctness.

**Deserialization Code Requirement**: High. Entire reader module must be implemented (~50-100 LOC). No ecosystem tooling - debugging requires custom scripts. Format versioning, schema evolution, corruption detection all manual. However, once implemented, NumPy/Pandas/Polars/DataSet integration is straightforward via numpy intermediate.

**Conclusion**: All 4 target formats supported BUT requires implementing complete custom reader module first. NumPy is natural target (zero-copy frombuffer). Pandas/Polars trivial once numpy arrays available. DataSet integration clean but reader module is significant implementation burden. Trade-off: Full control vs development/maintenance cost.