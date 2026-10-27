# Python Setup and VS Code — MANA v2.0.0

**Page kind:** How-to

MANA source execution and source editing are separate: Python runs the current interpreter, while an editor is used to write `.mana` files. VS Code support is optional.

## 1. Requirements

- Python 3.12 or newer. GitHub Actions is configured to test Python 3.12, 3.13, 3.14, and 3.15.
- No third-party packages for normal MANA execution; the interpreter currently uses the Python standard library only.
- For tests and development checks, install `requirements-dev.txt`.

Confirm Python is available from the project root:

```powershell
python --version
```

If Windows does not recognise `python`, try the Python launcher:

```powershell
py --version
py mana.py examples\fireball.mana
```

## 2. Run and check a MANA program

```powershell
python mana.py examples\standalone_release.mana
python mana.py --check examples\fireball.mana
python -m pytest -q
```

`--check` verifies lexing and syntax without executing program statements. It does not validate every runtime input or prove a spell will succeed.

## 3. Install the VS Code extension

The extension is named **MANA Language Support**. It recognises `.mana` files and supplies syntax highlighting, comments, indentation, bracket matching, and inline completions. Its only editor toolbar action is Run. Install the optional MANA Magic Visualiser extension for the second action, Visualiser; there is no Check toolbar button.

1. Open VS Code and select **Extensions** (`Ctrl+Shift+X`).
2. Open the `...` menu and select **Install from VSIX...**.
3. Choose `installers\vscode\mana-language-2.0.0.vsix`.
4. Open a `.mana` file and confirm that the language mode is MANA.
5. Click the **Run** triangle in the editor toolbar. MANA runs as a normal process, without a debugger, and writes its output to the MANA panel. You can also use the integrated terminal:

```powershell
python mana.py path\to\file.mana
```

The extension's source is in `tools/vscode-extension/`. Rebuild its package after changing the grammar, snippets, metadata, or icon:

```powershell
python tools/vscode/build_mana_vsix.py
```

The square MANA icon at `assets/branding/mana-icon.png` is included in both extension packages and their extension-listing metadata. The builder re-embeds this icon when rebuilding the VSIX.

## 4. Troubleshooting

- **Python command not found:** install Python 3.12 or newer, then reopen the terminal. Python is needed to run the current source implementation.
- **MANA file is not highlighted:** install the current VSIX and reopen the `.mana` file.
- **A syntax-check succeeds but execution fails:** `--check` does not execute statements. Run the program normally and consult the reported MANA diagnostic and [Error Catalogue](../reference/ERROR_CATALOGUE.md).
- **A custom library cannot load:** verify the project has the expected `libraries/` package directory and consult [Library Builder](../libraries/LIBRARY_BUILDER.md).


## Development-only tooling

`requirements.txt` lists third-party packages needed by the MANA runtime; it currently has no package entries because the runtime uses the Python standard library. `requirements-dev.txt` installs optional test and lint tools. Pytest runs the tests, and Ruff checks Python source for common errors and style issues. Neither is required to run a `.mana` program. `.editorconfig` coordinates indentation, text encoding, and line endings across compatible editors; `ruff.toml` configures Ruff.

## Optional Magic Visualiser

The Visualiser is a second, independent VS Code extension. It records a run only when you click the eye-shaped **MANA: Visual** button. Ordinary Run does not create a recording or open the viewer. MANA still works if the Visualiser is not installed.

Install `installers/vscode/mana-magic-visualiser-2.0.0.vsix` using **Extensions → … → Install from VSIX…**. Open a `.mana` source file in the MANA project, then click the eye-shaped **MANA: Visual** action in the editor toolbar. It records the run and opens the replay when execution finishes. For a terminal recording, use:

```powershell
python mana.py --record fireball.jsonl examples/fireball_contact.mana
```

Open a saved file with **MANA: Open Visualiser Recording**. Use `manaVisualiser.pythonPath` if the Python command on your system is `python3` or `py`. `manaVisualiser.reduceMotion` reduces decorative animation; `manaVisualiser.maximumRecordingMB` controls the largest file the viewer will open.

Use Play/Pause, the previous and next event buttons, Replay, the timeline, and the speed choices Slow motion, Slow, Normal, Fast and Very fast. This version is record-and-replay only. It shows spell effects and genuine contact events without displaying coordinates, energy ledgers, mana-flow graphics, portals or plane diagrams. The recording file is for the Visualiser; it is not a public engine-integration API. To rebuild the two extension packages after edits, run:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_visualiser_vsix.py
```

