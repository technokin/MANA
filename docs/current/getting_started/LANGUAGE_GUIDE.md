# MANA Language Guide

**Page kind:** Tutorial  

**Version:** 2.0.0
**Audience:** beginners learning to write and test MANA spells

MANA is a standalone language for programmable magic. Source files use `.mana` and follow MANA’s own defined grammar and runtime rules.

## 1. Definitions: functions, spells, and targets

MANA has two kinds of definitions and a separate target system.

### Ordinary functions: `def`

Use `def` for normal computation, such as mathematics, calculations, and reusable logic. Functions can accept parameters. `incant` provides their result and exits the function.

```mana
def square(value):
    incant value * value

result = square(12)
show result
```

Expected output:

```text
144
```

A direct ordinary-function call cannot create world objects or otherwise mutate the simulated world. This keeps helper calculations predictable.

### Spell definitions: `spell` (legacy alias: `spldef`)

Use `spell` for code that runs through `appraise` or `cast`. The older `post(...)` and `release(...)` execution forms remain supported. It uses the same indentation and colon block style as the rest of MANA, not curly braces. A spell takes no parameters, or one `element` selector for a base-element template. Existing programs using `spldef` continue to work unchanged.

```mana
spell warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

post(warm_stone)
release(warm_stone)
```

Expected output:

```text
[POST warm_stone] inputs: no parameters
[POST warm_stone] energy input: 293150 J (create Earth; matter creation (initial state))
[POST warm_stone] created Earth (Earth, 1 kg; create Earth)
[POST warm_stone] energy input: 100000 J (heat; spell energy input; mana-equivalent is readout only)
[POST warm_stone] stone.energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity: 0.9953940111610206 -> 0.9949206008522664 (heat)
[POST warm_stone] stone.integrity_effective_energy_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.integrity_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity_last_score_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.mana_cost: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.mana_used: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.temp: 293.15 K -> 393.15 K (heat)
[POST warm_stone] stone.thermal_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] spell completed
[POST warm_stone] mana appraisal: 100000 mana
[POST warm_stone] created: stone (Earth, 1 kg)
```

A parameterized elemental template looks like this:

```mana
spell e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
post(fire_ball)
```

Expected output:

```text
[POST fire_ball] inputs: element=Fire
[POST fire_ball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fire_ball] created Fire (Fire, 1 kg; create Fire)
[POST fire_ball] ball.shape: 'point' -> 'circle' (shape)
[POST fire_ball] energy input: 500000 J (heat; spell energy input; mana-equivalent is readout only)
[POST fire_ball] ball.energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] ball.integrity: 0.992062994740159 -> 0.9909143970358393 (heat)
[POST fire_ball] ball.integrity_effective_energy_j: 1000000.0 -> 1500000.0 (heat)
[POST fire_ball] ball.integrity_energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] ball.integrity_last_score_j: 1000000.0 -> 1500000.0 (heat)
[POST fire_ball] ball.mana_cost: 0.1 -> 500000.1 (heat)
[POST fire_ball] ball.mana_used: 0.1 -> 500000.1 (heat)
[POST fire_ball] ball.temp: 1000 K -> 1500 K (heat)
[POST fire_ball] ball.thermal_energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] energy input: 45000 J (velocity; spell work)
[POST fire_ball] ball.energy: 1.5e+06 J -> 1.545e+06 J (velocity)
[POST fire_ball] ball.integrity: 0.9909143970358393 -> 0.9908244347201649 (velocity)
[POST fire_ball] ball.integrity_effective_energy_j: 1500000.0 -> 1545000.0000000338 (velocity)
[POST fire_ball] ball.integrity_energy: 1.5e+06 J -> 1.545e+06 J (velocity)
[POST fire_ball] ball.integrity_last_score_j: 1500000.0 -> 1545000.0000000338 (velocity)
[POST fire_ball] ball.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fire_ball] ball.mana_cost: 500000.1 -> 545000.1000000337 (velocity)
[POST fire_ball] ball.mana_used: 500000.1 -> 545000.1000000337 (velocity)
[POST fire_ball] ball.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fire_ball] ball.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fire_ball] spell completed
[POST fire_ball] mana appraisal: 545000 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

The only currently supported spell-template parameter is `element`, selecting `Fire`, `Water`, `Earth`, or `Air`. Other spell settings are written in the body or changed using `tune`.

### Target profiles: `tgset`

`tgset` is not a definition keyword. `guard = tgset:` creates a target profile; `tgset(guard):` selects it for the enclosed casting commands. Target selection remains outside the spell body.

## 2. Create independent spell instances

Calling an element template with a base element configures a spell instance. It does **not** execute the spell body:

```mana
spell e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
earth_ball = e_ball(Earth)
water_ball = e_ball(Water)
air_ball = e_ball(Air)
```

Expected output:

```text
(no output)
```

Each name now refers to a separate configured instance of the same definition. The instances keep their own tuning. Changing `fire_ball` does not change `earth_ball`.

The argument to `e_ball(...)` must be exactly one of `Fire`, `Water`, `Earth`, or `Air`. The call must be assigned if you want to keep the configured instance.

## 3. Tune an existing operation

Use this syntax:

```mana
spell e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
tune(fire_ball.velocity) = ball, 600 m/s
tune(fire_ball.heat) = ball, 1500 K
```

Expected output:

```text
(no output)
```

Read it as: in `fire_ball`, find the existing `velocity` operation whose first argument is the internal variable `ball`, and replace its second argument with `600 m/s`.

Rules:

- `tune` changes an existing operation; it does not add a new operation or property.
- The target name must match the variable used by the operation inside the definition.
- The operation and target must identify exactly one operation call. No match or multiple matches produce an error.
- The value must have the correct type and physical units when the spell executes.
- Tuning affects only that configured instance and persists for the current program run.
- `post` rolls back trial world changes, but it does not undo the instance's configuration.
- To reapply tuning on later runs, keep the tuning statements in the `.mana` file.

The old syntax `spell.tune = parameter: value` is removed.

See [Spell Templates and Tuning](../language/SPELL_TEMPLATES_AND_TUNING.md) for more examples and error cases.

## 4. Previewing and firing

```mana
spell e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
post(fire_ball)
release(fire_ball)
```

Expected output:

```text
[POST fire_ball] inputs: element=Fire
[POST fire_ball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fire_ball] created Fire (Fire, 1 kg; create Fire)
[POST fire_ball] ball.shape: 'point' -> 'circle' (shape)
[POST fire_ball] energy input: 500000 J (heat; spell energy input; mana-equivalent is readout only)
[POST fire_ball] ball.energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] ball.integrity: 0.992062994740159 -> 0.9909143970358393 (heat)
[POST fire_ball] ball.integrity_effective_energy_j: 1000000.0 -> 1500000.0 (heat)
[POST fire_ball] ball.integrity_energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] ball.integrity_last_score_j: 1000000.0 -> 1500000.0 (heat)
[POST fire_ball] ball.mana_cost: 0.1 -> 500000.1 (heat)
[POST fire_ball] ball.mana_used: 0.1 -> 500000.1 (heat)
[POST fire_ball] ball.temp: 1000 K -> 1500 K (heat)
[POST fire_ball] ball.thermal_energy: 1e+06 J -> 1.5e+06 J (heat)
[POST fire_ball] energy input: 45000 J (velocity; spell work)
[POST fire_ball] ball.energy: 1.5e+06 J -> 1.545e+06 J (velocity)
[POST fire_ball] ball.integrity: 0.9909143970358393 -> 0.9908244347201649 (velocity)
[POST fire_ball] ball.integrity_effective_energy_j: 1500000.0 -> 1545000.0000000338 (velocity)
[POST fire_ball] ball.integrity_energy: 1.5e+06 J -> 1.545e+06 J (velocity)
[POST fire_ball] ball.integrity_last_score_j: 1500000.0 -> 1545000.0000000338 (velocity)
[POST fire_ball] ball.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fire_ball] ball.mana_cost: 500000.1 -> 545000.1000000337 (velocity)
[POST fire_ball] ball.mana_used: 500000.1 -> 545000.1000000337 (velocity)
[POST fire_ball] ball.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fire_ball] ball.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fire_ball] spell completed
[POST fire_ball] mana appraisal: 545000 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

| Command | Meaning |
|---|---|
| `post(spell_name)` | Runs a trial, prints the execution steps and result details, then restores the world state. |
| `release(spell_name)` | Runs the spell and commits its world changes. |
| `show value` or `show(value)` | Prints a value or message. It does not execute spells or create a trace. |
| `incant value` | Ends the current definition and supplies a value to its caller. `incant` is a statement that exits the current definition. |
| `skip` | Does nothing. Useful as a placeholder for an unfinished block. |

`post` accepts a named spell or configured instance and an optional presentation: `post(spell)` and `post(spell, text)` print the text report, while `post(spell, visual)` records the non-committing preview for the optional Visualiser. The Visualiser appears only when you click its Visual button or open a recording. `release` accepts only the spell name and commits successful world changes. These are standalone commands: do not assign them to variables or place them inside another expression. Their detailed execution record is available to the host runtime and tests, not as a MANA-source return value.

`show` is ordinary printing. For example, `show stone.temp` prints the temperature; it does not provide the step-by-step report that `post` provides.

## 5. Variables, values, and properties

```mana
stone = create Earth
stone.mass = 2 kg
stone.temp = 500 K
show stone.mass
show stone.temp
```

Expected output:

```text
2 kg
500 K
```

The uppercase type name (`Earth`) identifies a catalogue type. The lowercase variable (`stone`) refers to the created object.

Common properties:

| Property | Meaning | Unit or type |
|---|---|---|
| `mass` | Object mass | `kg` |
| `volume` | Object volume | `m3` |
| `area` | Projected area used by 2D collider bounds | `m2` |
| `density` | Mass per volume | `kg/m3` |
| `pos` | Position | `m` vector |
| `vel` | Velocity | `m/s` vector |
| `acc` | Acceleration | `m/s2` vector |
| `force` | Force | `N` vector |
| `momentum` | Momentum | `kg*m/s` vector |
| `temp` | Temperature | `K` |
| `thermal_energy` | Thermal energy component | `J` |
| `kinetic_energy` | Kinetic energy component | `J` |
| `energy` | Total tracked energy | `J` |
| `pressure` | Pressure | `Pa` |
| `state` | State label | Text |
| `material` | Material label | Text |
| `shape` | Shape label | Text |
| `direction` | Direction vector | Dimensionless vector |
| `rot` | Rotation angle | Number (radians) |
| `scale` | Scale factor | Number |

Energy components, momentum, lifecycle flags and mana-cost readouts are runtime-managed. Change canonical inputs such as mass, temperature and velocity; the engine updates derived values.

## 6. Units and physical limits

MANA tracks dimensions for mass, distance, time, temperature, and mana. Frequently used units include `kg`, `m`, `s`, `K`, `mana`, `m/s`, `m/s2`, `kg/m3`, `N`, `J`, `Pa`, and `W`.

```mana
stone = create Earth
speed = 300 m/s
shot_distance = 20 m
duration = 5 s
heat(stone, 100 K)
```

Expected output:

```text
(no output)
```

Heating and cooling are changes: `heat(stone, 100 K)` adds 100 K and `cool(stone, 100 K)` subtracts 100 K. Cooling below absolute zero is rejected. Incompatible dimensions raise `UnitErrorML`; impossible physical states raise `PhysicsErrorML`.

## 7. First physics simulation

The world engine is 2D by default. For a targeted projectile, scalar speed can be used inside a target context and MANA automatically calculates the heading. Import `geometry2d` only when you want to manually build directions or inspect geometry.

```mana
load geometry2d
stone = create Earth
velocity(stone, geometry2d.direction(1, 0) * 10 m/s)
accelerate(stone, geometry2d.direction(0, 1) * 2 m/s2)
advance_time(1 s, timestep=0.01 s, gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
show stone.pos
show stone.vel
show last_collisions()
```

Expected output:

```text
Vector3(10, -3.905, 0) [m]
Vector3(10, -7.81, 0) [m/s]
[]
```

The primary world engine is always the x-y plane (`z = 0`) and does not require importing a library to function. `geometry2d.direction(x, y)` becomes available after `load geometry2d` for explicit vector control. `vector3d` is available only after `load vector3d` and supports three-dimensional calculation, not 3D world motion. `planes` is available after `load planes` for plane identification, pathway configuration, route lookup, and internal energy transport; plane creation is handled separately. The default time step is `1/60 s`, the maximum step is `0.1 s`, and each `advance_time` call is capped at 100,000 steps. A positive `object.collision_radius` in metres overrides the area-derived circle bound; setting it to zero restores the area-derived radius. `object.collidable = false` disables collisions without disabling motion. See [Physics Engine](../physics/PHYSICS_ENGINE.md) for details and limitations.
MANA syntax decisions for this release:

- `def` is for ordinary computational helper functions.
- `spell` declares spells executed through `appraise` or `cast`; `spldef` remains a compatible legacy alias, as do `post(...)` and `release(...)`.
- `tgset` creates/selects a target context; it is not a definition keyword.
- `load` loads a library namespace; `skip` is the empty/no-operation statement.
- `span(...)` produces an integer iteration span; `length(...)` counts supported sequences.
- Use `incant value` to provide a definition result. `incant` is the definition-exit statement.

## 8. Variables, lists, and helper definitions

Assignments made inside `if`, `while`, `for`, `tgset`, `after`, `every`, and `when` blocks belong to the enclosing definition or module scope. Each `def` creates its own local scope. A variable first assigned inside a definition does not become a caller variable.

Lists work in expressions, function arguments, and loops. They support integer indexing, negative indexes, and indexed assignment:

```mana
values = [10, 20, 30]
values[1] = 25
first = values[0]
last = values[-1]
show length(values)
show first + last
```

Expected output:

```text
3
40
```

`length()` supports lists, strings, and `span()` values. Invalid index types and out-of-range indexes raise clear MANA errors. Nested indexing such as `matrix[0][1]` works when the selected item is itself a list. Tuple, set, and dictionary literals are not supported.

A normal definition call calculates a value; use `incant value` to supply that value to its caller. Direct helper calls cannot create objects or mutate the world. Run world-changing spell definitions with standalone `post(spell)` or `release(spell)` commands. Definitions can register `when` event handlers, which act only when the matching event occurs.

## 9. Control flow and placeholders

MANA supports `if`, `elif`, `else`, `while`, `for`, `simul:`, `wait`, `after`, `every`, and `when` constructs.

Use `skip` when a block is intentionally empty while you are developing it:

```mana
spell future_spell():
    skip
```

Expected output:

```text
(no output)
```

`skip` is a reserved statement, not a function. Write `skip`, never `skip()`.

## 10. Errors

| Error | Typical cause |
|---|---|
| `SyntaxErrorML` | Invalid syntax, indentation, obsolete `.tune` syntax, or a malformed definition |
| `TypeErrorML` | Wrong value type, missing property, unknown operation target for `tune`, or ambiguous tuning |
| `UnitErrorML` | Incompatible physical dimensions |
| `RuntimeErrorML` | Undefined name, invalid call, or runtime safety limit |
| `MagicErrorML` | Forbidden magical interaction or invalid element selection |
| `PhysicsErrorML` | Impossible physical state or universal physical limit violation |

## 11. Current implementation limits

MANA provides deterministic 2D time stepping, x-y vector motion, optional explicit gravity, swept-circle collision detection, basic collision response, collision heat, and prototype target damage. Three-dimensional vector calculations remain available through the optional `vector3d` library but cannot move objects in the 2D world. These are approximate systems: exact shape geometry, relativistic collision response, friction, rotation dynamics, fluids, combustion, and full phase-change simulation are not implemented. Integrity tracking and collapse are implemented with configurable starting thresholds; those values still need calibration. See [Physics Engine](../physics/PHYSICS_ENGINE.md). Run a source file with `python mana.py path/to/file.mana`. The VS Code extension provides optional language support but does not execute programs.


## Python-to-MANA quick lookup

Use this table when translating familiar concepts into MANA. It is a comparison aid, not a promise of full syntax compatibility.

| Python word | MANA equivalent or behaviour |
|---|---|
| `import` | `load` |
| `pass` | `skip` |
| `range` | `span` |
| `len` | `length` |
| `return` | `incant value` |
| `print` | `show` |
| `def` | `def` for calculations; `spell` for spells (`spldef` is a backward-compatible alias) |
| `True`, `False` | `true`, `false` |
| `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not` | Same spellings in MANA |
| `None`, `lambda`, `class`, `try`, `except`, `with`, `yield`, `raise`, `global`, `del`, `assert`, `break`, `continue` | Not identified as MANA constructs |

The [Language Specification](../language/LANGUAGE_SPEC.md) contains the full comparison table and grammar rules. Any word not in MANA's keyword table is not identified as a keyword; non-reserved names can still be user-defined.


## Native local weather and conjuration

Weather can be written as a language statement inside a spell instead of requiring every spell to call the weather API explicitly:

```mana
spell summer_rain():
    weather rain, intensity=0.85, temperature=290 K, duration=45 s, radius=75 m
    blade = conjure steel, mass=3 kg, shape=ring, anchored=false
    incant blade

appraise summer_rain
cast summer_rain
```

Expected output:

```text
[APPRAISAL summer_rain] inputs: no parameters
[APPRAISAL summer_rain] local weather configured: rain (radius 75 m, intensity 0.85)
[APPRAISAL summer_rain] energy input: 879450 J (conjure steel; matter manifestation)
[APPRAISAL summer_rain] created Steel (Compound, 3 kg; conjured material steel)
[APPRAISAL summer_rain] executed conjure('steel')
[APPRAISAL summer_rain] spell completed
[APPRAISAL summer_rain] mana appraisal: 0.3 mana
[APPRAISAL summer_rain] created: Steel (Compound, 3 kg)
[CAST summer_rain] spell committed
[CAST summer_rain] mana appraisal: 0.3 mana
```

A weather statement without `radius` configures the global climate. Supplying `radius=75 m` creates local weather around the caster's position; objects outside that radius are not affected by that zone. Optional `center=...` targets an explicit 2D world position or positioned object. Zones are recorded as world state and are rolled back by `appraise` (or legacy `post`), then committed by `cast` (or legacy `release`).

The bare-material conjure form is equivalent to a normal built-in call, but is easier to read: `anvil = conjure iron, mass=40 kg, shape=sphere`. Options include `mass`, `position`, `shape`, `name`, `temperature`, `density`, `state`, `velocity`, `anchored`, `collidable`, `restitution`, `friction`, and `drag_coefficient`. Material creation is appraised and recorded by MANA; mana usage is not a spendable personal casting pool.


## Native summoning

Summoning uses an existing being record; conjuring creates physical matter. Open the required pathway, then describe the summon directly inside a spell:

```mana
load planes
planes.open_path("Wild Realm", "Mortal Plane")

spell call_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    incant griffin

appraise call_griffin
cast call_griffin
```

Expected output:

```text
[APPRAISAL call_griffin] inputs: no parameters
[APPRAISAL call_griffin] planar energy transfer: 293150 J (Wild Realm -> Mortal Plane)
[APPRAISAL call_griffin] created Griffin (Being, 1 kg; summoned from Wild Realm)
[APPRAISAL call_griffin] executed summon('Griffin', 'Wild Realm')
[APPRAISAL call_griffin] spell completed
[APPRAISAL call_griffin] mana appraisal: 0 mana
[APPRAISAL call_griffin] created: Griffin (Being, 1 kg)
[CAST call_griffin] spell committed
[CAST call_griffin] mana appraisal: 0 mana
```

Use `summon (chosen_being) from (chosen_plane)` for computed names. Optional `position=...` sets the arrival position and `requirements=[...]` supplies conditions declared by the being record. The route must be open. `appraise` is a non-committing record; `cast` commits a successful result.
