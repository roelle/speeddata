---
target: stripchart-server-decimation-with-configurable-pipeline
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-internal-stripchart-server-decimation-with-configurable-pipeline.md
type: internal
content_hash: 31c1794d7c18d8438a802cb8816eaf74
---

**Performance Benchmark (tests/benchmark_nodejs_decimation.js):**
- Light load (5 channels, 3 clients): 0.1% CPU overhead
- Medium load (20 channels, 10 clients): 0.8% CPU overhead  
- Heavy load (100 channels, 20 clients): 6.0% CPU overhead

All scenarios well below 50% threshold. Node.js event loop can handle decimation without blocking.

**Implementation Feasibility:**
- Current server.js is 83 lines
- Adding decimation pipeline requires:
  1. Load decimation config from JSON (~10 lines)
  2. Create circular buffer per channel (~20 lines)
  3. Implement decimation algorithms (~30 lines)
  4. Modify UDP message handler to buffer/decimate (~15 lines)
  5. Hot-reload config on file change (~15 lines)
- Estimated implementation: ~90 LOC addition

**Separation of Concerns Validation:**
- Relay responsibility: receive UDP, write to disk, multicast
- Server responsibility: subscribe to multicast, process for visualization, serve WebSocket
- Decimation is visualization processing concern → belongs in server layer ✓

**Architectural Research:**
- Layered architecture separates presentation (WebSocket/frontend), business logic (decimation), and data access (multicast subscription)
- "Backend manages data processing... keeping it separate from presentation layer" - applies to decimation as visualization preprocessing
- Service isolation maintains clean boundaries between relay (data ingestion) and stripchart (visualization)

**Configuration Management:**
- Separate JSON config file: stripchart/config/decimation.json
- Hot-reload via fs.watch() in Node.js - no server restart required
- Per-channel algorithm selection enables flexibility

**Sources:**
- [Separation of Concerns in Software Design](https://nalexn.github.io/separation-of-concerns)
- [Layered Architecture](https://www.geeksforgeeks.org/separation-of-concerns-soc/)
- [Software Architecture Patterns 2024](https://www.sayonetech.com/blog/software-architecture-patterns/)

**Conclusion:** Performance validated, implementation feasible, architecturally sound separation of concerns.