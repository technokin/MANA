# MANA v0.10.0 — Physics and Library-System Audit

**Release identifier:** remains `0.10.0`. This revision extends the documentation and library tooling on the same release line; it does not redesign `post` or `release`.

## Implemented in the v0.10.0 line

- The default world engine is 2D in the x-y plane and runs without an import. Scalar `velocity(object, speed)` uses the active `tgset(target):` context to calculate the direction; explicit vectors remain available for low-level control.
- `post(spell)` executes the normal spell logic as a trial, reports what would happen, and restores world state. `release(spell)` executes the same logic and commits successful world changes. These mode semantics are unchanged by the documentation/library work.
- Deterministic stepping, persistent acceleration, explicit per-call gravity, swept-circle collision checks, basic impulse response, impact heat, prototype target damage, `impact`/`collision`/`damaged` events, collision history, and runtime safety caps are implemented.
- `geometry2d` is an optional namespace for advanced planar calculations and explicitly controlled motion. Its functions—including angles, coordinates, intersections, `aim`, and `geometry2d.launch(object, speed, angle_radians)`—are only available through the namespace after `import geometry2d`. The helper `launch` does not choose a target.
- `vector3d` is an optional calculation-only namespace. It provides 3D vector operations and physical calculations, but does not enable 3D world movement or collision physics.
- Both built-in libraries may be imported together. Their exports remain namespaced, and core world operations remain available. User-authored MANA libraries can also export names that match global operations because those helpers are called through their own namespace.
- The Library Builder supports `init`, `validate`, and `build` for MANA-native `.manalib` packages. It validates manifests, source grammar, top-level declarations, exports, reserved package names, and archive integrity. The runtime does not execute arbitrary Python payloads from packages.
- Current docs are categorized by purpose under `docs/current/`; historical material is under `docs/archive/`; unimplemented ideas are under `docs/ideas/`.

## Documentation coverage

The documentation coverage audit and tests cross-check the implementation-derived inventories:

- 50 token kinds and 28 AST node classes.
- 19 registered element/catalogue entries.
- 68 globally reserved/built-in names, including operations, constants, namespace names and geometry labels.
- 29 `geometry2d` exports and 25 `vector3d` exports.

See [Documentation Coverage Audit](DOCUMENTATION_COVERAGE_V0_10_0.md) for the complete map and automated coverage rules. See [Implementation Component Reference](../../current/internals/COMPONENT_REFERENCE.md) for what each source module does, all token categories, AST node inventory, runtime values, error classes and test ownership.

## Known limitations

- The world engine uses circle colliders derived from projected area or an explicit radius; it does not yet simulate exact polygon/wall geometry.
- Collision response is Newtonian even though some energy and momentum readouts use relativistic formulas. Near-light-speed collisions are not a validated regime.
- Fluids, air resistance, friction, rolling, torque/angular response, combustion, pressure waves, full phase-change simulation, integrity/breakage, stabilizers and uncontrolled collapse remain unfinished.
- Default target positions in the headless prototype use a target's explicit `pos`; a `distance`-only target profile falls back to the forward (+X) axis. A future world engine should supply actual world/NPC positions.
- `geometry2d.launch` is a manual-angle advanced helper; the normal target-directed flow is `velocity()` plus an external `tgset(target):` context.
- `.manalib` currently packages one entry source file and an optional README. General multi-file source packages and dependency/version resolution are future work.
- The graphical world viewer and standalone Grimoire IDE are not implemented. The simulation remains authoritative; graphics must only display results.
- Windows registry/Explorer file association has not been validated on an actual Windows host in this environment.

## Verification

Validation was run from the release source tree before packaging:

- **137 automated tests passed**, including physics, energy, spell execution modes, library isolation/coexistence, library-builder safety, documentation coverage, examples and editor tooling.
- All **9 public `.mana` examples** executed through fresh runtimes.
- `python -m compileall -q magiclang mana.py tools/library_builder.py` completed successfully.
- A real command-line invocation of `mana.py` was smoke-tested.
- Markdown local links were checked; no broken local links were found.
- The VSIX and final ZIP are checked for archive integrity and version consistency; the final extracted ZIP will be tested as a release artifact.

The documentation/library changes do not alter the defined `post`/`release` policy. Regression tests continue to cover the trial rollback and committed execution paths.
