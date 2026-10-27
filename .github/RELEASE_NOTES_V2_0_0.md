# MANA 2.0.0 — Magic Programming Language

MANA 2.0.0 expands the language, built-in libraries, 2D world engine, runnable examples, optional Visualiser, and VS Code support.

## Highlights

- A consistent 2.0.0 source version across the interpreter, editor extensions, documentation, and installer packages.
- Broader geometry/vector calculations, library compatibility, and creature/material reference catalogues.
- A separate magic-first 2D Visualiser for replaying recorded spells, with scene navigation, character inspection, adaptive graphics, and bounded recording resources.
- Additional `.mana` examples for preview/commit boundaries, plane paths, energy accounting, selective targets, and recorded impacts.
- Clearer documentation of implemented capabilities and limitations.

## Scope

The world simulation remains **2D**. `vector3d` provides calculations, not a complete 3D world. The optional Magic Visualiser replays recorded runs; it is not a live world editor. MANA programs run from Python without either VS Code extension.

## Package contents

The source package contains the interpreter, built-in libraries, 67 runnable examples, current documentation, project tools, and both versioned VS Code extensions. Automated GitHub Actions workflow files and the bundled test suite are not included.

Python 3.12 or newer is required to run MANA from source. The VS Code extensions are optional. `CHANGELOG.md` and `MANA_v2.0.0_RELEASE_LOG.md` preserve the version history and feature notes.
