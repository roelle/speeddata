---
type: external
target: library-first-architecture-with-reference-implementations
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-library-first-architecture-with-reference-implementations.md
content_hash: 3120088455dca09d0d3fd98ec97391c1
---

Research findings on library-first architectures for domain toolkits:

**Similar Systems:**
- libpcap (packet capture library) + tcpdump (reference tool) - standard pattern for network tools
- SQLite (library) + sqlite3 CLI (reference implementation) - embedded database model
- FFTW (Fast Fourier Transform library) + examples - scientific computing pattern
- ZeroMQ (messaging library) + example programs - networking toolkit

**Evidence for SpeedData context:**
1. **Library boundaries match functional decomposition:**
   - libspeeddata-wire (encoding/decoding for sources)
   - libspeeddata-relay (UDP ingestion engine)
   - libspeeddata-archive (HDF5/Parquet export)
   - Reference: relay daemon, stripchart server, pivot utility

2. **Usability for "barely-programmers":**
   - Copy/paste from reference implementations (proven pattern in scientific computing)
   - Language bindings enable Python/Matlab integration (critical for "dumb nodes")
   - Examples serve as documentation (common in research software)

3. **Ecosystem benefits:**
   - Third-party tools can integrate wire encoding library directly
   - Alternative visualization tools can read archive format
   - Enables community contributions without forking entire system

**Risks validated:**
- API stability critical - breaking changes frustrate users (mitigated by semantic versioning)
- Reference implementations MUST stay in sync with libraries (requires monorepo or strict release process)
- Higher upfront cost: ~2-3x development time for v0.1 (design APIs + implementations)
- Premature for current stage (v0.1 = proof-of-concept, not stable APIs)

**Conclusion:** Excellent long-term architecture (v0.5+) but premature for v0.1-v0.3. Roadmap v0.5 "firm interfaces" suggests this becomes viable after API stabilization. Recommend: defer until interfaces proven through monolith/service experience.