---
scope: All services (relay, stripchart, frontend). Requires shared decimation library (lib/python/ for Python services, lib/js/ for Node/browser). Plugin discovery and loading mechanism.
kind: system
content_hash: bf70c3ac6194e2b276d720aea1c0e6d4
---

# Hypothesis: Plugin-Based Decimation Framework with Runtime Selection

Implement decimation as pluggable modules that can run in ANY service (relay/server/frontend) via runtime configuration. Create abstract decimation interface with algorithm plugins.

**Core Framework:**
```python
# lib/python/decimation.py
class DecimationPlugin:
    def process(self, samples, factor): pass

class DownsamplePlugin(DecimationPlugin): ...
class AveragePlugin(DecimationPlugin): ...
class MinMaxPlugin(DecimationPlugin): ...
class RMSPlugin(DecimationPlugin): ...
```

**Runtime Config (config/decimation.yaml):**
```yaml
pipelines:
  - name: high_rate_viz
    location: stripchart_server  # or: relay, frontend
    channels: [high_rate, ultra_rate]
    algorithm: min-max
    input_hz: 5000
    output_hz: 100
  - name: network_optimization
    location: relay
    channels: [*]
    algorithm: downsample
    factor: 10
```

Each service loads applicable pipeline configs at startup. Plugins registered in plugin directory. New algorithms added without service code changes. Location can be moved via config without code refactor.

## Rationale
{"anomaly": "Architecture choice is uncertain - need flexibility to experiment and migrate decimation location", "approach": "Decouple algorithm from location, enable A/B testing of different placements via config", "alternatives_rejected": ["Hard-coded location (cannot experiment)", "Duplicate implementations per service (maintenance burden)", "No abstraction (algorithm changes require code changes in multiple services)"]}