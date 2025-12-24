---
target: per-channel-relay-fleet-zig-direct-i-o
verdict: pass
assurance_level: L2
carrier_ref: auditor
valid_until: 2026-03-24
date: 2025-12-24
id: 2025-12-24-audit_report-per-channel-relay-fleet-zig-direct-i-o.md
type: audit_report
content_hash: d9b4f902acda83be1cd2f3864c35adce
---

**WLNK Analysis:**
- Single evidence source: external research (Uber/Bun production use, O_DIRECT benchmarks)
- No dependencies declared
- R_eff: 1.00 (research evidence at L2)

**Risk Factors:**
- Language novelty: User unfamiliar with Zig. Smaller community than Rust/C++ (slower Stack Overflow answers).
- O_DIRECT complexity: 512-byte alignment requirements add cognitive load. Easy to get wrong (EINVAL errors).
- Production maturity: Zig ecosystem younger than Rust (fewer libraries, less tooling).

**Weakest Link:**
- Team Zig proficiency: No existing expertise. Learning curve unknown (estimated 2-4 weeks for productivity).
- Mitigation: Prototype single-channel relay, measure learning velocity, decide to continue or pivot.

**Bias Check:**
- "Hipster tech" risk: Zig trendy but unproven in telemetry relay domain specifically.
- Process isolation benefit real, but achievable with Rust too (less risk).

**Upside:**
- Simplicity: Comptime + manual memory management simpler than Rust borrow checker.
- Binary size: Smallest option (~100KB), beneficial for Pi deployment.
- Cross-platform: Works on macOS (F_NOCACHE abstraction), unlike io_uring.

**Overall Assessment:**
- Technical risk: MEDIUM (O_DIRECT proven, Zig production-ready)
- Implementation risk: MEDIUM-HIGH (learning curve + smaller ecosystem)
- Differentiation: Best "simple compiled language" option if C too low-level, Rust too complex