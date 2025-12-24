---
scope: Linux 5.15+ with XDP-capable network interface (Intel X710, Mellanox ConnectX). Targets high-end deployments (10-100Gbps Xeon servers). NOT suitable for Raspberry Pi or general-purpose systems. Research/experimental approach.
kind: system
content_hash: fb40af742a68733ca3c23bf1844a2ff5
---

# Hypothesis: Radical Shared-Memory Relay (Rust + io_uring + eBPF)

Zero-copy relay using kernel eBPF programs and shared memory rings for extreme performance.

**Architecture:**
- Rust relay with io_uring for all I/O
- eBPF XDP program attached to network interface:
  - Filters UDP packets by dest port in kernel
  - Writes directly to io_uring shared memory ring
  - Bypasses socket layer entirely (XDP_PASS for non-relay traffic)
- Userspace relay process:
  - Reads from io_uring completion queue
  - AVRO encoding in userspace
  - io_uring batch writes to file
  - io_uring sendmsg for multicast
- BPF maps for per-channel routing configuration

**I/O Flow (extreme zero-copy):**
1. XDP program intercepts packet at NIC driver level
2. Packet placed directly in io_uring shared buffer
3. Relay reads via io_uring IORING_OP_PROVIDE_BUFFERS
4. Wraps in AVRO framing (minimal copy)
5. io_uring vectored write to file
6. io_uring multicast send

**Channel Management:**
- BPF map updates for dynamic channel routing
- No process restart needed for config changes
- Per-channel statistics via BPF maps

**Trade-offs:**
+ Absolute maximum performance (kernel bypass)
+ True zero-copy (packet never leaves kernel memory)
+ Sub-microsecond latency possible
+ Scales to 100Gbps on modern NICs
+ Real-time statistics via BPF maps
- Extreme complexity (eBPF, io_uring, Rust)
- Requires Linux 5.15+ and XDP-capable NIC
- Debugging difficult (eBPF verifier, kernel interactions)
- Overkill for most deployments
- Raspberry Pi support questionable (NIC drivers)
- Long development time
- Expertise required (kernel programming)

## Rationale
{
  "anomaly": "Even io_uring incurs socket syscall overhead. For 100Gbps target, need kernel bypass.",
  "approach": "Use eBPF XDP to intercept packets before socket layer, combined with io_uring shared buffers for true zero-copy. Pushes performance limits but requires exotic hardware and kernel features.",
  "alternatives_rejected": [
    "DPDK (bypasses kernel entirely, incompatible with multicast to other apps)",
    "AF_XDP alone (still requires userspace polling loop)",
    "Netmap (less portable than XDP, smaller ecosystem)"
  ]
}