---
scope: Relay service (relay/python/rowdog.py). All channels with decimation.enabled=true in schema config. Requires multicast group reservation for dual streams.
kind: system
content_hash: baf0eed3936f9bb7d0b6b2df834c767f
---

# Hypothesis: Relay-Side Decimation with Dual Multicast

Implement decimation in relay service before multicast transmission. Relay subscribes to incoming UDP on per-channel ports, applies configurable decimation algorithm (loaded from config/agents/*.avsc extensions), and publishes TWO multicast streams per channel:
- Full-rate multicast (224.0.0.X:portA) for archival subscribers
- Decimated multicast (224.0.0.X:portB) for visualization subscribers

Decimation config in schema files:
```json
{
  "decimation": {
    "enabled": true,
    "factor": 50,
    "algorithm": "average",
    "output_rate_hz": 100
  }
}
```

Algorithms: downsample (every Nth), average (mean), min-max (envelope), RMS. Per-channel configuration. Relay writes full-rate AVRO to disk unchanged.

## Rationale
{"anomaly": "No decimation exists, visualization needs lower-rate data", "approach": "Centralize decimation in relay to avoid duplicate logic in multiple consumers", "alternatives_rejected": ["Single multicast with mixed rates (breaks per-channel isolation)", "Consumer-side decimation (duplicates logic, wastes bandwidth)"]}