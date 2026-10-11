# Python Runtime and Development Tools

**Page kind:** Explanation

**Current source version:** v1.0.0

MANA is a language with its own `.mana` source syntax, lexer, parser, runtime, and semantics. The current implementation of that language is written in Python. Python is therefore required to execute MANA programs from this source project, but MANA programs are not written in Python.

## Running the language

The supported source entry point is `mana.py`:

```powershell
python mana.py examples/fireball.mana
python mana.py --check examples/fireball.mana
```

The runtime currently depends only on Python's standard library. The `--check` option reads, lexes, and parses a source file without executing its statements; it is not a guarantee that runtime operations or physical effects will succeed.

## Editing MANA source

MANA programs are ordinary text files with the `.mana` extension. They can be edited in VS Code or any other editor. The maintained VS Code extension is optional and supplies syntax highlighting, comment toggling, indentation rules, bracket matching, and snippets. It does not parse or execute programs; `mana.py` and `magiclang/` remain authoritative for language behaviour.

## Project boundaries

- `magiclang/` contains the lexer, parser, AST, runtime, units, physics, errors, and built-in libraries.
- `mana.py` is the command-line runner and syntax-check entry point.
- `tools/vscode-extension/` contains VS Code language-support source.
- `tools/vscode/build_mana_vsix.py` builds the installable VSIX.
- `tests/` contains language, physics, library, stress, and documentation checks.
- `docs/current/` is maintained documentation; `docs/archive/` preserves historical audit reports.

There is no separate MANA IDE to install or maintain. Runtime or language changes should normally be made in `magiclang/` and covered by tests. The VS Code extension needs changes only when its highlighting or editing support must be updated.
