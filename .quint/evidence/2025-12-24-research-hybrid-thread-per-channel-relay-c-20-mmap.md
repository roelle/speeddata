---
date: 2025-12-24
id: 2025-12-24-research-hybrid-thread-per-channel-relay-c-20-mmap.md
type: research
target: hybrid-thread-per-channel-relay-c-20-mmap
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-24
content_hash: 624b82e9897ef6dfa4ad1ffa2e101ad9
---

**Research Findings: C++20 Threads + mmap Architecture**

**C++20 Thread Safety Features:**
- std::jthread: RAII thread management (auto-join on destruction)
- std::atomic: lock-free primitives for coordination
- std::latch/barrier: modern synchronization (replaces pthread primitives)
- No Boost required: std library sufficient (user constraint satisfied)

**mmap Performance & Behavior:**
- Memory-mapped I/O: kernel manages dirty page writeback
- Performance: comparable to buffered I/O for sequential writes (~1-2GB/s)
- Latency unpredictability: dirty page writeback scheduled by kernel (10-30s default on Linux)
- msync() forces immediate flush: adds explicit control but syscall overhead
- Page fault overhead: first write to unmapped page triggers minor fault (~1μs)

**Thread-Per-Channel Scaling:**
- OS thread overhead: ~8KB stack + kernel metadata per thread
- 20 channels = 20 threads = ~200KB overhead (negligible)
- Context switch: 1-5μs on modern CPUs (acceptable for kHz-rate telemetry)
- Thread bugs: race conditions, deadlocks possible despite atomics (C++ doesn't prevent all issues)

**Cross-Platform Support:**
- POSIX mmap: Linux, macOS, BSD, even Windows (via MapViewOfFile compatibility)
- C++20 std library: mature on GCC 10+, Clang 12+, MSVC 2019+
- Best macOS support among compiled options (mmap native, no io_uring)

**Complexity Assessment:**
- Lock-free programming: challenging even with std::atomic
- Template instantiation: binary size grows (~500KB-2MB for relay with templates)
- Debugging: thread race conditions require tools (ThreadSanitizer, helgrind)
- No Boost bloat: validated, but C++20 still more complex than C

**mmap vs Explicit I/O Trade-off:**
- mmap benefit: zero-copy API (direct memory access)
- mmap cost: unpredictable writeback latency
- For real-time telemetry: explicit I/O (write/io_uring) more predictable
- mmap better for: large files accessed randomly (not sequential relay workload)

**Production Use Cases:**
- Databases use mmap (PostgreSQL, SQLite) but tune writeback aggressively
- Log aggregators avoid mmap (prefer buffered I/O for predictability)

**Verdict:** C++20 delivers on portability (best macOS support). Complexity manageable without Boost. mmap latency unpredictability is concern for real-time relay. Thread-per-channel proven pattern. Better choice if macOS support critical, but mmap not ideal for sequential relay workload.