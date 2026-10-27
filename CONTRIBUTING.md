# Contributing to MANA

Thanks for your interest in improving MANA. Contributions are welcome: bug reports, small example programs, regression tests, documentation fixes, language-reference improvements, and VS Code syntax support are all useful.

## Requirements

- Python 3.12 or newer (GitHub Actions is configured to test Python 3.12–3.15).
- Git for source control.
- VS Code is optional; the extension is included for editing `.mana` files.

MANA currently runs with Python's standard library and has no third-party runtime dependencies. For tests and contributor checks, install the optional tools:

```powershell
python -m pip install -r requirements-dev.txt
```

## Before submitting a change

Run the regression suite and the relevant source/documentation checks:

```powershell
python -m pytest -q
ruff check magiclang tests tools mana.py
python tools/version_sync.py --check
python tools/sync_documentation_outputs.py --check
python tools/generate_reference_index.py --check
python tools/generate_error_catalogue.py --check
python mana.py --check examples/fireball.mana
```

If you modify the VS Code grammar, snippets, extension metadata, or branding, rebuild and verify the installable package:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_vsix.py --check
```

## Language and runtime changes

- MANA programs use `.mana` syntax; do not accidentally introduce Python syntax as a language feature.
- Preserve the distinction between ordinary `def` functions and `spell` declarations; keep `spldef` working as a backward-compatible alias.
- `incant` is a MANA statement, not a function; `show` displays output; `post` runs a trial and rolls state back; `release` commits successful spell effects; `tgset` establishes target context outside the spell body.
- Do not add keywords or change spell semantics without a documented reason and appropriate tests.
- Add regression tests for bugs, boundary cases, invalid inputs, and rollback behaviour.
- Update current documentation and expected outputs when observable behaviour intentionally changes. Keep historical audit files in `docs/archive/` as history.

## Documentation and examples

Use `docs/current/INDEX.md` as the main documentation map. Runnable examples belong in `examples/`; test fixtures and failure cases belong in `tests/`. Describe actual implemented behaviour separately from planned design. Do not mark a feature implemented merely because its name appears in a catalogue or example.

## How to contribute

For a bug, provide a minimal `.mana` program, the command used, expected behaviour, actual behaviour, and Python version. For a proposal, explain the problem it solves and how it fits the language's current rules. Pull requests should focus on one change where practical and include relevant tests/documentation updates.

Please discuss language-design changes before implementing them so that keywords and spell semantics remain consistent. All contributions must be compatible with the project's GPL-3.0-only license.

## License

MANA is licensed under the **GNU General Public License v3.0 only (GPL-3.0-only)**. See [`LICENSE`](LICENSE).
