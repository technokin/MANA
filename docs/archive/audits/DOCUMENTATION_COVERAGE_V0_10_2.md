# MANA v0.10.2 — Library Documentation Coverage

> Historical report: the export names below describe v0.10.2. Links lead to the current plane-library guide, whose API may have changed since that version.

The API coverage test in `tests/test_planes_library.py` checks that every exported name from `magiclang.libraries.planes.build_library()` appears in `docs/current/libraries/PLANES_LIBRARY.md`.

## Planes exports

| Export | Documented in |
|---|---|
| `identify` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `exists` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `known` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `category` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `based_on` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `connections` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `connect` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `disconnect` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `add_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `remove_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `has_pathway` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `locate` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `path_length` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |
| `transport_energy` | [Planes Library](../../current/libraries/PLANES_LIBRARY.md) |

`PlaneReference` is a returned read-only value, not a callable export. Its fields are documented in the plane identity section.
