# MANA v0.10.2 — Planes Library Verification

## Scope

This revision adds the built-in `planes` library, updates references and documentation, and adds regression tests. It does not add the `summoning` library or the separate plane-creation library.

## Implemented API

- `identify(plane)`: resolve a plane name, alias, or ID to a read-only reference.
- `exists(plane)`: check whether a plane is in the active runtime registry.
- `known(category)`: list registered plane names, optionally filtered to `foundational` or `ordinary`.
- `category(plane)` and `based_on(plane)`: read metadata.
- `connections(plane)`: list directly reachable pathways.
- `connect(source, destination)` / `disconnect(source, destination)`: add/remove a bidirectional pathway.
- `add_pathway(source, destination)` / `remove_pathway(source, destination)`: add/remove a directed pathway.
- `has_pathway(source, destination)`: check a direct directed pathway.
- `locate(source, destination)`: find a deterministic shortest route or return an empty list if unreachable.
- `path_length(source, destination)`: return the number of edges or `-1` when unreachable.
- `transport_energy(source, destination, energy)`: require an existing route and add a source/target-balanced internal transfer to the runtime energy ledger.

## Registry model

The current built-in catalogue includes foundational references for Fire, Water, Earth, Air, Ice, Life, Death and the Underworld, plus the configured ordinary-plane names documented in `PLANES_LIBRARY.md`. The registry is scoped to each runtime instance. It contains identifiers, categories and structural relationships, not coordinates. Ice records Water Plane and Air Plane as its structural basis; Underworld records Death Plane as its structural basis. Those relationships do not automatically create pathways.

The shared `planar_registry.py` module exposes an internal Python-side `register_plane` hook so a future plane-creation library can add player-defined plane references without merging creation into `planes`. That hook is not exported to MANA source by the current `planes` API.

## Pathway rules

Pathway edits are configuration operations and are blocked during spell trials/releases and from directly called helper definitions, avoiding state changes that would bypass the runtime rollback model. Pathway edits written at top level in a `.mana` program are applied in source order. The graph supports directed links and bidirectional links, and path selection is deterministic among equal-length routes.

Energy transport requires a `Quantity` dimensioned in joules, two distinct known planes, and a reachable route. The ledger entry records `amount_j`, a negative source-side delta, a positive destination-side delta and a net `delta_j` of zero. It does not increase external energy input/output totals. This records planar energy movement but does not create a plane-specific energy reservoir or move physical objects; entity transfer belongs to the later cross-plane access work.

## Validation

- `python -m pytest -q`: **206 passed** after updating example-count and tool-version checks for this release.
- `python -m compileall -q magiclang tools mana.py`: passed.
- The `planes_navigation.mana` example runs in a fresh runtime.
- Existing `geometry2d`, `vector3d` and core world operations remain usable when `planes` is imported.
- VS Code extension metadata and the generated `.vsix` are validated against the root `VERSION` file.

## Current limits

- The initial catalogue is fixed in the built-in registry; the public `planes` API cannot create or remove plane definitions.
- Registry changes exist only for the current runtime; a program should express its pathway setup in source. Persistent project storage is not implemented.
- No arbitrary planar coordinates, region hierarchy, or 3D spatial map is modelled. `locate` searches the directed pathway graph.
- Energy transfer is ledger accounting only; the runtime does not store a separate energy total per plane.
- `summoning` and the plane-creation library are not included in this revision.
