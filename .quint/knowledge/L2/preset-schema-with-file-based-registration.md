---
scope: Microcontrollers without REST capability, 5000 Hz sampling, static agent population
kind: system
content_hash: a9e672d94ae34a0f052885108c1620b3
---

# Hypothesis: Preset Schema with File-Based Registration

Use AVRO with preset schemas defined in configuration files. Remote agents are pre-registered via config files on relay system (edited manually or via web UI). Agents send data with agent ID in header. No runtime registration - agents assumed to boot and send immediately.

**Schema Model**: Preset, defined in relay config files  
**Registration**: Configuration files (`/config/agents/{agent_id}.avsc`) edited manually or via web UI  
**Hot Loop**: Manual packing into AVRO binary with agent ID prefix  
**Microcontroller Friendliness**: Zero registration protocol, just send data with ID  
**Evolution**: Manual schema updates in config, requires relay restart  

**Pros**:
- Zero registration overhead - agents just boot and send
- No network stack required on microcontroller
- Simple for barely-programmers (just pack and send)
- Relay-side schema management

**Cons**:
- Manual config editing error-prone
- Schema changes require relay restart
- Agent ID assignment must be coordinated manually
- No runtime schema validation - bad data silently dropped

## Rationale
{
  "anomaly": "Not all microcontrollers have network stack for REST registration",
  "approach": "Conservative: preset schemas via config files, zero-registration protocol",
  "alternatives_rejected": "REST registration (not available on all microcontrollers), dynamic discovery (unreliable for hot loop)"
}