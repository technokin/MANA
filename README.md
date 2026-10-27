<p align="center">
  <img src="assets/branding/mana-icon.png" alt="MANA logo" width="176" />
</p>

<h1 align="center">MANA — Magic Programming Language</h1>

<p align="center">
  <a href="https://www.python.org/"><img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="LICENSE"><img alt="License: GPL-3.0-only" src="https://img.shields.io/badge/license-GPL--3.0--only-blue.svg"></a>
  <a href="VERSION"><img alt="Version 2.0.0" src="https://img.shields.io/badge/version-2.0.0-orange.svg"></a>
  <a href="examples/"><img alt="MANA source files" src="https://img.shields.io/badge/source-.mana-purple.svg"></a>
</p>

**MANA is a magic programming language for writing spells in code.** MANA programs use their own syntax and are saved as `.mana` files. They define calculations, spell behaviour, target contexts, transformations, motion, and supported physical effects.

New to MANA's magical model? Start with the [magic-first introduction](MANA_INTRO.md), then read the [Magic System Compendium](docs/current/foundations/MAGIC_SYSTEM_COMPENDIUM.md) for detailed definitions of spells, elements, conjuration, summoning, planes, pathways, weather, and world laws. For physical matter, custom alloys, equipment and metal magic, see [Materials and Forging](docs/current/libraries/MATERIALS_AND_ARMORY.md); for organs, blood magic, transformation, death and revival, see [Physiology and Body Magic](docs/current/libraries/PHYSIOLOGY_LIBRARY.md). The separate [MANA Magic Inspiration Catalogue](MANA_MAGIC_INSPIRATION_CATALOGUE.md) collects future spell concepts and is intentionally not a changelog.

MANA's current interpreter is implemented in Python. Python is the implementation language, not the language you write MANA programs in. The runtime currently uses only Python's standard library.

> **MANA source/package version: v2.0.0.** This source package contains the interpreter, libraries, examples, documentation, and optional VS Code extensions. GitHub Actions workflow files and the bundled automated test suite are not included in this package. The existing [v1.0.0 release](https://github.com/technokin/MANA/releases/tag/v1.0.0) remains available. Check [Implementation Status](docs/current/foundations/IMPLEMENTATION_STATUS.md) and [Not Supported Yet](docs/current/foundations/NOT_SUPPORTED_YET.md) for the exact feature boundaries.

## Contents

- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Visualiser graphics and resource use](#visualiser-graphics-and-resource-use)
- [VS Code support](#vs-code-support)
- [Build VS Code packages](#build-vs-code-packages)
- [What is included](#what-is-included)
- [Documentation](#documentation)
- [Repository layout](#repository-layout)
- [Development files explained](#development-files-explained)
- [License](#license)
- [Contributing](#contributing)
- [What can I build with MANA?](#what-can-i-build-with-mana)
- [Materials, equipment, and body magic](#materials-equipment-and-body-magic)

## Requirements

- **Python 3.12 or newer** to run the interpreter from source ([download Python](https://www.python.org/downloads/)). We recommend using a current stable Python release compatible with the project. On Windows, ensure Python is available as `python` or `py`.
- **No third-party runtime packages** are currently required. MANA uses Python's standard library.
- **An editor** of your choice. VS Code users can install the included optional MANA Language Support extension. Other editors can also edit `.mana` files.

`requirements.txt` is reserved for runtime third-party packages. It currently contains no package entries because the runtime does not need external dependencies.

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

## Visualiser graphics and resource use

The 2D Visualiser uses one automatic graphics policy rather than manual quality tiers. Spell silhouettes remain readable while trail/particle detail adapts to measured frame cost. The main canvas backing store has a hard 4-million-pixel cap, event parsing cache and motion tracks are bounded, and hidden-webview idle animation pauses. These controls limit known avoidable work but cannot guarantee identical FPS or total RAM use on different graphics hardware.

## VS Code support

The optional **MANA Language Support** extension adds syntax highlighting, comments, indentation, bracket matching and inline completions while you type. The editor toolbar stays limited to two actions when both extensions are installed: **Run** and **Visualiser**. Run executes the `.mana` file and sends output to the MANA output panel. Visualiser runs it with recording enabled and opens the recorded scene. The interpreter still works from the terminal without either extension.

To install the packaged extension:

1. Open VS Code and go to **Extensions**.
2. Open the `...` menu and choose **Install from VSIX...**.
3. Select [`installers/vscode/mana-language-2.0.0.vsix`](installers/vscode/mana-language-2.0.0.vsix).
4. Open a `.mana` file and click **Run** in the editor toolbar, or run **MANA: Run File** from the Command Palette. The command does not start a debugger. You can also use `python mana.py path/to/file.mana` in a terminal.

To rebuild the extension packages after changing their source, grammar, completion logic, metadata, or icons, use the build commands in [Build VS Code packages](#build-vs-code-packages).

The language extension source lives in [`tools/vscode-extension/`](tools/vscode-extension/); the Visualiser source is in [`tools/mana-visualiser-extension/`](tools/mana-visualiser-extension/). See the [VS Code Extension Guide](docs/current/tooling/VSCODE_EXTENSION_GUIDE.md) for installation, settings, editor actions and troubleshooting. The extensions do not require a custom MANA IDE.

### Optional Magic Visualiser

The separate **MANA Magic Visualiser** replays a recorded run as a magical 2D scene. It is deliberately not a science-style dashboard: entity names are shown, distance is one value, and a contact flash appears only when the runtime reports an actual contact. It has no plane view, portal visuals, energy-flow arrows or mana-fuel meter. The Visualiser remains a record-and-replay viewer, not a live world editor.

Install [`mana-magic-visualiser-2.0.0.vsix`](installers/vscode/mana-magic-visualiser-2.0.0.vsix) from **Extensions → … → Install from VSIX…**. Open a `.mana` file in the MANA project and click **Visualiser** in the editor toolbar, or open an existing JSONL recording with **MANA: Open Visualiser Recording**. From a terminal, create a recording with:

```powershell
python mana.py --record fireball.jsonl examples/fireball_contact.mana
```

The recording is an internal replay file for the optional Visualiser, not a public game-integration API. See [Where MANA Could Be Used](docs/current/foundations/FUTURE_USES_AND_ROADMAP.md) for possible application areas and the longer-term roadmap. For replay controls, see the [Visualiser guide](docs/current/tooling/MAGIC_VISUALISER.md).

## Build VS Code packages

The installable VSIX files are included under `installers/vscode/`. To rebuild both extensions after editing their source, run the builders and package utility from the project root:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_visualiser_vsix.py
python tools/package_project_zip.py
```

The source ZIP does not include GitHub Actions workflows, a bundled test suite, or separate lint/audit dependencies. The interpreter remains usable directly with Python and does not require either VS Code extension.

## What is included

- A MANA lexer, parser, language diagnostics, and interpreter.
- Ordinary `def` functions and `spell` declarations (`spldef` remains a backward-compatible alias).
- MANA operations and statements including `incant`, `tgset`, `appraise`, `cast`, `load`, `skip`, `span`, and `length`; legacy `post(...)` and `release(...)` remain supported.
- Four foundational elements: Fire, Water, Earth, and Air, plus pure-mana operations and conceptual catalogues.
- Built-in libraries for pure mana, 2D geometry, 3D vector calculations, weather and matter, materials and metals, equipment, anatomy, physiology, arcana, planes, summoning, and necromancy.
- A developing 2D world solver with motion, collisions, supported thermal and material-state effects, energy bookkeeping, and explicit resource limits.
- Expanded material and creature catalogues, including comparative body plans. Catalogue values are reference/gameplay data, not a complete chemistry or biology simulator.
- A set of 67 runnable examples, generated references, and optional editor tools.
- Two independent optional VS Code extensions: language support and the Magic Visualiser. Neither is required to run `.mana` programs.

Names and examples do not imply that every envisioned subsystem is a complete simulator. See the implementation-status and limitations pages linked above.

## Documentation

- **[MANA Introduction](MANA_INTRO.md):** a magic-first introduction to mana, elements, spells, summoning, planes, pathways, matter, weather, and world laws.
- **[MANA Magic System Compendium](docs/current/foundations/MAGIC_SYSTEM_COMPENDIUM.md):** the extensive conceptual reference, with definitions, relationships, current limitations, and links to implemented rules.
- **[Documentation Index](docs/current/INDEX.md):** complete documentation map.
- **[Language Guide](docs/current/getting_started/LANGUAGE_GUIDE.md):** learn to write MANA.
- **[Building Your First Spells](docs/current/getting_started/BUILDING_FIRST_SPELLS.md):** worked examples from objects to summoning.
- **[Language Specification](docs/current/language/LANGUAGE_SPEC.md):** syntax and semantics.
- **[Function Reference](docs/current/reference/FUNCTION_REFERENCE.md):** implemented built-ins and signatures.
- **[MANA Cheat Sheet](docs/current/reference/MANA_CHEAT_SHEET.md):** keywords, operators, units, and reserved names.
- **[Library guides](docs/current/libraries/):** library behaviour and requirements, including [Anatomy](docs/current/libraries/ANATOMY_LIBRARY.md), [Physiology and Body Magic](docs/current/libraries/PHYSIOLOGY_LIBRARY.md), [Materials and Armory](docs/current/libraries/MATERIALS_AND_ARMORY.md), [Arcana](docs/current/libraries/ARCANA_LIBRARY.md), and [World Weather and Matter](docs/current/libraries/WORLD_WEATHER_AND_MATTER.md).
- **[Implementation Status](docs/current/foundations/IMPLEMENTATION_STATUS.md):** implemented, partial, and planned functionality.
- **[Not Supported Yet](docs/current/foundations/NOT_SUPPORTED_YET.md):** known boundaries.
- **[Troubleshooting](docs/current/troubleshooting/TROUBLESHOOTING.md):** common setup and runtime errors.
- **[Contributing](CONTRIBUTING.md):** how to report bugs, improve docs, and propose changes.
- **[Security policy](SECURITY.md):** how to report suspected vulnerabilities and the boundaries of code execution.
- **[Security and runtime boundaries](SECURITY_AUDIT.md):** a summary of runtime limitations and safe-use boundaries.
- **[Changelog](CHANGELOG.md):** the cumulative release history, including the changes since the public v1.0.0 source tag.
- **[MANA 2.0.0 Source Snapshot Notes](docs/current/RELEASE_V2_0_0_REPORT.md):** what is included in this package and its scope boundaries.
- **[MANA 2.0.0 Release Log](MANA_v2.0.0_RELEASE_LOG.md):** historical plain-English release notes.

## Repository layout

```text
MANA/
├── README.md                 # GitHub landing page, setup, and links
├── MANA_INTRO.md             # Separate conceptual introduction
├── MANA_MAGIC_INSPIRATION_CATALOGUE.md # Future design ideas, not release history
├── MANA_v2.0.0_RELEASE_LOG.md # Historical notes for the 2.0.0 snapshot
├── CHANGELOG.md              # Cumulative release history
├── CONTRIBUTING.md            # Contribution workflow and style
├── SECURITY.md               # Security-reporting policy and execution limits
├── SECURITY_AUDIT.md          # Security and runtime boundaries
├── LICENSE                   # GPL-3.0-only licence text
├── VERSION                   # Single current-version source (2.0.0)
├── mana.py                   # Command-line interpreter and syntax checker
├── magiclang/                # Lexer, parser, runtime, physics, units, libraries
├── libraries/                # User/project library packages and library notes
├── examples/                 # Runnable .mana programs (67 examples)
├── docs/
│   ├── current/              # Maintained language/runtime documentation
│   ├── ideas/                # Proposals, not release promises
│   └── archive/              # Historical audits and release reports
├── .github/                  # Release notes; no Actions workflows included
├── tools/
│   ├── vscode-extension/     # MANA editing, Run/Check, hover and completion
│   ├── mana-visualiser-extension/ # Optional magic-first scene replay
│   ├── vscode/               # VSIX build scripts
│   ├── generate_*.py         # Documentation/reference generators
│   ├── package_project_zip.py # Clean source ZIP with both VSIX installers
│   └── sync_documentation_outputs.py # Documentation output generator
├── installers/vscode/        # Versioned VSIX distribution
├── assets/branding/          # MANA logo source
├── requirements.txt          # Runtime third-party dependencies (none today)
├── .editorconfig             # Shared editor indentation/line-ending rules
├── .gitattributes            # Git text/binary and line-ending rules
└── .gitignore                # Files Git should not track
```

## Development files explained

- **`requirements.txt`** lists external packages needed to run the MANA interpreter. It is intentionally empty of package entries while MANA uses only Python's standard library.
- **`.editorconfig`** asks compatible editors to use consistent text encodings, line endings, indentation, and whitespace. It does not affect program execution.
- **`tools/package_project_zip.py`** builds a clean source ZIP, keeps both VSIX installers inside it, and excludes caches and generated files. ZIPs are made from files only, so empty source folders are not carried across.
- **[Project file map](docs/current/tooling/PROJECT_LAYOUT.md)** explains where source, docs, examples, extension code, and packaged VSIX files belong.
- **`.gitignore`** keeps generated files, local environments, and caches out of Git commits. The versioned VSIX is intentionally kept as a release artifact.

## License

MANA is distributed under the **GNU General Public License v3.0 only (GPL-3.0-only)**. See [`LICENSE`](LICENSE). The VS Code extension uses the same license.

## Contributing

MANA is an open project, and contributions are welcome. You can help by reporting reproducible bugs, improving documentation, building small example spells, reviewing language behaviour, or improving VS Code syntax support.

Before changing language syntax or spell semantics, read the language specification and contributing guide. Describe behaviour changes clearly and include a small `.mana` example when useful. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md); open an issue in the repository to discuss a bug or proposal, or submit a pull request for a focused improvement.


## What can I build with MANA?

MANA is a language and small 2D simulation for describing magical behaviour. You can write a spell, run it, and inspect whether the runtime reports an impact or changes an object. It is useful for exploring rules and sketching spell behaviour, but it is not a finished game engine and does not include a supported external-engine integration.

Here is a small example using the v2 `spell` declaration to send a fire spell at a training target:

```mana
load geometry2d

training_knight = tgset:
    hp = 100
    max_hp = 100
    defence = 0
    pos = geometry2d.point(10 m, 0 m)

spell ember_shot():
    ember = create Fire
    shape(ember, circle)
    velocity(ember, 100 m/s)
    incant ember

tgset(training_knight):
    cast ember_shot
```

Run a source file with `python mana.py examples/fireball.mana`. To create a local replay for the optional Visualiser, use `python mana.py --record fireball.jsonl examples/fireball.mana`. The recording contains scene changes, real contact events, visual effects and spell outcomes. It is an internal viewer format, not a stable interface for game engines or third-party tools.

See [Where MANA Could Be Used](docs/current/foundations/FUTURE_USES_AND_ROADMAP.md) for possible applications and future plans, and the [Visualiser guide](docs/current/tooling/MAGIC_VISUALISER.md) for how to record and replay a spell.

## Materials, equipment, and body magic

MANA includes a read-only 118-element reference table, world-local custom alloy definitions, reusable equipment blueprints, magnetic-response-based metal control, and a fictional physiology library for body-form changes, blood-state effects, injuries, enhancements, death and revival. Read [Materials and Forging](docs/current/libraries/MATERIALS_AND_ARMORY.md), [Anatomy and Comparative Biology](docs/current/libraries/ANATOMY_LIBRARY.md), [Comparative Anatomy Research](docs/current/libraries/COMPARATIVE_ANATOMY_RESEARCH.md), [Physiology and Body Magic](docs/current/libraries/PHYSIOLOGY_LIBRARY.md), [Arcana: Magical Disciplines](docs/current/libraries/ARCANA_LIBRARY.md), and the separate [MCU/DC-Inspired Magic Catalogue](MANA_MAGIC_INSPIRATION_CATALOGUE.md) for detailed mechanics and ideas. The catalogue is inspiration and design guidance, not a promise that every listed spell already exists.
