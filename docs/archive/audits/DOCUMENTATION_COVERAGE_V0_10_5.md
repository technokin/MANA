# MANA v0.10.5 — Documentation coverage

## Plane creation (`drafter`)

| Export | Documented purpose |
|---|---|
| `begin` | Begin an unregistered plane draft. |
| `alias` | Add a lookup alias before registration. |
| `set_value` | Attach inert custom data to a plane or region draft. |
| `add_region` | Add a region within a draft. |
| `add_being` | Define a being and supported data fields. |
| `set_being` | Change a being record while its plane is still a draft. |
| `create` | Register a complete plane draft atomically. |
| `properties_of` | Read a copy of custom values. |
| `get_value` | Read an individual custom value. |
| `beings_of` | Read beings assigned to a plane or region. |

## Summoning

| Export | Documented purpose |
|---|---|
| `find_being` | Resolve a being record from supplied data or loaded data libraries. |
| `summon` | Manifest a configured being through an open path into the Mortal Plane. |

## Necromancy

| Export | Documented purpose |
|---|---|
| `reanimate` | Reanimate one eligible local body using transferred Underworld energy. |
| `reanimate_many` | Reanimate distinct eligible bodies in one aggregate transfer. |
| `is_undead` | Inspect the undead marker on an object. |

## 3D interoperation

| Export | Documented purpose |
|---|---|
| `planar` | Explicitly set a 3D vector's z coordinate to zero. |
| `is_planar` | Test whether the z coordinate is within tolerance. |
| `object_vector` | Read a documented vector property from an ordinary world object. |

## Integration examples and dependencies

- `examples/drafter_define_plane.mana` exercises custom values, beings, categories and pathways.
- `examples/summoning_example.mana` exercises plane access, being lookup, placement, and 3D-vector projection.
- `examples/necromancy_example.mana` exercises Underworld invocation, energy transfer, local reanimation, and ordinary movement.
- `examples/drafter_summoning_necromancy_3d_bridge.mana` runs the libraries together.
- `drafter`, `summoning`, and `necromancy` require `planes` first; `necromancy` does not depend on `summoning`.
- Current library references: [Drafter](../../current/libraries/DRAFTER_LIBRARY.md), [Summoning](../../current/libraries/SUMMONING_LIBRARY.md), [Necromancy](../../current/libraries/NECROMANCY_LIBRARY.md), [Planes](../../current/libraries/PLANES_LIBRARY.md), and [3D Vectors](../../current/libraries/VECTOR3D_LIBRARY.md).
