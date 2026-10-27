![MANA logo](images/mana-icon.png)

# MANA Language Support

**Write and run MANA magic programs in VS Code.** This extension provides MANA syntax highlighting, indentation and bracket matching, inline completion suggestions while you type, and a single **Run** action. It is intentionally a small language extension, not a custom IDE.

Install the optional **MANA Magic Visualiser** extension alongside it to add the second editor action, **Visualiser**. With both extensions installed, the `.mana` editor toolbar contains only those two actions.

## Features

- **MANA syntax** — colouring for language keywords, elemental names, shapes, units, libraries and spell definitions.
- **Inline completion** — suggests the next word or namespace member while typing; no extra completion button or dedicated assistant panel.
- **Context-sensitive materials** — inside `conjure(...)` and `transmute(...)`, suggests periodic-table element names/symbols and common material names.
- **Library-aware completions** — includes current names and namespace members for `geometry2d`, `vector3d`, materials, metals, anatomy, physiology, armory, planes, summoning, necromancy, weather and world helpers.
- **Run** — launches the current `.mana` source with the project's interpreter and writes output and errors to the **MANA** Output channel. Clicking Run again stops a running process.
- **Ordinary files, ordinary workflow** — no special editor format, project conversion, or background service. `.mana` source can be edited in any text editor.

## World-engine language helpers

MANA keeps world rules in the runtime, not in the editor extension. The built-in `world` namespace exposes the current physics configuration and rule descriptions:

```mana
load geometry2d
world.configure(
    gravity=geometry2d.direction(0, -1) * 9.81 m/s2,
    air_density=1.225,
    restitution=0.2,
    drag=true,
    thermal_exchange=true,
    phase_changes=true,
    wetting=true
)
show world.laws()
```

Matter operations have separate responsibilities:

- `shape(object, sphere)` changes an object's primitive geometry.
- `conjure("iron", mass=2 kg)` manifests physical matter with mass, volume, density, state and collision data.
- `transmute(object, "gold")` changes its material composition while preserving mass by default.
- `transfigure(object, "knight")` changes the displayed/physical form of a living being or matter originally created by `conjure()`; it is not a replacement for `shape()`.
- The built-in `periodic` namespace provides lookup and reference data for all 118 chemical elements; no `load` is required. Uncertain superheavy-element values are marked as estimates or left unavailable.

Wind, rain, fog, clouds and temperature are adjustable environment parameters under `weather`; they are not separate hard-coded spells. `advance_time()` applies configured gravity, collisions, drag, ambient heat exchange, wetting and supported material phase changes.

## Install from VSIX

1. Open VS Code.
2. Open **Extensions** with `Ctrl+Shift+X`.
3. Open the `...` menu and select **Install from VSIX...**.
4. Choose `installers/vscode/mana-language-2.0.0.vsix` from the MANA project, or choose the standalone file you received.
5. Open a `.mana` file in the MANA project and click **Run**.
6. Install `installers/vscode/mana-magic-visualiser-2.0.0.vsix` the same way to add **Visualiser**.

The `mana.py` runtime must be present in the project. The extension does not bundle Python or the runtime and does not need network access. Configure **MANA: Python Path** in VS Code Settings if your interpreter is called `python3` or `py` instead of `python`.

## Run without the extension

```powershell
python mana.py examples/fireball.mana
python mana.py --check examples/fireball.mana
```

## Extension detail and support

The **Details** page for this VSIX is sourced from this `README.md`. It includes usage, command behavior, supported world APIs and limitations so that locally installed builds have real documentation instead of an empty Details panel.

Source code, syntax grammar, completion provider and package metadata are under `tools/vscode-extension/`. Rebuild with `python tools/vscode/build_mana_vsix.py` and validate the README details asset with `python tools/vscode/build_mana_vsix.py --check`.

## License

GPL-3.0-only. See [`LICENSE.txt`](LICENSE.txt).


## Execution safety

MANA execution is disabled in untrusted VS Code workspaces. The Run command rejects non-regular source files and files larger than 2 MB, starts Python without a shell, passes a reduced environment, caps output at 2 MB, and terminates a run after five minutes. These are defence-in-depth measures, not an operating-system sandbox. Run untrusted programs in a disposable VM/container or low-privilege account.
