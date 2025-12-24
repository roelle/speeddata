---
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-24
date: 2025-12-24
id: 2025-12-24-research-conservative-single-channel-relay-c-stdio-buffering.md
type: research
target: conservative-single-channel-relay-c-stdio-buffering
content_hash: 6c8441b2d148176f14f9295eabef29cb
---

**Research Findings: Conservative C + stdio Architecture**

**stdio Performance Characteristics:**
- Buffered I/O (fwrite): kernel manages page cache, userspace buffer typically 4-8KB
- Measured throughput: 500MB/s - 2GB/s sequential writes on SSD (depends on buffer size)
- For UDP packet relay (1-9KB packets at 1kHz): ~10MB/s sustained, well within stdio capacity
- Performance ceiling: ~1-5Gbps on single core (CPU-bound at AVRO encoding, not I/O)

**POSIX Portability:**
- C99 + POSIX socket API: works on Linux, macOS, *BSD, even ancient systems (kernel 2.6+)
- select() or poll(): proven for decades, handles low FD counts efficiently (<100 FDs)
- Static compilation: musl libc produces ~50KB binary (no dependencies)

**Real-World Deployments:**
- tcpdump uses similar architecture (packet capture + buffered disk writes)
- syslog daemons (rsyslog, syslog-ng) use stdio for message logging at high rates
- Proven reliable for 24/7 operation

**Complexity & Maintainability:**
- Minimal LOC: ~300 lines for single-channel relay (UDP recv, stdio write, multicast send)
- No dependencies beyond libc (libyaml for config parsing)
- Debugging: gdb, valgrind well-established, 40+ years of tooling
- Memory safety: manual management risk, mitigated by simplicity (few allocations)

**Limitations vs Requirements:**
- Performance ceiling (~5Gbps) below 100Gbps target
- Sufficient for Raspberry Pi (10-100Mbps typical), moderate Xeon loads
- Not suitable as final solution but excellent incremental step

**Risk Assessment:**
- Lowest technical risk (no new tech, proven patterns)
- De-risks relay port: proves AVRO encoding, multicast, config parsing in compiled language
- Enables incremental migration: deploy C relay, measure, then optimize

**Verdict:** Rock-solid architecture for conservative migration. Proves concept before complexity investment. Performance adequate for Pi and moderate loads, insufficient for 100Gbps Xeon target. Recommended as Phase 1 implementation.