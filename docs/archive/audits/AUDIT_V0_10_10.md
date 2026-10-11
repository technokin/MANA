# MANA v0.10.11 — Audit and project-organization report

**Audit source:** the owner-supplied *MANA v0.10.7: Audit*.  
**Code reviewed:** MANA v0.10.9 source, revised for v0.10.11.  
**Purpose:** apply still-relevant findings, record findings already fixed, improve formatting conventions, and put historical audit material in the archive.

The supplied audit describes v0.10.7, so each item was checked against the later source before changes were made. It was not treated as a claim that every listed defect still existed.

## Results by audit ID

| ID | Status | Change or finding |
|---|---|---|
| PL1 | Fixed | Direct creation of non-base plane elements now requires `import planes` and a matching `planes.invoke(...)` permission. The four base elements remain directly available. Derived materials may still be created by valid combinations of base elements. |
| PL4 | Partially addressed | Added `.editorconfig` and `pyproject.toml` to define UTF-8/LF, indentation, Ruff formatting and lint rules. Reformatted the affected plane-data modules and current documentation. A whole-tree Ruff formatting pass was not run because Ruff is not installed in this environment. |
| PL5 | Fixed | All built-in being records now have initial `hp`, `max_hp`, `defence` and `attack` values. Values are editable prototype balance baselines, not canonical numbers from a real-world species or a specific fictional franchise. Each supported element has a resistance entry; the default is `0` (no protection). |
| PL7 | Fixed | `planes.send_energy(..., kind)` validates labels against the known elemental/plane-energy catalogue and registered internal transfer labels. Typos such as `deth` now produce a MANA error. |
| PL8 | Fixed | `planes.plane_of()` rejects string plane names and `PlaneReference` values rather than silently returning the Mortal Plane for them. Being records and world objects retain their intended behaviour. |
| E1 | Already fixed; covered | The parser already warns when statements follow `incant` in the same block. The behaviour is retained and documented. |
| E2 | Fixed | Unknown event names now emit a MANA-format warning on standard error with the source file, line and column, rather than using Python's `RuntimeWarning`. |
| E3 | Fixed | `collapsed_into` now exists on every new object and is `None` until collapse. Added a regression test for reading it before collapse. |
| E4 | Rechecked | The commit path already uses set-based identity membership. A local 20,000-object `release` benchmark completed in about 2.0 seconds. Profiling 5,000 object creations points to `MagicObject.__post_init__`/initial property and energy setup as the primary cost, not a quadratic commit membership check. The default `release` path did not print per-property trace output in this run. |
| E5 | Fixed; pyflakes command pending | Replaced the wildcard AST import and removed the unused imports identified in the supplied audit. A local AST-based import-use scan found no remaining unused explicit imports. `pyflakes` is included in development requirements, but `python -m pyflakes magiclang` could not be run here because the package is not installed and package installation is unavailable in this environment. |
| T1 | Fixed | Changed the necromancy example from unsupported `m^3` to the accepted MANA unit literal `m3`. |
| T2 | Fixed and enforced | Current documentation examples now run standalone, or are explicitly marked as a package/library fragment or expected failure. An automated test executes current-doc MANA fences and prevents unmarked examples from becoming broken. |
| T3 | Fixed | Older audits and coverage records are under `docs/archive/audits/`; prior build reports are under `docs/archive/audits/release_reports/`. They are historical records, not the current API reference. Relative links in the moved audit files were updated where they point to current documentation. |
| T4 | Fixed | VS Code grammar highlighting now names the built-in library namespaces and common library calls, including `planes`, `drafter`, `summoning`, `necromancy`, `geometry2d`, `vector3d`, `mana`, `bring`, `tame`, `send_back`, `reanimate`, and pathway operations. The VSIX package was rebuilt for 0.10.11. |

## Project layout changes

- `mana.py` and `grimoire.py` remain at the root as developer/source launchers until MANA v1.0.
- PyInstaller source entry points were moved and renamed to `tools/windows/entrypoints/mana_executable_entry.py` and `tools/windows/entrypoints/grimoire_executable_entry.py`. These are build inputs, not user-facing executables and not generated frozen files.
- The project root no longer contains release audit reports. Audits and earlier package reports live under `docs/archive/audits/`.
- `.gitignore` now covers Python bytecode, caches, Ruff cache, virtual environments and build output. Generated cache directories were removed from the release archive.
- `.editorconfig`, `pyproject.toml`, and the expanded `requirements-dev.txt` establish shared source-formatting and static-check conventions.

## Verification

- `279` tests passed from the working source tree for this revision.
- All runnable MANA code fences in `docs/current/` executed successfully in isolated runtimes; the remaining four snippets are explicitly marked as a package/library fragment or an intentional expected failure.
- The current VS Code VSIX was rebuilt as `installers/vscode/mana-language-0.10.11.vsix` and validated as a ZIP with matching version metadata.
- Python compilation checks passed for `magiclang/`, `grimoire/`, and the executable build-entry scripts.
- The package was checked for local Markdown links; historical references were adjusted to reflect the archive move.
- A native Windows executable was not built in this environment. The Windows build scripts remain the way to produce the portable `Grimoire.exe` and `MANA.exe` on Windows.

## Limits and notes

The combat statistics assigned in this revision are initial editable balance values. They should be tuned through gameplay/simulation tests later. The supplied PL4 finding did not name specific malformed source blocks; formatting rules are now defined, but a full Ruff formatter pass should be run after installing the development requirements.
