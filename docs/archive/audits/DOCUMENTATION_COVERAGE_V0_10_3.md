# MANA v0.10.3 — Planes API Documentation Coverage

Every exported name from `magiclang.libraries.planes.build_library()` is required to appear in `docs/current/libraries/PLANES_LIBRARY.md`. `tests/test_planes_library.py` enforces this coverage.

| API group | Exported names | Reference |
|---|---|---|
| Identification | `identify`, `exists`, `plane_of`, `all_planes`, `regions_of`, `parent_of` | [Planes Library: plane identification and categories](../../current/libraries/PLANES_LIBRARY.md#plane-identification-and-categories) |
| Categories | `category_of`, `planes_in`, `same_category` | [Planes Library: plane identification and categories](../../current/libraries/PLANES_LIBRARY.md#plane-identification-and-categories) |
| Pathways | `open_path`, `close_path`, `is_open`, `paths_of`, `neighbors`, `find_route`, `reachable` | [Planes Library: pathways](../../current/libraries/PLANES_LIBRARY.md#pathways) |
| Energy | `send_energy`, `open_channel`, `close_channel`, `energy_sent` | [Planes Library: energy transfer](../../current/libraries/PLANES_LIBRARY.md#energy-transfer) |
| Elemental data and permission | `invoke`, `revoke`, `has_permission`, `element_of`, `spirit_of` | [Planes Library: elemental planes](../../current/libraries/PLANES_LIBRARY.md#elemental-planes) |

## Plane-data coverage

| Data library | Documented contents |
|---|---|
| `elemental_planes` | 13 elemental plane records and their elemental spirits |
| `hell` | Hell and its three regions |
| `heaven` | Separate data module; no named beings yet supplied |
| `atlantis` | Mermaid |
| `fae_paradise` | Elf |
| `lineage_halls` | Separate data module; no named beings yet supplied |
| `wild_realm` | Griffin, Werewolf, Vampire, Chimera, Giant, Orc |

See [Planes Library](../../current/libraries/PLANES_LIBRARY.md) for accepted arguments, returned records, errors, events, energy-accounting rules and dependency behavior. See [Implementation Audit](AUDIT_V0_10_3.md) for implementation details and current limits.
