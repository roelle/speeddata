---
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-audit_report-preset-schema-with-file-based-registration.md
type: audit_report
target: preset-schema-with-file-based-registration
verdict: pass
assurance_level: L2
carrier_ref: auditor
content_hash: 0c5473175468dff5e0b4789f190173fa
---

## Risk Analysis: Preset Schema with File-Based Registration

### Technical Risks

**1. Schema Evolution Risk (MEDIUM)**
- **Issue**: Changing field types or removing fields breaks backward compatibility
- **Mitigation**: AVRO supports schema evolution via default values, but requires coordination
- **Impact**: MCU firmware updates required for schema changes; relay must handle version mismatches
- **Likelihood**: HIGH (telemetry needs evolve frequently)
- **Severity**: MEDIUM (requires coordinated deployment)

**2. Config File Management Risk (LOW-MEDIUM)**
- **Issue**: Manual config file editing error-prone at scale
- **Mitigation**: Validated against `.avsc` schema format; can add validation tooling
- **Impact**: Invalid config prevents channel startup; file conflicts in version control
- **Likelihood**: MEDIUM (human error factor)
- **Severity**: LOW (detectable at relay startup)

**3. Port Exhaustion Risk (LOW)**
- **Issue**: Each channel requires dedicated UDP port
- **Mitigation**: UDP ephemeral range (49152-65535) provides 16,384 ports; typical deployments <<100 channels
- **Impact**: Hard limit on number of channels per relay instance
- **Likelihood**: LOW (requires 100+ channels per machine)
- **Severity**: LOW (deploy multiple relay instances)

**4. Zero-Registration Failure Mode (MEDIUM)**
- **Issue**: MCU sending to wrong port = silent data loss (UDP)
- **Mitigation**: MCU hardcodes port from config; relay logs missing packets; monitoring via packet counts
- **Impact**: Data silently dropped until monitoring detects anomaly
- **Likelihood**: LOW (configuration managed centrally)
- **Severity**: HIGH (silent failure)

**5. AVRO Encoding Bug Risk (LOW)**
- **Issue**: Manual AVRO packing on MCU prone to endianness/encoding errors
- **Mitigation**: AVRO binary format is simple (floats = little-endian IEEE 754); validation tools can verify packets
- **Impact**: Corrupted data or relay decode failure
- **Likelihood**: LOW (one-time implementation, simple encoding)
- **Severity**: MEDIUM (detectable via relay validation)

### Operational Risks

**6. Config Drift Risk (MEDIUM)**
- **Issue**: MCU firmware and relay config schemas out of sync
- **Mitigation**: Version control config files; MCU firmware includes schema hash; config deployment tooling
- **Impact**: Decode errors at relay; requires manual reconciliation
- **Likelihood**: MEDIUM (multi-component system)
- **Severity**: MEDIUM (requires operational discipline)

**7. No Dynamic Discovery Risk (LOW)**
- **Issue**: Adding new channel requires relay restart
- **Mitigation**: File-based config reloaded on SIGHUP; graceful restart mechanisms
- **Impact**: Brief data loss during config reload
- **Likelihood**: LOW (channels added infrequently)
- **Severity**: LOW (planned maintenance window)

### Dependency Risks

**8. AVRO Library Dependency (LOW)**
- **Issue**: Relay depends on `avro-js` library for decoding
- **Mitigation**: Mature library (v1.12.0); minimal dependencies; can vendor if needed
- **Impact**: Security vulnerabilities or breaking changes in upstream
- **Likelihood**: LOW (stable library)
- **Severity**: LOW (can freeze version)

### Congruence Penalties

**9. External Evidence Congruence (CL1-CL2)**
- **Assessment**: Research sources (Juniper, Cisco, Azure IoT) are CL1 (different context) to CL2 (similar context)
- **Penalty**: 10-30% R_eff reduction for external evidence
- **Justification**: Commercial telemetry systems operate at larger scale but similar constraints (UDP, schema management)

### WLNK Analysis

**Weakest Links Identified**:
1. **Zero-registration silent failure mode** (SEVERITY: HIGH, LIKELIHOOD: LOW)
   - Mitigation: Monitoring layer + packet count alerts
   
2. **Schema evolution coordination** (SEVERITY: MEDIUM, LIKELIHOOD: HIGH)
   - Mitigation: Schema versioning strategy + backward compatibility requirements

**Overall Assessment**: Risks are manageable with operational discipline. No fundamental architectural blockers. Primary concern is operational complexity of multi-component schema coordination.

**Recommended Controls**:
- Schema validation tooling (pre-deployment checks)
- Monitoring dashboards for per-channel packet rates
- Config management automation (prevent manual edits)
- Schema versioning policy (require backward compatibility)
