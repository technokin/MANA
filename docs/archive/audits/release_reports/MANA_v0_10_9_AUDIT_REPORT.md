# MANA v0.10.9 — Portable IDE packaging report

## What changed

- Added `grimoire_frozen.py`, a PyInstaller entry point for the windowed Grimoire IDE.
- Added `mana_frozen.py`, a PyInstaller entry point for the console runtime that executes `.mana` source files.
- Added `tools/windows/Grimoire.spec` and `tools/windows/MANA.spec`. Both collect the built-in MANA library modules, including dynamically loaded plane-data modules.
- Added `tools/windows/Build-Portable-MANA.bat` and `tools/windows/build_portable.py`. On Windows, they build `Grimoire.exe` and `MANA.exe`, package the documentation/examples/assets/library data, and produce `dist/MANA_v0.10.9_Portable_Windows.zip`.
- Updated Grimoire's frozen-mode path resolution so it reads `VERSION`, docs, examples and assets from the folder beside `Grimoire.exe`.
- In frozen mode, Grimoire runs saved MANA programs by launching the bundled `MANA.exe`, not by starting `python mana.py`. The source-development workflow remains available for contributors.
- Disabled the developer test-suite button in the portable build because pytest and the project tests are not shipped to end users.
- Updated current documentation, release metadata and VS Code extension metadata to 0.10.9.

## Validation performed here

- 270 project tests passed on the source checkout.
- The MANA VS Code extension package was rebuilt and verified as `mana-language-0.10.9.vsix`; the installer directory contains only that version.
- Python source compilation completed successfully for the interpreter, IDE, launchers and build helper.
- Relative Markdown links in the current documentation, README and Windows tooling docs were checked; no broken local links were found.
- The packaging configuration and frozen CLI entry point were covered by automated tests.

## Important limitation

This environment runs Linux and has no Windows build host. PyInstaller produces native executables for the operating system it runs on, so a genuine Windows `.exe` cannot be compiled and verified here. No fake `.exe` or Linux binary with a Windows filename has been placed in the archive.

The attached project is the **portable Windows build kit**, not the compiled portable application. On a Windows development machine, run `tools\\windows\\Build-Portable-MANA.bat`. That script uses Python 3.10+ and PyInstaller at build time, then produces a portable folder with `Grimoire.exe` and `MANA.exe`. Users of the resulting folder should not need Python installed. Before distributing it, test both executables on a clean Windows machine without Python.

## Product distinction

MANA remains its own language. Python is the current implementation host, but in the intended portable distribution the user runs `Grimoire.exe` to edit and `MANA.exe` to run `.mana` files. No user workflow should require typing `python grimoire.py` or `python mana.py` after the portable build has been produced.
