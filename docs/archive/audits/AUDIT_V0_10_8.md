# MANA v0.10.8 — Grimoire IDE audit

## Added

- `grimoire.py`: desktop launcher with `--version` and optional source-file/project-directory arguments.
- `grimoire/app.py`: window, menus, project explorer, document tabs, save/open flow, interpreter subprocess runner, Stop control, test-suite runner, output capture, and document navigation.
- `grimoire/editor.py`: line-number gutter, current-line tracking, MANA-oriented indentation, and multi-tab editor widget.
- `grimoire/syntax.py`: lightweight text-only syntax highlighting for MANA keywords, definitions, elements, built-in operations, namespaces, units, numbers, strings, comments and operators.
- `docs/current/tooling/GRIMOIRE_IDE.md`: installation, controls, shortcuts and known limits.
- `tools/windows/Start-Grimoire.bat`: Windows launcher using `python` with `py -3` fallback.

## Verification

- Full automated regression suite: **265 passed**.

- `python grimoire.py --version` reports the matching MANA and Grimoire versions.
- Tk window constructed, processed events, accepted editor input, marked a document dirty, and closed successfully under an X virtual framebuffer.
- The MANA interpreter's existing smoke example still runs through the normal `mana.py` entry point.
- Regression tests cover syntax highlighting boundaries, launch/version output, IDE files, Windows launcher, documentation index, and current task/extension metadata.
- VS Code extension package is rebuilt from source and validated against `VERSION`.

## Boundaries

- Grimoire is a desktop IDE and front end for the existing interpreter. It does not include a graphical World Engine viewport in v0.10.8.
- The IDE has no semantic language server, autocomplete, debugger/breakpoints, object inspector, graphical simulation view, or interactive stdin terminal.
- Run actions use the external interpreter and display its stdout, stderr, and exit code; syntax colours do not validate or change program semantics.
- Python needs a working Tcl/Tk installation to open the GUI. The core MANA runtime has no new third-party dependency.
- The supplied SVG logo remains optional. An exported `assets/branding/mana-logo.png` is used as the native Tk window icon if present.
