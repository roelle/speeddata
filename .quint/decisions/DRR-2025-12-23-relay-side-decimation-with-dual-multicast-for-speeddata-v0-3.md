---
type: DRR
winner_id: relay-side-decimation-with-dual-multicast
created: 2025-12-23T13:08:21-08:00
content_hash: 799991f38274e537094c68088086f041
---

# Relay-Side Decimation with Dual Multicast for SpeedData v0.3

## Context
SpeedData v0.3 requires decimation architecture to reduce 5000 Hz high-rate telemetry to ~100 Hz for browser visualization. Multiple deployment scenarios exist: single-machine (relay + server co-located) and multi-machine (separate hosts). Future v0.4 will migrate relay to Rust/compiled language for performance. Network bandwidth is a critical constraint, especially on systems with single NIC.

README line 164 explicitly flagged this as requiring FPF architectural decision: where to decimate (relay/server/frontend), algorithm selection, per-channel configuration, and dual-output strategy for visualization vs archival streams.

## Decision
**Selected Option:** relay-side-decimation-with-dual-multicast

Adopt relay-side decimation with dual multicast streams for SpeedData v0.3 decimation architecture.

**Implementation:**
- Relay applies configurable decimation algorithms (downsample, average, min-max, RMS) before multicast transmission
- Dual multicast output: full-rate stream (224.0.0.X:portA) for archival, decimated stream (224.0.0.X:portB) for visualization
- Per-channel configuration via AVRO schema extensions
- Relay writes full-rate AVRO to disk unchanged (archival path unaffected)

## Rationale
**Why This Decision:**

**1. Multi-Server Support**
User selected relay-side approach, likely prioritizing the ability to support multiple independent stripchart servers subscribing to separate multicast streams. Dual multicast enables:
- Multiple visualization clients with different decimation needs
- Independent server instances without coordination
- Broadcast efficiency (one decimation, N subscribers)

**2. Performance Validated (R_eff = 1.00)**
- Empirical benchmark: 0.4% CPU overhead (Python relay)
- All algorithms (downsample/average/min-max/RMS) well below 10% threshold
- Hot loop performance risk: LOW (mitigated by testing)
- Future Rust migration: 0.004% overhead (negligible)

**3. Centralized Processing**
- Single decimation point for all consumers (no duplicate logic)
- Consistent decimation across multiple visualization clients
- Relay controls data quality at source

**4. Trade-offs Accepted**

**Network Bandwidth Cost (Known Risk):**
- Single-machine multicast: 80.8 MB/sec NIC load (vs 40.8 MB/sec for server-side)
- Doubles outgoing multicast bandwidth (full-rate + decimated streams)
- At 100 channels: ~8 Gbps (exceeds 1 Gbps NIC capacity)
- Mitigations:
  - IPC for single-machine deployments (eliminates bandwidth penalty)
  - Multi-machine deployments likely have dedicated network segments
  - Network upgrade path available if needed

**Separation of Concerns (Accepted Coupling):**
- Relay handles both ingestion AND visualization preprocessing
- Couples relay to visualization requirements
- Alternative view: Relay provides multiple data products (full-rate archival, decimated visualization)

**v0.4 Rust Migration (Known Burden):**
- Decimation logic must be ported from Python to Rust
- ~40 LOC addition in Rust (straightforward port)
- But: CPU overhead becomes negligible in Rust, validating that network is true bottleneck

**5. R_eff Comparison**
Both hypotheses achieved R_eff = 1.00 based on internal testing (CL3). Decision based on qualitative factors:
- Multi-server architecture support (relay-side advantage)
- Network bandwidth efficiency (server-side advantage)
- User prioritized multi-server support

### Characteristic Space (C.16)
**Deployment Flexibility:** HIGH - Supports single-machine and multi-machine deployments, IPC and multicast transports

**Network Efficiency:** MODERATE - Doubles multicast bandwidth but mitigable via IPC

**Separation of Concerns:** MODERATE - Couples relay to visualization but provides multiple data products

**Implementation Complexity:** LOW - 40 LOC addition, straightforward algorithms

**Performance:** HIGH - 0.4% CPU overhead (Python), 0.004% (Rust)

**Maintainability:** MODERATE - Decimation logic in relay, v0.4 Rust migration required

**Scalability:** MODERATE - Network bandwidth limited at high channel counts

**Multi-Server Support:** HIGH - Dual multicast enables independent server instances

## Consequences
**Immediate Actions (v0.3 Implementation):**

1. **Relay Enhancement (~40 LOC)**
   - Import numpy for decimation algorithms
   - Load decimation config from AVRO schema extensions (config/agents/*.avsc)
   - Implement decimation functions: downsample, average, min-max, RMS
   - Create second multicast socket for decimated stream
   - Send to dual multicast groups (full-rate + decimated)

2. **Schema Extensions**
   - Add decimation configuration to AVRO schema files:
     ```json
     {
       "decimation": {
         "enabled": true,
         "factor": 50,
         "algorithm": "min-max",
         "output_rate_hz": 100,
         "multicast_group": "224.0.0.2",
         "multicast_port": 26002
       }
     }
     ```

3. **Network Configuration**
   - Reserve multicast groups: full-rate (224.0.0.1), decimated (224.0.0.2+)
   - Document port-per-channel assignments
   - Plan for multicast group exhaustion at scale

4. **Documentation**
   - Update README with dual multicast architecture
   - Document decimation algorithm selection guidelines
   - Create "Adding Decimated Channel" guide

**Operational Impacts:**

5. **Single-Machine Deployments**
   - Option A (Multicast): 80.8 MB/sec NIC load - acceptable for <20 channels
   - Option B (IPC): Switch to Unix domain sockets for relay→server communication
     - Eliminates 40 MB/sec multicast overhead
     - Implementation: Add IPC transport option to relay/server
     - Preserves dual-output architecture (IPC can multiplex streams)

6. **Multi-Machine Deployments**
   - Relay NIC becomes bottleneck at ~80 MB/sec
   - Acceptable for moderate channel counts (<50 channels at 5000 Hz)
   - Network upgrade path: dedicated 10 Gbps NIC for telemetry

7. **Monitoring**
   - Add NIC bandwidth metrics to relay monitoring
   - Alert on >80% NIC saturation
   - Per-channel decimation performance metrics

**Future Roadmap:**

8. **v0.4 Rust Migration (April 2025)**
   - Port decimation algorithms to Rust (~40 LOC)
   - CPU overhead becomes negligible (0.004%)
   - Validates network bandwidth as true bottleneck
   - Consider: Rust relay could support IPC natively (zero-copy shared memory)

9. **v0.5+ Optimization (If Needed)**
   - If network bottleneck proven in production: add IPC option
   - If multi-server support unused: reconsider server-side decimation
   - Evidence-driven decision: measure actual bandwidth usage

**Risks and Mitigations:**

10. **Network Saturation Risk**
    - Risk: High channel counts (>50) on single 1 Gbps NIC
    - Mitigation: IPC for single-machine, network upgrade for multi-machine
    - Monitoring: NIC bandwidth alerting

11. **Schema Coupling Risk**
    - Risk: Decimation config in data schema couples concerns
    - Mitigation: Document as "data product specification" not just schema
    - Future: v0.5 could separate decimation config if needed

12. **Multi-Server Coordination Risk**
    - Risk: Multiple servers with different decimation needs
    - Mitigation: Dual multicast already provides two streams
    - Future: Additional decimation factors could add more multicast streams if needed

**Non-Consequences (Explicitly Out of Scope):**

- ❌ Frontend decimation (rejected in Phase 2 - WebSocket bandwidth waste)
- ❌ Multi-tier cascading (rejected in Phase 2 - over-engineered)
- ❌ Plugin framework (rejected in Phase 2 - YAGNI violation)
- ❌ Dynamic decimation factor changes (static config in v0.3)
- ❌ Algorithm selection per client (single algorithm per channel in v0.3)
