---
scope: Microcontrollers with network stack, 5000 Hz sampling, 10-100 fields, preset data model
kind: system
content_hash: 1127752619126d24b6eaa2affb4ae8db
---

# Hypothesis: Preset Schema with REST Self-Registration

Use AVRO with preset schemas negotiated before data transmission. Remote agents register via REST API on boot, uploading their schema definition. Relay validates schema compatibility and assigns agent ID. Agents pack data manually in hot loop using pre-generated schema structs.

**Schema Model**: Preset, validated on registration  
**Registration**: REST API (`POST /agents/register` with schema payload)  
**Hot Loop**: Manual packing into AVRO binary format using schema structs  
**Microcontroller Friendliness**: Agents generate schema once, pack manually (no runtime schema overhead)  
**Evolution**: Versioned schemas, backward compatibility enforced at registration  

**Pros**:
- Zero runtime overhead for schema (preset)
- REST is standard, easy for sophisticated senders
- Schema validation at boundary prevents bad data
- AVRO binary format is compact and efficient

**Cons**:
- REST requires network stack on microcontroller (may not be available)
- Manual AVRO packing error-prone for barely-programmers
- Preset schema limits runtime flexibility
- Registration failure blocks data transmission

## Rationale
{
  "anomaly": "Current naive packing may be too dumb, need structured serialization with schema enforcement",
  "approach": "Conservative: keep AVRO, add REST registration for schema validation",
  "alternatives_rejected": "Self-describing formats (too much overhead per packet), dynamic schema discovery (unreliable)"
}