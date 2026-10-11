# Changelog

## v1.0.0 — First public 1.0 release

- Declared the current MANA language/runtime implementation as the v1.0.0 public release while documenting known implementation boundaries rather than promising unfinished systems.
- Kept MANA programs in `.mana` source files and Python as the current implementation runtime; no third-party runtime packages are required.
- Removed the custom Grimoire IDE and its custom-IDE build components from the distributable project; retained the Python runner, examples, libraries, tests, documentation, and VS Code Language Support extension.
- Added the MANA logo to the GitHub README and packaged VS Code extension.
- Clarified runtime versus development requirements, added Ruff configuration guidance, and retained `.editorconfig` for consistent editor behaviour.
- Reorganized contribution guidance and release-facing documentation while preserving historical audit reports and changelog entries.
- Release verification: the exact test and packaging results are recorded in `docs/archive/audits/release_reports/RELEASE_V1_0_0_REPORT.md`.

## Pre-v1.0 project organization update (historical)

- Removed the custom Grimoire IDE, its Windows launcher/build workflow, and IDE-specific tests and documentation from the current source tree. Historical changelog entries and archived audit reports are preserved as history.
- Kept the Python MANA interpreter, `.mana` source files, examples, libraries, tests, documentation, and VS Code extension.
- Reworked the root README into a GitHub landing page with accurate Python/license/runtime requirements; kept `MANA_INTRO.md` as a separate conceptual introduction and added `CONTRIBUTING.md` and `tests/README.md`.
- Replaced the IDE-specific Windows build workflow with cross-platform Python test CI, added a current-file syntax-check task, and moved Ruff settings from an otherwise unnecessary `pyproject.toml` to `ruff.toml`.
- Prepared optional VS Code icon packaging from `assets/branding/mana-icon.png`; the actual logo was added with the v1.0.0 release.
- Recorded the checks and outstanding verification items in [`PROJECT_ORGANIZATION_REPORT_V0_10_14.md`](docs/archive/audits/release_reports/PROJECT_ORGANIZATION_REPORT_V0_10_14.md).
- At the time of this organization update, the project remained at 0.10.14. The later v1.0.0 release is recorded above.

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
