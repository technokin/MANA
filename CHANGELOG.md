# Changelog

This changelog records changes since the public GitHub `v1.0.0` source tag. The project version is 2.0.0. The release workflow publishes the matching `v2.0.0` tag only after its configured Linux/Windows and Python-version quality matrix passes.

## [2.0.0]

MANA 2.0.0 is a major expansion of the existing language, libraries, 2D world simulation, Visualiser, examples, and development tools. It does **not** add a full 3D world.


### Visual Lab, adaptive graphics, bug fixes, and additional examples

MANA 2.0.0 consolidates the following Visualiser, runtime, documentation, and example improvements.

- Made the travelling spell a first-class scene object: the rendered body keeps its recorded spell identity, visible form, orientation, and label independently from its trail and impact effects. Added a spell-anatomy inspector that seeks through the available lifecycle trace without inventing operations absent from recordings.
- Added the Visual Lab with 32 colour themes, 18 backdrops, 15 spell-body treatments, 13 trail styles, 14 glyph grammars, 12 complete-look recipes, and seven independently configurable colour channels. User overrides now flow through the corresponding renderer layers.
- Removed user-facing graphics-quality tiers. The renderer now uses one adaptive policy, retaining a readable spell silhouette while simplifying expensive decorative detail under sustained load. Added a four-million-pixel canvas backing-store ceiling, bounded event-parse cache, off-screen culling, reusable per-frame position maps, and hidden-view idle pausing.
- Motion-path bounds are cached once per recording instead of rescanning recorded waypoints on each frame or interaction; the cache is replaced when a new recording is loaded. Corrected reduced-motion preference transitions, rejected malformed/non-finite/out-of-policy recording coordinates across fit/draw/selection/effect paths, improved large-world camera fitting, and retained contact character cues for older recordings when a validated entity position is available.
- Hardened version synchronisation so current labels can be updated without rewriting historical references. Release workflow tag routing now accepts version-shaped tags but checks an exact match to `VERSION`, and release notes are rendered from the matching current changelog section.
- Corrected documentation navigation, current-report labels, and the release archive requirements. Current documentation remains separated from historical audit reports; archived records are preserved rather than silently rewritten as current results.
- Added five new end-to-end examples: `preview_commit_boundary.mana`, `plane_path_lifecycle.mana`, `kinetic_thermal_ledger.mana`, `selective_two_target_cast.mana`, and `impact_handler_counter.mana`. They cover preview rollback versus committed release, one-way plane-path lifecycle, combined heat/motion accounting, external target selection, and runtime-reported impacts.
- Added focused regression tests that assert runtime state for those examples, in addition to the all-example execution smoke test. The source now contains 67 runnable `.mana` examples.

### Visualiser — new optional 2D tool

- Added a separate Visualiser extension for Visual Studio Code. It is optional; MANA programs can still be checked and run without installing it.
- Added a large scene view with pan and zoom, entity selection, double-click focus, touch/pen/mouse panning, and a dedicated Character view that recentres on the selected being.
- Added illustrative 2D silhouettes for humanoids, dragons, dinosaurs, birds, serpents, ants, minotaurs, and slimes. Where anatomy information is available, the viewer uses it to improve the depiction and the read-only inspection panel.
- Fixed the main steering-spell problem: moving effects now follow recorded intermediate world positions rather than drawing a straight line between the start and end. Motion uses recorded world timestamps when available, so bends and uneven timing are retained.
- Added different visual treatments for the four base elements and other supported effect categories: flames, water ribbons and droplets, ice shards, branched lightning, earth/metal fragments, flowing air, plant-like life effects, shadow/death tendrils, and geometric mana seals.
- Improved the presentation of beams, radial bursts, impacts, summoning and reanimation, shaped mana constructs, transformations, body-state changes, magnetic effects, smoke, and flares. The viewer displays recorded events; it does not decide whether a spell succeeds.
- Added bounded recording/replay, reduced-motion support, more robust handling of malformed recording events, and a runnable steering-firebolt example.
- Improved character movement cues, facing direction, casting presentation, and brief collision reactions when the recording contains a real contact.
- Made the travelling spell itself a first-class scene layer, separate from trails and impact FX: moving spell bodies use the recorded spell identity where available, recognisable form silhouettes, directional alignment, and a spell-name label. The independent **Spell form** toggle keeps the difference visible.
- Added a **Spell anatomy** inspector with cast status, observed stages, bounded operation trace and click-to-seek replay rows. It reports the recording rather than fabricating source-level spell details that were never captured.
- Capped high-detail spell-body rendering at 96 visible bodies per frame and culled fully off-screen projectile tracks when their recent trail is also outside the view; replay data and physics results remain untouched.

### Language and spell authoring

- Added `spell name():` as a natural spelling for defining a spell. Existing `spldef` spell definitions remain supported.
- Changed pure-mana construct creation to use `weave mana`. The old `create Mana` form now gives a migration message; ordinary elemental creation is unchanged.
- Added the native `weather` statement, including local weather areas that affect objects within a selected radius, expire as world time advances, and participate in trial/rollback versus committed execution.
- Added a more natural matter-conjuring form with named options for material, mass, shape, initial movement, anchoring, collision, bounce, friction, and drag. Existing runtime safety budgets still apply.
- Clarified that mana figures shown in reports are accounting and appraisal information, not a finite personal pool that must be replenished before each cast.

### Geometry, movement, and 2D world engine

- Added `geometry2d.rotate()` and `geometry2d.scale()` helpers, including unit-preserving vector scaling.
- Added `vector3d.rotate()` with a documented X-then-Y-then-Z angle order, plus dimension-checked interpolation and midpoint helpers. These are calculation tools only; they do not create a 3D simulated world.
- Expanded general movement support through anatomy-aware physical profiles and `physiology.propel()`, with explicit physical and arcane movement modes, direction checks, movement/energy accounting, and a speed cap for massive bodies.
- Improved large-world collision performance using spatial grouping and ordered candidate checks instead of repeatedly testing every object pair. Added bounded handling for oversized paths and work limits so extreme scenes fail safely rather than consume unbounded time or memory.
- Reduced long-run energy-ledger growth by grouping continuous environmental and motion accounting during each time-advance operation while retaining the overall energy totals and input/output counters.
- Hardened physics edge cases involving extreme coordinates, non-finite values, swept movement bounds, repeated time steps, and invalid mixed world settings. World configuration changes are applied together or rejected without leaving a half-updated configuration.
- Improved object-creation performance through cached default properties and creation-cost values. The stress benchmark now checks that the requested work really completed and remains within the supported object limit.

### New libraries and expanded catalogues

- Added libraries for anatomy, physiology, arcana, armory/equipment, materials and metals, periodic-element data, and world/weather operations. These complement the existing language, mana, geometry, plane, summoning, and necromancy systems.
- Expanded the anatomy catalogue to **91 body-plan templates**, **991 named structure records**, and **23 body-system categories**. The human template includes 691 addressable structures across more detailed nervous, circulatory, respiratory, digestive, renal, endocrine, immune, and joint records.
- Added templates covering more dinosaurs and other prehistoric animals, western and eastern dragons, minotaur, ant castes, and slime, alongside human and other creature forms.
- Added custom anatomy definitions, body-system declarations, multi-template creature composition, configurable merge choices, movement declarations, physical-size overrides, and anatomy audit warnings. The limits remain separate: up to 1,024 tracked structures per body and 512 user-defined structure definitions.
- Added per-template starting estimates for mass, dimensions, density, volume, and 2D collision radius. These are game-scale model values, not claims of complete biological simulation or certified scientific measurements.
- Consolidated the stock materials catalogue into **407 unique profiles**, including the **118 periodic elements**, with a shared property layout, ten broad material families, search/category/state access, and family summaries.
- Expanded materials for alloys, minerals, terrain feedstock, glass and ceramics, polymers and composites, organic and biological feedstock, textiles, process fluids, and fictional crafting materials. Estimated properties are labelled as model/gameplay values where appropriate.
- Standardised material and equipment-name matching across the libraries, so equivalent names using spaces, underscores, or hyphens resolve consistently. Runtime-defined materials are included in category-wide searches.
- Added general creature propulsion and support for different life-support structures, including invertebrate-style body plans, rather than assuming every living creature must use a vertebrate brain-and-heart arrangement.
- Improved editor suggestions and references for the new libraries and current geometry helpers.

### Documentation, examples, and developer workflow

- Expanded the runnable `.mana` example collection from 15 files in the public v1.0.0 snapshot to **67 examples**. The collection now covers language basics, elements, materials, matter creation, weather, movement, collision, targeting, mana constructs, anatomy, and Visualiser recordings.
- Added or expanded guides for the Visualiser, anatomy, comparative anatomy, physiology, materials and equipment, library compatibility, weather and matter, geometry, project layout, stress testing, and future project direction.
- Added a consolidated project audit, world-engine stress report, release verification report, and clearer lists of implemented and unsupported behaviour.
- Improved automated example checks, generated references and indexes, version consistency checks, and package validation. Moved a release-failure test input to the fixtures folder and excluded generated caches and stale installers from the clean source package.
- Added a release workflow that checks the version, runs the configured quality gates, builds the source archive and both Visual Studio Code extensions, and attaches the downloads when the matching version tag is published.
- Updated the language extension's syntax support, completion suggestions, help text, starter material, and documentation for the added language features and libraries.
- Replaced the old single-extension installer in the source package with the current **2.0.0 language-support and Visualiser installers**. The runtime remains usable without either extension.

### Compatibility and scope

- MANA scripts remain `.mana` files, and Python remains the implementation runtime. The custom Grimoire IDE was already absent from the public v1.0.0 release and remains absent.
- The world simulation remains **2D**, with planar collisions and 2D movement. Three-dimensional vector helpers are for calculation/interoperation only.
- The Visualiser displays recorded scenes and events; it is not a live world editor and dragging objects in it does not change the real simulation.
- Character illustrations are procedural 2D drawings, not rigged 3D models. A visual category does not guarantee a fully simulated physical, chemical, biological, or magical process.
- Full fluid simulation, comprehensive chemistry, complete biological systems, and autonomous creature intelligence remain outside the scope of this release. Older recordings cannot provide motion detail that was never recorded.

### Documentation integrity and release-readiness audit

- Fixed Python lint findings that stopped the hosted quality matrix before tests and documentation checks could run: missing type/error imports, unused imports and assignments, one-line control flow, and duplicate orca aliases. The alias correction preserves the dedicated orca profile.

- Corrected generated API links for names containing underscores. The generator now preserves valid characters in GitHub heading IDs, and a regression test checks that heading links in the current documentation resolve.
- Corrected a mislabeled historical audit reference in the component reference page.
- Moved two old pre-release audit snapshots out of `docs/current/` and into `docs/archive/audits/release_reports/`, then updated the index, version-sync exclusions, generated glossary usage index, and historical links. The current documentation index now links all 65 current documentation pages.
- Fixed the version synchroniser so a line mentioning current documentation and then a historical version cannot rewrite that old version by mistake. Added regression tests for this case and the new archive paths.
- Updated the pinned Ruff version to 0.17.1 and refreshed the pinned `actions/setup-python` version to 7.1.0 after checking upstream release records. The audit snapshot dated 2026-10-15 remains unchanged as a historical record.
- Changed the release workflow so public release creation waits for all eight Linux/Windows × Python 3.12–3.15 verification jobs. Moved tag validation into a small cross-platform helper and added tests for incorrect or missing tags.
- Made the publishing step safe to rerun: if a release entry already exists, the workflow updates its notes and replaces the release assets instead of failing at release creation. Removed unnecessary developer-tool installation from the artifact-only publishing job.
- Repeated a targeted safety-pattern scan across 54 Python source files; no direct uses of `eval`, `exec`, `shell=True`, `os.system`, or pickle deserialization were found. The Visualiser renderer does not use `innerHTML`. These searches are not a full security proof or a substitute for dependency auditing.
- Expanded the root README's feature inventory to include the materials, armory, anatomy, physiology, arcana, weather, and matter libraries, and added direct links to the specialist guides.
- Improved the release checklist so it regenerates documentation outputs before checking them and includes the same full Python lint and dependency-audit commands used by release CI.
- Reviewed links across all 124 Markdown files; no broken local file links were found. The test suite also verifies local heading anchors across the Markdown set.

### Baseline verification recorded at the initial 2.0.0 snapshot (historical)

- Full project test suite: **480 passed** (the public v1.0.0 report recorded 316 passed).
- Visualiser-focused tests: **36 passed**.
- All **62** shipped MANA examples passed both CLI syntax checks and the example smoke checks.
- Python compilation, JavaScript syntax checks, generated-documentation checks, version checks, local documentation link and heading-anchor checks, extension packaging checks, and source archive integrity checks passed in the available environment.
- The Visualiser webview harness exercised a recorded scene containing a steering spell.
- Ruff, Pyflakes, and the dependency audit were not verified locally because the optional tools were unavailable and the package index could not be reached. The configured release workflow runs the quality gates on GitHub and gates publication on the full supported-platform matrix; hosted results still need to complete after upload.
- These results describe the source snapshot and local checks. They do not, by themselves, claim that a GitHub tag or public 2.0.0 release has already been published.

## [1.0.0] — First public stable release

- Published the Python-hosted MANA interpreter and `.mana` source language as the v1.0.0 baseline.
- Removed the custom Grimoire IDE before this release, retaining the runtime, examples, libraries, documentation, tests, and optional VS Code language-support extension.
- Included the language's spell definitions, elemental operations, 2D physics, mana controls, plane/pathway registry, summoning, necromancy, 2D geometry helpers, and 3D vector calculations.
- Added the public-facing project README, separate introduction, contribution guidance, logo integration, release documentation, and a clean source-package workflow.
- The published v1.0.0 verification report recorded 316 passing tests. The world remained 2D; the 3D vector library was a calculation layer, not a 3D world engine.

## Pre-v1.0 project organization update (historical)

- Removed the custom Grimoire IDE, its Windows launcher/build workflow, and IDE-specific tests and documentation from the current source tree. Historical changelog entries and archived audit reports are preserved as history.
- Kept the Python MANA interpreter, `.mana` source files, examples, libraries, tests, documentation, and VS Code extension.
- Reworked the root README into a GitHub landing page with accurate Python/license/runtime requirements; kept `MANA_INTRO.md` as a separate conceptual introduction and added `CONTRIBUTING.md` and `tests/README.md`.
- Replaced the IDE-specific Windows build workflow with cross-platform Python test CI, added a current-file syntax-check task, and moved Ruff settings from an otherwise unnecessary `pyproject.toml` to `ruff.toml`.
- Prepared optional VS Code icon packaging from `assets/branding/mana-icon.png`; the logo was added to the v1.0.0 source snapshot.
- Recorded the checks and outstanding verification items in [`PROJECT_ORGANIZATION_REPORT_V0_10_14.md`](docs/archive/audits/release_reports/PROJECT_ORGANIZATION_REPORT_V0_10_14.md).
- At the time of this organization update, the project remained at 0.10.14. A later source snapshot identifies itself as v1.0.0; creating a Git tag and publishing a GitHub release are separate steps.

## v0.10.14 audit-fix follow-up (no version bump)

- Added stable diagnostic code families, machine-readable error records, unknown-name hints, concise internal-error reporting, and the `mana.py --check` mode.
- Added deterministic fuzz and randomized energy-ledger tests.
- Added expected output to runnable current documentation examples and made tests compare the captured output.
- Added version synchronization, generated API/glossary/error indexes, a cheat sheet, error catalogue, supported-limitations page, tutorial, recipes, page-kind tags, and release checklist.
- Added a Windows Grimoire build workflow.
- Full suite: 310 tests passed; Ruff/pyflakes commands remain unverified in the offline environment.

## v0.10.14 stress-test follow-up (no version bump)

- Hardened oversized/non-finite numeric literals, parser/evaluator nesting, huge integer powers, complex arithmetic, and string/list result allocation limits.
- Converted extreme numeric inputs across target fields, unit conversions, timers, vector/geometry helpers, and plane/being helpers into MANA diagnostics instead of leaked Python exceptions.
- Made property assignment rollback failed updates, prevalidated scaling before mutating object fields, and prevented rejected over-`c` targeted velocity calls from changing aim state.
- Added deterministic boundary/fuzz regressions. Final suite: **327 passed**; target-field matrix: 74 cases with zero host exceptions; operation matrix: 16 cases with zero host exceptions.
- Added `docs/archive/audits/release_reports/STRESS_TEST_REPORT_V0_10_14.md`. Windows executable build and external lint checks remain unverified in this Linux/offline environment.

## v0.10.14 — Foundations handbook and portable Grimoire bundling architecture

- Rewrote the root README as a concise project introduction; detailed learning and design material now lives in a multi-file Foundations Handbook rather than repeating the Getting Started guide.
- Added dedicated foundations chapters for glossary/terminology, universal control and pure mana, world objects/materials/state, and execution/time/events/transactions. Expanded the navigation index so users can find magic foundations, code syntax, API references, physics, planes, beings, necromancy, and tooling separately.
- Reconciled current-document version labels and updated the VS Code extension metadata/license to GPL-3.0-only; rebuilt the versioned VSIX. Historical audits remain in `docs/archive/audits/`.
- Reworked the Windows Grimoire launcher/build recipe to embed the MANA app plus a Windows Python/Tcl/Tk runtime in the final executable, eliminating any target-machine Python requirement by design.
- **Packaging limitation:** this Linux build environment has no Windows CPython/Tcl/Tk runtime binaries, so it cannot produce or verify the final self-contained Windows EXE. The current source release contains the bundling implementation/build recipe, not a falsely labelled launcher that still requires host Python.
- Added the GPL-3.0 license and third-party-runtime redistribution guidance.

## v0.10.12 — MANA keyword migration and IDE/runtime separation

- Finalized the MANA-facing keyword migration: `load`, `skip`, `span(...)`, and `length(...)` replace the prior language forms; no `return` statement is supported.
- Kept `def` for ordinary computational functions and `spldef` for spell definitions; `tgset` remains the target-profile/context construct. The shared operators `and`, `or`, and `not`, plus `if`, `elif`, `else`, `while`, `for`, and `in`, remain as explicitly chosen syntax. The shape label `round` remains unchanged.
- Renamed the internal no-op AST node to `SkipStatement` so implementation terminology matches the MANA source keyword.
- Updated current language documentation, examples, Grimoire highlighting, VS Code grammar/snippets, and regression tests together.
- Kept Grimoire separate from the MANA source/runtime project. The native Go-built `Grimoire.exe` embeds the Grimoire interface, but this preview launches the selected project with an existing Python 3 + Tcl/Tk installation; it does not bundle Python and does not use a companion `MANA.exe`.
- Verified the full test suite and standalone MANA examples; rebuilt the versioned VS Code extension.

## v0.10.11 — Audit fixes and project organization

- Applied the supplied v0.10.7 audit to the v0.10.9 codebase, fixing applicable issues instead of blindly replaying obsolete fixes.
- Required invocation before directly creating non-base elemental-plane types; base elements remain freely usable, and combination-based derived materials remain supported.
- Validated planar energy-kind labels and made `plane_of()` reject plane names/references rather than reporting them as beings in the Mortal Plane.
- Defined `collapsed_into` on every object as `None` until collapse; changed unknown-event warnings to MANA diagnostics with source locations.
- Added initial editable HP, maximum HP, defence and attack values to built-in beings; resistance defaults to zero for every supported element.
- Rechecked the large-object commit path, replaced wildcard parser AST imports, cleaned unused imports, and added Ruff/editor configuration.
- Moved historical audits and build reports under `docs/archive/audits/`, removed superseded PyInstaller and batch-based packaging helpers, and cleaned caches/stale installers from the release archive.
- Fixed the necromancy unit example, made current MANA examples standalone or explicitly labelled as fragments/expected failures, and improved VS Code library namespace/function highlighting.
- Added automated smoke tests that execute the runnable MANA examples in current documentation.

## v0.10.9 — Portable Windows IDE packaging

- Added Windows-native PyInstaller entry points and build specs for `Grimoire.exe` (windowed IDE) and `MANA.exe` (console runner).
- Added `Build-Portable-MANA.bat`, which bootstraps a private build environment, creates a portable folder, includes docs/examples/assets/library data, and validates the ZIP.
- Updated Grimoire's frozen mode to locate resources beside the executable and run `.mana` files through the bundled `MANA.exe`; packaged use does not require users to install Python or invoke `.py` files.
- Kept source-development mode unchanged: contributors can still run the IDE/interpreter from Python and use the project's test suite.
- The portable executable build must be produced on Windows. This source revision includes and tests the build recipe; it does not contain a Windows binary built on this Linux host.

## v0.10.8 — Grimoire desktop IDE

- Added Grimoire, a standard-library desktop IDE for editing MANA source and project text files.
- Added multi-tab editing, line numbers, MANA syntax highlighting, smart indentation, save/open workflows, project explorer, find, execution output, and run/stop controls.
- Added direct launch of the MANA interpreter and the test suite from the IDE, with output captured in the app and process termination support.
- Added a Windows launcher and documentation for Grimoire. Tk/Tcl is supplied by the Python installation; no extra package is added to MANA's runtime requirements.
- Updated all current release metadata and rebuilt the VS Code language-support package at 0.10.8.
- Grimoire is an editor and runtime front end. A graphical World Engine viewport is not implemented in this release; the engine remains authoritative and the IDE displays interpreter output rather than inventing simulation visuals.

## v0.10.7 — Distinguish user-authored undead spells from cross-plane transfer

- Removed `necromancy.animate_construct()`: creating/summoning an undead construct is a regular MANA spell composed from object creation, properties, Necro-channel invocation, and ordinary movement/control operations.
- Kept `necromancy.reanimate()` and `reanimate_many()` specifically for already-existing eligible remains; a newly formed Earth object retagged as Bone is not retroactively treated as a corpse.
- Renamed the cross-plane transfer operation from `summoning.summon()` to `summoning.bring()` to avoid conflating that library operation with a user-defined spell such as `summon_skeleton`. `bring()` only transports a defined being through an open pathway; it does not define a skeleton spell.
- Added a runnable `summon_skeleton_spell.mana` example and regression tests that verify the spell is ordinary MANA code, and the removed special operations are not exported.
- Updated current library references and examples to match.

## v0.10.6 — Necromantic accounting and creature lifecycle corrections

- Reanimation no longer accepts an energy quantity from the caller and does not add the bookkeeping amount to the body's physical energy or integrity. Ledger usage is recorded internally as `Necro` mana, with the Underworld retained as the physical accounting source.
- `planes.invoke("Necro")` is now the explicit invocation name for the necromantic mana channel; it grants the Underworld permission used by the accounting transfer. `planes.invoke("Underworld")` remains accepted.
- Reanimation requires a body described as bone/corpse/remains when it is created, rather than accepting ordinary Earth that was relabelled afterward. `tgset` records this initial body declaration.
- Added `necromancy.animate_construct()` for animating a pre-existing solid Earth/stone/rock/clay construct without treating it as a corpse. This is separate from `reanimate()` and also uses ledger-only Necro accounting.
- Simplified built-in summoning: `summoning.summon("Griffin")` infers the registered home plane, manifests into the Mortal Plane, and defaults to 10 m ahead of the runtime caster position. Destination is implicit.
- Assigning a summoned being to a variable automatically tames that instance. Added explicit `summoning.tame()`, `send_back()`, and `call()` operations to name it, return it along a reverse route, and recall that same instance. Added `being_tamed`, `being_returned`, and `being_animated` events.
- Rechecked documentation and examples, added regression tests for the updated behaviours, and added `assets/branding/README.md` with the canonical path for the language logo SVG.
- The 3D vector library remains a calculation/interoperation tool; the world simulation itself remains 2D.

## v0.10.5 — Plane creation, summoning, necromancy and 3D interoperation

- Added the built-in `drafter` library: create a plane definition, attach custom data values, define regions, add beings and configure supported being fields before registration. Registered planes cannot be edited through `drafter`; custom data is scoped to the current runtime and can be recreated from a setup `.mana` file.
- Added `summoning` to resolve built-in or player-created being records, validate their declared requirements, require an open pathway, and manifest the being as a normal MANA world object. Existing movement and universal mana controls can operate on it. This revision manifests entities into the Mortal Plane only because it is the only simulated world space.
- Added `necromancy` to reanimate already-present corpse/bone/skeleton/remains objects using energy routed from the Underworld through `planes`. Added batch reanimation and an `is_undead` query. It does not depend on `summoning`.
- Added balanced ledger records for being transit and bound necromantic energy, and included bound energy in energy totals and integrity calculations. Added `plane_created`, `being_summoned`, and `being_reanimated` events.
- Improved custom plane category support, added the `drafter.create(...)` namespaced call syntax despite `create` being a statement keyword, and fixed rollback if a plane-created event handler fails.
- Rechecked `vector3d` integration: `planar()` converts a 3D calculation vector into an explicit z=0 vector, `is_planar()` validates the projection, and `object_vector()` reads vector properties from summoned/reanimated objects. These are calculation/interoperability tools; the world remains 2D.
- Updated library docs, function reference, language and architecture docs, release metadata, examples and VS Code extension. Added regression tests for plane configuration, region beings, summoning constraints, necromantic energy transfer, rollback, dependencies and 3D-to-2D interoperability. The new examples are included in the all-examples runtime smoke test.

## v0.10.4 — Pure mana effects and universal object control

- Added the built-in lowercase `mana` namespace for pure-mana constructs, radial bursts, directed beams, and element-independent object control; uppercase `Mana` remains the `create` type selector.
- Added `mana.form`, `mana.burst`, and `mana.emit` with named optional parameters and defaults: 1000 J construct/burst energy, 1 m effect radius, 1000 W beam power, 1 s duration, 10 m range, and default effect position 10 m along +X from the runtime caster position.
- Added accessible control helpers `mana.toward`, `mana.away`, `mana.lift`, `mana.hold`, `mana.levitate`, `mana.stop`, `mana.release_control`, `mana.collect`, and the combined `mana.control` operation. `tgset(target):` provides a default destination/source for toward/away.
- Added pure-mana projectile contact handling: a projectile's remaining mana energy is transferred to a struck material as heat, the projectile is deactivated, and the internal transfer is balanced in the energy ledger.
- Added material-profile inference in `tgset`: common wood/paper/fabric/plant materials default to combustible unless overridden; solid materials default to powderable unless overridden. Heating through the configured ignition threshold switches a combustible material to `burning`; `transform(object, "powder")` retains mass and tracked energy on the aggregate object.
- Made `mana.stop` and `mana.hold` conserve kinetic energy by converting it to thermal energy before anchoring/stopping an object. Collection skips objects already at the destination rather than failing on a zero direction.
- Expanded the pure-mana/universal-control documentation, added function-reference and getting-started coverage, updated the language spec and VS Code grammar, and rebuilt the current VSIX.
- Added regression tests for defaulted effects, named arguments, material inference and overrides, targeting-context control, collection, stopping/holding energy conservation, helper-call safety, and mana projectile collision transfers.
- The implementation remains a 2D world simulation. Terrain extraction, continuous combustion, dust-particle generation, and full sustained motion planning remain outside this revision.

## v0.10.3 — Planes library aligned to the full plan

- Replaced the earlier pathway/navigation API with the planned API: plane identification/existence, categories, region lookup, `open_path`/`close_path`, direct pathway checks, shortest route, and reachability.
- Kept the always-loaded plane records compact: ID, name, category, optional parent plane, and data-library reference. Elemental identity/spirit information now resides in the lazily loaded `elemental_planes` data library.
- Added 13 distinct elemental plane records: Fire, Water, Earth, Air, Ice, Metal, Thunder, Life, Death, Underworld, Holy, Shadow, and Void. Each has a corresponding elemental spirit data record.
- Added the other seven top-level planes: Mortal Plane, Hell, Heaven, Atlantis, Fae Paradise, Lineage Halls, and Wild Realm. Hell's currently defined regions are Naraka, The Ten Courts, and Yomi Hollows; Naraka's 16 subregions are not created yet.
- Added the specified category catalogue, the `exists()` check, and data-only `plane_of`, `element_of`, and `spirit_of` operations. MANA objects do not gain a plane property; non-being values resolve to the Mortal Plane.
- Represented a pathway explicitly with its endpoints, one-way/bidirectional setting, and open/closed state. Route search and reachable-neighbor output follow only open directed access.
- Added `invoke`, `revoke`, and `has_permission`; only the four base elements bypass invocation when their elemental energy is taken.
- Added joule-based `send_energy`, virtual-time `open_channel`/`close_channel`, `energy_sent`, and `path_opened`, `path_closed`, and `energy_arrived` events. Transfers use the existing energy ledger with balanced source/target deltas.
- Added separate data modules for elemental planes, Hell, Heaven, Atlantis, Fae Paradise, Lineage Halls, and Wild Realm. Being records contain their home plane, element tie, summoning requirements, HP, max HP, defence, attack, and resistance fields; resistance defaults to zero, while unspecified combat stats remain unset. These records do not implement entity transfer or combat.
- Enforced dependencies for built-in plane data libraries and user-library manifest `dependencies`. Fixed rollback of newly loaded data-library caches alongside pathway, permission, and ledger rollback.
- Updated the language/function references, plane-library guide, builder guide, component reference, README, current index, example, and release metadata. Added regressions for the complete public API, custom-library dependencies, one-way pathways, lazy loading, ledger conservation and rollback.
- `drafter` and `summoning` remain separate future libraries; neither is implemented by `planes` in this release.

## v0.10.2 — Plane identification and pathway navigation

- Added the built-in `planes` namespace for resolving registered plane identities and reading categories/structural relationships.
- Added bidirectional `connect`/`disconnect` and directed `add_pathway`/`remove_pathway` operations.
- Added deterministic shortest-route lookup, direct-pathway checks, outgoing connection listing and route-length lookup.
- Added joule-validated planar energy transfer records to the runtime energy ledger. Source and destination deltas balance to zero net external energy change.
- Added a runtime-scoped shared registry and an internal registration hook for a future, separate plane-creation library; no creation API is exposed by `planes`.
- Added a runnable pathway/energy example, a complete library reference, and regression tests for aliases, directions, routing, transfer accounting, spell rollback boundaries and coexistence with the 2D/3D calculation libraries.
- Updated release metadata and VS Code packaging to `0.10.2`, using the root `VERSION` file as the package builder's version source.
- The `summoning` library is not part of this revision.

## v0.10.1 — Audit fixes, integrity and library verification

- Corrected release metadata to `0.10.1` across `VERSION`, the Python package, VS Code extension metadata, VSIX filename, README and current documentation.
- Fixed deterministic `simul:` execution: statements run in source order after conflict validation, with rollback if any operation fails.
- Added list indexing for list/string/range reads, indexed list assignment, and `len()` for lists, strings and ranges.
- Standardized variable scope: assignments first introduced inside control-flow blocks belong to the enclosing definition or module scope.
- Defined direct definition calls as helper execution: direct helpers may calculate and return values but cannot create or mutate world objects. Use `post` or `release` for spell execution; event-registration helpers may register `when` handlers.
- Added Celsius absolute-temperature literals (`C`) and signed Celsius literals; absolute readings cannot be multiplied, divided, exponentiated, or passed as `heat()`/`cool()` increments, which require temperature changes in K.
- Added configurable element/material integrity thresholds, baseline integrity calculations, stabilizer effects, integrity readouts and collapse to a `ThermalRelease` carrier at zero integrity.
- Removed the optional `geometry2d.launch` helper; motion continues to use `velocity()` with external target selection where appropriate.
- Rechecked 2D and 3D calculation libraries: fixed polygon-edge tolerance, robust 3D vector normalization/magnitudes, unit-composing 3D dot products, validated pressure inputs, and corrected the displacement API documentation.
- Expanded regression coverage and refreshed current language, physics, library, tooling and function-reference documentation.

## v0.10.0 — First deterministic physics engine

At the time of this release, the identifier was **0.10.0**. The primary world physics is 2D in the x-y plane; 3D vector calculations are retained in the library layer. `post(spell)` fully executes a trial and rolls world changes back, while `release(spell)` commits the same spell execution.

- Added fixed-step motion integration with a configurable timestep and optional explicit world-gravity vector.
- Added vector-valued velocity, acceleration and deceleration support, including vector-times-quantity unit composition.
- Added swept equivalent-circle collision detection for the 2D world, mass/restitution-based normal response, overlap correction, and collision history.
- Scaling an object now scales its positive explicit 2D collision radius linearly alongside projected area scaling by the square of the factor.
- Added prototype collision heat, target impact damage using HP, defence and elemental resistance, and automatic `impact`, `collision` and `damaged` events.
- Added `last_collisions()` and expanded `active_objects()` inspection.
- Fixed `push`/`pull` action acceleration so it is not integrated a second time during later clock steps.
- Added detailed physics documentation, motion/collision examples, and regression coverage.
- Added a collision-pair safety budget to prevent a large collision world plus tiny timesteps from locking the interpreter.
- Documented limitations: circular bounds in 2D, Newtonian collision solver, no fluids/combustion/friction/angular dynamics, and unfinished integrity/breakage.
- The v0.10.0 build included the targeted-casting correction under the `0.10.0` label: `tgset(target):` provides an external target context; scalar `velocity(object, speed)` aims at it and targeted `post`/`release` simulate flight and collision. In v0.10.1, use `velocity()` with external target selection; the optional `geometry2d.launch(...)` helper described below is no longer exported.
- At v0.10.0, `launch()` was removed from the global built-in namespace. That historical build also exposed `geometry2d.launch(object, speed, angle_radians)` as an optional helper. v0.10.1 removes that helper from the current API; motion uses `velocity()` with external target selection.
- Added target-flight regression tests and a `targeted_fireball.mana` example. `post` verifies the hit then restores target/world state; `release` commits damage and collisions.
- Organized the current documentation under purpose-based folders and added a component reference covering the exact token, AST, runtime-value, module, element, library and test inventories.
- Expanded library-builder validation so package names and exports are checked against the interpreter's full reserved-name catalogue before a package is built.
- Corrected API-documentation coverage checks for function signatures and namespaced constants; added regressions proving `geometry2d`, `vector3d`, and normal world operations coexist without shadowing one another.
- Kept the existing `post`/`release` execution policy unchanged: preview runs and rolls back; release commits successful world changes.

## v0.9.0 — Element spell templates, tuning, pass, and documentation

- Element-parameterized definitions accept only `element`, selecting one of the four fundamental element types.
- `configured_spell = template(Fire)` creates an independent spell instance without executing its body.
- `create element` resolves the selected element type inside a template.
- Replaced parameter tuning with `tune(spell.operation) = target, value`.
- `tune` modifies an existing operation/target pair only; missing or ambiguous targets raise a clear error.
- Tuning is stored per configured spell instance and persists across `post` rollback.
- Added the reserved `pass` no-operation statement.
- Rewrote public examples and expanded/reformatted the beginner guide, language specification, built-in reference, and spell template/tuning guide.
- Moved the v0.8.0 audit into the historical archive and updated the VS Code extension's syntax grammar and snippets.
- Added regression tests for template construction without execution, four-element validation, operation tuning, tune isolation, errors, and `pass`.

## v0.8.0 — Execution commands and early tuning model

Historical release. See `docs/archive/v0.8/AUDIT_V0_8_0.md`.

## v0.7.1 — Documentation and packaging cleanup

Historical release. See the matching release archive.

## v0.6.2 — Energy ledger fixes

- Corrected derived energy updates, mana cost readouts, composite/split bookkeeping, and release provenance.

## v0.6.1 — Semantic and energy patches

- Introduced the modern `show`, `post`, `release`, and `incant` semantics.
