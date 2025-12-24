---
scope: Linux systems with kernel 5.10+ (io_uring support). Suitable for dedicated relay servers (Xeon class) but also works on Raspberry Pi 4+ with modern kernel. All channels managed by single process.
kind: system
content_hash: 16d47299db9e7e66f26027579c3a3f29
---

# Hypothesis: Monolithic Multi-Channel Relay (Rust + io_uring)

Single relay process handling all channels using async I/O and zero-copy techniques.

**Architecture:**
- Single Rust binary using tokio async runtime
- io_uring for all I/O operations (UDP recv, file writes, multicast send)
- One task per channel, each with:
  - UDP socket listener on configured port
  - Ring buffer for packet batching
  - io_uring submission queue for disk writes
  - Multicast sockets (full-rate + decimated)
- Shared thread pool for CPU-bound work (decimation)
- Central YAML config loader at startup

**I/O Flow:**
1. io_uring IORING_OP_RECV → UDP packet into kernel-provided buffer
2. Zero-copy reference to buffer for multicast relay
3. io_uring IORING_OP_WRITE → batch AVRO writes with vectored I/O
4. Decimation in separate task pool (doesn't block I/O)

**Channel Management:**
- Reads config/relay.yaml at startup
- Spawns task per channel definition
- Dynamic channel addition requires restart (or SIGHUP reload)

**Trade-offs:**
+ Single binary, simple deployment
+ Shared memory for efficient decimation
+ io_uring maximizes throughput on modern kernels (5.10+)
+ Rust safety prevents memory corruption
- Requires Linux 5.10+ (io_uring maturity)
- Single point of failure (all channels down if process crashes)
- More complex codebase than per-channel approach
- io_uring has learning curve

## Rationale
{
  "anomaly": "Python relay cannot scale to 100Gbps on multi-core systems due to GIL and interpreted overhead",
  "approach": "Use Rust async + io_uring for maximum throughput on modern Linux. Single process simplifies deployment while async tasks provide isolation between channels.",
  "alternatives_rejected": [
    "Thread-per-channel in Rust (io_uring works better with async)",
    "C with manual async state machines (Rust tokio provides better ergonomics)"
  ]
}