---
target: per-service-yaml-files-with-shared-globals
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-per-service-yaml-files-with-shared-globals.md
type: external
content_hash: ac6b12506325fcd36cc591ac83a78a0d
---

External research validates per-service YAML files with shared globals pattern:

**Docker Compose Multiple Files Pattern:**
- Docker Compose supports multiple compose files: base compose.yaml + optional compose.override.yaml (docs.docker.com)
- Override file contains "configuration overrides for existing services or entirely new services"
- Merge behavior: "compose.yaml contains your base configuration and the override file can contain configuration overrides"
- Use case: "When targeting different environments, you should use multiple compose files" (docs.docker.com)

**Extends/Sharing Pattern:**
- Docker Compose 'extends' attribute: "share common configurations among different files, or even different projects entirely"
- "Useful if you have several services that reuse a common set of configuration options"
- "Define a common set of service options in one place and refer to it from anywhere" (docs.docker.com)

**Python Configuration Best Practices:**
- "Break down your configurations into modular components, which makes it easier to manage and update specific parts" (Toxigon)
- Modularization recommended for complex multi-service systems (Configu)
- Each service validates only its own config section (Micropole Belux)

**SpeedData Alignment:**
- global.yaml pattern matches Docker Compose base file
- Service-specific YAML files match Docker Compose service-per-file pattern
- Merge logic (service-specific overrides global) is proven Docker pattern
- Multi-machine deployment: each service only needs its file + global (distributed friendly)

**Limitations Confirmed:**
- Config drift risk if global.yaml not synchronized across machines
- Requires deployment discipline (mentioned in research: version control, consistency across environments)
- Runtime detection possible but not prevention (services warn if multicast mismatch)

**Production Usage:**
- Docker Compose not for production at scale, but pattern itself is valid (Kubernetes uses similar ConfigMap + per-service overrides)
- Config management tools (Ansible, Chef, Puppet) handle multi-file sync in production

**Verdict:** Pattern validated by Docker Compose and Kubernetes ecosystems. Well-suited for multi-machine SpeedData deployments with proper config management tooling.