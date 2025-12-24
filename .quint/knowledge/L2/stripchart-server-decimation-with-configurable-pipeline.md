---
scope: Stripchart server service (stripchart/server/server.js). All channels requiring visualization decimation. Does not affect relay or archival data path.
kind: system
content_hash: a099885a0133dd9f12b166318cfa2bc6
---

# Hypothesis: Stripchart Server Decimation with Configurable Pipeline

Implement decimation in stripchart server (stripchart/server/server.js) after receiving full-rate multicast but before WebSocket transmission. Server subscribes to single full-rate multicast per channel, applies decimation pipeline, publishes decimated data over WebSocket to frontend clients.

Configuration in stripchart/config/decimation.json:
```json
{
  "channels": {
    "high_rate": {
      "algorithm": "min-max",
      "factor": 50,
      "output_hz": 100
    },
    "medium_rate": {
      "algorithm": "average",
      "factor": 10,
      "output_hz": 10
    }
  }
}
```

Pipeline stages: receive multicast → buffer N samples → apply algorithm → emit to WebSocket. Algorithms: downsample, average, min-max envelope, RMS. Hot-reload config without restart. Relay unchanged (single multicast stream).

## Rationale
{"anomaly": "No decimation exists, browsers cannot render 5000 Hz WebSocket streams", "approach": "Decouple decimation from relay (single responsibility), apply transformation at visualization boundary", "alternatives_rejected": ["Relay decimation (couples relay to visualization requirements)", "Frontend decimation (wastes WebSocket bandwidth, duplicates logic per client)"]}