# MANA 2.0.0 — Magic Programming Language

MANA 2.0.0 focuses on a polished, consistent release of the existing language, 2D world engine, libraries, examples, optional Visualiser, and VS Code workflow.

## Highlights

- One consistent version across the Python runtime, both VS Code extensions, documentation, and release installers.
- Improved release checks that validate both extensions and preserve historical release records.
- Cleaner project archives containing only the current release's VSIX installers, plus a plain-English release log.
- A repeatable release workflow that checks the pushed tag, runs the full quality gates on Linux and Windows across Python 3.12–3.15, and publishes assets only after the verification matrix passes.
- Better geometry and vector calculation helpers, library compatibility and name matching, broader anatomy/material catalogues, and Visualiser character inspection and scene controls.
- Continued validation of bounded recordings and runtime inputs, world-state rollback, 2D physics behaviour, and large-scene limits.

## Scope

The world simulation stays **2D**. `vector3d` provides calculations only. The optional Magic Visualiser replays recorded runs; it is not a live world editor and does not change the simulation when inspecting a recording. MANA programs still run without either VS Code extension.

## Install

Download `MANA-2.0.0-source.zip` for the source project, or install either `.vsix` package from VS Code's **Install from VSIX…** command. Python 3.12 or newer is required to run MANA from source; the extensions are optional.

The root `CHANGELOG.md` in the source archive is the cumulative version history and documents the changes since the public v1.0.0 source tag. `MANA_v2.0.0_RELEASE_LOG.md` is the shorter plain-English release summary; `docs/archive/audits/release_reports/MANA_2_0_2_LOCAL_PACKAGE_REPORT.md` records verification and limitations.
