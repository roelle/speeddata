---
scope: Any POSIX system (Linux/macOS/BSD/even ancient kernels). Best for 1-5 channels. Suitable for Raspberry Pi (minimal dependencies). Conservative choice for gradual migration from Python.
kind: system
content_hash: 9fa75c21684b7099528b7e42f8d4768e
---

# Hypothesis: Conservative Single-Channel Relay (C + stdio buffering)

Minimal-risk port to C maintaining current single-channel semantics with standard I/O.

**Architecture:**
- Pure C99 (maximum portability)
- Single channel per process (like current Python version)
- Standard library I/O (fwrite with setvbuf for buffering)
- Simple select() or poll() for UDP socket
- No async, no threads, no exotic syscalls
- YAML config parsed via libyaml
- Orchestration by existing init system (systemd/supervisor)

**I/O Flow:**
1. select() on UDP socket
2. recvfrom() into stack buffer
3. fwrite() to AVRO file (stdio buffered)
4. sendto() for multicast relay
5. Decimation with simple in-memory counter
6. fflush() on sync boundaries (configurable)

**Channel Management:**
- One relay process per channel (systemd units)
- Config change = restart process
- Standard Unix signals (SIGHUP, SIGTERM)
- File rotation via rename + reopen

**Trade-offs:**
+ Lowest risk (proven patterns, minimal complexity)
+ Maximum portability (works on anything with C99)
+ Easy to debug (gdb, valgrind well-established)
+ Small binary (~50KB static)
+ stdio buffering "good enough" for most cases
+ Familiar to any C programmer
+ Works on ancient kernels (2.6+)
- stdio buffering less efficient than io_uring
- select() doesn't scale to many FDs (but we only have 1-2)
- Manual memory management (buffer overflows possible)
- No modern language safety features
- Per-process overhead for many channels

## Rationale
{
  "anomaly": "Python performance insufficient but radical rewrite risks project timeline",
  "approach": "Direct port to C preserving current architecture. Proves concept before investing in complex async/io_uring solutions. stdio buffering provides 80% of benefit with 20% of complexity.",
  "alternatives_rejected": [
    "Keep Python with minor optimizations (already exhausted)",
    "C with hand-rolled buffering (reinventing stdio wheel)"
  ]
}