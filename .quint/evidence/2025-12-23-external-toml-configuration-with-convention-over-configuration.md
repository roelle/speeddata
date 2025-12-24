---
carrier_ref: test-runner
valid_until: 2026-03-23
date: 2025-12-23
id: 2025-12-23-external-toml-configuration-with-convention-over-configuration.md
type: external
target: toml-configuration-with-convention-over-configuration
verdict: pass
assurance_level: L2
content_hash: 963ae9cef5c371c71c8ab5b8c0aef1fa
---

External research validates TOML configuration approach for Python:

**Python 3.11+ Native Support (2025):**
- Built-in tomllib library introduced in Python 3.11 for native TOML parsing (Real Python, Jan 2025)
- Backward compatibility: `tomli ; python_version < "3.11"` in pyproject.toml dependencies (devgem.io)
- Standard library support indicates TOML is becoming Python standard for config files

**TOML Advantages for Configuration:**
- "TOML has become the modern standard for configuration files in Python projects" (FreeCodeCamp)
- "More expressive than INI files and cleaner than JSON or YAML" (FreeCodeCamp, Hackers & Slackers)
- Supports comments like YAML (toml.io spec)
- Strong native typing: integers, booleans, floats, strings, dates auto-converted to Python types (Real Python)

**Industry Adoption:**
- Python packaging ecosystem standardized on pyproject.toml (packaging.python.org)
- Rust ecosystem uses Cargo.toml extensively (growing influence)
- "Using a configuration file is a good way to separate your code from its settings" (Real Python)

**Implementation Details:**
- tomllib.load() parses TOML files and returns regular Python dictionary (Real Python)
- Requires binary mode file opening ('rb') (Real Python, GeeksforGeeks)
- Simple interface for loading, values automatically typed (Real Python)

**Convention-Over-Configuration:**
- Best practice: "Break down your configurations into modular components" (Toxigon)
- Defaults reduce boilerplate and config errors (industry pattern, not TOML-specific)
- Variable interpolation requires custom parser (not native to TOML spec) - implementation effort

**SpeedData Alignment:**
- TOML's strong typing prevents string-parsing bugs (port: 8000 vs port: '8000')
- Native support in Python 3.11+ reduces dependencies
- Comments support (unlike JSON) for documenting config decisions
- Array tables `[[relay.channels]]` naturally represent lists of objects (TOML spec)

**Limitations Confirmed:**
- Less familiar than YAML/JSON in Python ecosystem (though growing rapidly post-3.11)
- Variable interpolation ${section.key} is custom logic, not TOML standard
- Convention-over-config adds "magic" requiring documentation

**User Preference Check:**
- User said "config feels like JSON or YAML" - TOML not explicitly mentioned
- However, TOML is config-oriented format (not data interchange like JSON)
- Python 3.11+ adoption may shift user expectations toward TOML

**Verdict:** TOML validated as emerging Python standard for configuration (Python stdlib adoption signals endorsement). Strong typing and readability advantages confirmed. Convention-over-config pattern requires implementation effort but reduces user burden. Trade-off: less familiar vs. better DX (developer experience).