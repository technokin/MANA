# MANA 2.0.0 Source Snapshot Notes

**Page kind:** Source snapshot notes  
**Version:** 2.0.0  
**Updated:** 27 October 2026

This page describes the contents and boundaries of the MANA 2.0.0 source snapshot. It is not a quality-gate report, security certification, or promise that every planned feature is implemented.

## Included

- The MANA lexer, parser, runtime, units, physics engine, built-in libraries, and command-line entry point.
- Runnable `.mana` examples covering language constructs, spell execution modes, planes, materials, creature systems, physics, and Visualiser recordings.
- Maintained language, library, architecture, troubleshooting, and implementation-status documentation.
- The optional MANA Language Support VS Code extension and MANA Magic Visualiser extension, including their source and versioned VSIX packages.
- Source-generation and extension-packaging utilities under `tools/`.

## Not included in this source package

- GitHub Actions workflow definitions or automatic CI/release jobs.
- The bundled automated test suite and test-only fixtures.
- Separate linting and dependency-audit configuration or dependencies.

## Version and scope

The `VERSION` file is the source version marker and contains `2.0.0`. MANA is implemented in Python at present; `.mana` programs are interpreted by `mana.py` and `magiclang/`. VS Code extensions are optional and are not required to run programs. The world engine is a prototype 2D simulator, and the `vector3d` library provides calculations rather than a complete three-dimensional world solver. See [Implementation Status](foundations/IMPLEMENTATION_STATUS.md) and [Not Supported Yet](foundations/NOT_SUPPORTED_YET.md) for current feature boundaries.
