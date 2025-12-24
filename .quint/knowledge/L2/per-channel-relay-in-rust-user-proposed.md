---
scope: Linux systems with kernel 3.10+ (tokio compatible). Works on Raspberry Pi 3+ and Xeon servers. Each channel is independent Rust process. Best for 2-50 channel deployments.
kind: system
content_hash: 41105d95417ba5b877e0331bba2214c5
---

# Hypothesis: Per-Channel Relay in Rust (User Proposed)

Separate Rust process per channel combining Rust's safety with process isolation.

**Architecture:**
- Single Rust binary compiled to static executable
- Each instance handles one channel:
  - Single UDP socket (one port from config)
  - Async I/O using tokio runtime (single-threaded per process)
  - AVRO file writes with tokio::fs (async file I/O)
  - Two multicast sockets (full-rate + decimated)
  - Built-in decimation logic (async task)
- Python or shell-based orchestrator:
  - Reads config/relay.yaml
  - Spawns relay processes (one per channel definition)
  - Supervises with restart on crash
  - Handles SIGHUP for config reload

**I/O Flow:**
1. tokio UDP socket recv_from() → packet into buffer
2. Immediate multicast relay via send_to() (both streams)
3. Decimation in separate async task (doesn't block recv)
4. tokio::fs write to AVRO file (async, kernel buffered)
5. Periodic flush for durability

**Channel Management:**
- Dynamic: orchestrator spawns/kills processes on config change
- Isolation: each channel is independent process
- Resource limits: can use cgroups/systemd for per-channel limits
- Logging: each process logs independently (easier debugging)

**Trade-offs:**
+ Rust safety guarantees (no memory corruption, data races)
+ Process isolation (channel crash doesn't affect others)
+ Simpler than monolithic async (each relay is single-channel)
+ Good performance with tokio async I/O
+ Familiar to Rust developers
+ Works on Linux 3.10+ (no io_uring requirement)
+ Static binary deployment (no runtime dependencies)
- More memory than threads (each process has own heap)
- No shared memory optimization for decimation
- Orchestrator needed (Python dependency)
- More processes to manage than monolithic approach
- tokio async still has learning curve (but simpler than io_uring)

## Rationale
{
  "source": "User input",
  "anomaly": "Need compiled language performance with fault isolation benefits",
  "approach": "Combine Rust's memory safety with per-channel process model. User specifically requested this combination.",
  "note": "Manually injected via /q1-add. Bridges safety of Rust (#1) with isolation of per-process (#2)."
}