# MANA v0.10.9 — Portable IDE packaging audit

## Goal

The end-user workflow must be a portable Windows application, not a requirement to install Python or invoke `grimoire.py` / `mana.py`. MANA remains its own language; Python is the current implementation host and is bundled into the executable build.

## Included in this source revision

- `grimoire_frozen.py` — frozen, windowed Grimoire entry point.
- `mana_frozen.py` — frozen console entry point for executing `.mana` files.
- `tools/windows/Grimoire.spec` and `tools/windows/MANA.spec` — one-file PyInstaller builds with dynamic built-in library imports collected.
- `tools/windows/Build-Portable-MANA.bat` and `build_portable.py` — build and package a portable folder containing both executables plus docs, examples, assets and library data.
- Frozen Grimoire mode resolves resources beside `Grimoire.exe` and launches `MANA.exe` to run code. Source mode continues to use the Python source runner and test suite.

## Verification and limitation

Source-mode tests and packaging configuration checks can run on Linux, but a Windows PE executable cannot be built or truthfully verified from this Linux host. The build helper explicitly rejects non-Windows hosts rather than producing a Linux binary with an `.exe` name. On Windows, run `tools/windows/Build-Portable-MANA.bat`; test the resulting `Grimoire.exe` and `MANA.exe` on a machine without Python installed before distributing the portable bundle.

## Expected output

- `dist/MANA_v0.10.9_Portable_Windows/Grimoire.exe`
- `dist/MANA_v0.10.9_Portable_Windows/MANA.exe`
- `dist/MANA_v0.10.9_Portable_Windows.zip`

The finished user package should be moved as a folder or ZIP; keep `Grimoire.exe` and `MANA.exe` together.
