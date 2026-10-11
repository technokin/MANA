# MANA v0.10.12 — Keyword Migration and Grimoire Packaging Audit

**Status:** implemented in the v0.10.12 source revision. The Windows launcher is built as a native Go PE executable; it has not been run on a real Windows host in this environment.

## 1. Language terminology and syntax

| Area | Final MANA form | Behaviour |
|---|---|---|
| Ordinary computational functions | `def name(...):` | Helpers for calculations and general programming. Results are supplied with `incant`. |
| Spell definitions | `spldef name(...):` | The separate spell-definition category used by `post` and `release`. |
| Library loading | `load library_name` | Replaces MANA-source `import` statements. |
| Empty/no-operation statement | `skip` | Replaces `pass`. |
| Iteration span | `span(...)` | Replaces the MANA built-in previously named `range`. |
| Sequence length | `length(value)` | Replaces the MANA built-in previously named `len`. |
| Definition result | `incant value` | Exits the current definition and supplies its result. MANA has no `return` statement. |
| Target context | `tgset(...)` | Unchanged. |

`if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, and `not` remain valid MANA syntax as requested. Arithmetic and comparison operators remain unchanged. The `round` shape label remains available in its MANA geometry context. Python's similarly named operators or built-ins inside the Python implementation are implementation details, not MANA language features.

The parser, tokens, runtime built-ins, examples, Grimoire syntax highlighter, VS Code grammar, language guide, language specification, function reference, troubleshooting pages, component reference and regression tests were aligned with this vocabulary. A scan of live `.mana` files found no statement-leading `import`, `return`, `pass`, `range`, or `len` forms. The current docs mention old names only to explain that they are not supported MANA forms.

## 2. Grimoire and runtime separation

- The MANA source/development archive and Grimoire portable application are separate downloads.
- The MANA source project keeps its Python implementation, tests, examples, libraries, documentation, Grimoire source for maintainers, and VS Code extension source/package.
- The Grimoire user ZIP contains a native `Grimoire.exe`, a `VERSION` marker and `START_HERE.txt`; it does not contain the MANA source tree or a separate `MANA.exe`.
- The native launcher is built with Go's Windows GUI target and embeds the Grimoire interface source in the executable. It extracts that interface to a temporary directory, detects a Python 3 interpreter that can import `tkinter`, and starts the interface without opening a console window.
- This is a portable, non-installing **preview**, not a self-contained Python distribution: the target Windows machine still needs Python 3 with Tcl/Tk. The EXE was cross-compiled on Linux as a Windows PE32+ GUI application but could not be launched on a real Windows host here. Windows execution must be checked by the recipient.
- The old PyInstaller `.spec`, entry-point, build-python and batch-wrapper files were removed. No PyInstaller artifact is required for the new launcher.

## 3. File organisation

- Current documentation points to this audit under `docs/archive/audits/`; audit material is not stored at the project root.
- `tools/windows/grimoire-launcher/` contains the native launcher's Go source and maintainer build script.
- Generated payload staging is temporary and is removed by the build script. It is not included in the source archive.
- Generated caches, build output and executables are excluded from the MANA source ZIP. The Grimoire EXE has its own ZIP.

## 4. Verification performed

- Regression suite: **286 tests passed** after the final source/documentation updates.
- All current documentation examples are covered by the project's example-smoke tests; fragments and expected failures are explicitly labelled.
- `compileall` was run on the interpreter, Grimoire source and library builder.
- VS Code extension package metadata and packaged VSIX version were checked against `VERSION`.
- Go cross-compilation produced a PE32+ Windows GUI executable (`amd64`). The launcher code and ZIP layout were inspected; actual launch behaviour on Windows remains unverified.
- A source scan found no live `.mana` files using the removed statement/builtin forms at the start of a statement. Historical audit reports remain archived and are not treated as current syntax documentation.
- Ruff/Pyflakes were not available in this environment, so no claim is made that either external linter ran. Compilation, automated tests and targeted repository scans were used instead.

## 5. Known limitations

1. Grimoire's portable preview relies on Python 3 and Tcl/Tk already being installed on Windows. It does not bundle the Python runtime.
2. The Windows EXE has not been interactively tested on Windows; the recipient should run it and report any startup diagnostic.
3. The source project still includes Python implementation code until the language reaches v1.0, as intended. Users can edit and run `.mana` files through Grimoire without manually invoking Python.
