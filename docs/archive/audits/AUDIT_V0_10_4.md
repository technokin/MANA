# MANA v0.10.4 — Implementation audit

## Scope

This release adds a built-in pure-mana effect namespace and more accessible universal object control on the runtime carried forward from v0.10.3. The existing `push`, `pull`, `move`, `velocity`, geometry operations, `planes` library, and calculation-only `vector3d` library remain present.

## Implemented

- Uppercase `Mana` remains a type selector accepted by `create Mana`. Lowercase `mana` is a separate namespace, installed automatically; `import mana` is also accepted.
- `mana.form`, `mana.burst`, and `mana.emit` create a finite-energy pure-mana construct, apply a radial pulse, and emit a directed ray. Numeric defaults are documented in [the Pure Mana and Universal Control guide](../../current/libraries/MANA_LIBRARY.md). The current world collision representation is 2D circular bounds even when a construct carries a shape label such as `wall` or `disc`.
- `mana.control`, `mana.toward`, `mana.away`, `mana.lift`, `mana.hold`, `mana.levitate`, `mana.stop`, `mana.release_control`, and `mana.collect` provide element-independent control over existing objects. The current implementation uses the existing 2D runtime and its motion operations. In a terminal-only runtime the caster position starts at (0 m, 0 m), so the default offset resolves to (10 m, 0 m) until an engine supplies a different caster position.
- Within `tgset(target):`, an omitted `toward` destination or `away` source uses the selected target position. `collect` defaults to the selected target, or the runtime caster position when no target context is active. Objects already at the collection destination are left untouched.
- `mana.stop` / `mana.hold` convert kinetic energy into the same object's thermal energy before stopping it, rather than deleting kinetic energy. `mana.hold` and `mana.levitate` then anchor the object.
- Pure-mana projectile collision transfers the construct's remaining `mana_energy` to the contacted material as thermal energy. The projectile is then deactivated. The energy ledger records equal-and-opposite internal transfer deltas.
- `tgset` material profiles infer `combustible` for supported wood, paper, plant and fabric materials unless explicitly overridden. The default ignition threshold is 573.15 K. When a heat operation leaves an object at or above that threshold and it is not already burning, the object state becomes `burning` and an `object_ignited` event is emitted.
- Solid `tgset` materials default to `powderable` unless they are a non-solid or special construct. `transform(object, "powder")` checks that field and preserves mass and tracked energy on the same aggregate object.
- The VS Code syntax grammar recognises `Mana` and the new material/control properties. Current language guides, built-in reference, library reference, component reference, index, README and changelog were updated.

## Defaults

| Operation | Current default |
|---|---|
| `mana.form()` | sphere; 1000 J; 1 m radius; position 10 m along +X from runtime caster |
| `mana.burst()` | 1000 J; 1 m radius; position 10 m along +X from runtime caster |
| `mana.emit()` | 1000 W; 1 s; 10 m range; 1 m beam radius; position 10 m along +X from runtime caster |
| `mana.toward` / `mana.away` / `mana.lift` | 100 N for 1 s |
| `mana.collect` | 100 N for 1 s; destination defaults to selected target or caster position |

All of these are defaults, not fixed limits. `mana.emit` uses power × duration as its total energy. All effect positions and directions are interpreted by the existing 2D world.

## Verification

- Final packaged verification: **238 tests passed** from the extracted v0.10.4 ZIP.
- Regression tests cover namespace and type-selector availability, default values, named optional arguments, wood ignition, powderability overrides, contextual targeting, collection of multiple objects, stop/hold energy conservation, direct-helper safety, and projectile collision transfer.
- Existing language, physics, audit-regression, planes, geometry and 3D-vector tests remain in the same suite.
- The VS Code extension package is built from the versioned source metadata and checked for archive integrity and matching version.
- The delivered project ZIP is extracted and tested after packaging.

## Current limitations

- The world engine remains 2D; `vector3d` remains a calculation library and does not enable 3D world physics.
- `tgset` creates object/material profiles but does not extract matter from continuous terrain.
- Combustion is currently an ignition state transition; continuing fuel consumption, smoke, fire spread and burn products are not simulated.
- `powder` is one aggregate object, not a collection of independently simulated particles.
- `mana.lift` applies a force for a duration; `mana.hold` / `mana.levitate` provide fixed-position anchoring rather than a general trajectory planner. Barrier-style constructs currently do not have energy-based durability or maintenance costs.
- The new namespace does not implement `drafter`, `summoning`, or necromancy. Those remain separate libraries/systems.
