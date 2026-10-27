# MANA Security and Runtime Boundaries

**Source version:** 2.0.0

This document describes the current runtime boundaries; it is not an independent security audit or a guarantee that no vulnerabilities remain. The source package does not include GitHub Actions workflows or a bundled automated test suite.

## Execution model

- MANA source is interpreted by the Python implementation in `magiclang/`.
- The runtime currently uses Python's standard library and does not install a separate dependency tree for ordinary execution.
- MANA is not an operating-system sandbox. Do not execute untrusted source on a machine where it can access data or resources you need to protect.
- The interpreter has input-size and runtime resource limits, but these limits do not turn the process into a security boundary.
- The VS Code extensions provide editor and replay UI. They are optional and do not replace the interpreter's runtime rules.
- Visualiser recordings are treated as viewer input and are subject to parsing and size limits; they are not a public engine-integration API.

## Reporting a suspected vulnerability

Follow the private-reporting instructions in [`SECURITY.md`](SECURITY.md). Include a minimal reproduction, affected version, platform, and the impact you observed. Avoid publishing sensitive reproduction details before maintainers have had a chance to review them.

## Scope

MANA is an experimental magic programming language and prototype 2D world simulator. It is not a full security sandbox, general-purpose game engine, or scientifically complete physics, chemistry, or biology simulator. Treat its simulation results as experimental.
