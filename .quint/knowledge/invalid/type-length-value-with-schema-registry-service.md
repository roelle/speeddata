---
scope: Microcontrollers with minimal resources, 5000 Hz sampling, barely-programmer simplicity priority
kind: system
content_hash: d820f70768850656531d412d7f4f50dc
---

# Hypothesis: Type-Length-Value with Schema Registry Service

Use custom TLV (Type-Length-Value) binary format optimized for hot loop. Separate schema registry service (part of relay) for schema management. Agents register via UDP announcement (schema in first N packets, repeated), relay caches and assigns schema ID. Data packets use schema ID + TLV fields.

**Schema Model**: Preset after announcement, custom TLV binary  
**Registration**: UDP announcement packets (repeated until ACK)  
**Hot Loop**: Schema ID (2 bytes) + TLV fields (1 byte type + 2 bytes length + value)  
**Microcontroller Friendliness**: Very simple - just pack bytes into TLV  
**Evolution**: Versioned schema IDs, backward compatibility via schema registry  

**Pros**:
- Minimal hot loop overhead (TLV is simplest binary format)
- UDP announcement avoids REST requirement
- Custom format optimized for 5000 Hz use case
- Easy to hand-code on microcontroller (just byte packing)

**Cons**:
- Custom format means custom tooling (no AVRO/Protobuf ecosystem)
- TLV less compact than AVRO for fixed schemas
- Schema registry adds service complexity
- Announcement retry logic on microcontroller

## Rationale
{
  "anomaly": "Standard serialization formats (AVRO, Protobuf) may be too complex for barely-programmers or too slow for hot loop",
  "approach": "Radical: custom TLV format optimized for microcontroller hot loop, schema registry service",
  "alternatives_rejected": "AVRO (complex manual packing), Protobuf (library overhead), JSON (too verbose)"
}