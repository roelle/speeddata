---
scope: Any Linux kernel 3.10+. Optimized for systems with 2-20 channels. Works on Raspberry Pi (low memory per relay) and Xeon (many channels in parallel). Each relay is independent process.
kind: system
content_hash: 8c23e39eaf3f1c0017e6600a342a8223
---

# Hypothesis: Per-Channel Relay Fleet (Zig + Direct I/O)

Separate relay process per channel with lightweight orchestrator for lifecycle management.

**Architecture:**
- Single relay binary written in Zig (compiles to tiny static executable ~100KB)
- Each instance handles one channel:
  - Single UDP socket (one port)
  - Direct file I/O with O_DIRECT flag (bypass page cache)
  - Two multicast sockets (full-rate + decimated)
  - Simple synchronous event loop (no async complexity)
- Python orchestrator (speeddata-relay-manager):
  - Reads config/relay.yaml
  - Spawns/supervises relay processes via subprocess
  - Handles SIGHUP for config reload
  - Implements retention policy (cleanup old files)

**I/O Flow:**
1. recvfrom() UDP packet into aligned buffer (4KB for O_DIRECT)
2. Immediate multicast relay (zero-copy sendto)
3. Append to AVRO file with O_DIRECT write
4. Decimation in same process (simple buffer + counter)

**Channel Management:**
- Dynamic: orchestrator can spawn/kill relay processes
- Isolation: channel crash doesn't affect others
- Resource limits: cgroups per process (CPU/memory)

**Trade-offs:**
+ Simple per-relay code (no async, no shared state)
+ Fault isolation (one channel failure doesn't cascade)
+ Easy to reason about (single-threaded per relay)
+ Zig's comptime eliminates runtime overhead
+ Works on older kernels (no io_uring dependency)
+ Easy horizontal scaling (relay per core if needed)
- More processes (higher memory overhead per channel)
- Python orchestrator adds dependency
- O_DIRECT requires aligned I/O (complexity)
- IPC needed if relays need to coordinate

## Rationale
{
  "anomaly": "Monolithic relay creates single point of failure and complex async code",
  "approach": "Embrace Unix philosophy: one process per channel, orchestrated. Zig provides C-level performance with better safety than C. O_DIRECT bypasses page cache for predictable latency.",
  "alternatives_rejected": [
    "Go with goroutines (GC pauses unacceptable for real-time)",
    "C with fork() (more complex than Zig, harder to maintain)"
  ]
}