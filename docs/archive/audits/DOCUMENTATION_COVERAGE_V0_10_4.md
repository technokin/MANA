# MANA v0.10.4 — Documentation coverage

## Pure mana and universal control

Every name exported by `magiclang.libraries.mana.build_library()` is documented in [Pure Mana and Universal Control](../../current/libraries/MANA_LIBRARY.md) and the matching built-in reference section. The regression suite in `tests/test_mana_control.py` covers the principal public behaviour and error boundaries.

| Exported name | Documented role |
|---|---|
| `form` | Create a finite-energy pure-mana construct |
| `burst` | Release a radial pure-mana pulse |
| `emit` | Emit a directed pure-mana ray |
| `control` | Common action dispatcher for element-independent object control |
| `toward` | Apply force toward a destination or selected target |
| `away` | Apply force away from a source or selected target |
| `lift` | Apply upward force for a specified duration |
| `hold` | Stop, conserve kinetic energy as heat, and anchor |
| `levitate` | Accessible fixed-position form of `hold` |
| `stop` | Stop movement while conserving kinetic energy |
| `release_control` | Release a controlled anchor |
| `collect` | Apply toward-control to one object or a list |

## Language and material-profile documentation

- `docs/current/getting_started/LANGUAGE_GUIDE.md` introduces `Mana`, the lowercase `mana` namespace, defaulted effect calls and `tgset` material profiles.
- `docs/current/reference/FUNCTION_REFERENCE.md` describes the public pure-mana namespace and material fields.
- `docs/current/language/LANGUAGE_SPEC.md` describes the auto-installed namespace, `Mana` type selector, recognized events and reserved material fields.
- `docs/current/internals/COMPONENT_REFERENCE.md` includes the new `magiclang/libraries/mana.py` module.
- `README.md` and `docs/current/INDEX.md` link to the new library guide.

## Existing subsystems rechecked

The full test suite still covers the existing 2D physics engine, `geometry2d`, calculation-only `vector3d`, plane identification/pathways, runtime unit rules and language behaviour. This release does not claim to provide 3D world simulation, continuous combustion, terrain extraction, or the `drafter` and `summoning` implementations.
