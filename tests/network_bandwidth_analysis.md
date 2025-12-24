# Network Bandwidth Analysis: Relay vs Server Decimation

## Scenario: Single NIC System

### Assumptions
- **Data rate**: 5000 Hz per channel
- **Fields per sample**: 100
- **Bytes per field**: 8 (double precision)
- **Number of channels**: 10 (moderate load)
- **Decimation factor**: 50x (5000 Hz → 100 Hz)

### Bandwidth Calculations

#### Relay-Side Decimation (Dual Multicast)

**Incoming UDP (from sensors):**
- Per channel: 5000 samples/sec × 100 fields × 8 bytes = 4 MB/sec
- Total (10 channels): 40 MB/sec

**Outgoing Multicast:**
- Full-rate stream (archival): 40 MB/sec
- Decimated stream (viz): 0.8 MB/sec (40 MB / 50)
- **Total outgoing: 40.8 MB/sec**

**Total NIC Load: 40 MB/sec (in) + 40.8 MB/sec (out) = 80.8 MB/sec**

---

#### Server-Side Decimation (Single Multicast)

**Incoming UDP (from sensors to relay):**
- 40 MB/sec

**Relay → Server Multicast:**
- Full-rate stream: 40 MB/sec

**Server → Frontend WebSocket:**
- Decimated stream: 0.8 MB/sec

**Total NIC Load (relay): 40 MB/sec (in) + 40 MB/sec (out) = 80 MB/sec**
**Total NIC Load (server): 40 MB/sec (in) + 0.8 MB/sec (out) = 40.8 MB/sec**

---

## Bottleneck Analysis

### Single-Machine Deployment (Relay + Server on same host)

**Relay-Side Decimation:**
- Loopback traffic (relay → server): 40.8 MB/sec (does NOT use NIC)
- NIC usage: 40 MB/sec (in) + 40.8 MB/sec (out to external clients) = 80.8 MB/sec
- **Risk: MODERATE** - NIC saturation at ~800 Mbps (10% of 1 Gbps NIC)

**Server-Side Decimation:**
- Loopback traffic (relay → server): 40 MB/sec (does NOT use NIC)
- NIC usage: 40 MB/sec (in) + 0.8 MB/sec (out to external clients) = 40.8 MB/sec
- **Risk: LOW** - NIC saturation at ~320 Mbps (3.2% of 1 Gbps NIC)

**Winner: Server-Side** (saves 40 MB/sec of outgoing bandwidth)

---

### Multi-Machine Deployment (Relay and Server on different hosts)

**Relay-Side Decimation:**
- Relay NIC: 40 MB/sec (in) + 40.8 MB/sec (out) = 80.8 MB/sec
- Server NIC: 40.8 MB/sec (in) + 0.8 MB/sec (out) = 41.6 MB/sec
- **Relay becomes bottleneck**

**Server-Side Decimation:**
- Relay NIC: 40 MB/sec (in) + 40 MB/sec (out) = 80 MB/sec
- Server NIC: 40 MB/sec (in) + 0.8 MB/sec (out) = 40.8 MB/sec
- **Relay becomes bottleneck** (only 0.8 MB/sec savings)

**Winner: Server-Side** (marginal improvement, but relay is bottleneck in both)

---

## IPC Alternative (Single-Machine Deployment)

If relay and server use Unix domain sockets instead of multicast:

**Server-Side Decimation with IPC:**
- Relay NIC: 40 MB/sec (in) + 0 MB/sec (IPC, no NIC) = 40 MB/sec
- Server NIC: 0 MB/sec (IPC, no NIC) + 0.8 MB/sec (out) = 0.8 MB/sec
- **Total NIC Load: 40.8 MB/sec** (optimal)

**Relay-Side Decimation with IPC:**
- Relay NIC: 40 MB/sec (in) + 0 MB/sec (IPC, no NIC) = 40 MB/sec
- Server NIC: 0 MB/sec (IPC, no NIC) + 0.8 MB/sec (out) = 0.8 MB/sec
- **Total NIC Load: 40.8 MB/sec** (same as server-side)

**Winner: TIE** - IPC eliminates the multicast bandwidth difference

---

## Rust Performance Impact

Current benchmark: Python relay with 0.4% CPU overhead for decimation.

**Rust relay expectations:**
- 10-100x faster than Python for numerical operations
- Decimation overhead: 0.004% - 0.04% CPU (negligible)
- Network I/O becomes dominant cost, not decimation

**Conclusion:** Decimation performance is NOT the bottleneck in compiled relay. Network bandwidth IS the bottleneck.

---

## Recommendations

### Single-Machine Deployment
1. **If using multicast (current architecture):** Server-side decimation saves 40 MB/sec NIC bandwidth
2. **If switching to IPC:** Both approaches are equivalent - choose based on separation of concerns

### Multi-Machine Deployment
Server-side decimation has marginal benefit (0.8 MB/sec savings), but relay NIC is bottleneck in both cases.

### Future Rust Relay
Network bandwidth, not CPU, will be the limiting factor. Choose architecture based on:
- Separation of concerns (server-side wins)
- Deployment flexibility (relay-side supports multiple independent servers)
