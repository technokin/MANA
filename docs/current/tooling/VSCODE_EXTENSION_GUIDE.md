# Using MANA in VS Code

**Page kind:** How-to

MANA has two separate VS Code extensions. **MANA Language Support** helps you write and run `.mana` files. **MANA Magic Visualiser** records an execution and replays the spell as a scene. You can install either one, both, or neither.

## Install from the project ZIP

Both packages are included under `installers/vscode/`:

- `mana-language-2.0.0.vsix`
- `mana-magic-visualiser-2.0.0.vsix`

In VS Code, open Extensions with `Ctrl+Shift+X`, choose the menu button (`...`), and select **Install from VSIX...**. Select the extension package you want. Reload the window if VS Code asks you to.

The same MANA logo is used for the language extension and Visualiser. The project keeps the canonical image at `assets/branding/mana-icon.png`; each VSIX packages it at `images/mana-icon.png` so the icon is available to VS Code and its extension details page.

## Write, check and run

Open the MANA project folder, then open a `.mana` file from it. The status bar should identify the file's language as **MANA**.

- **Run** (the triangle) executes the saved file as a normal process. It does not start the debugger and does not open the Visualiser.
- **Check** parses the saved file without executing its statements.
- **Stop Run** stops an active MANA process.
- **Open Quick Start** opens the tutorial.
- **Open Examples** opens the example catalogue.
- **Open Function Reference** opens the built-in operation reference.
- **Insert Spell** and **Insert Target Profile** insert editable starter templates.

Completion suggests common keywords, operations, elements, units, shapes and library functions. Hover over known words for short explanations. The Outline view lists spell/function definitions, target profiles and woven constructs. Quick fixes can convert `create Mana` to `weave mana`, `range()` to `span()`, and `len()` to `length()` when those forms appear in the current line.

The editor buttons only call the included interpreter. They do not require a project-specific executable, network service, or debugger configuration.

## Choose a Python command

The source interpreter currently needs Python 3.12 or newer. Open VS Code Settings, search for **MANA: Python Path**, and set the command if your system uses something other than `python`.

Examples:

```powershell
python --version
python mana.py examples\fireball.mana
```

On Windows, `py` may be available instead. In Settings, `mana.pythonPath` is the command, not the path to a `.mana` file.

## Open the Visualiser only when you ask for it

The eye-shaped **Visualiser** button belongs to the second extension. It launches MANA with recording enabled and opens the replay when execution finishes. If you do not click it, the viewer does not run. The interpreter works even if the Visualiser is not installed.

The replay includes names, spell effects and genuine contact events. It intentionally omits world coordinates, scientific vectors, energy-flow diagrams, plane workspaces and portals. `post(spell, visual)` records a hypothetical preview; it must not commit the previewed changes to the world. `release(spell)` commits successful effects.

A CLI recording can be opened later with **MANA: Open Visualiser Recording**:

```powershell
python mana.py --record fireball.jsonl examples\fireball_contact.mana
```

## If VS Code shows a blank extension details page

The installed VSIX should contain `extension/README.md`, `extension/package.json`, `extension/images/mana-icon.png` and an `extension.vsixmanifest` that points the details asset to the README. Rebuild both packages from the project root:

```powershell
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_visualiser_vsix.py
```

The build scripts verify the package version, README, icon and archive contents. If you changed the source code but are still seeing an older installed extension, uninstall the old copy, install the newly built VSIX, then reload VS Code.

## Run outside VS Code

Neither extension is required. Use the terminal or any editor:

```powershell
python mana.py examples\fireball.mana
python mana.py --check examples\fireball.mana
```

For a source-level change, run the tests and rebuild the extensions. The extension provides convenience features; it does not change what the MANA interpreter accepts or what the physics engine decides.
