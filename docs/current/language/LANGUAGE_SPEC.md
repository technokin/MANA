# MANA Language and Runtime Specification

**Page kind:** Reference  


Any word that is not defined in the MANA keyword table is not identified as a keyword.

**Version:** 1.0.0
**Status:** prototype specification. The function reference documents registered built-ins.

## 1. Source format

- Extension: `.mana`; UTF-8 text. Source files with a UTF-8 BOM are accepted.
- Indentation defines blocks; four spaces are recommended. Do not mix tabs and spaces in indentation. A tab is expanded to four spaces by the current lexer.
- Newlines inside parentheses and square brackets are ignored, allowing multi-line expressions.
- `#` begins a comment.
- Identifiers are case-sensitive.
- MANA has `incant` is the definition-exit statement. `incant value` supplies a definition result and exits that definition. The word `return` has no language-level control-flow meaning.
- `load library_name` loads an optional library into a named namespace. Library helpers are used with that namespace prefix, such as `geometry2d.distance(...)` or `planes.find_route(...)`. The lowercase `mana` namespace is installed automatically; `load mana` is also accepted. Uppercase `Mana` is a type selector used by `create Mana`.

## 2. Definitions and element templates

MANA distinguishes normal calculation functions from magical spell definitions.

- `def` defines an ordinary function. It may accept parameters and defaults, calculate a value, and supply that value with `incant`. Direct calls are for calculation and cannot create objects or mutate the world.
- `spldef` defines a spell that is run with standalone `post(spell)` or `release(spell)`. It accepts no parameters, or one `element` selector for a reusable base-element spell template. Other spell settings belong in the body and are changed with `tune`.
- `tgset` is separate: it creates a target profile or opens a target context. It is not a definition keyword.

```mana
spldef e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
earth_ball = e_ball(Earth)
```

Expected output:

```text
(no output)
```

Calling an element template with a base element returns a configured `SpellInstance`; it does not execute the body. A template's parameter must evaluate to the registered base type `Fire`, `Water`, `Earth`, or `Air`. The created spell instance must be assigned if it is to be used later.

`create` must be assigned directly: `ball = create element`. The element expression may be a static catalogue type or the `element` selector within a template. `create` is not valid as an unassigned expression or nested argument.

## 3. Tuning an operation

Syntax:

```mana
spldef e_ball(element):
    ball = create element
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
tune(fire_ball.velocity) = ball, 600 m/s
```

Expected output:

```text
(no output)
```

The left side names a configured spell instance and an operation name. The first item after `=` is the source-level variable targeted by that operation inside the definition; the second item replaces the operation's second positional argument.

- The operation/target pair must already exist exactly once in the definition.
- Missing or ambiguous matches raise `TypeErrorML`.
- A configured instance's tuning does not affect other instances made from the same template.
- Tuning persists for the current program run and survives `post` rollback.
- Unit and value validation is enforced when the tuned spell executes.
- The removed syntax `spell.tune = parameter: value` is invalid.

## 4. Statements and expression behaviour

- `incant value`: immediately exits the current definition and supplies a value to its caller. It is a statement, not a function.
- `skip`: no-operation statement; no world mutation or mana cost.
- `show value` / `show(value)`: prints values and is not assignable.
- `post(spell_name)`: runs a trial, prints a trace and restores world state.
- `release(spell_name)`: fires the named spell and commits world changes. When inside `tgset(target):`, the engine automatically resolves scalar-speed direction and flight for the selected target.

`post` and `release` each accept exactly one identifier referring to a spell definition or configured instance. Neither is an expression; assignments and nested calls are rejected. Their `SpellResult` records are for host APIs and tests rather than MANA source.

## 5. Target profiles and casting context

Define a target profile separately from the spell:

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

Select that target only when casting:

```mana
guard = tgset:
    hp = 250
    max_hp = 250
    defence = 40
    resist_fire = 0.6
    distance = 12 m

spldef fireball():
    projectile = create Fire
    shape(projectile, circle)
    velocity(projectile, 300 m/s)
    incant projectile

tgset(guard):
    post(fireball)
    release(fireball)
```

Expected output:

```text
[POST fireball] inputs: no parameters
[POST fireball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fireball] created Fire (Fire, 1 kg; create Fire)
[POST fireball] projectile.shape: 'point' -> 'circle' (shape)
[POST fireball] energy input: 45000 J (velocity; spell work)
[POST fireball] projectile.energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fireball] projectile.integrity: 0.992062994740159 -> 0.9919456821384532 (velocity)
[POST fireball] projectile.integrity_effective_energy_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fireball] projectile.integrity_energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fireball] projectile.integrity_last_score_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fireball] projectile.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fireball] projectile.mana_cost: 0.1 -> 45000.10000003379 (velocity)
[POST fireball] projectile.mana_used: 0.1 -> 45000.10000003379 (velocity)
[POST fireball] projectile.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fireball] projectile.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fireball] target selected: guard; simulating targeted motion for 0.0566667 s
[POST fireball] collision: guard ↔ projectile; impact energy 22500 J; 21600 J converted to heat
[POST fireball] hit: projectile hit guard; 50 HP damage; HP 200
[POST fireball] spell completed
[POST fireball] mana cost: 45000.1 mana
[POST fireball] created: projectile (Fire, 1 kg)
[POST fireball] hits: guard
```

The two forms have distinct meanings: `guard = tgset:` creates a target profile; `tgset(guard):` temporarily selects an existing target for statements in the block. Target choice is outside the spell definition. Inside the selected-target block, a scalar `velocity(object, speed)` automatically points at the target, and targeted `post`/`release` advance the projectile through the simulated flight. A distance-only profile is placed along the default forward axis (+X) in this headless prototype; explicit `pos` takes precedence.

## 6. Expressions and data

Values include numbers, strings, booleans, lists, quantities, vectors, element-type selectors, magical objects, definitions, and configured spell instances. Supported operators include arithmetic, comparisons, and boolean `and`, `or`, and `not`. String literals accept single or double quotes and the escapes `\n`, `\t`, `\r`, `\\`, and an escaped matching quote. Tuple, set, and dictionary literals are not part of this prototype.

Lists support indexed reads and writes, including nested indexing such as `matrix[0][1]`. Indexing accepts integer indexes; negative indexes count from the end. An invalid index or index type raises a MANA error. `length(value)` returns the length of a list, string, or `span`. Lists can be passed into helper functions and used inside other expressions; indexing is part of the expression grammar, not a standalone feature. MANA does not provide tuple, set, or dictionary literals.

Control-flow blocks share the enclosing definition/module scope: a variable first assigned inside `if`, `while`, `for`, `tgset(...)`, `after`, `every`, or `when` remains in that enclosing scope. Each `def` creates a new local scope, so names first assigned inside the definition do not leak into the caller. Ordinary direct calls to definitions are helper calls: they may calculate and `incant` a value, but cannot create objects, mutate object properties, run object-changing operations, or schedule time work. Use `post(name)` to test spell execution and `release(name)` to commit it. A helper may register `when` handlers; those handlers execute only when their event occurs.

## 7. Units, energy and errors

MANA uses dimension-aware quantities for mass, distance, time, temperature, and mana. The `c` constant represents the speed of light. Operation-level mana-cost values are readouts, not an expendable pool. Matter creation uses the configured matter-to-mana multiplier. See `../physics/ENERGY_MODEL.md` for current energy rules.

Error families: `SyntaxErrorML`, `TypeErrorML`, `UnitErrorML`, `RuntimeErrorML`, `MagicErrorML`, and `PhysicsErrorML`. Runtime diagnostics include the source file, line, and column where available and are written to standard error. The CLI exits with `0` on success, `1` on a language/runtime error, and `2` for incorrect invocation or usage. Unexpected host-language exceptions include a Python traceback for debugging.

Unit literals use SI base units and support prefixes `k`, `M`, `G`, `m`, `u`, and `n` on supported units; `g` is also accepted and converted to kilograms. Examples include `1 km` (= `1000 m`), `3 ms` (= `0.003 s`), `1 MJ` (= `1,000,000 J`), and `2 g` (= `0.002 kg`). Unsupported units produce an `unknown unit` error. Celsius (`C`) is accepted only as a standalone absolute-temperature literal: `20 C` is stored as `293.15 K`, and `-10 C` is stored as `263.15 K`. Absolute temperatures cannot be below `0 K`; `heat()` and `cool()` accept temperature changes in K, not absolute Celsius literals. Absolute Celsius values cannot be multiplied, divided, or exponentiated; convert the operation to a temperature difference in K when appropriate.

## 8. Libraries and namespaces

The main 2D world engine always runs for world objects; it does not require an explicit library load. `load geometry2d` makes advanced planar math, intersections, angles, and explicit direction helpers available under the `geometry2d` namespace. `load vector3d` provides 3D calculations under `vector3d`, but does not enable a 3D world. `load planes` exposes plane identification, pathway configuration, route search and energy-transfer accounting through `planes`; it does not create plane definitions. The built-in lowercase `mana` namespace is installed automatically and provides pure-mana effects and universal object control. Uppercase `Mana` is the `create` type selector; it is not the same value as the `mana` namespace. User-authored MANA helper libraries use `.manalib` packages built by `tools/library_builder.py`. See [2D Geometry Library](../libraries/GEOMETRY2D_LIBRARY.md), [3D Vector Library](../libraries/VECTOR3D_LIBRARY.md), [Planes Library](../libraries/PLANES_LIBRARY.md), [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md), and [Library Builder](../libraries/LIBRARY_BUILDER.md).

## 9. Control flow

Supported constructs include `if` / `elif` / `else`, `while`, `for`, `simul:`, `wait`, `after`, `every`, and `when`. Loop and persistence safety limits apply in the prototype.

## 10. Physics stepping and collisions

`advance_time(duration[, timestep=...][, gravity=...])` advances virtual time through deterministic substeps, integrates persistent acceleration and optional world gravity, resolves swept-circle contacts in the 2D x-y plane, runs time/event handlers, and returns elapsed seconds. The default timestep is `1/60 s`; the maximum per-step duration is `0.1 s`, and each call is limited to 100,000 steps and 20,000,000 estimated collision-pair checks. Gravity defaults to zero and must be passed as an acceleration vector when desired.

Objects default to `collidable = true`, `restitution = 0.2`, `area = 1 m2`, and `collision_radius = 0 m`. A zero collision radius derives an equivalent circle from projected area (`r = sqrt(area/pi)`); a positive radius overrides it. World object position, velocity, acceleration, direction and gravity vectors must have z = 0. General 3D vector calculations remain available as library-style calculations, but the primary world engine is 2D. `collidable = false` disables contacts without disabling motion. Collisions emit `impact` and `collision`; positive HP damage to one target profile also emits `damaged`. `last_collisions()` reads recent contact summaries.

The current world contact geometry is circular, and contact impulses are Newtonian. Relativistic kinetic energy and momentum calculations remain available through the retained vector/physics library, but relativistic collision outcomes are not yet supported. Targeted flight currently considers only suitable objects created by the spell, uses the innermost active target context, places distance-only targets on the positive X axis, and rejects estimated flight times over 60 seconds. These are headless-prototype limits, not general world-engine rules. See `../physics/PHYSICS_ENGINE.md` for equations, examples, and limitations.


## 11. Reserved names

The following names cannot be used as variable or ordinary definition names. They are reserved to protect language syntax, object properties, operations, element selectors, or geometry labels. `load` and `skip` are language keywords. `return`, `import`, `pass`, `range`, and `len` do not have language-statement or built-in semantics in MANA; they are not supported alternatives to `incant`, `load`, `skip`, `span`, or `length`. `break` and `continue` are not implemented and produce a clear unsupported-construct error. See [Keyword Migration](KEYWORD_MIGRATION.md) for the rationale and the deliberately retained overlaps.

**Programming keywords:**

`def`, `spldef`, `load`, `incant`, `tgset`, `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not`, `true`, `false`, `create`, `simul`, `wait`, `after`, `every`, `when`, `skip`, `tune`.

**Operations, measurements, constants and library names:**

`shape`, `move`, `heat`, `cool`, `accelerate`, `decelerate`, `velocity`, `aim`, `rotate`, `scale`, `push`, `pull`, `reflect`, `split`, `anchor`, `unanchor`, `dispel`, `bind`, `combine`, `separate`, `transform`, `compress`, `expand`, `detect`, `has_domain`, `distance`, `magnitude`, `force`, `pressure`, `momentum`, `kinetic_energy`, `span`, `sqrt`, `active_objects`, `last_collisions`, `matter_to_mana`, `mana_to_matter`, `mana_to_energy`, `energy_to_mana`, `advance_time`, `emit`, `show`, `post`, `release`, `length`, `c`, `pi`, `geometry2d`, `vector3d`, `planes`, `mana`, `Mana`.

**Object property names:**

`mass`, `volume`, `area`, `density`, `pos`, `vel`, `acc`, `force`, `energy`, `temp`, `pressure`, `state`, `material`, `mana`, `integrity`, `integrity_break_energy`, `integrity_energy`, `stabilizers`, `rot`, `scale`, `anchored`, `anchor_pos`, `direction`, `active`, `released`, `bound`, `collision_radius`, `restitution`, `collidable`, `acceleration_persistent`, `combustible`, `powderable`, `ignition_temp`, `kind`, `hp`, `max_hp`, `defence`.

**Shape labels:**

`point`, `line`, `ray`, `segment`, `circle`, `round`, `arc`, `ellipse`, `ring`, `polygon`, `beam`, `wave`, `disc`, `spiral`, `fan`, `wall`, `field`, `dome`, `cage`, `chain`, `tendril`, `cone`, `corridor`.

**Registered element selectors:**

`Air`, `Darkness`, `Death`, `Earth`, `Entropy`, `Fire`, `Light`, `Lightning`, `Life`, `Mana`, `Metal`, `Nature`, `Order`, `Soul`, `Sound`, `Space`, `Spirit`, `Time`, `Void`, `Water`.

## 12. Events, tracing and loop limits

The recognized event names are `impact`, `collision`, `damaged`, `path_opened`, `path_closed`, `energy_arrived`, `mana_formed`, `mana_burst`, `mana_emitted`, and `object_ignited`. Registering or emitting an unknown event raises a runtime warning; the name remains inert unless it matches an event the engine emits. `simul` validates conflicts between supported operations and then executes them in source order. If an operation fails, the block's changes are rolled back. `simul` is deterministic; it is not a parallel-thread scheduler.

`post` reports a trace change using the format `object.property: before -> after (operation)`. Set the environment variable `MANA_TRACE_DETAIL=summary` to suppress per-change trace lines and retain the summary. `MANA_TRACE_DETAIL=full` enables detailed trace lines; full is the default for compatibility. A `for` or `while` loop terminates when its iteration condition ends or when it reaches the safety limit of 1,000,000 iterations. There is no `break` or `continue` statement in this build; make the loop condition reflect when the loop should stop. For example:

```mana
finished = false
while not finished:
    show "running once"
    finished = true
```

Expected output:

```text
running once
```


## Python-to-MANA lookup

This table is a migration aid for readers familiar with Python. The mappings are conceptual, not a claim that MANA supports Python's complete syntax or execution model. Words not supported by MANA are not identified as MANA constructs.

| Python word or construct | MANA equivalent or behaviour |
|---|---|
| `import` | `load` loads a MANA library namespace. |
| `pass` | `skip` marks an intentionally empty block. |
| `range` | `span` creates a range-like sequence for MANA loops. |
| `len` | `length` reports a supported value's length. |
| `return` | `incant value` supplies a result and exits the current definition. |
| `print` | `show` displays values; it does not return a printable value. |
| `def` | `def` defines calculations; `spldef` defines world-changing spells. |
| `True`, `False` | `true`, `false` (lowercase). |
| `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not` | These control-flow and boolean words are supported in MANA. |
| `None`, `lambda`, `class`, `try`, `except`, `with`, `yield`, `raise`, `global`, `del`, `assert`, `break`, `continue` | Not identified as MANA constructs. |

Any word that is not in the MANA keyword table is not identified as a keyword. A word can still be a valid user-defined name unless it is reserved by the runtime.
