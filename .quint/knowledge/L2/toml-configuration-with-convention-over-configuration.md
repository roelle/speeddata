---
kind: system
scope: SpeedData v0.3 all services. Single-machine or multi-machine deployments. Optimized for typical deployments where defaults work for 80% of settings. Users only configure what they need to change.
content_hash: 8ad965eff773d85f49bc1708beac8041
---

# Hypothesis: TOML Configuration with Convention-Over-Configuration

TOML-based configuration emphasizing sensible defaults and minimal required settings.

**File Structure:**
```toml
# speeddata.toml

# Global defaults (can be overridden per-service)
[defaults]
storage_path = "/var/speeddata/avro"
multicast_base = "239.1.1.0"  # Services auto-increment from base

# Relay configuration
[relay]
storage_path = "${defaults.storage_path}"  # Inherits default

[[relay.channels]]
name = "ch1"
port = 5001
schema = "config/agents/channel1.avsc"

[[relay.channels]]
name = "ch2"
port = 5002
schema = "config/agents/channel2.avsc"

[relay.multicast.full_rate]
address = "239.1.1.1"  # Explicit override
port = 6000

[relay.multicast.decimated]
address = "239.1.1.2"
port = 6001

[relay.rotation]
mode = "time"          # Options: "time" | "size"
threshold = 3600       # seconds if mode=time, bytes if mode=size

[relay.retention]
mode = "ttl"           # Options: "ttl" | "quota"
value = 86400          # seconds if mode=ttl, bytes if mode=quota

# Stripchart configuration
[stripchart]
# Minimal config - subscribes to relay.multicast.decimated by convention
websocket_port = 8080
decimation_factor = 50
decimation_algorithm = "average"  # Options: "downsample" | "average" | "minmax" | "rms"

# Pivot configuration
[pivot]
storage_path = "${defaults.storage_path}"  # Read-only, shared with relay
api_port = 8000

[pivot.limits]
max_channels = 20
max_duration_minutes = 5
timeout_seconds = 60
```

**Convention-Over-Configuration Rules:**
1. **Multicast Auto-Discovery:** Stripchart/pivot default to relay's decimated multicast (no duplicate config)
2. **Storage Path Sharing:** Pivot inherits relay storage path unless overridden
3. **Port Defaults:** Services use standard ports (relay=none, stripchart WS=8080, pivot API=8000)
4. **Schema Path Convention:** If not specified, schema defaults to `config/agents/{channel_name}.avsc`

**Discovery:**
- CLI arg: `--config path/to/speeddata.toml`
- ENV var: `SPEEDDATA_CONFIG`
- Default search path: `./speeddata.toml`, `~/.config/speeddata/speeddata.toml`, `/etc/speeddata/speeddata.toml`

**Variable Interpolation:**
- `${section.key}` references within config
- ENV var substitution: `${env:STORAGE_PATH}`
- Computed values: `address = "${defaults.multicast_base}/24"`

**Validation:**
- Python: `tomli` (read) + `tomli-w` (write) for parsing
- Custom validator checks cross-references (stripchart subscribes to relay publish)
- Warnings for deprecated fields, errors for required missing fields
- Type checking via annotations in parsing code

**Benefits:**
- **Minimal Config:** Only specify what differs from defaults
- **Strong Typing:** TOML supports integers, bools, dates natively (no string parsing)
- **Comments:** Like YAML, supports inline comments
- **Nested Sections:** Clear hierarchy with `[section.subsection]` syntax
- **Array Tables:** `[[relay.channels]]` naturally represents lists of objects

## Rationale
{"anomaly": "Verbose config files create maintenance burden. Most deployments use same settings except channel-port mappings.", "approach": "Convention-over-configuration reduces boilerplate. TOML provides strong typing without JSON verbosity. Variable interpolation DRYs up shared values.", "alternatives_rejected": ["INI format (no nesting, poor structure)", "Python ConfigParser (INI limitations)", "Environment variables only (no structure, 100+ vars for complex config)"]}