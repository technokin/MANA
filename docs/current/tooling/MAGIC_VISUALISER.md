# MANA Magic Visualiser

**Page kind:** Guide  
**Current source version:** v2.0.0

The Visualiser replays a recorded MANA run as a magical scene. It is an optional VS Code extension; the interpreter and `.mana` programs do not depend on it.

## Install

Install `installers/vscode/mana-magic-visualiser-2.0.0.vsix` from a terminal in the repository:

```sh
code --install-extension installers/vscode/mana-magic-visualiser-2.0.0.vsix
```

On Windows, use `code.cmd` if that is how VS Code is available on your PATH. The existing MANA Language Support extension remains a separate install; the Visualiser can be used without it.

## Run a scene

1. Open a `.mana` file inside a project folder that contains `mana.py`.
2. Click **Visualiser** button in the editor title. This is separate from the ordinary **MANA: Run File** triangle; only the eye button creates a recording and opens the replay.
3. The Visualiser opens in the active editor area as a full-scene workspace. Use Fit scene, the zoom buttons, the mouse wheel, or drag the scene to pan. Select an object to inspect it; use Play, step, speed and the timeline to replay the recording. The X closes the scene and the maximise control expands the editor group.

You can also record from the terminal:

```sh
python mana.py --record fireball.jsonl examples/fireball_contact.mana
```

Then run **MANA: Open Visualiser Recording**.


## Scene navigation and display controls

The graphite grid represents the 2D world plane. It is not a transparency checkerboard, selection region, or physics overlay. The grid tracks the camera, and the view can be panned and zoomed without changing the recorded world. Use the scene toolbar to independently show or hide the grid, object names, spell effects, and weather. **Focus target** centres the selected object. **Fit scene** resets the view around the scene bounds.

| Action | Mouse / control | Keyboard (focus the scene canvas first) |
|---|---|---|
| Pan | Drag the scene | — |
| Zoom in / out | Scroll or +/− toolbar | `+` / `-` |
| Fit scene | Fit scene button | `0` |
| Focus the selected object | Focus target button | `F` |
| Toggle Character view | Character view / Exit character view | `I` |
| Toggle grid | Grid button | `G` |
| Toggle object names | Names button | `L` |
| Toggle spell trails and impact effects | Magic FX button | `E` |
| Toggle spell bodies, glyphs and spell-name labels | Spell form button | `S` |
| Toggle weather rendering | Weather button | `W` |
| Step through events | Previous / Next | Left / Right arrow |
| Play / pause | Play button | Space |
| Open Inspect panel | Inspect tab | Enter |

The keyboard shortcuts are scene-canvas shortcuts; click or focus the canvas before using them. The extension respects reduced-motion settings for decorative animation. All controls have keyboard focus indicators, labels, and pressed states where applicable.

## Objects, activity, and world inspector

The **Objects** panel lists entities present at the current replay position. Search by name, material, element, kind, or visible form. Filters separate living beings, summoned or reanimated entities, physical materials, mana constructs, anchored targets, and objects that participate in physics. Select an entry to focus and inspect it. The list caps rendered rows at 250 so the side panel remains responsive in large scenes; the count reports matching objects, and a note indicates when the display is capped.

The **Activity** panel filters recorded narrative events, magic/spell results, collisions, world/weather changes, and failures. Search narrows the list by event kind and summary. Each activity item can seek the recording to the event; source links are shown only when the recording contains a workspace-safe `.mana` source location. The **Inspect** panel describes the selected entity using available recorded fields. The **World** panel reports recorded physics laws, current weather, and a compact world snapshot.

These panels are views into the recording, not editing tools. Searching, filtering, selecting an entity, hiding effects, or moving the camera cannot alter a spell outcome, target position, or world law.

## What it shows

The scene is designed to look magical rather than like a scientific debugger. It uses a drawn caster and target character, element-specific spell shapes, recorded curved projectile tracks, impact bursts and a camera that can be moved and zoomed. A projectile follows the intermediate positions recorded by the runtime, turns to face its direction of travel, and stops at the contact frame; a contact flash and short character stagger appear only for a contact reported by MANA's physics engine. The Details view uses scalar distance such as `6 m`; it does not display X/Y coordinates, grids or vectors. Developer messages live in the Activity view. Combat/distance target profiles created with `tgset:` are anchored by default; ordinary material profiles remain movable. Set `anchored = false` when a target profile is intentionally movable.

The Visualiser has no plane workspace and no portal/gateway visuals. Plane rules still affect whether summoning succeeds; when a being is successfully summoned, the viewer may show a local manifestation effect without suggesting that a portal opened or mana travelled from a plane.

It does not display energy-flow diagrams or mana fuel bars. The environment renderer consumes parameter-driven world state for clouds, wind, rain, snow, dust, fog, heat shimmer and lightning. MANA programs can set it with `weather.configure()`, `weather.wind()`, `weather.precipitation()`, `weather.temperature()`, `weather.clouds()`, and related controls. The viewer never infers weather from spell names; recorded `weather.changed` / `environment.changed` events are the source of truth. Wind and precipitation also affect supported runtime material/physics properties, while clouds, fog, heat shimmer and lightning presentation remain simplified rather than full atmospheric simulations. The Visualiser does not decide spell success or simulate features absent from the runtime. Current world physics are 2D and use simplified circular contact bounds.

## Character focus and input

Character view is an immersive canvas-first layout, not a separate simulation mode. It hides the inspector, keeps the selected actor centred, and preserves scene pan/zoom. Double-click an entity to focus it; drag uses pointer events so mouse, pen, and touch input follow the same camera path. Creature drawing is procedural and recognises common names/body forms such as eastern and western dragons, dinosaurs, ants, minotaurs, slimes, and generic humanoids. Humanoids and knights animate a walking gait and turn to face their recorded direction of motion; birds flap, dragons flap their wings, serpents undulate and slimes wobble. Idle movement continues while inspecting a paused scene, unless reduced-motion is enabled. These are illustrative 2D silhouettes, not anatomical 3D models or skeletal animation rigs.

## Curved movement and distinct magic

Moving entities use their recorded intermediate world positions rather than a straight path between the first and last samples. When timestamps differ, the viewer interpolates using the recorded world clock; unusually long trails are kept within a memory cap while preserving recent turns and sharp bends. To see this, run:

```sh
python mana.py --record steering.jsonl examples/visualiser_steering_firebolt.mana
```

Then choose **MANA: Open Visualiser Recording**. The example deliberately changes a firebolt's velocity several times while it is already moving. The viewer follows the recorded result; it does not create steering or add physics that the runtime never reported. Old recordings without intermediate positions cannot show turns that were never recorded.

Projectile visuals are distinct by identity: flame tongues, water ribbons, ice shards, branching lightning, solid earth/metal fragments, flowing air, life-vines, shadow/death tendrils and geometric mana bolts. Dedicated visual treatments also exist for beams, bursts and impacts, summoning and reanimation, woven constructs, transformations, body-state effects, metal manipulation and magnetic fields, smoke, flares and weather changes. The shapes are 2D procedural drawings; they are meant to explain the recorded action, not to claim that the underlying physical or magical behaviour is more complete than it is.

## Spell-first view and anatomy

The **Spell form** layer is separate from **Magic FX**. It renders the travelling spell as a recognisable body—contained orb, directed lance, forked bolt, ribbon, boundary/ward, ring, or geometric construct—aligned to the recorded direction of travel. The label uses the spell name recorded on the runtime event when available; entity element and material are fallbacks for choosing an illustrative form. This is an interpretive 2D silhouette, not a claim that the recording contains a complete spell blueprint. Switch **Spell form** off to compare the body with trails and impacts alone.

The **Spell** inspector tracks the named cast through its recorded creation, movement, magic operations, contacts and outcome. Select any sequence entry to seek the scene to that event. It makes the observed sequence navigable instead of treating the whole cast as a single impact flash. Preview (`post`) remains labelled as a preview/rollback; the Visualiser never treats the preview as a committed world change. If the JSONL recording does not contain source-level shape or operation data, the panel reports only what was recorded.

For crowded recordings, the renderer automatically caps expensive detail while preserving a simple spell silhouette for each visible projectile. Off-screen moving tracks are culled unless their recent recorded trail crosses the view. The underlying replay tracks and timeline are retained; automatic detail changes affect presentation only, not recorded positions, collision outcomes or playback state.

## Visual Lab: styles, colour and adaptive graphics

Open **✦ Customize** in the scene toolbar. The Visual Lab is an appearance workspace layered on top of the recording; changing it never changes spell success, object properties, collision results, or world time.

- **Start from a look:** 12 curated recipes include Arcane Scholar, Infernal Court, Glacial Cathedral, Abyssal Leviathan, Fae Wild, Prismatic Astral, Void Necromancy, Stormglass, Antique Tome, Verdigris Alchemy, Mythic Relic, and High Clarity. Each is a starting configuration, not a locked theme.
- **Choose an art direction:** 32 colour themes, 18 backdrops, 15 spell-body styles, 13 projectile-trail styles and 14 glyph grammars can be mixed independently. Shapes and construction patterns differ by style; element identity is not communicated by colour alone.
- **Override individual colours:** change element/material colours or the seven rendering channels—spell core, travel trail, casting glyph, impact, being aura, internal accent and outline. This fixes the old limitation where hard-coded highlights could make a spell ignore a selected palette. Clear a channel or all element overrides to return to automatic colours.
- **Tune visual weight:** effect intensity, glow, trail length, particle detail, spell size, weather/atmosphere, and grid strength are adjustable. There are no user-facing graphics tiers. The renderer starts with detailed spell forms and adapts automatically to sustained frame cost: it first trims particles and trail detail, then inner spell decoration, and gradually recovers when time is available. Visible projectiles keep a basic, recognisable silhouette, and tracks and timeline records are not deleted when detail is reduced.
- **Refine presentation and accessibility:** optional particles, impacts, vectors, auras, paths, glyphs and spell-name labels are independently switchable. Strong outlines and a high-contrast look improve edge separation, and reduced motion suppresses decorative movement. Shape, label and construction differences remain available even when colours are similar.
- **Reuse looks:** Save defaults persists appearance settings for later sessions. Export preset writes a settings file; Import preset loads one after schema and allowlist validation. Reset restores normal defaults. Older schema-version-1 settings remain supported, so existing user settings do not need manual migration.

The art-direction controls were informed by [Riot Games' VFX guidance](https://www.riotgames.com/en/artedu/visual-effects), which emphasises communicating the action clearly while balancing thematic impact, and its [VFX update notes](https://www.leagueoflegends.com/en-au/news/dev/dev-behind-the-scenes-of-vfx-updates/) prioritise gameplay readability and reducing visual noise. The settings expose colour, shape and visual intensity separately so a dramatic preset does not become the only readable option. The adaptive policy follows [Epic's Niagara scalability guidance](https://dev.epicgames.com/documentation/unreal-engine/scalability-and-best-practices-for-niagara) on controlling effect work and culling, rather than asking users to choose a quality tier. [MDN's Canvas optimisation guidance](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas) informs avoiding redundant draws and unnecessary backing-store resets; [MDN's WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices) inform explicit graphics-memory budgeting even though this viewer uses Canvas 2D. Accessibility follows the principle that [colour is not the only visual cue](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color); outlines, shape grammar and labels supplement the palette.

## Automatic resource protection

The renderer uses one adaptive graphics policy, not Performance/Balanced/High/Ultra/Cinematic modes. Its resource safeguards are:

- The main canvas backing store is capped at **4,000,000 pixels** after rounding (about 16 MB of raw RGBA pixel storage for that single buffer). Browser compositing, temporary surfaces and other tabs can require additional memory, so this is a limit on the viewer's canvas buffer, not a total-process RAM promise.
- Frame cost is measured while rendering. After sustained slow frames, particle density, detailed spell-body count and expensive trail treatment are reduced in small steps; they recover gradually after sustained fast frames to avoid visible quality oscillation.
- Every visible projectile retains a basic spell silhouette when detailed drawing is budgeted. Expensive inner construction and trail decoration are simplified before the core form is removed. Off-screen tracks are culled using a bounded recent path window.
- Event JSON parsing uses an LRU cache capped at 512 objects / 1.5 million source characters, and skips caching large snapshot records. Per-frame position maps are reused. Playback avoids a second full scene render for each event step.
- Idle animation stops while the webview is hidden. Resizing does not clear/reallocate the canvas backing buffer unless its pixel dimensions actually change.

These bounds reduce known sources of avoidable RAM and rendering work, but available GPU memory and browser compositing behaviour vary by machine. This code does not claim a universal FPS or total-RAM guarantee.

## Recording and privacy

The first implementation is record-and-replay, not a live control panel. Recordings are written as JSON Lines to the chosen local file. The extension does not open a network port or upload data. It rejects oversized files, oversized lines, excessive record counts and unsupported schema versions. Program-supplied strings are rendered as plain text in a sandboxed webview.

The recording is private to the Visualiser and is not a public game-integration API. See [Where MANA Could Be Used](../foundations/FUTURE_USES_AND_ROADMAP.md) for potential future application areas.
