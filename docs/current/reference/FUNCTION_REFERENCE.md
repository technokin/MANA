# MANA Built-in Function and Statement Reference

**Page kind:** Reference  

**Version:** 1.0.0
This reference covers behaviour implemented in the v1.0.0 interpreter. Square brackets in signatures mean optional arguments.

## A. Definitions and execution commands

### `def name(parameters):` — define a normal calculation function

Use `def` for ordinary reusable code such as mathematics and data calculations. Parameters are supported; `incant` supplies the result and ends the function. Direct helper calls cannot create world objects or mutate the simulated world.

```mana
def square(value):
    incant value * value

answer = square(12)
show answer
```

Expected output:

```text
144
```

**Arguments and error cases:** Parameters must be valid, unique identifiers. Required parameters must precede parameters with defaults. A direct helper call that attempts world-changing operations raises a MANA error.

### `spldef name():` — define a spell

A `spldef` body is executed through the standalone `post(spell)` or `release(spell)` statement. It does not run by directly calling it as a value.

```mana
spldef warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

post(warm_stone)
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
[POST warm_stone] mana cost: 100000 mana
[POST warm_stone] created: stone (Earth, 1 kg)
```

**Arguments and error cases:** A spell definition accepts no parameters or the single `element` selector described below. Use `post` for a trial and `release` to commit the spell's world changes.

### `spldef name(element):` — define a base-element spell template

The single `element` parameter selects one of the four fundamental types: `Fire`, `Water`, `Earth`, or `Air`.

```mana
spldef e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
earth_ball = e_ball(Earth)
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
[POST fire_ball] mana cost: 545000 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

Calling `e_ball(Fire)` creates a configured spell instance; it does not execute the body. Assign it to a name if it will be tuned or fired later.

**Arguments and error cases:** The selector must be named `element` and select a supported base element. Other parameters or element values raise MANA errors.

### `tune(spell.operation) = target, value` — update an existing operation

Changes the second positional argument of a matching operation call in a configured spell instance.

**Runnable example:**

```mana
spldef e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
tune(fire_ball.velocity) = ball, 600 m/s
tune(fire_ball.heat) = ball, 1500 K
post(fire_ball)
```

Expected output:

```text
[POST fire_ball] inputs: element=Fire
[POST fire_ball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fire_ball] created Fire (Fire, 1 kg; create Fire)
[POST fire_ball] ball.shape: 'point' -> 'circle' (shape)
[POST fire_ball] energy input: 1.5e+06 J (heat; spell energy input; mana-equivalent is readout only)
[POST fire_ball] ball.energy: 1e+06 J -> 2.5e+06 J (heat)
[POST fire_ball] ball.integrity: 0.992062994740159 -> 0.9892278265498405 (heat)
[POST fire_ball] ball.integrity_effective_energy_j: 1000000.0 -> 2500000.0 (heat)
[POST fire_ball] ball.integrity_energy: 1e+06 J -> 2.5e+06 J (heat)
[POST fire_ball] ball.integrity_last_score_j: 1000000.0 -> 2500000.0 (heat)
[POST fire_ball] ball.mana_cost: 0.1 -> 1500000.1 (heat)
[POST fire_ball] ball.mana_used: 0.1 -> 1500000.1 (heat)
[POST fire_ball] ball.temp: 1000 K -> 2500 K (heat)
[POST fire_ball] ball.thermal_energy: 1e+06 J -> 2.5e+06 J (heat)
[POST fire_ball] energy input: 180000 J (velocity; spell work)
[POST fire_ball] ball.energy: 2.5e+06 J -> 2.68e+06 J (velocity)
[POST fire_ball] ball.integrity: 0.9892278265498405 -> 0.9889752622855019 (velocity)
[POST fire_ball] ball.integrity_effective_energy_j: 2500000.0 -> 2680000.0000005406 (velocity)
[POST fire_ball] ball.integrity_energy: 2.5e+06 J -> 2.68e+06 J (velocity)
[POST fire_ball] ball.integrity_last_score_j: 2500000.0 -> 2680000.0000005406 (velocity)
[POST fire_ball] ball.kinetic_energy: 0 J -> 180000 J (velocity)
[POST fire_ball] ball.mana_cost: 1500000.1 -> 1680000.1000005407 (velocity)
[POST fire_ball] ball.mana_used: 1500000.1 -> 1680000.1000005407 (velocity)
[POST fire_ball] ball.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(600, 0, 0) [kg*m/s] (velocity)
[POST fire_ball] ball.vel: Vector3(0, 0, 0) [m/s] -> Vector3(600, 0, 0) [m/s] (velocity)
[POST fire_ball] spell completed
[POST fire_ball] mana cost: 1.68e+06 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

The operation name must exist and the target must match the variable name passed as its first positional argument. Exactly one match is required. Missing and ambiguous matches raise `TypeErrorML`. Tuning affects only that instance and remains set for later `post` and `release` executions in the current run. `post` rolls back world changes, not configuration.

The older `spell.tune = parameter: value` syntax is removed. A tuned value must satisfy the operation's type and unit requirements when the spell runs. Property-path tuning and changing a new/nonexistent operation are not supported. `post` and `release` remain standalone execution commands, never expressions.

### `skip` — no-operation statement

Does nothing, makes no world change, and consumes no mana. Use `skip`, not `skip()`, as a temporary placeholder for an unfinished block.

```mana
spldef future_spell():
    skip
```

Expected output:

```text
(no output)
```

**Arguments and error cases:** Use the statement as `skip`, not as `skip()`. It takes no arguments and is intended only as a placeholder.

### `incant value` — supply a result to the caller

A statement, not a function. It exits the current definition immediately and supplies `value` to its ordinary caller. Use `incant value`, not `incant(value)`. `incant` supplies a value and exits the current definition.

**Runnable example:**

```mana
def answer():
    incant 42

answer_value = answer()
show(answer_value)
```

Expected output:

```text
42
```

**Arguments and error cases:** `incant` must appear inside a definition and exits that definition immediately. A second statement after it is unreachable and is warned about; Use `incant` to exit the current definition and optionally supply a value.

### `name = create Element` — create a magical object

Creates an object and assigns it directly to a variable. A static type is valid (`fire = create Fire`). Inside an element template, `create element` uses the selected base element. An unassigned create expression or a nested `create` is invalid.

A fresh object has 1 kg mass, 1 m³ material volume, 1 m² projected area for its 2D collider, zero velocity, and its configured starting temperature. Creation reports the matter-manifestation cost; its starting thermal state is not billed as an extra creation-energy charge.

**Runnable example:**

```mana
stone = create Earth
show stone.mass
```

### `Mana` — pure-mana type selector

`Mana` is the registered type selector accepted by `create`, like `Fire`, `Water`, `Earth`, and `Air`. The lowercase `mana` name is a separate built-in namespace for constructing pure-mana effects and applying element-independent control. A bare `create Mana` makes a massless zero-mana-energy construct; use `mana.form(...)` when you want a construct with finite effect energy and a collision radius.

```mana
orb = mana.form("sphere", energy=750 J, radius=0.15 m)
velocity(orb, 25 m/s)
show orb.mana_energy
```

Expected output:

```text
750 J
```

**Arguments and error cases:** `Mana` takes no arguments as a type selector. Pure-mana effect functions validate energy, power, duration, radius, range, position, and control inputs against the expected units. Mana energy is carried by a construct; mana is not stored on ordinary objects as an assignable `.mana` property.

### `mana` — pure-mana effects and universal control namespace

The built-in namespace is available without a load; `load mana` is also accepted. Its effect functions use ambient mana, write to the existing energy ledger, and record a mana-equivalent usage readout rather than consuming a stored pool.

| Function | Behaviour and defaults |
|---|---|
| `mana.form(shape, energy, radius, collidable, anchored, position)` | Forms a finite-energy pure-mana construct. Defaults: sphere, 1000 J, 1 m radius, position 10 m along +X. Barrier-like shapes anchor by default; projectile-like shapes are collidable. |
| `mana.burst(energy, radius, position)` | Radial pulse. Defaults: 1000 J, 1 m radius, position 10 m along +X. |
| `mana.emit(power, duration, direction, range, beam_radius, position)` | Directed energy ray. Defaults: 1000 W, 1 s, 10 m range, 1 m radius, position 10 m along +X. In a `tgset` block, omitted direction aims toward the selected target. |
| `mana.control(object, action, strength, duration, destination)` | Underlying actions are `toward`, `away`, `lift`, `hold`, `stop`, and `release`. Default force is 100 N and default action duration is 1 s where relevant. |
| `mana.toward(object, destination, strength, duration)` | Applies force toward a position or object. Destination can be omitted in `tgset(target):`. |
| `mana.away(object, source, strength, duration)` | Applies force away from a position or object. Source can be omitted in `tgset(target):`. |
| `mana.lift(object, strength, duration)` | Applies an upward impulse; default 100 N for 1 s. For a fixed position, use `mana.hold` or `mana.levitate`. |
| `mana.hold(object, position)` / `mana.levitate(object, position)` | Converts current kinetic energy to heat, then anchors the object at its current or supplied position. |
| `mana.stop(object)` | Stops motion and converts kinetic energy to heat on the same object. |
| `mana.release_control(object)` | Removes the hold; it does not delete energy. |
| `mana.collect(objects, destination, strength, duration)` | Moves one object or a list toward a destination. Destination defaults to the selected `tgset` target or the caster position. |

```mana
load geometry2d
stone = tgset:
    material = "Rock"
    mass = 1 kg
    volume = 0.001 m3
    pos = geometry2d.point(0 m, 0 m)
marker = tgset:
    pos = geometry2d.point(5 m, 0 m)
tgset(marker):
    mana.toward(stone)
```

Expected output:

```text
(no output)
```

**Arguments and error cases:** Energy must be finite and non-negative; radius and range must be positive where required; power and duration must be finite and non-negative; control strength must be finite and non-negative, and control duration cannot exceed 60 s. `toward`/`away` need an explicit destination/source outside a target block. Positions are 2D vectors in metres. The energy ledger tracks effect input and internal transfers. Unabsorbed burst/beam energy is accounted for as environmental energy. See the [Pure Mana and Universal Control guide](../libraries/MANA_LIBRARY.md) for full behaviour and limitations.

### `name = tgset:` — define a target profile

Creates a target profile, not a spell or another type of `def`.

```mana
guard = tgset:
    hp = 250
    max_hp = 250
    defence = 40
    resist_fire = 0.6
    distance = 12 m
```

Expected output:

```text
(no output)
```

Common fields include `hp`, `max_hp`, `defence`, `resist_fire`, `resist_water`, `resist_earth`, `resist_air`, `distance`, and `pos`. `tgset` can also define manipulable materials using `kind`, `material`, `shape`, `state`, `mass`, `volume`, `temp`, `combustible`, `ignition_temp`, and `powderable`. Wood-like materials infer combustibility unless overridden; `heat()` ignites a combustible object when its threshold is crossed. `transform(object, "powder")` preserves mass and energy on the aggregate object. Resistances range from 0 (none) to 1 (full). See the [Pure Mana and Universal Control guide](../libraries/MANA_LIBRARY.md).

**Arguments and error cases:** Target fields are checked by their expected type and unit. HP/defence fields must be numeric; resistances are fractions from 0 to 1; distance must be a length and positions must be planar position vectors.

### `show value[, value ...]` or `show(value)` — print output

Prints supplied values to the terminal and returns no usable value. It does not fire a spell or generate a `post` trace. Both parenthesized and print-style forms are accepted. `show` must be a standalone command; assignments and nested uses are invalid.

**Runnable example:**

```mana
show 42, "mana"
show(3 km)
```

Expected output:

```text
42 mana
3000 m
```

### `post(spell_name)` — trial command

Runs one named definition or configured spell instance. The runtime prints its inputs and step-by-step trace, then restores world state. It displays changes, created objects, hits, rules, mana-cost readouts, and errors where present.

It must be a standalone command. `trial = post(spell)` and `post(spell, 300 m/s)` are invalid. The host runtime receives a `SpellResult` record for tests and tools; MANA source cannot assign that record.

**Runnable example:**

```mana
spldef warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

post(warm_stone)
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
[POST warm_stone] mana cost: 100000 mana
[POST warm_stone] created: stone (Earth, 1 kg)
```

### `release(spell_name)` — fire command

Runs one named definition or configured instance and commits the resulting world changes. It accepts exactly one spell name and has no inline argument overrides. It is also standalone: `result = release(spell)` and `release(spell, 300 m/s)` are invalid. On a failure, the runtime prints an error and restores prior world state.

**Runnable example:**

```mana
spldef warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

release(warm_stone)
```

Expected output:

```text
(no output)
```

### `load library_name` — load an optional library namespace

Loads an approved built-in library or a user-built `.manalib` package. Loaded functions are accessed through namespaces, such as `geometry2d.distance(...)`, `vector3d.cross(...)`, `planes.find_route(...)`, `drafter.begin(...)`, `summoning.bring(...)`, and `necromancy.reanimate(...)`; functions are not copied into the global namespace. Built-ins include `geometry2d`, `vector3d`, `planes`, `drafter`, `summoning`, and `necromancy`; `necromancy` is a built-in specialist library; lowercase `mana` is also built in and can be used without loading it. Independent plane data libraries are `elemental_planes`, `hell`, `heaven`, `atlantis`, `fae_paradise`, `lineage_halls`, and `wild_realm`; load `planes` before explicitly loading one of these. `drafter`, `summoning`, and `necromancy` each require `planes` to be imported first. `necromancy` does not require `summoning`. See the [2D library guide](../libraries/GEOMETRY2D_LIBRARY.md), [3D library guide](../libraries/VECTOR3D_LIBRARY.md), [Planes Library guide](../libraries/PLANES_LIBRARY.md), [Drafter guide](../libraries/DRAFTER_LIBRARY.md), [Summoning guide](../libraries/SUMMONING_LIBRARY.md), [Necromancy guide](../libraries/NECROMANCY_LIBRARY.md), and [Library Builder guide](../libraries/LIBRARY_BUILDER.md).

**Runnable example:**

```mana
load geometry2d
heading = geometry2d.direction(1, 0)
show heading
```

Expected output:

```text
Vector3(1, 0, 0) [dimensionless]
```

**Arguments and error cases:** Unknown libraries, malformed manifests, invalid exports, unsafe entry paths, corrupt archives, and packages exceeding 128 members or 2,000,000 uncompressed bytes raise `RuntimeErrorML`.

### `active_objects()` — inspect committed objects

Returns a list of currently active magical objects reachable from program globals, the committed world, and active spell results. Objects held only by inaccessible local state may not be included. Use each object's `.active` field when inspecting retained references.

## B. Creation, output, and inspection

**Runnable example:**

```mana
stone = create Earth
show active_objects()
```

Expected output:

```text
[<element:stone#53>]
```

**Arguments and error cases:** Takes no arguments. Passing positional or named arguments raises `TypeErrorML`.

### `detect(object[, property_name])`

Inspects an object. With no property name it returns the object; with a text property name it returns that property. Unknown properties raise a type error.

**Runnable example:**

```mana
stone = create Earth
show detect(stone, "mass")
```

Expected output:

```text
1 kg
```

### `has_domain(element_object, domain_name)`

Returns true if the registered element owns or is explicitly involved in the named domain. `domain_name` is text, for example `has_domain(fire, "temperature")`. It checks the element catalogue; it does not perform a spell.

**Runnable example:**

```mana
stone = create Earth
show has_domain(stone, "strength")
```

Expected output:

```text
True
```

**Arguments and error cases:** `element_object` must be a magical object and `domain_name` must be text; unsupported argument types raise `TypeErrorML`.

### `span(stop)` / `span(start, stop[, step])`

Returns an integer span usable in `for`. Arguments must be integers; the resulting iteration count is limited for safety.

**Runnable example:**

```mana
for index in span(1, 4):
    show index
```

Expected output:

```text
1
2
3
```

### `length(value)` — count a supported sequence

Returns the number of items in a list, string, or `span`. It works inside expressions and helper calls, and is not limited to standalone display statements.

**Runnable example:**

```mana
values = [10, 20, 30]
values[1] = 25
show length(values)
show values[0]
```

Expected output:

```text
3
10
```

**Arguments and error cases:** Accepts a list, string, or `span`; other values raise `TypeErrorML`. List/string/span indexing uses integer indices, accepts negative indices, and reports an out-of-range access as a MANA runtime error.

### `sqrt(value)`

Returns the real square root of a non-negative plain number or dimensionless quantity. Negative input raises `PhysicsErrorML`; incompatible units raise `UnitErrorML`; unsupported value types raise `TypeErrorML`.

## C. Shape, position, and movement

Advanced geometry helpers such as explicit directions, distances, angles, and manual trajectory control are not global functions. Import `geometry2d` and call them through that namespace; 3D calculations use `vector3d`.

**Runnable example:**

```mana
show sqrt(9)
```

Expected output:

```text
3.0
```

### `shape(object, geometry)`

Sets the object's semantic/visual shape label. Common labels include `circle`, `wall`, `cone`, `polygon`, `beam`, and `point`. Labels do not yet create exact collision geometry. The 2D world physics engine uses an equivalent circle based on projected `area`, or the object's explicit `collision_radius`. Returns the object.

**Runnable example:**

```mana
stone = create Earth
shape(stone, circle)
show stone.shape
```

Expected output:

```text
circle
```

**Arguments and error cases:** `object` must be a magical object and `geometry` must be a built-in geometry label (text). The label does not create exact collision geometry.

### `move(object, distance[, direction_vector])`

Moves an object by a distance in metres along the supplied direction or its current direction. Direction must be non-zero. Anchored objects cannot move until `unanchor(object)` is used. Returns the object.

**Runnable example:**

```mana
load geometry2d
stone = create Earth
move(stone, 2 m, geometry2d.direction(1, 0))
show stone.pos
```

Expected output:

```text
Vector3(2, 0, 0) [m]
```

### `velocity(object, speed_or_vector)`

Sets velocity. A scalar quantity in `m/s` sets the speed. Inside a `tgset(target):` casting block, the engine automatically points that speed from the moving object toward the selected target; it resolves the 2D geometry internally. Outside a target context, scalar speed retains the default positive-x direction. A vector in `m/s` sets explicit x/y components for advanced control. A non-zero z component is rejected by the 2D world engine. Recalculates kinetic energy, momentum, and total energy. A massive object cannot reach or exceed `c`. Returns the object.

**Runnable example:**

```mana
stone = create Earth
velocity(stone, 5 m/s)
show stone.vel
```

Expected output:

```text
Vector3(5, 0, 0) [m/s]
```

### `accelerate(object, acceleration)`

Sets a persistent acceleration. A scalar in `m/s2` acts along the positive x-axis; an acceleration vector sets x/y components in the 2D world. A non-zero z component is rejected. Updates force to `mass × acceleration`. Velocity and position change only when virtual time advances, for example with `advance_time(1 s)`. Returns the object.

**Runnable example:**

```mana
stone = create Earth
accelerate(stone, 2 m/s2)
show force(stone)
```

Expected output:

```text
Vector3(2, 0, 0) [N]
```

### `decelerate(object, acceleration)`

Sets persistent acceleration opposite the supplied direction. A scalar is interpreted along the negative x-axis; a planar vector is negated component by component. A non-zero z component is rejected by the 2D world engine. Motion is integrated when virtual time advances. Returns the object.

**Runnable example:**

```mana
stone = create Earth
velocity(stone, 5 m/s)
decelerate(stone, 2 m/s2)
show stone.acc
```

Expected output:

```text
Vector3(-2, 0, 0) [m/s2]
```

### `tgset(target):` — temporary casting target

Selects a target for the statements inside the indented block. It is separate from a target profile definition (`npc = tgset:`). For example:

```mana
npc = tgset:
    hp = 250
    defence = 10
    distance = 12 m

spldef fireball():
    fire = create Fire
    shape(fire, circle)
    velocity(fire, 300 m/s)
    incant fire

tgset(npc):
    post(fireball)
    release(fireball)
```

Expected output:

```text
[POST fireball] inputs: no parameters
[POST fireball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fireball] created Fire (Fire, 1 kg; create Fire)
[POST fireball] fire.shape: 'point' -> 'circle' (shape)
[POST fireball] energy input: 45000 J (velocity; spell work)
[POST fireball] fire.energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fireball] fire.integrity: 0.992062994740159 -> 0.9919456821384532 (velocity)
[POST fireball] fire.integrity_effective_energy_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fireball] fire.integrity_energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fireball] fire.integrity_last_score_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fireball] fire.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fireball] fire.mana_cost: 0.1 -> 45000.10000003379 (velocity)
[POST fireball] fire.mana_used: 0.1 -> 45000.10000003379 (velocity)
[POST fireball] fire.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fireball] fire.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fireball] target selected: npc; simulating targeted motion for 0.0566667 s
[POST fireball] collision: npc ↔ fire; impact energy 22500 J; 21600 J converted to heat
[POST fireball] hit: fire hit npc; 215 HP damage; HP 35
[POST fireball] spell completed
[POST fireball] mana cost: 45000.1 mana
[POST fireball] created: fire (Fire, 1 kg)
[POST fireball] hits: npc
```

Inside the casting block, scalar `velocity(object, speed)` automatically aims at the selected target. The engine advances the projectile through its flight as part of `post` or `release`; `post` rolls the world changes back after reporting a hypothetical hit, while `release` commits them. In this headless prototype, a target profile that supplies only `distance` is placed along the default forward axis (+X); an explicit `pos` takes precedence. Real world entities should supply their actual world position. Explicit velocity vectors still override automatic direction selection.

**Arguments and error cases:** The selected target must be targetable. If it has only a distance and no position, targeted flight uses the documented default +X direction; malformed target fields raise a MANA error.

### `rotate(object, angle)`

Adds an angle in radians to the object's rotation, normalized into one full turn. Angle is a plain dimensionless number. Returns the resulting rotation angle.

**Runnable example:**

```mana
stone = create Earth
rotate(stone, pi / 2)
show stone.rot
```

Expected output:

```text
1.5707963267948966
```

**Arguments and error cases:** Angle must be a finite dimensionless number interpreted as radians. Wrong types, non-finite values, and dimensionful quantities are rejected.

### `scale(object, factor)`

Multiplies the object's scale, changes material volume by the cube of the factor and 2D projected area by the square of the factor, scales a positive explicit collision radius linearly, and recalculates density while keeping mass fixed. Factor must be finite and greater than zero. Returns the object.

**Runnable example:**

```mana
stone = create Earth
scale(stone, 2)
show stone.volume
```

Expected output:

```text
8 m3
```

### `reflect(object, surface_normal)`

Reflects the current velocity vector around a non-zero planar surface-normal vector, then updates momentum and kinetic/total energy. A non-zero z component is rejected by the 2D world engine. Returns the object. The operation does not discover walls automatically; the normal must be supplied by the code.

**Runnable example:**

```mana
load geometry2d
stone = create Earth
velocity(stone, 5 m/s)
reflect(stone, geometry2d.direction(-1, 0))
show stone.vel
```

Expected output:

```text
Vector3(-5, 0, 0) [m/s]
```

### `anchor(object[, position_vector])`

Locks movement. If a position vector is supplied, it is set before the anchor location is stored. Returns the object.

**Runnable example:**

```mana
stone = create Earth
anchor(stone)
show stone.anchored
```

Expected output:

```text
True
```

**Arguments and error cases:** The optional position must be a position vector in metres in the x-y plane. Wrong units, non-zero z components, and invalid object types are rejected.

### `unanchor(object)`

Removes the movement lock set by `anchor`. Returns the object.

## D. Temperature, state, and element interactions

**Runnable example:**

```mana
stone = create Earth
anchor(stone)
unanchor(stone)
show stone.anchored
```

Expected output:

```text
False
```

**Arguments and error cases:** The argument must be a valid magical object with an anchoring property; invalid object references are rejected.

### `heat(object, temperature_change)`

Adds a non-negative temperature delta in kelvin. For example, an object at 293.15 K becomes 393.15 K after `heat(object, 100 K)`. It updates thermal energy, total energy, the energy ledger, and the mana-equivalent cost readout. It does not consume from a mana pool.

**Runnable example:**

```mana
stone = create Earth
heat(stone, 100 K)
show stone.temp
```

Expected output:

```text
393.15 K
```

### `cool(object, temperature_change)`

Subtracts a non-negative temperature delta in kelvin. It cannot lower temperature below 0 K. For example, an object at 293.15 K becomes 193.15 K after `cool(object, 100 K)`. It records removed heat and the cost readout.

**Runnable example:**

```mana
stone = create Earth
cool(stone, 10 K)
show stone.temp
```

Expected output:

```text
283.15 K
```

### `transform(object, state)`

Changes an object's state label, such as `solid`, `liquid`, `gas`, or another text state supported by the operation. In this prototype it does not yet perform a full phase-change simulation or automatically calculate latent heat.

**Runnable example:**

```mana
stone = create Earth
transform(stone, "solid")
show stone.state
```

Expected output:

```text
solid
```

**Arguments and error cases:** The state argument must be text and the target must be an object. This records a state label and does not simulate phase-change physics.

### `compress(object, pressure)`

Sets the object's pressure property to a non-negative pressure quantity, normally in pascals. It does not yet implement a material equation of state or automatically shrink volume.

**Runnable example:**

```mana
stone = create Earth
compress(stone, 200000 Pa)
show stone.pressure
```

Expected output:

```text
200000 Pa
```

### `expand(object, volume)`

Sets volume in cubic metres and updates density from mass and volume. Negative volume is invalid. It does not model detailed expansion dynamics.

**Runnable example:**

```mana
stone = create Earth
expand(stone, 2 m3)
show stone.volume
```

Expected output:

```text
2 m3
```

### `combine(object_a, object_b[, mana_a=...][, mana_b=...])`

Evaluates the registered interaction between two active objects and returns a new composite/material/element result. The optional `mana_a` and `mana_b` values are interaction intensities; they are not a spendable mana budget. If omitted, each object's `mana_intensity` is used. The current runtime marks source objects inactive while preserving them in the composite's provenance, so source matter is not simultaneously counted as active. Defined interactions include Fire + Water cancellation, Water + Earth → Mud, Mud + Life → Wood, and Water + Air → Ice when heat is available for removal. Unspecified pairings produce a structured compound result.

**Runnable example:**

```mana
water = create Water
stone = create Earth
mud = combine(water, stone)
show mud.display_name
```

Expected output:

```text
mud
```

**Arguments and error cases:** Both inputs must be distinct active objects with supported properties. Combining an object with itself is rejected to prevent duplicating matter and energy.

### `separate(composite)`

Attempts to restore source objects recorded by `combine`. The composite becomes inactive and restored sources become active. Energy generated locally by the interaction may be returned in a `ThermalRelease` carrier; energy inherited from source objects must not be released a second time. If no source objects are recorded, the operation returns component labels or the original object as a list.

**Runnable example:**

```mana
water = create Water
stone = create Earth
mud = combine(water, stone)
restored = separate(mud)
show restored
```

Expected output:

```text
[<element:water#77>, <element:stone#78>]
```

**Arguments and error cases:** The input must be an active composite. A composite without source provenance can only return its available component labels/original value; inactive or invalid inputs are rejected.

### `split(object, parts)`

Splits an active object into 2–10,000 pieces and returns a list of objects. Mass, volume, projected area and tracked energy components are distributed across the pieces, and the original object becomes inactive. This is bookkeeping-level splitting, not fracture simulation.

**Runnable example:**

```mana
stone = create Earth
pieces = split(stone, 3)
show pieces
```

Expected output:

```text
[<element:Earth_part_1#81>, <element:Earth_part_2#82>, <element:Earth_part_3#83>]
```

**Arguments and error cases:** `parts` must be an integer from 2 through 10,000. Non-integer counts and counts outside that range are rejected.

### `bind(object[, anchor])`

Marks the object as bound, optionally recording what it is bound to. Returns the object.

**Runnable example:**

```mana
stone = create Earth
bind(stone, "wall")
show stone.bound
```

Expected output:

```text
wall
```

**Arguments and error cases:** The target must be a magical object with a `bound` property. The optional anchor is recorded; it is not a separate physical simulation.

### `dispel(object)`

Marks an active object inactive/released and records its energy leaving the active runtime world. It does not yet simulate a detailed destination or blast from released energy. Returns the object.

## E. Force and physical calculations

**Runnable example:**

```mana
stone = create Earth
dispel(stone)
show stone.active
```

Expected output:

```text
False
```

**Arguments and error cases:** The target must be an active magical object. Invalid or already inactive references are rejected.

### `push(object, force[, direction])`

Applies a non-negative force in the given direction or the object's current direction. In this prototype it applies a one-second action immediately as `Δv = F/m × 1 s`, updating velocity and energy at once. The stored acceleration readout from this action is not persistent and will not be applied again by `advance_time`. The object must have positive mass, be active, and not be anchored. Returns the object.

**Runnable example:**

```mana
stone = create Earth
push(stone, 10 N)
show stone.vel
```

Expected output:

```text
Vector3(10, 0, 0) [m/s]
```

### `pull(object, source_object, force)`

Applies the same one-second action as `push`, directed toward the source object's current position. Both objects need position vectors. The resulting stored acceleration is an action readout, not ongoing acceleration. Returns the target object.

**Runnable example:**

```mana
load geometry2d
stone = create Earth
source = create Earth
move(source, 2 m, geometry2d.direction(1, 0))
pull(stone, source, 10 N)
show stone.vel
```

Expected output:

```text
Vector3(10, 0, 0) [m/s]
```

**Arguments and error cases:** Both arguments must be objects with position vectors; force must be non-negative and in newtons (`N`). Missing positions, invalid force units, or an invalid direction raise MANA errors.

### `force(object)`

Calculates and returns the force vector from the object's mass and acceleration (`F = ma`), updating its stored force property.

**Runnable example:**

```mana
stone = create Earth
accelerate(stone, 2 m/s2)
show force(stone)
```

Expected output:

```text
Vector3(2, 0, 0) [N]
```

**Arguments and error cases:** The target must have mass and acceleration properties. It returns a force vector in newtons (`N`).

### `momentum(object)`

Calculates and returns the object's relativistic momentum vector from mass and velocity. It updates the stored momentum property.

**Runnable example:**

```mana
stone = create Earth
velocity(stone, 5 m/s)
show momentum(stone)
```

Expected output:

```text
Vector3(5, 0, 0) [kg*m/s]
```

**Arguments and error cases:** The target must have mass and velocity properties; massive objects cannot reach or exceed `c`.

### `kinetic_energy(object)`

Calculates and returns relativistic kinetic energy from mass and velocity, then refreshes stored kinetic energy, momentum, and total energy. The implementation rejects a massive object's speed reaching `c`.

**Runnable example:**

```mana
stone = create Earth
velocity(stone, 5 m/s)
show kinetic_energy(stone)
```

Expected output:

```text
12.5 J
```

**Arguments and error cases:** The target must have mass and velocity properties. Invalid motion state or reaching/exceeding `c` for a massive object is rejected.

### `pressure(object, area)`

Calculates pressure from the magnitude of the object's stored force divided by a positive area in `m2`. Returns a quantity in pascals. The object must have a force property.


## F. Mana, matter, and energy conversion readouts

The conversion rates are editable rules and are deliberately independent from `E = mc²`.

**Runnable example:**

```mana
stone = create Earth
accelerate(stone, 2 m/s2)
force(stone)
show pressure(stone, 1 m2)
```

Expected output:

```text
2 Pa
```

### `matter_to_mana(mass)`

Converts a mass quantity to its manifestation cost. Current rule: `1 mana` manifests `10 kg`, or `0.1 mana/kg`.

**Runnable example:**

```mana
show matter_to_mana(5 kg)
```

**Arguments and error cases:** The input must be a non-negative mass quantity, normally kilograms (`kg`). Incompatible units and invalid numeric values raise a MANA error.

### `mana_to_matter(mana_amount)`

Returns the corresponding mass. Current rule: `1 mana` maps to `10 kg`.

**Runnable example:**

```mana
show mana_to_matter(2 mana)
```

Expected output:

```text
20 kg
```

**Arguments and error cases:** The input must be a non-negative mana quantity; other dimensions are rejected.

### `mana_to_energy(mana_amount)`

Returns a joule quantity using the current readout rate `1 mana = 1 J`. It does not consume a stored mana amount.

**Runnable example:**

```mana
show mana_to_energy(2 mana)
```

Expected output:

```text
2 J
```

**Arguments and error cases:** The input must be a non-negative mana quantity; this reports a conversion and does not consume stored mana.

### `energy_to_mana(energy)`

Returns the equivalent mana readout for energy in joules. Current rate: `1 J = 1 mana`.

**Runnable example:**

```mana
show energy_to_mana(2 J)
```

Expected output:

```text
2 mana
```

**Arguments and error cases:** The input must be a non-negative energy quantity, normally joules (`J`); incompatible dimensions are rejected.

### Cost fields and reporting

Creating matter records a creation cost. Operations that add/remove heat or change motion may record energy-equivalent mana cost. These are readouts; no spendable mana pool or per-spell mana budget exists. Initial thermal energy is not added to the cost of creating the object.

**Runnable example:**

```mana
show matter_to_mana(1 kg)
show mana_to_energy(2 mana)
```

Expected output:

```text
0.1 mana
2 J
```

**Arguments and error cases:** Cost values are runtime-managed readouts, not an assignable or spendable mana pool. Direct writes to derived energy/cost fields are rejected.

## G. Time, events, and concurrent execution

**Arguments and error cases:** Mana cost and energy readouts are derived outputs; they are not an assignable mana pool. Direct writes to runtime-managed energy/cost fields raise `MagicErrorML`.

### `wait duration`

**Statement.** Advances virtual time by a non-negative duration. The current per-wait safety cap is 60 seconds.

```mana
wait 2 s
```

Expected output:

```text
(no output)
```

### `after duration:`

**Block statement.** In the current prototype it advances virtual time by the specified delay, then executes the indented block. It is not yet a full asynchronous scheduler.

**Runnable example:**

```mana
after 1 s:
    show "after block"
```

Expected output:

```text
after block
```

**Arguments and error cases:** Delay must be non-negative and within the persistence safety cap. This is a synchronous virtual-time block, not a general asynchronous task.

### `every interval:`

**Block statement.** Registers the block as a repeating timer with a positive interval. It runs when virtual time advances. Persistence and per-advance firing counts are capped for safety.

**Runnable example:**

```mana
every 1 s:
    show "tick"
advance_time(1 s)
```

Expected output:

```text
tick
```

### `when event_name:`

**Block statement.** Registers a handler for a named event. Handlers receive emitted arguments through the `event_args` list in their environment. Active handlers expire after the persistence cap.

**Runnable example:**

```mana
when impact:
    show "impact received"
emit("impact")
```

Expected output:

```text
impact received
```

**Arguments and error cases:** Known event names are `impact`, `collision`, and `damaged`. Unknown names generate a warning and will not match engine events.

### `advance_time(duration[, timestep=...][, gravity=...])`

Advances virtual time using deterministic physics steps, processes timers and active event lifetimes, and returns elapsed virtual time in seconds. `duration` and `timestep` may be numbers interpreted as seconds or time quantities. The default timestep is `1/60 s`, a step cannot exceed `0.1 s`, one call is capped at `100,000` steps and `20,000,000` estimated collision-pair checks. `gravity` is an optional acceleration vector; it defaults to zero, so no planetary gravity is assumed. Example:

```mana
load geometry2d
advance_time(1 s, timestep=0.01 s, gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
```

Expected output:

```text
(no output)
```

Persistent acceleration is integrated over the time step. World objects and gravity are restricted to the x-y plane; a non-zero z component raises `PhysicsErrorML`. `push` and `pull` have their separate one-second action semantics and do not repeat as persistent acceleration. The operation is atomic: an error restores the world to its state before the call.

### `emit(event_name[, arguments...])`

Invokes active handlers matching the event name and returns the number of handlers fired. The event name is text. The physics engine also emits `impact` and `collision` when two objects contact, and `damaged` when a target profile loses HP from a collision.

**Runnable example:**

```mana
when impact:
    show "impact received"
emit("impact", "test")
```

Expected output:

```text
impact received
```

**Arguments and error cases:** The event name must be text. Known names are `impact`, `collision`, and `damaged`; unknown names warn and fire no known handler.

### `simul:`

**Block statement.** Validates known writes to the same object property and rejects conflicting writes, then executes supported direct operations in source order. The block is transactional: if one operation fails, changes from the block are rolled back. `simul` is deterministic and is not a parallel-thread scheduler.

**Runnable example:**

```mana
stone = create Earth
water = create Water
simul:
    heat(stone, 10 K)
    cool(water, 10 K)
```

Expected output:

```text
(no output)
```

**Arguments and error cases:** Only supported direct operation calls are accepted and known conflicting writes are rejected. Unsupported operations or conflicting writes raise `MagicErrorML` before the block can commit changes.

### `last_collisions()` — inspect recent collision records

Returns readable summaries of recent contacts, including object names, normal impact energy, kinetic energy converted to heat, and collision time. The runtime keeps up to 1,000 records. The most recent records are part of runtime state, so `post` rolls trial records back with the rest of the world. Returns a list of text strings.

```mana
advance_time(1 s)
show last_collisions()
```

Expected output:

```text
[]
```

## H. Constants and geometry labels

**Arguments and error cases:** Takes no arguments and returns up to 1,000 text summaries. Invalid arguments raise `TypeErrorML`.

### `c`

Built-in speed-of-light constant in `m/s`; reserved and cannot be used as a variable name. Massive objects cannot reach or exceed this speed.

**Runnable example:**

```mana
show c
```

Expected output:

```text
2.99792e+08 m/s
```

### `pi`

Built-in mathematical constant π; reserved.

**Runnable example:**

```mana
show pi
```

Expected output:

```text
3.141592653589793
```

### Geometry labels

The following identifiers are predeclared strings accepted by `shape`: `point`, `line`, `ray`, `segment`, `circle`, `round`, `arc`, `ellipse`, `ring`, `polygon`, `beam`, `wave`, `disc`, `spiral`, `fan`, `wall`, `field`, `dome`, `cage`, `chain`, `tendril`, `cone`, `corridor`.

They label the shape in this prototype. The 2D world simulation uses circle bounds, not exact shapes or wall/polygon edges. The optional 3D vector calculations are retained in the library layer, but 3D world simulation is not part of the primary engine.

## I. Operators and standard expressions

Supported expression operators:

| Category | Operators |
|---|---|
| Arithmetic | `+`, `-`, `*`, `/`, `%`, `**` |
| Comparison | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Boolean | `and`, `or`, `not` |
| Unary | `+value`, `-value`, `not value` |

Library helper functions support positional arguments, named arguments, and parameter defaults. Ordinary MANA helper functions use `def` and may accept parameters for calculations. Spell definitions use `spldef` and accept either no parameters or the single `element` selector in `spldef name(element):`; general helper parameters/defaults are permitted in ordinary definitions and packaged library modules. Attribute reads/writes use dot notation, such as `stone.temp`. Only expressions defined by the MANA grammar are supported; unlisted syntax is not identified as a MANA construct.

## J. Common failure categories

- `SyntaxErrorML`: malformed syntax/indentation or use of a malformed definition or syntax.
- `TypeErrorML`: wrong value type or missing property.
- `UnitErrorML`: incompatible dimensions.
- `RuntimeErrorML`: undefined name, invalid call, or execution limit.
- `MagicErrorML`: invalid magical interaction or write to a runtime-managed property.
- `PhysicsErrorML`: invalid physical values, absolute-zero violation, or speed limit violation.

**Runnable example:**

```mana
stone = create Earth
shape(stone, circle)
show stone.shape
```

Expected output:

```text
circle
```


## K. Plane-linked entities and necromancy

These are namespaced library functions. See the linked library guides for validation rules and errors.

- `summoning.bring(being[, source_plane][, position][, requirements])` manifests a known being into the Mortal Plane. Destination is implicit; built-in home planes are inferred. If its result is assigned to a variable, that instance is automatically tamed under the variable name.
- `summoning.tame(being[, name])` gives a summoned instance a stable name; `summoning.send_back(being)` returns it through a reverse pathway; `summoning.call(being)` recalls the same returned instance. All route changes require open pathways.
- `necromancy.reanimate(corpse[, name])` reanimates existing bones/corpse/remains and does not take an energy argument. A summon spell is ordinary user-written MANA code, not a built-in function.
- `necromancy.reanimate_many(corpses[, name])` reanimates a list of distinct, eligible bodies, recording use per body.
- `necromancy.is_undead(thing)` checks an object's undead marker.
- `planes.invoke("Necro")` grants the invocation permission for the necromantic mana channel. The physical ledger source is recorded as Underworld. The transfer entries are accounting records, not energy added to a body or a spendable mana pool.

See [Summoning](../libraries/SUMMONING_LIBRARY.md), [Necromancy](../libraries/NECROMANCY_LIBRARY.md), and [Planes](../libraries/PLANES_LIBRARY.md).
