---
scope: SpeedData pivot component (catcol.py and successors). Python implementation. Linux/Raspberry Pi deployment. v0.2-v0.3 roadmap timeframe (February-March 2025).
kind: episteme
content_hash: bd82bd1e6e65e1cb8ef45d1b5b6eca45
---

# Hypothesis: Pivot Disk Serialization Format Decision

Decision problem: Select optimal disk serialization format for SpeedData pivot storage layer. Pivot transforms row-based AVRO relay data into column-oriented files for analysis. Requirements: time-range queries (30-60s windows), multi-channel aggregation (2-100 channels), column-oriented storage, file-based output, integration with Roelle DataSet, human-initiated tagging workflow.

## Rationale
{"anomaly": "Need to verify HDF5 (current plan) is optimal for pivot storage use case", "approach": "Evaluate alternatives systematically through FPF process", "alternatives_rejected": []}