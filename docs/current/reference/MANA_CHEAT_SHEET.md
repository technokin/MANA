# MANA Cheat Sheet

**Page kind:** Reference  
**Version:** read from the repository's `VERSION` file at release time.

This is a compact lookup page. For full rules, see the [Language Specification](../language/LANGUAGE_SPEC.md), [Function Reference](FUNCTION_REFERENCE.md), [Glossary](../foundations/GLOSSARY_AND_DESIGN_TERMS.md), and [Troubleshooting](../troubleshooting/TROUBLESHOOTING.md).

## Core keywords

`def`, `spell` (legacy alias `spldef`), `appraise`, `cast`, `load`, `incant`, `tgset`, `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not`, `true`, `false`, `create`, `simul`, `wait`, `after`, `every`, `when`, `skip`. Legacy `post(...)` and `release(...)` forms remain supported.

`post(...)` runs a spell as a trial; `release(...)` commits its changes. `show(...)` displays values. These are built-ins, not control keywords. `tune(...)` is the tuning operation.

Any word that is not a supported keyword, built-in, variable, property, or loaded library member is reported as **not identified**. See the reserved names below before choosing names.

## Operators

| Category | Operators |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%`, `**` |
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Boolean | `and`, `or`, `not` |
| Assignment | `=` |
| Access and collections | `.`, `[...]`, `(...)`, `,` |

## Units and prefixes

| Unit | Meaning |
|---|---|
| `kg` | mass |
| `m`, `m2`, `m3` | length, area, volume (`m^2` and `m^3` are also accepted) |
| `s` | time |
| `K` | absolute temperature |
| `m/s`, `m/s2` | speed, acceleration (`m/s^2` is also accepted) |
| `N`, `J`, `Pa`, `W` | force, energy, pressure, power |
| `kg/m3`, `kg*m/s`, `mana`, `mana/s` | density, momentum, mana-equivalent quantity, mana-equivalent rate |

Supported SI prefixes are `k` (10³), `M` (10⁶), `G` (10⁹), `m` (10⁻³), `u` (10⁻⁶), and `n` (10⁻⁹). Exact registered units take precedence over prefix parsing. Use lowercase `c` in MANA for the speed-of-light constant; the implementation names this constant `C` internally. Speeds at or above the supported limit are rejected.

## Reserved names

Language keywords and runtime built-ins cannot be used as ordinary names. Important built-ins include `show`, `post`, `release`, `span`, `length`, `heat`, `cool`, `velocity`, `combine`, `transform`, `move`, `force`, `pressure`, `geometry2d`, `vector3d`, `planes`, `summoning`, `necromancy`, and `mana`. Runtime-managed object properties include `mass`, `volume`, `area`, `density`, `pos`, `vel`, `acc`, `force`, `energy`, `temp`, `pressure`, `state`, `material`, `mana`, `integrity`, `hp`, and `max_hp`.

The exact reserved sets are maintained in `magiclang/runtime.py`; this list is a quick guide, not a substitute for the runtime's validation.

## Events

`impact`, `collision`, `damaged`, `path_opened`, `path_closed`, `energy_arrived`, `plane_created`, `being_summoned`, `being_returned`, `being_tamed`, `being_reanimated`, `being_animated`, `mana_formed`, `mana_burst`, `mana_emitted`, `object_ignited`.

## Error classes

| Class | Meaning |
|---|---|
| `SyntaxErrorML` | Syntax or structure is invalid. |
| `TypeErrorML` | A value has an unsupported type. |
| `UnitErrorML` | A unit or dimension is invalid or incompatible. |
| `RuntimeErrorML` | A name, call, index, or execution operation is invalid. |
| `MagicErrorML` | A magical operation or managed state violates MANA rules. |
| `PhysicsErrorML` | A physical value or operation violates the world model. |

CLI diagnostics include a stable diagnostic code and source location. Set `MANA_DEBUG=1` to display a full internal traceback for unexpected interpreter failures.

## Common commands

```powershell
python mana.py examples\fireball.mana
python mana.py --check examples\fireball.mana
python tools\library_builder.py validate libraries\my_geometry
```
