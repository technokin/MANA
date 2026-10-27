![MANA logo](images/mana-icon.png)

# MANA Magic Visualiser

**Inspect what a MANA program actually did.** The Visualiser renders the recorded 2D world as a zoomable magical scene with curved projectile paths, animated characters, element-specific spell shapes, real contact reactions, weather and a physical-property inspector. It is an optional VS Code extension; the language runtime works without it.

## Installation

1. In VS Code, open **Extensions** (`Ctrl+Shift+X`).
2. Open the `...` menu and choose **Install from VSIX...**.
3. Select `mana-magic-visualiser-2.0.0.vsix`.
4. Open a `.mana` file inside a MANA project and click the **Visualiser** eye icon in the editor title bar.

Install **MANA Language Support** too for the editor's **Run** action. With both installed, the editor toolbar is deliberately limited to **Run** and **Visualiser**. Run executes normally; Visualiser executes with recording enabled and opens the scene. You can also open an existing `.jsonl` recording from the Command Palette with **MANA: Open Visualiser Recording**. The picker only offers `.jsonl` because that is the supported recording format.

## Scene controls

The scene opens in an expanded editor area by default so it feels like a dedicated window. Closing it restores the normal editor layout. Change **MANA Visualiser: Start Maximised** in settings to disable this behaviour.

- **Pan:** drag the canvas.
- **Zoom:** scroll over the scene or use the +/− controls; the camera zooms around the pointer position.
- **Fit scene:** reset the camera to include recorded objects and their motion.
- **Select an object:** click it to inspect form, material, composition, mass, volume, density, temperature, known melting/boiling points, movement state, health and surface condition when the runtime recorded those values.
- **Scene layers:** the Grid, Names, Magic FX, Spell form and Weather switches can be turned on/off independently. Spell form displays the structured spell body separately from trails/impacts and names the moving spell from runtime records when available. They affect presentation only.
- **Focus target:** centre the camera on the selected object; Fit scene returns to the complete recorded scene.
- **Character view:** expand the canvas across the editor, hide the inspector and focus the selected character. Press `I` or click Character view to toggle it; the button label changes to **Exit character view** while active. Double-click any entity to centre the camera on it. Character silhouettes can be selected by clicking their body as well as through the Objects panel; pointer-based dragging works with mouse, pen and touch devices, and zoom continues to work. Actor silhouettes include generic NPCs, knights, western and eastern dragons, several dinosaur body cues, ants, slimes, minotaurs and serpent/bird/beast forms when the recorded name or form identifies them.
- **Impact stepping:** Previous Impact and Next Impact jump between recorded contacts and selected magic-effect events. Characters briefly stagger only when the recording contains an actual contact; nearby spell art alone never counts as a hit.
- **Objects panel:** search by name, material, element or form; filter living beings, summoned/undead entities, physical materials, mana constructs, anchored targets and physics-enabled objects. The inspector renders up to 250 rows at once to stay responsive. When anatomy metadata is present, it also shows species/body-plan and skeleton type; the renderer uses that metadata only to choose a generic silhouette.
- **Activity panel:** search events and filter magic, recorded impacts, environment/weather, or failures. Select an event to jump to its replay position. A source link is only available when a safe `.mana` source location was recorded.
- **Spell anatomy panel:** inspect the observed cast stages and the bounded operation trace; click a stage to seek directly to its recorded event. It does not fabricate details missing from the JSONL recording.
- **Visual Lab:** open **✦ Customize** to change the entire visual direction without changing the runtime simulation. It offers 12 complete-look recipes, 32 elemental/material palette themes, 18 scene backdrops, 15 spell-body treatments, 13 trail styles, and 14 casting-glyph grammars. Select a recipe as a starting point, then customise any part.
- **Seven independent colour channels:** recolour the spell core, travel trail, glyph/seal, impact burst, being aura, internal accents, and spell outline separately. Element/material colours can also be individually overridden. Overrides have separate clear/reset controls and are validated as hex colours.
- **Fine controls:** adjust effect intensity, glow, trail length, particle detail, spell size, atmosphere and grid strength. Graphics use one adaptive policy: detailed spell silhouettes are the default, and only decorative complexity is reduced automatically when frame time rises. Dense recordings keep their timeline and visible spell forms; trails and inner details are simplified before the renderer reduces core silhouettes.
- **Accessibility:** stronger outlines/high-contrast settings, reduced motion, non-colour shape cues, textual spell labels, keyboard focus indicators and responsive settings are included. The high-clarity look is a low-glow starting preset.
- **Presets:** **Save defaults** keeps the current appearance for later sessions; **Export preset** and **Import preset** let you move settings between workspaces. Preset import is normalised against a schema and allowlisted values; older version-1 settings remain valid. **Reset** returns to default styles and clears custom overrides.
- **Inspect / World panels:** inspect recorded entity properties, configured physical rules, current atmospheric values and a world snapshot. The panels are read-only; changing the camera or filters cannot change simulation state.
- **Replay:** use Play/Pause, Replay, Previous/Next, Previous/Next Impact, the timeline and playback-speed selector.
- **Close / maximise:** use the scene's top-bar controls.

The default background is a matte graphite grid, aligned to world units. The **Visual Lab** can replace it with 18 backdrop variants, from parchment and studio slate to nebula, moonlit blue and volcanic glass. It is not a transparency checkerboard, and the grid follows camera pan and zoom. The scene avoids diagnostic coordinate labels, force arrows and an energy-flow dashboard. **Spell form** is an independent layer from **Magic FX**: it draws a structured body at the projectile position and uses the spell identity from recorded events for its form and optional label. The **Spell** inspector exposes the recorded creation-to-outcome trace with click-to-seek rows. The renderer automatically adjusts detailed bodies, trail complexity and particle density from recent frame timings. It has no manual quality tiers. A hard four-million-pixel canvas backing limit bounds the main RGBA buffer to roughly 16 MB; the actual browser compositor can use additional memory. Event parsing cache and recording track limits are bounded, and off-screen tracks are culled without trimming the recorded timeline.

## Animation and spell effects

The viewer follows the positions actually recorded by the runtime. A projectile that steers, curves, is redirected or changes direction uses its recorded intermediate positions; the viewer does not draw an invented straight line from spawn to final position. Positions are interpolated using recorded world time when timestamps differ, and the projectile turns to face the direction it is travelling. Long paths are kept within a memory cap while preserving recent bends and sharp older turns.

Magic is not one shared glitter effect, and moving projectiles are no longer represented by their trail alone: the Spell form layer adds a separate body silhouette and form-specific inner structure aligned to recorded travel. The entity retains its runtime-recorded position and movement; the drawing is only a visual interpretation. Fire uses flame tongues; water uses moving ribbons and droplets; ice uses angular shards; lightning uses jagged branching strokes; earth and metal use solid fragments; air uses flowing ribbons; life uses vine-like forms; shadow/death uses tendrils; and pure mana uses a geometric seal. Beams, bursts, impacts, summoned-being manifestations, reanimation, woven constructs, transformations, body-state changes, magnetic fields, smoke and flares each have their own drawing treatment. Effects still represent presentation of recorded events; the runtime remains responsible for whether the spell works, what it hits and how the world changes.

Humanoid and knight figures animate their gait while moving and turn to face their travel direction. Dragons flap, serpents undulate, birds flap, slimes wobble, and other creature silhouettes retain their individual motion cues. Idle animation continues while inspecting a paused scene, and reduced-motion settings suppress decorative movement. The artwork is procedural 2D drawing, not a skeletal animation rig or imported frame-by-frame art.

To try a projectile that genuinely turns while it moves, run `python mana.py --record steering.jsonl examples/visualiser_steering_firebolt.mana`, then open `steering.jsonl` with **MANA: Open Visualiser Recording**. If an external or old recording has no intermediate positions, the viewer cannot recover turns that were never recorded.


## Keyboard shortcuts

Focus the scene canvas first. Arrow keys step through events, Space toggles play/pause, `+` and `-` zoom, `0` fits the scene, `F` focuses the selected target, `I` toggles Character view, `G` toggles the grid, `L` toggles names, `E` toggles magical effects, `W` toggles weather, and Enter opens Inspect. Buttons remain available for every main action.

## World rules, not renderer guesses

The runtime is authoritative. Motion and contacts come from recorded simulation events; the renderer does not decide if a spell hit. The motion trail ends at recorded contact instead of travelling through a target.

The `world` library exposes configurable gravity, air density, default restitution, drag, thermal exchange, material phase changes and wetting. `world.laws()` explains the current law configuration. The engine uses swept 2D collision checks, mass-aware motion, a bounded integration step, material density and volume, energy accounting, and a curated temperature/phase catalogue. Phase transitions are currently a simple reference-pressure rule, not molecular or high-pressure chemistry.

`conjure()` creates physical matter with mass, volume, density, temperature and collision data. `transmute()` changes material/composition and preserves mass by default. `shape()` changes primitive geometry. `transfigure()` changes a living entity's form or the form of matter created by `conjure()`; ordinary existing matter must use `shape()` for geometry changes. A periodic-table library describes all 118 elements; missing data is not invented, and uncertain density/composition values are marked as estimates.

Weather is a parameter-driven atmosphere, not a catalogue of weather spells. `weather.configure()`, `weather.wind()`, `weather.precipitation()`, `weather.temperature()`, `weather.humidity()`, `weather.fog()`, `weather.clouds()` and related controls can be composed. The runtime applies supported physical changes; the viewer renders the recorded parameters using a shared atmospheric renderer.

## Example

```mana
load geometry2d
world.configure(
    gravity=geometry2d.direction(0, -1) * 9.81 m/s2,
    restitution=0.2
)
weather.configure("custom", precipitation="rain", intensity=0.75,
                  wind_speed=10 m/s, clouds=0.9)
metal = conjure("iron", mass=2 kg,
                position=geometry2d.point(3 m, 2 m), name="Iron sample")
show periodic.lookup("Fe")
show world.laws()
advance_time(2 s, timestep=0.02 s)
```

## Recording and resource use

Create a recording manually with:

```sh
python mana.py --record spell.jsonl examples/fireball_contact.mana
python mana.py --record steering.jsonl examples/visualiser_steering_firebolt.mana
```

The extension reads JSONL from disk in bounded chunks and applies recording-size/schema safety caps. The viewer uses an automatic rendering budget, a four-million-pixel canvas ceiling, a small bounded event parse cache, bounded motion tracks and cosmetic effects, and pauses idle animation while the webview is hidden. High-density scenes retain the recorded world data while expensive decoration is simplified. These measures lower avoidable resource use but are not a guarantee of fixed RAM/GPU consumption on every machine. The viewer is a completed-run recorder/replayer rather than a live game editor.

Recordings are read locally and are not uploaded. The webview has no network connection, uses a restrictive Content Security Policy, and inserts program-supplied text as text rather than HTML.

## Extension details and support

The **Details** page for this VSIX is generated from this `README.md`; package verification checks that `extension.vsixmanifest` maps the Details asset to `extension/README.md` and that the full document is present in the package.

Source, scene drawing, playback and package metadata are in `tools/mana-visualiser-extension/`. Build with `python tools/vscode/build_mana_visualiser_vsix.py` and verify with `python tools/vscode/build_mana_visualiser_vsix.py --check`.

## Limitations

The scene is currently 2D because the world engine is 2D. The `vector3d` library provides standalone calculations only; it does not imply 3D movement, depth collision or 3D world rendering. Some atmospheric properties, such as clouds and fog, are visual parameters rather than full fluid-dynamics simulations. Phase points use simplified reference-pressure values. The package is not a Unity/Godot/Unreal plugin or a separate desktop application.

## License

GPL-3.0-only. See [`LICENSE.txt`](LICENSE.txt).


## Safety and resource limits

Running a MANA file requires a trusted VS Code workspace. The extension launches Python with an argument array (`shell: false`), a reduced environment, a five-minute timeout, and a 2 MB captured-output ceiling. Source files are capped at 2 MB. Generated recordings live in a random private temporary directory, are capped at 25 MB, and are deleted when their visualiser panel closes. Imported recordings are streamed in bounded chunks and validated for schema, JSON nesting depth, record size, field count, and collection limits before being sent to the webview. Source navigation only opens `.mana` files inside the current workspace. These safeguards do not turn MANA into an OS-level sandbox; do not run hostile programs with sensitive account access.
