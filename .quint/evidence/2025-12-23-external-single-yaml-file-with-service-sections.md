---
id: 2025-12-23-external-single-yaml-file-with-service-sections.md
type: external
target: single-yaml-file-with-service-sections
verdict: pass
assurance_level: L2
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
content_hash: 72d8dd2b085bfcbbe15a7a0546bc5243
---

External research validates monolithic YAML approach for multi-service configuration:

**Industry Best Practices (2025):**
- YAML widely-used for configuration due to readability and support for nested structures (CloudBees, Toxigon)
- Schema validation via jsonschema or pydantic recommended for all YAML configs (Configu, Toxigon)
- Kubernetes recommends single manifest files when Deployment/Service/ConfigMap belong to one app: "easier to track changes and apply as a unit" (k8s.io)
- Keep configuration files under version control (Toxigon)
- Avoid hardcoding secrets, use environment variables instead (Toxigon)

**Docker Compose Pattern Validation:**
- Docker Compose successfully uses monolithic docker-compose.yml for multi-container apps (docs.docker.com)
- Single YAML file manages container dependencies, networks, volumes, and environment variables (Microsoft Learn)
- Docker Compose supports override files (compose.override.yaml) for environment-specific variants (docs.docker.com)

**SpeedData Alignment:**
- Services (relay, stripchart, pivot) map to Docker Compose service sections pattern
- Multicast endpoint consistency requirement matches Kubernetes single-manifest recommendation
- PyYAML + pydantic/jsonschema provides validation stack (Configu)
- YAML more readable than JSON for human-edited configs (FreeCodeCodeCamp, Hackers & Slackers)

**Limitations Confirmed:**
- Not designed for production orchestration at scale (Docker docs: "lacks auto-scaling, rolling updates")
- Single file = single point of failure if corrupted
- Multi-machine deployment requires shared filesystem or config management tool

**Verdict:** Pattern validated by widespread industry adoption (Docker Compose, Kubernetes manifests). Well-suited for SpeedData v0.3 service-oriented architecture on single-machine or LAN deployment.