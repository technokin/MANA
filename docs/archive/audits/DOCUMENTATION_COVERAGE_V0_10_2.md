# MANA v0.10.2 — Library Documentation Coverage

The API coverage test in `tests/test_planes_library.py` checks that every exported name from `magiclang.libraries.planes.build_library()` appears in `docs/current/libraries/PLANES_LIBRARY.md`.

## Planes exports

| Export | Documented in |
|---|---|
| `identify` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesidentifyplane) |
| `exists` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesexistsplane) |
| `known` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesknowncategory) |
| `category` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planescategoryplane-and-planesbasedonplane) |
| `based_on` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planescategoryplane-and-planesbasedonplane) |
| `connections` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesconnectionsplane) |
| `connect` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesconnectsource-destination) |
| `disconnect` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesdisconnectsource-destination) |
| `add_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesadd_pathwaysource-destination) |
| `remove_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planesremove_pathwaysource-destination) |
| `has_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planeshas_pathwaysource-destination) |
| `locate` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planeslocatesource-destination) |
| `path_length` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planespath_lengthsource-destination) |
| `transport_energy` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md#planestransport_energysource-destination-energy) |

`PlaneReference` is a returned read-only value, not a callable export. Its fields are documented in the plane identity section.
