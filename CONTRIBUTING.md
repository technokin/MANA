# Contributing to MANA

Contributions are welcome: reproducible bug reports, runnable `.mana` examples, documentation fixes, language-reference improvements, and VS Code syntax support.

## Requirements

- Python 3.12 or newer to run the source interpreter.
- A text editor; VS Code support is optional.
- The runtime has no third-party Python package requirements at present.

## Working on the project

- `.mana` files define the public language behaviour; do not introduce Python syntax as a MANA language feature by accident.
- Read `docs/current/language/LANGUAGE_SPEC.md` before changing grammar or spell semantics.
- Keep general-purpose runtime functions separate from individual spell examples.
- Describe what changed, why it changed, and any limitations in the relevant documentation.
- Keep public examples runnable from the repository root using `python mana.py examples/FILE.mana`.
- The GitHub Actions workflow files and bundled automated test suite are intentionally not part of this source package.

## VS Code extensions

The two optional extensions are built from `tools/vscode-extension/` and `tools/mana-visualiser-extension/`. After editing extension source, rebuild the appropriate installer using one of these commands:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_visualiser_vsix.py
```

The language interpreter does not require the extensions. Keep language semantics in `magiclang/`; keep editor presentation and replay controls in the extension sources.

## Documentation and bug reports

Use `docs/current/INDEX.md` as the main documentation map. Put public runnable programs in `examples/`. Keep statements about implemented behaviour separate from planned design. For a bug report, provide a minimal `.mana` program, the command used, expected behaviour, actual behaviour, and Python version.
