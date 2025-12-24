---
scope: SpeedData v0.3 all services. Single-machine deployment or shared filesystem. Suitable for simple deployments where all services on same host or NFS-mounted config.
kind: system
content_hash: 5faf4111c5e5a1290f7bdce59d268cc6
---

# Hypothesis: Single YAML File with Service Sections

Monolithic YAML configuration file with top-level sections for each service.

**File Structure:**
```yaml
# speeddata.yaml
relay:
  channels:
    - name: ch1
      port: 5001
      schema: config/agents/channel1.avsc
    - name: ch2
      port: 5002
      schema: config/agents/channel2.avsc
  
  multicast:
    full_rate:
      address: 239.1.1.1
      port: 6000
    decimated:
      address: 239.1.1.2
      port: 6001
  
  storage:
    path: /var/speeddata/avro
    rotation:
      mode: time  # or 'size'
      threshold: 3600  # seconds or bytes
    retention:
      mode: ttl  # or 'quota'
      value: 86400  # seconds or bytes

stripchart:
  multicast:
    subscribe:
      address: 239.1.1.2
      port: 6001
  websocket:
    port: 8080

pivot:
  storage:
    path: /var/speeddata/avro  # read-only
  api:
    port: 8000
    limits:
      max_channels: 20
      max_duration_minutes: 5
```

**Discovery:**
- CLI arg: `--config path/to/speeddata.yaml`
- ENV var: `SPEEDDATA_CONFIG`
- Default: `./speeddata.yaml`, `/etc/speeddata/speeddata.yaml`

**Validation:**
- Python: `pyyaml` + schema validation (cerberus, jsonschema)
- Services fail-fast on startup if config invalid
- YAML syntax errors produce clear error messages

**Cross-Service Consistency:**
- All services read same file
- Relay multicast.decimated must match stripchart subscribe
- Storage paths consistent between relay (write) and pivot (read)

## Rationale
{"anomaly": "Multiple services need coordinated configuration (multicast endpoints must match, storage paths must align)", "approach": "Single source of truth prevents config drift. YAML is human-readable, supports comments, widely understood.", "alternatives_rejected": ["Multiple config files (risk of inconsistent multicast endpoints)", "JSON (no comments, less human-friendly)", "Environment variables only (too many vars, no structure)"]}