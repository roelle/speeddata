---
kind: system
scope: Microcontrollers with sufficient flash/RAM for Protobuf, variable field counts, dynamic schemas
content_hash: 605a02ad9b7701816090173795232b24
---

# Hypothesis: Fully Self-Describing Protobuf with Inline Schema

Use Protocol Buffers with inline schema descriptors. Each packet contains schema hash + field descriptors for unknown schemas. Relay caches schemas by hash. No registration required - schemas travel with data.

**Schema Model**: Dynamic - self-describing per packet  
**Registration**: None - schemas embedded in wire format  
**Hot Loop**: Protobuf encoding with schema hash prefix  
**Microcontroller Friendliness**: Moderate - Protobuf libraries available but larger  
**Evolution**: Automatic - new schemas just work  

**Pros**:
- Zero registration complexity
- Schema evolution automatic
- Protobuf more efficient than AVRO for sparse data
- Strong typing, backward/forward compatibility

**Cons**:
- Protobuf encoding more complex than AVRO
- Schema descriptors add overhead (mitigated by hashing)
- Requires Protobuf library on microcontroller (larger footprint)
- 5000 Hz with 100 fields may hit encoding performance limits

## Rationale
{
  "anomaly": "Preset schemas require coordination, registration adds complexity",
  "approach": "Radical: self-describing wire format, zero registration",
  "alternatives_rejected": "AVRO preset (requires registration), JSON (too verbose for hot loop)"
}