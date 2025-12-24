---
scope: SpeedData v0.3 all services. Multi-machine deployment where services run on different hosts. Each service only needs its own config file plus global.
kind: system
content_hash: 6dc6b9420169e8854c7fb9a4ce2f114b
---

# Hypothesis: Per-Service YAML Files with Shared Globals

Distributed configuration with per-service files plus shared global config.

**File Structure:**
```
config/
├── global.yaml          # Shared settings
├── relay.yaml           # Relay-specific
├── stripchart.yaml      # Stripchart-specific
└── pivot.yaml           # Pivot-specific
```

**global.yaml:**
```yaml
multicast:
  full_rate:
    address: 239.1.1.1
    port: 6000
  decimated:
    address: 239.1.1.2
    port: 6001

storage:
  avro_path: /var/speeddata/avro
```

**relay.yaml:**
```yaml
channels:
  - name: ch1
    port: 5001
    schema: config/agents/channel1.avsc
  - name: ch2
    port: 5002
    schema: config/agents/channel2.avsc

rotation:
  mode: time
  threshold: 3600

retention:
  mode: ttl
  value: 86400
```

**stripchart.yaml:**
```yaml
websocket:
  port: 8080
decimation:
  factor: 50
  algorithm: average
```

**pivot.yaml:**
```yaml
api:
  port: 8000
  limits:
    max_channels: 20
    max_duration_minutes: 5
```

**Discovery:**
- CLI arg: `--config-dir path/to/config/`
- ENV var: `SPEEDDATA_CONFIG_DIR`
- Default: `./config/`, `/etc/speeddata/`

**Loading Logic:**
1. Load global.yaml
2. Load service-specific YAML (relay.yaml, etc.)
3. Merge: service-specific overrides global
4. Services only load files they need

**Validation:**
- Each service validates only its own config
- Shared settings (multicast endpoints) validated by both publisher and subscribers
- Config drift detection: services warn if multicast mismatch detected at runtime

## Rationale
{"anomaly": "Services may run on different machines, monolithic config creates deployment complexity", "approach": "Separation of concerns - each service gets minimal config. Global file ensures consistency for shared settings (multicast).", "alternatives_rejected": ["No global file (duplicated multicast endpoints risk drift)", "Service autodiscovery (too complex for v0.3)", "Config server (over-engineered)"]}