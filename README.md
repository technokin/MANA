<p align="center">
  <img src="assets/branding/mana-icon.png" alt="MANA logo" width="176" />
</p>

<h1 align="center">MANA — Magic Programming Language</h1>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="LICENSE"><img alt="License: GPL-3.0-only" src="https://img.shields.io/badge/license-GPL--3.0--only-blue.svg"></a>
  <a href="VERSION"><img alt="Version 1.0.0" src="https://img.shields.io/badge/version-1.0.0-orange.svg"></a>
  <a href="examples/"><img alt="MANA source files" src="https://img.shields.io/badge/source-.mana-purple.svg"></a>
</p>

**MANA is a magic programming language for writing spells in code.** MANA programs use their own syntax and are saved as `.mana` files. They define calculations, spell behaviour, target contexts, transformations, motion, and supported physical effects.

MANA's current interpreter is implemented in Python. Python is the implementation language, not the language you write MANA programs in. The runtime currently uses only Python's standard library.

> **Release: v1.0.0.** This is the first 1.0 release of the current language implementation. MANA still has documented limits in parts of its world simulation and magic systems; check [Implementation Status](docs/current/foundations/IMPLEMENTATION_STATUS.md) and [Not Supported Yet](docs/current/foundations/NOT_SUPPORTED_YET.md) before depending on a specific feature.

## Contents

- [Requirements](#requirements)
- [Quick start](#quick-start)
- [VS Code support](#vs-code-support)
- [Run checks and tests](#run-checks-and-tests)
- [What is included](#what-is-included)
- [Documentation](#documentation)
- [Repository layout](#repository-layout)
- [Development files explained](#development-files-explained)
- [License](#license)
- [Contributing](#contributing)

## Requirements

- **Python 3.12 or newer** to run the interpreter from source ([download Python](https://www.python.org/downloads/)). GitHub Actions is configured to test Python 3.12, 3.13, 3.14, and 3.15 on Windows and Linux. We recommend using the latest stable Python release; Python 3.15 is the latest stable release at the time of this release packaging. On Windows, ensure Python is available as `python` or `py`.
- **No third-party runtime packages** are currently required. MANA uses Python's standard library.
- **An editor** of your choice. VS Code users can install the included optional MANA Language Support extension. Other editors can also edit `.mana` files.

`requirements.txt` is the list for runtime third-party packages. It intentionally contains no package entries today because the runtime does not need external dependencies. `requirements-dev.txt` installs the optional tools used to run tests and check contributor code; it is not required just to use MANA.

## Quick start

Run these commands from the repository root. On Windows, use `py` instead of `python` if that is how Python is installed.

```powershell
# Check Python
python --version

# Run an example MANA program
python mana.py examples/fireball.mana

# Check syntax without executing the program
python mana.py --check examples/fireball.mana
```

Start with the [Ten-Minute Tutorial](docs/current/getting_started/TEN_MINUTE_TUTORIAL.md) and the programs in [`examples/`](examples/).

## VS Code support

The optional extension is named **MANA Language Support**. It adds syntax highlighting, comments, indentation, bracket matching, snippets, and the MANA logo. It is editor support only: the Python interpreter runs MANA programs.

To install the packaged extension:

1. Open VS Code and go to **Extensions**.
2. Open the `...` menu and choose **Install from VSIX...**.
3. Select [`installers/vscode/mana-language-1.0.0.vsix`](installers/vscode/mana-language-1.0.0.vsix).
4. Open a `.mana` file. Run the active file with the **MANA: Run current file** workspace task, or use `python mana.py path/to/file.mana` in a terminal.

To rebuild the extension package after changing its source, grammar, snippets, metadata, or icon:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_vsix.py --check
```

Extension source lives in [`tools/vscode-extension/`](tools/vscode-extension/). The extension does not require a custom MANA IDE.

## Run checks and tests

Install the optional developer tools first:

```powershell
python -m pip install -r requirements-dev.txt
```

Then run the full test suite and main checks:

```powershell
python -m pytest -q
ruff check magiclang tests tools mana.py
python tools/version_sync.py --check
python tools/sync_documentation_outputs.py --check
python tools/generate_reference_index.py --check
python tools/generate_error_catalogue.py --check
python mana.py --check examples/fireball.mana
```

`pytest` runs the regression tests. **Ruff** checks Python source for common bugs and style issues; it can also format Python code. Ruff is a development tool, not a MANA runtime dependency. Its settings are in [`ruff.toml`](ruff.toml). The [test guide](tests/README.md) describes test coverage and focused commands.

## What is included

- A MANA lexer, parser, language diagnostics, and interpreter.
- Ordinary `def` functions and `spldef` spell definitions.
- MANA operations and statements including `incant`, `tgset`, `post`, `release`, `load`, `skip`, `span`, and `length`.
- Four foundational elements: Fire, Water, Earth, and Air, plus pure-mana operations and conceptual catalogues.
- Libraries for mana effects, 2D geometry, plane/pathway records, summoning, necromancy, and 3D vector calculations.
- A developing 2D physics/world simulation, energy bookkeeping, examples, stress tests, and regression tests.
- Optional VS Code language support and a packaged VSIX installer.

Names and examples do not imply that every envisioned subsystem is a complete simulator. See the implementation-status and limitations pages linked above.

## Documentation

- **[MANA Introduction](MANA_INTRO.md):** purpose and foundational concepts.
- **[Documentation Index](docs/current/INDEX.md):** complete documentation map.
- **[Language Guide](docs/current/getting_started/LANGUAGE_GUIDE.md):** learn to write MANA.
- **[Language Specification](docs/current/language/LANGUAGE_SPEC.md):** syntax and semantics.
- **[Function Reference](docs/current/reference/FUNCTION_REFERENCE.md):** implemented built-ins and signatures.
- **[MANA Cheat Sheet](docs/current/reference/MANA_CHEAT_SHEET.md):** keywords, operators, units, and reserved names.
- **[Library guides](docs/current/libraries/):** library behaviour and requirements.
- **[Implementation Status](docs/current/foundations/IMPLEMENTATION_STATUS.md):** implemented, partial, and planned functionality.
- **[Not Supported Yet](docs/current/foundations/NOT_SUPPORTED_YET.md):** known boundaries.
- **[Troubleshooting](docs/current/troubleshooting/TROUBLESHOOTING.md):** common setup and runtime errors.
- **[Release checklist](docs/current/RELEASE_CHECKLIST.md):** release verification steps.
- **[Contributing](CONTRIBUTING.md):** how to report bugs, improve docs, and propose changes.
- **[Changelog](CHANGELOG.md):** release history.
- **[v1.0.0 Release Verification Report](docs/archive/audits/release_reports/RELEASE_V1_0_0_REPORT.md):** checks run and known verification limits.

## Repository layout

```text
MANA/
├── README.md                 # GitHub landing page, setup, and links
├── MANA_INTRO.md             # Separate conceptual introduction
├── LICENSE                   # GPL-3.0-only licence text
├── VERSION                   # Single current-version source (1.0.0)
├── mana.py                   # Command-line interpreter and syntax checker
├── magiclang/                # Lexer, parser, runtime, physics, units, libraries
├── libraries/                # User/project library packages and library notes
├── examples/                 # Runnable .mana programs
├── tests/                    # Regression, stress, example, and tooling tests
├── docs/
│   ├── current/              # Maintained language/runtime documentation
│   ├── ideas/                # Proposals, not release promises
│   └── archive/              # Historical audits and release reports
├── tools/
│   ├── vscode-extension/     # VS Code extension source
│   ├── vscode/               # VSIX build/validation script
│   ├── generate_*.py         # Documentation/reference generators
│   └── version_sync.py       # Version-label consistency check
├── installers/vscode/        # Versioned VSIX distribution
├── assets/branding/          # MANA logo source
├── requirements.txt          # Runtime third-party dependencies (none today)
├── requirements-dev.txt      # Optional test and lint tools
├── ruff.toml                 # Ruff lint/format rules
├── .editorconfig             # Shared editor indentation/line-ending rules
├── .gitattributes            # Git text/binary and line-ending rules
└── .gitignore                # Files Git should not track
```

## Development files explained

- **`requirements.txt`** lists external packages needed to run the MANA interpreter. It is intentionally empty of package entries while MANA uses only Python's standard library.
- **`requirements-dev.txt`** lists optional maintainer tools, currently pytest and Ruff. Installing it is only necessary to run tests or code-quality checks.
- **Ruff** is a Python code checker (and formatter). It helps contributors find common mistakes and keep style consistent; it does not execute MANA programs and is not required by users.
- **`.editorconfig`** asks compatible editors to use consistent text encodings, line endings, indentation, and whitespace. It does not affect program execution.
- **`ruff.toml`** stores Ruff's project rules. We do not need a `pyproject.toml` just to configure Ruff.
- **`.gitignore`** keeps generated files, local environments, and caches out of Git commits. The versioned VSIX is intentionally kept as a release artifact.

## License

MANA is distributed under the **GNU General Public License v3.0 only (GPL-3.0-only)**. See [`LICENSE`](LICENSE). The VS Code extension uses the same license.

## Contributing

MANA is an open project, and contributions are welcome. You can help by reporting reproducible bugs, adding regression tests, improving documentation, building small example spells, reviewing language behaviour, or improving VS Code syntax support.

Before changing language syntax or spell semantics, read the language specification and contributing guide. For code changes, please run the test suite and relevant checks, describe the behaviour changed, and include an example when useful. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md); open an issue in the repository to discuss a bug or proposal, or submit a pull request for a focused improvement.

**Want to help build MANA?** Contributions of all sizes are welcome. Report a bug, suggest an improvement, improve the docs or examples, or open a pull request. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and help us make MANA better.
