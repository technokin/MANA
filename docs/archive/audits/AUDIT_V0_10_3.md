# MANA v0.10.3 — Planes Library Implementation Audit

## Scope

This revision replaces the earlier `planes` API with the owner's full plane-library plan. The plane registry is deliberately small: it stores identities, categories, region parents, data-library names, pathway records, and invocation permissions. Plane content is loaded from independent data libraries when needed.

This release does not implement the `drafter` or `summoning` APIs. Both are reserved and declare a dependency on `planes`; importing either without `planes` produces a dependency error, and importing it after `planes` produces a clear not-implemented error.

## Built-in catalogue

The registry contains 20 top-level planes:

- Elemental: Fire, Water, Earth, Air, Ice, Metal, Thunder, Life, Death, Underworld, Holy, Shadow, Void.
- Mortal: Mortal Plane.
- Afterlife: Hell, Heaven, Lineage Halls.
- Living realm: Atlantis, Fae Paradise, Wild Realm.

Hell's `hell` data library registers three regions on demand: `Hell.Naraka`, `Hell.The Ten Courts`, and `Hell.Yomi Hollows`. The sixteen Naraka subregions are not registered in this build.

## Public `planes` API

- Identification: `identify`, `exists`, `plane_of`, `all_planes`, `regions_of`, `parent_of`.
- Categories: `category_of`, `planes_in`, `same_category`.
- Pathways: `open_path`, `close_path`, `is_open`, `paths_of`, `neighbors`, `find_route`, `reachable`.
- Energy: `send_energy`, `open_channel`, `close_channel`, `energy_sent`.
- Elemental data and permissions: `invoke`, `revoke`, `has_permission`, `element_of`, `spirit_of`.

Every exported API name is checked against `docs/current/libraries/PLANES_LIBRARY.md` by the test suite.

## Pathways and energy accounting

Pathways are explicit records with two endpoint IDs, directionality (`one_way`), and an `open`/`closed` state. Pathways are closed by default. Open pathways can be direct or form a route through other planes or regions. Route lookup uses deterministic breadth-first search and respects one-way directionality and closed state.

`send_energy` accepts a finite, non-negative energy quantity in joules. It requires a route and, for non-base elemental source planes, permission from `invoke`. The existing energy ledger records a negative source delta, positive destination delta, and zero net delta; it does not count the transfer as external energy creation or loss. `open_channel` takes a positive power quantity in watts and records each time-step transfer through that ledger.

Being movement is not part of `planes`. The API does not add a plane property to MANA world objects. `plane_of` returns the home plane for a `BeingRecord`; any other input maps to Mortal Plane.

## Plane-data modules

- `elemental_planes`: data for all 13 elemental planes and one elemental spirit record per plane.
- `hell`: Hell's three current regions.
- `atlantis`: Mermaid.
- `fae_paradise`: Elf.
- `wild_realm`: Griffin, Werewolf, Vampire, Chimera, Giant, Orc.
- `heaven` and `lineage_halls`: separate data modules, currently with no named being records supplied.

Each plane-data module is loaded independently. Explicit imports require `planes` first; internal lazy loads by `planes` do not require a second import. Registry and loaded-library cache state participate in runtime rollback so a failed execution cannot leave region registrations or a newly cached module behind.

Being records have the specified fields: `name`, `kind`, `home_plane`, `element`, `summoning_requirements`, `hp`, `max_hp`, `defence`, `attack`, and `resistance`. Resistance is initialized to `0` for each listed element. HP, max HP, defence, and attack remain unset until assigned rather than being assigned fabricated defaults. These records are data only in this release.

## Dependency behavior

Built-in plane-data libraries require `planes` to be imported first. User `.manalib` dependencies are checked against the libraries imported in the current environment. The future `summoning` and `drafter` names also have explicit `planes` dependency declarations, but their implementations are not part of this release.

## Events

The library emits:

- `path_opened` when an open pathway is created or changed.
- `path_closed` when an open pathway is closed.
- `energy_arrived` after an energy transfer from `send_energy` or an active channel.

Event arguments are passed through MANA's existing `event_args` mechanism.

## Verification

- `python -m pytest -q`: **221 passed** in the working tree during release preparation.
- `python -m compileall -q magiclang tools mana.py`: passed.
- The planes navigation example runs using `find_route`, `send_energy`, and `energy_sent`.
- The API documentation coverage test passes.
- Tests cover catalogue/category data, region loading, one-way/bidirectional/closed pathways, deterministic routes, energy ledger balance, invocation, channels, events, dependency checking, runtime isolation, rollback and source-located MANA errors.
- Existing 2D geometry and 3D vector tests pass as part of the full suite.
- Release metadata and the VS Code extension package are built for `0.10.3`.

## Deliberate limits

- `drafter` does not create plane records yet; its internal registry hook is not exposed to MANA source.
- `summoning` does not transfer entities yet.
- There are no plane-specific energy reservoirs; movement is recorded as an internal ledger transfer.
- There is no arbitrary coordinate model or plane-internal simulation.
- The Naraka subregions are not added until their being catalogue is defined.
- The existing data records do not execute combat, summoning, or any other being behaviour.
