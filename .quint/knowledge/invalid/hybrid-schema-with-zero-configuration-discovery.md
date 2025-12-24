---
scope: Microcontrollers with simple UDP send, 5000 Hz sampling, dynamic agent population
kind: system
content_hash: 7254f2e904c97077b977112ccd848da9
---

# Hypothesis: Hybrid Schema with Zero-Configuration Discovery

Use hybrid approach: first packet from agent is self-describing (contains schema), subsequent packets use compact binary format with schema ID. Relay caches schema on first receive, assigns schema ID, sends acknowledgment. Agent switches to compact mode using schema ID.

**Schema Model**: Hybrid - self-describing on first packet, preset thereafter  
**Registration**: Implicit via first packet (zero-configuration)  
**Hot Loop**: After first packet, use schema ID + compact binary (AVRO or custom)  
**Microcontroller Friendliness**: Zero registration protocol, auto-discovery  
**Evolution**: New schema = new first packet, automatic versioning  

**Pros**:
- Zero-configuration - agents auto-register on first send
- No REST/network stack required
- Schema evolution built-in (new schema = new first packet)
- Hot loop uses compact format (only first packet has overhead)

**Cons**:
- First packet is large (contains schema)
- Relay must handle race conditions (multiple agents, same schema)
- More complex protocol (first packet vs subsequent)
- UDP loss of first packet blocks communication until retry

## Rationale
{
  "anomaly": "Registration protocols add complexity for barely-programmers, but preset schema limits flexibility",
  "approach": "Moderate: hybrid self-describing first packet, then compact binary",
  "alternatives_rejected": "Full self-describing (too much overhead), pure REST (not available on all platforms)"
}