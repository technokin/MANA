# MANA v0.10.5 — Library integration audit

## Scope

This release adds `drafter`, `summoning`, and `necromancy` to the existing `planes` and `mana` systems, then rechecks the 3D calculation library's integration with world entities. This is a targeted addition to the existing interpreter, not a rewrite. The authoritative code is the runtime and library implementation.

## Implemented

- **`drafter`** creates new plane definitions from a draft. A draft supports an ID, category, aliases, arbitrary safe custom values, regions, being records, selected combat fields, element ties, summoning conditions, and per-element resistance. A successful creation registers the plane and regions atomically. Registered planes cannot be edited through `drafter`.
- Custom plane data is stored in the current runtime session. The terminal workflow is a `.mana` setup file that is rerun when creating a new runtime. Persistent plane-data generation and an IDE editor are future work.
- Plane custom values are inert data. They do not alter units, physical laws, parser/runtime semantics, or world execution.
- **`summoning`** resolves built-in and custom `BeingRecord` data, checks the declared conditions, requires an open route in `planes`, and creates a standard world object with a home-plane identity and its optional configured stats. It does not use a separate movement/physics system.
- The current simulated world exists only in the **Mortal Plane**. `summoning` rejects another destination before registering an entity or transfer. This restriction is enforced in code.
- Summoning is a world-changing operation and must execute inside `post()` or `release()` spell execution; a direct call from a pure helper is rejected. Its entity and internal-transfer record roll back if an event handler fails, and `post()` restores the trial.
- **`necromancy`** reanimates eligible existing local corpse/bone/skeleton/remains objects, after verifying a route from the Underworld and invoking that source. It transfers bound energy through `planes`, adds that energy to the object's energy/integrity state, and marks it as an undead being. It has no dependency on `summoning`.
- `necromancy.reanimate_many()` checks distinct eligible bodies, transfers their total required energy once, and rolls back as a group if event dispatch fails. Both necromancy world operations are restricted from unsafe direct helper calls.
- Added `plane_created`, `being_summoned`, and `being_reanimated` events to the MANA event registry. Errors follow the existing MANA error classes and are wrapped with source locations by the runtime.
- **3D interoperation:** `vector3d.planar()`, `vector3d.is_planar()`, and `vector3d.object_vector()` bridge vector calculations and world objects. A 3D-calculated position with nonzero z is rejected for world placement. These utilities do not enable 3D world physics.
- Added runnable examples for plane creation, summoning, necromancy, and combined use of all three libraries with the 3D vector bridge.

## Boundaries

- Custom plane configuration is runtime-scoped and is not serialized to disk automatically.
- The simulator is still 2D. Non-Mortal destinations cannot host simulated beings, and 3D vector math does not enable 3D collision or motion simulation.
- Summoning conditions are explicitly supplied condition strings; item inventory lookup or consumption is not implemented.
- Beings are regular world objects for motion and collision. This revision does not implement AI, autonomous orders, combat decisions, or creature-specific behaviour.
- Necromancy reanimates an existing local body; it does not create a skeleton from nothing, import a body from another plane, or invoke summoning.
- The libraries keep stats as data. Unspecified HP, max HP, defence and attack remain unset; element resistances default to zero.

## Verification

- The full automated suite passes **257 tests** and covers parser/runtime behaviour, physics and energy rules, `planes`, `drafter`, `summoning`, `necromancy`, 2D/3D calculation helpers, packaging, and examples.
- Four standalone workflow examples are included: `drafter_define_plane.mana`, `summoning_example.mana`, `necromancy_example.mana`, and `drafter_summoning_necromancy_3d_bridge.mana`.
- Regression tests cover invalid destinations, missing pathways/permissions/dependencies, custom definitions and regions, configured requirements, event-failure rollback, `post()` rollback, batch energy transfer, and 3D-to-2D position validation.
- The current VS Code extension package is generated from the same `0.10.5` version metadata as `VERSION` and the Python package.
- The final ZIP is extracted and tested after packaging.
