---
target: hybrid-thread-per-channel-relay-c-20-mmap
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-24
date: 2025-12-24
id: 2025-12-24-audit_report-hybrid-thread-per-channel-relay-c-20-mmap.md
type: audit_report
content_hash: 7eed08639cad340d9dd8af685ae04279
---

**WLNK Analysis:**
- Single evidence source: external research (PostgreSQL/SQLite mmap use, C++20 adoption)
- No dependencies declared
- R_eff: 1.00 (research evidence at L2)

**Risk Factors:**
- mmap latency unpredictability: Kernel writeback behavior non-deterministic (10-30s Linux default). Real-time relay may see latency spikes.
- Thread synchronization: Lock-free C++ challenging despite std::atomic. Race conditions possible (ThreadSanitizer required).
- Binary bloat: Template instantiation grows binary (500KB-2MB vs 50-100KB for C/Zig/Rust).
- No Boost constraint satisfied but C++20 still more complex than C.

**Weakest Link:**
- mmap writeback unpredictability: Measured concern for real-time telemetry. msync() forces flush but adds syscall overhead (defeats zero-copy benefit).
- Mitigation: Profile with realistic workload. Compare mmap vs buffered write latency distribution.

**Bias Check:**
- macOS support bias: C++20 best macOS support but user said "maybe ignore macOS until v1.0".
- Overvaluing portability vs performance predictability trade-off.

**Upside:**
- macOS native support: Best option if macOS becomes priority.
- C++ ecosystem: Mature tooling, large developer pool.

**Overall Assessment:**
- Technical risk: MEDIUM-HIGH (mmap latency, thread races)
- Implementation risk: MEDIUM (C++ familiar but lock-free hard)
- Recommendation: Only if macOS support critical AND willing to accept latency variability