---
scope: SpeedData as reusable components for users to build custom data acquisition systems
kind: system
content_hash: dae2d161a5c2b09d00d254d8fdab414b
---

# Hypothesis: Library-First Architecture with Reference Implementations

Develop SpeedData as a set of libraries rather than applications:

Core Libraries:
- libspeeddata-wire: Wire encoding/decoding (C with language bindings)
- libspeeddata-relay: UDP multicast relay primitives (Rust/C++)
- libspeeddata-archive: Archive read/write (Python/C++)

Reference Implementations:
- speeddata-relay: Reference relay using libspeeddata-relay + libspeeddata-wire
- speeddata-web: Reference web visualization
- speeddata-pivot: Reference export tool

Users can compose libraries into custom applications OR use reference implementations.
Deployment: Libraries published to package managers (cargo, pip, npm), references as Docker images or binaries.
Repository: Monorepo with library-focused directory structure (libs/, examples/, references/).

## Rationale
{"anomaly": "Current monolithic applications limit reusability - users can't extract just the relay or just the wire encoding", "approach": "Library-first design maximizes reusability, allows users to build custom systems (e.g., embedded relay without web UI, custom visualization)", "alternatives_rejected": ["Application-only approach (limits adoption)", "Framework approach (too opinionated)"]}