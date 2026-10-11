# MANA v0.10.14 — Documentation and Packaging Audit

**Scope:** documentation structure, foundation coverage, current-version consistency, runnable documentation examples, relative links, source tests, and the Grimoire portable-build contract.

## Summary

This release focuses on making the project understandable as a language and system—not merely as a list of functions. The root README is intentionally brief for repository visitors. `MANA_INTRO.md` explains the central idea and core foundations, while `docs/current/` remains the detailed reference set.

## Documentation changes

- Added a standalone introduction covering mana, four base elements, pure mana, objects/physics, planes/pathways, beings, necromancy, ordinary functions, spells, target context, and design-versus-implementation boundaries.
- Added a conceptual-domain guide distinguishing base elements, specialised/derived labels, conceptual domains, plane/channel names, and pure-mana operations.
- Added a plane catalogue covering all 13 elemental/special plane records, the other top-level planes, Hell's current regions, pathways, invocation, and explicit non-goals.
- Added a creature catalogue listing all 13 spirit records and the 8 other built-in being records with their current prototype statistics and limitations.
- Updated the documentation index, foundations reading order, extension references, component references, troubleshooting links, and version markers to v0.10.14.
- Corrected the recall example to pass the original tamed being object to `summoning.call`; the current implementation does not recall by a string name.
- Kept older audits and superseded design notes under `docs/archive/`.

## Source-grounded boundaries documented

- MANA is currently implemented in Python, but `.mana` is the user-facing language.
- `def` is for ordinary functions; `spldef` defines spells; `tgset` supplies target context; `incant` is the result statement; `load` imports libraries; `span`, `length`, and `skip` are MANA vocabulary.
- Mana is not a finite personal pool. Invocation grants channel permission; energy ledger amounts are bookkeeping/physical accounting.
- Fire, Water, Earth, and Air are the four base elements. Specialised labels and conceptual domains are not automatically base elements.
- `planes` identifies and connects planes and records energy transfers; `drafter` creates custom records; `summoning.bring` transfers a defined being; `necromancy.reanimate` requires existing remains.
- The world solver is 2D. `geometry2d` and `vector3d` are calculation libraries; the latter does not create a 3D world simulation.
- Creature statistics and several physics behaviours are prototype values/rules, not a complete combat or world simulator.

## Automated checks

- Test suite: **286 passed** using `python -m pytest -q`.
- Documentation examples: all standalone current `.mana` fenced examples accepted by the documentation smoke test; intentionally partial/invalid fragments retain their markers.
- Relative Markdown links in the root README, `MANA_INTRO.md`, `docs/README.md`, and `docs/current/`: **0 broken relative links** at audit time.
- Formatting scan across 44 current/root documentation files: **0 broken links, 0 unbalanced fenced-code blocks, 0 trailing-whitespace findings**.
- Version references in current documentation and extension metadata: updated to **0.10.14**.
- VS Code VSIX: rebuilt as `installers/vscode/mana-language-0.10.14.vsix` and package integrity/version checked.
- Python compilation: `python -m compileall -q magiclang grimoire tools mana.py grimoire.py` completed successfully.

## Formatting review

- Markdown uses ATX headings, fenced code blocks with language identifiers, and tables for comparable structured data.
- Root README is kept short; the longer conceptual explanation is separated into `MANA_INTRO.md` and the foundations handbook.
- `.editorconfig` defines consistent line endings and indentation. Ruff is configured in `pyproject.toml`, but Ruff itself was not installed in the execution environment, so a Ruff lint/format command could not be run here.

## Grimoire standalone EXE status — important

The intended build uses a native Go launcher embedding a ZIP payload containing Grimoire, the MANA interpreter/runtime, Windows CPython, Tcl/Tk, and the current app resources. There is no separate user-facing `MANA.exe` and no PyInstaller build.

The Windows build script is `tools/windows/grimoire-launcher/build.ps1`. It must be run on a Windows build host with Go and a full supported Windows Python installation including Tcl/Tk. The resulting target EXE is intended to run on a computer without Python or a downloaded MANA source folder.

**The final self-contained Windows EXE is not certified by this audit.** This audit environment is Linux and does not have the Windows CPython/Tcl/Tk runtime needed to assemble the embedded payload, nor a Windows host on which to launch-test the result. The previously available small launcher binary must not be represented as self-contained unless rebuilt with the payload and verified on a clean Windows machine. A successful Windows release test must open Grimoire, create/edit/save a `.mana` file, execute it, run library-backed examples, and confirm no host Python/MANA checkout is required.

## Remaining release work

1. Build the Grimoire payload on Windows with the documented build script.
2. Test the resulting executable on a clean Windows account/VM without Python installed.
3. Verify bundled CPython/Tcl/Tk and Go license notices match the exact runtime versions included.
4. Run Ruff lint/format checks on a host where Ruff is installed.

Do not remove the caveat above until those checks are completed.
