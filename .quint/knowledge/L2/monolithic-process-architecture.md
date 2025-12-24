---
scope: SpeedData core (Relay+Stripchart+Pivot), excludes external Sources which remain independent
kind: system
content_hash: 33fd019acebcb4b4e925a7667b879ad4
---

# Hypothesis: Monolithic Process Architecture

Single executable integrating Relay, Stripchart Server, and Pivot functionality with internal message passing. Sources remain separate (external data generators). Architecture:
- Single process with thread pools for UDP receive, multicast relay, WebSocket serving, and pivot operations
- Shared memory for ephemeral cache (no serialization overhead between components)
- Single configuration file, single port allocation
- Deployment: single binary + web frontend assets
- Repository: monorepo with single build system

## Rationale
{"anomaly": "Current multi-process Python/Node.js architecture adds IPC overhead and deployment complexity for small-scale systems", "approach": "Minimize process boundaries and serialization overhead via shared memory, optimize for Pi deployment", "alternatives_rejected": ["Keeping current multi-language split (Python relay + Node stripchart)", "Microservices (too heavy for target scale)"]}