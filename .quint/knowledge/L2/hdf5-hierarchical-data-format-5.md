---
scope: SpeedData pivot storage. 2-100 channels per export. Time windows 30-60 seconds typical. Python 3.x environment. Linux/Raspberry Pi deployment. File sizes 10KB-100MB estimated.
kind: system
content_hash: 227a89b7e3f89940073c50460274a824
---

# Hypothesis: HDF5 (Hierarchical Data Format 5)

Use HDF5 as disk serialization format for pivot storage. Implementation: Python h5py library. Structure: Signal → dataset, Channel → group, Set → file (per README lines 30, 35, 41). Time-range queries via timestamp indexing. Multi-channel aggregation via multiple groups in single file. Column-oriented via dataset-per-signal layout. Integration with Roelle DataSet via h5py read operations (v0.2 roadmap). Existing catcol.py proof-of-concept demonstrates feasibility.

## Rationale
{"anomaly": "Need disk format for time-range exports with multi-channel aggregation", "approach": "HDF5 provides hierarchical structure (groups/datasets), native column-oriented storage, scientific computing maturity, proven in catcol.py", "alternatives_rejected": []}