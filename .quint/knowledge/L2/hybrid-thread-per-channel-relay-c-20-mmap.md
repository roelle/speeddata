---
scope: POSIX systems (Linux/macOS/BSD). Best for 1-10 channels on systems with 4+ cores. mmap writeback behavior kernel-dependent. Not ideal for Raspberry Pi Zero (limited RAM).
kind: system
content_hash: dba6bc2bdfa8cedc37d34bcce7d6c9a3
---

# Hypothesis: Hybrid Thread-Per-Channel Relay (C++20 + mmap)

Single process with OS thread per channel, using memory-mapped files for zero-copy writes.

**Architecture:**
- C++20 binary using std::jthread (RAII thread management)
- One OS thread per channel:
  - Dedicated UDP socket with SO_REUSEPORT
  - Memory-mapped AVRO file (mmap with MAP_SHARED)
  - Lock-free ring buffer for packets
  - Multicast sockets (full-rate + decimated)
- Decimation handled by thread pool (std::async)
- Lock-free data structures for coordination (std::atomic)

**I/O Flow:**
1. recvfrom() into thread-local buffer
2. Immediate multicast relay (sendto)
3. Write to mmap'd region (dirty pages flushed by kernel)
4. msync(MS_ASYNC) every N packets for durability
5. Decimation offloaded to thread pool

**Channel Management:**
- Fixed thread count at startup (from config)
- Each thread independent (no shared mutable state)
- File rotation via munmap + new mmap
- Crash in one thread can be caught and logged

**Trade-offs:**
+ C++20 brings modern safety (RAII, smart pointers, concepts)
+ mmap eliminates explicit write calls (kernel handles flushing)
+ Threads lighter than processes (shared address space)
+ No async complexity (blocking I/O per thread is fine)
+ Works on any POSIX system (macOS/Linux/BSD)
+ Familiar to many developers (C++ ecosystem)
- Thread synchronization bugs possible (despite lock-free design)
- mmap dirty page writeback unpredictable (latency spikes)
- Higher memory usage than io_uring (buffers in userspace)
- Manual memory management (even with smart pointers)

## Rationale
{
  "anomaly": "io_uring limits portability, per-process overhead too high for many channels",
  "approach": "Thread-per-channel strikes balance: lighter than processes, simpler than async. mmap gives zero-copy writes without io_uring dependency. C++20 modernizes the codebase.",
  "alternatives_rejected": [
    "C with manual thread management (error-prone, C++ RAII safer)",
    "Older C++ (C++20 jthread/concepts improve code quality)"
  ]
}