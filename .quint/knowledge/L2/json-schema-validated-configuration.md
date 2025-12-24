---
kind: system
scope: SpeedData v0.3 all services. Teams that value strict validation and tooling support. Suitable for production deployments where config errors must be caught early.
content_hash: 862642a08ef8ae4cbe997a521fce1511
---

# Hypothesis: JSON Schema-Validated Configuration

JSON-based configuration with formal schema validation and strict error checking.

**File Structure:**
```json
{
  "relay": {
    "channels": [
      {
        "name": "ch1",
        "port": 5001,
        "schema": "config/agents/channel1.avsc"
      }
    ],
    "multicast": {
      "full_rate": {"address": "239.1.1.1", "port": 6000},
      "decimated": {"address": "239.1.1.2", "port": 6001}
    },
    "storage": {
      "path": "/var/speeddata/avro",
      "rotation": {"mode": "time", "threshold": 3600},
      "retention": {"mode": "ttl", "value": 86400}
    }
  },
  "stripchart": {
    "multicast": {
      "subscribe": {"address": "239.1.1.2", "port": 6001}
    },
    "websocket": {"port": 8080}
  },
  "pivot": {
    "storage": {"path": "/var/speeddata/avro"},
    "api": {
      "port": 8000,
      "limits": {"max_channels": 20, "max_duration_minutes": 5}
    }
  }
}
```

**JSON Schema (speeddata-config.schema.json):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["relay", "stripchart", "pivot"],
  "properties": {
    "relay": {
      "type": "object",
      "required": ["channels", "multicast", "storage"],
      "properties": {
        "channels": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "port", "schema"],
            "properties": {
              "name": {"type": "string"},
              "port": {"type": "integer", "minimum": 1024, "maximum": 65535},
              "schema": {"type": "string"}
            }
          }
        },
        "multicast": {
          "type": "object",
          "required": ["full_rate", "decimated"],
          "properties": {
            "full_rate": {"$ref": "#/definitions/endpoint"},
            "decimated": {"$ref": "#/definitions/endpoint"}
          }
        }
      }
    }
  },
  "definitions": {
    "endpoint": {
      "type": "object",
      "required": ["address", "port"],
      "properties": {
        "address": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+\\.\\d+$"},
        "port": {"type": "integer", "minimum": 1024, "maximum": 65535}
      }
    }
  }
}
```

**Validation:**
- Python: `jsonschema` library validates on load
- Services fail-fast with detailed validation errors (field path, constraint violated)
- Schema evolution tracked in version control
- Cross-field validation (e.g., relay.multicast.decimated == stripchart.multicast.subscribe)

**Discovery:**
- CLI arg: `--config path/to/speeddata.json --schema path/to/schema.json`
- ENV vars: `SPEEDDATA_CONFIG`, `SPEEDDATA_SCHEMA`
- Default: `./speeddata.json` + `./speeddata-config.schema.json`

**Tooling:**
- JSON schema generators for IDE autocomplete
- Pre-commit hooks validate config against schema
- Config diff tools for deployment validation

## Rationale
{"anomaly": "Config errors (typos, invalid ports, missing fields) cause runtime failures. Need fail-fast validation.", "approach": "Formal JSON Schema provides machine-verifiable contract. Strict validation prevents deployment of invalid configs.", "alternatives_rejected": ["YAML without schema (no formal validation)", "Runtime validation only (errors discovered late)", "Python config files (executable code is security risk)"]}