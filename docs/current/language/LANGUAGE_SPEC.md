# MANA Language and Runtime Specification

**Page kind:** Reference  


Any word that is not defined in the MANA keyword table is not identified as a keyword.

**Version:** 2.0.0
**Status:** prototype specification. The function reference documents registered built-ins.

## 1. Source format

- Extension: `.mana`; UTF-8 text. Source files with a UTF-8 BOM are accepted.
- Indentation defines blocks; four spaces are recommended. Do not mix tabs and spaces in indentation. A tab is expanded to four spaces by the current lexer.
- Newlines inside parentheses and square brackets are ignored, allowing multi-line expressions.
- `#` begins a comment.
- Identifiers are case-sensitive.
- MANA has `incant` is the definition-exit statement. `incant value` supplies a definition result and exits that definition. The word `return` has no language-level control-flow meaning.
- `load library_name` loads an optional library into a named namespace. Library helpers are used with that namespace prefix, such as `geometry2d.distance(...)` or `planes.find_route(...)`. The lowercase `mana` namespace is installed automatically; `load mana` is also accepted. Pure-mana constructs are shaped with `weave mana`; `create Mana` is rejected with a migration hint.

## 2. Definitions and element templates

MANA distinguishes normal calculation functions from magical spell definitions.

- `def` defines an ordinary function. It may accept parameters and defaults, calculate a value, and supply that value with `incant`. Direct calls are for calculation and cannot create objects or mutate the world.
- `spell` is the primary, language-level spelling for a spell declaration. It uses the same indentation-based grammar as every MANA block and runs with standalone `appraise spell_name` or `cast spell_name`. It accepts no parameters, or one `element` selector for a reusable base-element spell template. `spldef` remains a fully supported legacy alias. Other spell settings belong in the body and are changed with `tune`. Legacy `post(spell_name)` and `release(spell_name)` remain supported.
- `weather preset, option=value, ...` is a native climate statement. It configures the global atmosphere when no `radius` is supplied; with `radius=...`, it creates or updates an area-weather zone centred at the caster's world position (or an explicit `center=...`). A zone affects supported objects only while they are inside its radius.
- `name = conjure material, option=value, ...` is the native matter-creation expression. It is equivalent to calling `conjure(...)` but makes matter declaration read naturally in a MANA program.
- `name = summon "Being Name" from "Plane Name", option=value, ...` is the native summoning expression. It brings a catalogue being through an already-open plane pathway. Parenthesised expressions can supply a computed being or plane name; `position=...` and `requirements=[...]` are optional. The `summoning.bring(...)` library form remains supported.
- `tgset` is separate: it creates a target profile or opens a target context. It is not a definition keyword.

```mana
spell e_ball(element):
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

### Native spell, weather, matter, and appraisal syntax

```mana
spell rain_circle():
    weather rain, intensity=0.8, wind_speed=8 m/s, wind_direction=north, duration=30 s, radius=80 m
    iron = conjure steel, mass=5 kg, shape=sphere, anchored=false
    shape iron into ring
    transmute iron into bronze
    incant iron

appraise rain_circle
cast rain_circle
```

Expected output:

```text
[APPRAISAL rain_circle] inputs: no parameters
[APPRAISAL rain_circle] local weather configured: rain (radius 80 m, intensity 0.8)
[APPRAISAL rain_circle] energy input: 1.46575e+06 J (conjure steel; matter manifestation)
[APPRAISAL rain_circle] created Steel (Compound, 5 kg; conjured material steel)
[APPRAISAL rain_circle] executed conjure('steel')
[APPRAISAL rain_circle] Steel.shape: 'sphere' -> 'ring' (shape)
[APPRAISAL rain_circle] Steel.area: 0.00740287 m2 -> 0.00686001 m2 (transmute)
[APPRAISAL rain_circle] Steel.collision_radius: 0.0485428 m -> 0.0467291 m (transmute)
[APPRAISAL rain_circle] Steel.composition: {'kind': 'alloy', 'name': 'Steel (generic estimate)', 'elements': [{'symbol': 'Fe', 'atomic_number': 26, 'mass_fraction': 0.985}, {'symbol': 'C', 'atomic_number': 6, 'mass_fraction': 0.015}], 'estimated': True} -> {'kind': 'alloy', 'name': 'Bronze (generic estimate)', 'elements': [{'symbol': 'Cu', 'atomic_number': 29, 'mass_fraction': 0.88}, {'symbol': 'Sn', 'atomic_number': 50, 'mass_fraction': 0.12}], 'estimated': True} (transmute)
[APPRAISAL rain_circle] Steel.corrosion_resistance: 0.42 -> 0.78 (transmute)
[APPRAISAL rain_circle] Steel.density: 7850 kg/m3 -> 8800 kg/m3 (transmute)
[APPRAISAL rain_circle] Steel.electrical_conductivity: 0.58 -> 0.35 (transmute)
[APPRAISAL rain_circle] Steel.hardness_index: 0.68 -> 0.5 (transmute)
[APPRAISAL rain_circle] Steel.hardness_index_before_transmute: '<unset>' -> 0.5 (transmute)
[APPRAISAL rain_circle] Steel.magnetic_response: 0.85 -> 0.0 (transmute)
[APPRAISAL rain_circle] Steel.material: 'steel' -> 'bronze' (transmute)
[APPRAISAL rain_circle] Steel.material_properties: {'density_kg_m3': 7850.0, 'state': 'solid', 'category': 'alloy', 'hardness_index': 0.68, 'toughness_index': 0.76, 'strength_mpa': 550.0, 'magnetic_response': 0.85, 'electrical_conductivity': 0.58, 'thermal_conductivity': 0.48, 'combustible': False, 'brittle': False, 'corrosion_resistance': 0.42, 'estimated': True, 'elastic_modulus_gpa': 200.0, 'specific_heat_j_kg_k': 480.0, 'melting_point_k': 1700.0, 'boiling_point_k': None, 'thermal_expansion_per_k': 1.2e-05, 'porosity_index': 0.04, 'toxicity_index': 0.0, 'optical_transparency_index': 0.0, 'magical_resonance_index': 0.0, 'tags': ['structural', 'workable', 'conductive'], 'common_uses': ['tools', 'structures', 'weapons', 'machines'], 'microstructure': 'alloy', 'property_scope': 'estimated gameplay coefficient; not certified engineering data', 'name': 'steel', 'source': 'estimated-material-profile', 'subcategory': 'alloy', 'family': 'metals and alloys'} -> {'density_kg_m3': 8800.0, 'state': 'solid', 'category': 'alloy', 'hardness_index': 0.5, 'toughness_index': 0.63, 'strength_mpa': 350.0, 'magnetic_response': 0.0, 'electrical_conductivity': 0.35, 'thermal_conductivity': 0.32, 'combustible': False, 'brittle': False, 'corrosion_resistance': 0.78, 'estimated': True, 'elastic_modulus_gpa': 100.0, 'specific_heat_j_kg_k': 500.0, 'melting_point_k': None, 'boiling_point_k': None, 'thermal_expansion_per_k': 1.2e-05, 'porosity_index': 0.04, 'toxicity_index': 0.0, 'optical_transparency_index': 0.0, 'magical_resonance_index': 0.0, 'tags': ['alloy', 'solid', 'conductive'], 'common_uses': ['general world simulation', 'crafting reference'], 'microstructure': 'alloy', 'property_scope': 'estimated gameplay coefficient; not certified engineering data', 'name': 'bronze', 'source': 'estimated-material-profile', 'subcategory': 'alloy', 'family': 'metals and alloys'} (transmute)
[APPRAISAL rain_circle] Steel.strength_mpa: 550.0 -> 350.0 (transmute)
[APPRAISAL rain_circle] Steel.thermal_conductivity: 0.48 -> 0.32 (transmute)
[APPRAISAL rain_circle] Steel.toughness_index: 0.76 -> 0.63 (transmute)
[APPRAISAL rain_circle] Steel.volume: 0.000636943 m3 -> 0.000568182 m3 (transmute)
[APPRAISAL rain_circle] spell completed
[APPRAISAL rain_circle] mana appraisal: 0.5 mana
[APPRAISAL rain_circle] created: Steel (Compound, 5 kg)
[CAST rain_circle] spell committed
[CAST rain_circle] mana appraisal: 0.5 mana
```

This is MANA's primary, indentation-based syntax: no curly braces, four-space blocks, and units attached to values. `appraise spell_name` runs a non-committing trial, records what would happen and reports calculated effort; `cast spell_name` commits the successful world changes and records an execution result. Existing `post(spell_name)` and `release(spell_name)` forms remain compatible. The operation APIs remain available for advanced arguments, but ordinary spell source can use native verbs such as `shape object into ring`, `transmute object into bronze`, `transfigure guardian into knight`, and `transform water into gas`. A dynamic destination can be parenthesised, as in `transmute ingot into (chosen_material)`.

Mana is not a personal battery that must be depleted to permit casting. The runtime calculates and records a mana-equivalent appraisal alongside physical energy, material, environmental changes, and impacts. `weather` inside a spell changes the simulated climate: no radius means global world climate; `radius=80 m` creates local weather centred on the caster unless an explicit `center=...` is supplied. A weather spell is therefore a reusable authored action, while rain, wind, fog, and other conditions are configurable environment properties rather than separate hard-coded spell types.

`conjure` accepts material, mass (up to the current 1e12 kg per object bound), position, shape, name, temperature, density, phase/state, velocity, anchored/collidable flags, restitution, friction, and drag coefficient. The language and runtime still enforce the world-object and numerical-safety budgets.


`create` must be assigned directly: `ball = create element`. The element expression may be a static catalogue type or the `element` selector within a template. `create` is not valid as an unassigned expression or nested argument.

## 3. Tuning an operation

Syntax:

```mana
spell e_ball(element):
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
- `post(spell_name)`: runs a trial, prints a text report and restores world state.
- `post(spell_name, text)`: explicitly requests the default text report.
- `post(spell_name, visual)`: runs the same non-committing trial and retains its hypothetical scene events for an active Visualiser recording.
- `release(spell_name)`: fires the named spell and commits world changes. When inside `tgset(target):`, the engine automatically resolves scalar-speed direction and flight for the selected target.

`post` accepts a spell identifier and an optional `text` or `visual` presentation; omitting the second argument is identical to `post(spell_name, text)`. `visual` never commits the trial and never launches an extension on its own. To see it, run the file with the VS Code Visual button or create a recording using `python mana.py --record file.jsonl source.mana`. `release` accepts only a spell identifier. Neither command is an expression; assignments and nested calls are rejected. Their `SpellResult` records are for host APIs and tests rather than MANA source.

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

spell fireball():
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
[POST fireball] collision: guard ↔ projectile; impact energy 45000 J; 43200 J converted to heat
[POST fireball] hit: projectile hit guard; 140 HP damage; HP 110
[POST fireball] spell completed
[POST fireball] mana appraisal: 45000.1 mana
[POST fireball] created: projectile (Fire, 1 kg)
[POST fireball] hits: guard
```

The two forms have distinct meanings: `guard = tgset:` creates a target profile; `tgset(guard):` temporarily selects an existing target for statements in the block. Target choice is outside the spell definition. Inside the selected-target block, a scalar `velocity(object, speed)` automatically points at the target, and targeted `post`/`release` advance the projectile through the simulated flight. A distance-only profile is placed along the default forward axis (+X) in this headless prototype; explicit `pos` takes precedence.

## 6. Expressions and data

Values include numbers, strings, booleans, lists, quantities, vectors, element-type selectors, magical objects, definitions, and configured spell instances. Supported operators include arithmetic, comparisons, and boolean `and`, `or`, and `not`. String literals accept single or double quotes and the escapes `\n`, `\t`, `\r`, `\\`, and an escaped matching quote. Tuple, set, and dictionary literals are not part of this prototype.

Lists support indexed reads and writes, including nested indexing such as `matrix[0][1]`. Indexing accepts integer indexes; negative indexes count from the end. An invalid index or index type raises a MANA error. `length(value)` returns the length of a list, string, or `span`. Lists can be passed into helper functions and used inside other expressions; indexing is part of the expression grammar, not a standalone feature. MANA does not provide tuple, set, or dictionary literals.

Control-flow blocks share the enclosing definition/module scope: a variable first assigned inside `if`, `while`, `for`, `tgset(...)`, `after`, `every`, or `when` remains in that enclosing scope. Each `def` creates a new local scope, so names first assigned inside the definition do not leak into the caller. Ordinary direct calls to definitions are helper calls: they may calculate and `incant` a value, but cannot create objects, mutate object properties, run object-changing operations, or schedule time work. Use `appraise name` to test spell execution and `cast name` to commit it; legacy `post(name)` and `release(name)` remain supported. A helper may register `when` handlers; those handlers execute only when their event occurs.

## 7. Units, energy and errors

MANA uses dimension-aware quantities for mass, distance, time, temperature, and mana. The `c` constant represents the speed of light. Operation-level mana-cost values are readouts, not an expendable pool. Matter creation uses the configured matter-to-mana multiplier. See `../physics/ENERGY_MODEL.md` for current energy rules.

Error families: `SyntaxErrorML`, `TypeErrorML`, `UnitErrorML`, `RuntimeErrorML`, `MagicErrorML`, and `PhysicsErrorML`. Runtime diagnostics include the source file, line, and column where available and are written to standard error. The CLI exits with `0` on success, `1` on a language/runtime error, and `2` for incorrect invocation or usage. Unexpected host-language exceptions include a Python traceback for debugging.

Unit literals use SI base units and support prefixes `k`, `M`, `G`, `m`, `u`, and `n` on supported units; `g` is also accepted and converted to kilograms. Examples include `1 km` (= `1000 m`), `3 ms` (= `0.003 s`), `1 MJ` (= `1,000,000 J`), and `2 g` (= `0.002 kg`). Unsupported units produce an `unknown unit` error. Celsius (`C`) is accepted only as a standalone absolute-temperature literal: `20 C` is stored as `293.15 K`, and `-10 C` is stored as `263.15 K`. Absolute temperatures cannot be below `0 K`; `heat()` and `cool()` accept temperature changes in K, not absolute Celsius literals. Absolute Celsius values cannot be multiplied, divided, or exponentiated; convert the operation to a temperature difference in K when appropriate.

## 8. Libraries and namespaces

The main 2D world engine always runs for world objects; it does not require an explicit library load. `load geometry2d` makes advanced planar math, intersections, angles, and explicit direction helpers available under the `geometry2d` namespace. `load vector3d` provides 3D calculations under `vector3d`, but does not enable a 3D world. `load planes` exposes plane identification, pathway configuration, route search and energy-transfer accounting through `planes`; it does not create plane definitions. The built-in `mana`, `weather`, `world`, and `periodic` namespaces are installed automatically. `mana` provides pure-mana effects and universal object control; `weather` configures atmospheric parameters; `world` configures active global physics laws; and `periodic` exposes the read-only 118-element material catalogue. The `weave mana` operation shapes pure-mana constructs. User-authored MANA helper libraries use `.manalib` packages built by `tools/library_builder.py`. See [2D Geometry Library](../libraries/GEOMETRY2D_LIBRARY.md), [3D Vector Library](../libraries/VECTOR3D_LIBRARY.md), [Planes Library](../libraries/PLANES_LIBRARY.md), [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md), [World Weather and Matter](../libraries/WORLD_WEATHER_AND_MATTER.md), and [Library Builder](../libraries/LIBRARY_BUILDER.md).

## 9. Control flow

Supported constructs include `if` / `elif` / `else`, `while`, `for`, `simul:`, `wait`, `after`, `every`, and `when`. Loop and persistence safety limits apply in the prototype.

## 10. Physics stepping and collisions

`advance_time(duration[, timestep=...][, gravity=...])` advances virtual time through deterministic substeps, integrates persistent acceleration and optional world gravity, resolves swept-circle contacts in the 2D x-y plane, runs time/event handlers, and returns elapsed seconds. The default timestep is `1/60 s`; the maximum per-step duration is `0.1 s`, and each call is limited to 100,000 steps and 20,000,000 estimated collision-pair checks. Gravity defaults to the configurable `world.current()` value (zero by default); a `gravity=` argument overrides that global setting for the current `advance_time` call.

Objects default to `collidable = true`, inherit world-default `restitution = 0.2` and `friction = 0.35` unless overridden per object, `area = 1 m2`, and `collision_radius = 0 m`. A zero collision radius derives an equivalent circle from projected area (`r = sqrt(area/pi)`); a positive radius overrides it. World object position, velocity, acceleration, direction and gravity vectors must have z = 0. General 3D vector calculations remain available as library-style calculations, but the primary world engine is 2D. `collidable = false` disables contacts without disabling motion. Collisions emit `impact` and `collision`; positive HP damage to one target profile also emits `damaged`. `last_collisions()` reads recent contact summaries.

The current world contact geometry is circular, and contact impulses are Newtonian. Relativistic kinetic energy and momentum calculations remain available through the retained vector/physics library, but relativistic collision outcomes are not yet supported. Targeted flight currently considers only suitable objects created by the spell, uses the innermost active target context, places distance-only targets on the positive X axis, and rejects estimated flight times over 60 seconds. These are headless-prototype limits, not general world-engine rules. See `../physics/PHYSICS_ENGINE.md` for equations, examples, and limitations.


## 11. Reserved names

The following names cannot be used as variable or ordinary definition names. They are reserved to protect language syntax, object properties, operations, element selectors, or geometry labels. `load` and `skip` are language keywords. `return`, `import`, `pass`, `range`, and `len` do not have language-statement or built-in semantics in MANA; they are not supported alternatives to `incant`, `load`, `skip`, `span`, or `length`. `break` and `continue` are not implemented and produce a clear unsupported-construct error. See [Keyword Migration](KEYWORD_MIGRATION.md) for the rationale and the deliberately retained overlaps.

**Programming keywords:**

`def`, `spell` (with legacy `spldef`), `load`, `incant`, `tgset`, `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not`, `true`, `false`, `create`, `simul`, `wait`, `after`, `every`, `when`, `skip`, `tune`.

**Operations, measurements, constants and library names:**

`shape`, `move`, `heat`, `cool`, `accelerate`, `decelerate`, `velocity`, `impulse`, `aim`, `rotate`, `scale`, `push`, `pull`, `reflect`, `split`, `anchor`, `unanchor`, `dispel`, `bind`, `combine`, `separate`, `transform`, `compress`, `expand`, `detect`, `has_domain`, `distance`, `magnitude`, `force`, `pressure`, `momentum`, `kinetic_energy`, `span`, `sqrt`, `active_objects`, `last_collisions`, `matter_to_mana`, `mana_to_matter`, `mana_to_energy`, `energy_to_mana`, `advance_time`, `emit`, `show`, `post`, `release`, `length`, `c`, `pi`, `geometry2d`, `vector3d`, `planes`, `mana`, `weather`, `world`, `periodic`, `Mana`.

**Object property names:**

`mass`, `volume`, `area`, `density`, `pos`, `vel`, `acc`, `force`, `energy`, `temp`, `pressure`, `state`, `material`, `mana`, `integrity`, `integrity_break_energy`, `integrity_energy`, `stabilizers`, `rot`, `scale`, `anchored`, `anchor_pos`, `direction`, `active`, `released`, `bound`, `collision_radius`, `restitution`, `friction`, `collidable`, `acceleration_persistent`, `combustible`, `powderable`, `ignition_temp`, `kind`, `hp`, `max_hp`, `defence`.

**Shape labels:**

`point`, `line`, `ray`, `segment`, `circle`, `round`, `arc`, `ellipse`, `ring`, `polygon`, `beam`, `wave`, `disc`, `spiral`, `fan`, `wall`, `field`, `dome`, `cage`, `chain`, `tendril`, `cone`, `corridor`.

**Registered element selectors:**

`Air`, `Darkness`, `Death`, `Earth`, `Entropy`, `Fire`, `Light`, `Lightning`, `Life`, `Mana`, `Metal`, `Nature`, `Order`, `Soul`, `Sound`, `Space`, `Spirit`, `Time`, `Void`, `Water`.

## 12. Events, tracing and loop limits

The recognized event names are `impact`, `collision`, `damaged`, `path_opened`, `path_closed`, `energy_arrived`, `mana_formed`, `mana_burst`, `mana_emitted`, and `object_ignited`. Registering or emitting an unknown event raises a runtime warning; the name remains inert unless it matches an event the engine emits. `simul` validates conflicts between supported operations and then executes them in source order. If an operation fails, the block's changes are rolled back. `simul` is deterministic; it is not a parallel-thread scheduler.

`appraise` and `post` report a trace change using the format `object.property: before -> after (operation)`. Set the environment variable `MANA_TRACE_DETAIL=summary` to suppress per-change trace lines and retain the summary. `MANA_TRACE_DETAIL=full` enables detailed trace lines; full is the default for compatibility. A `for` or `while` loop terminates when its iteration condition ends or when it reaches the safety limit of 1,000,000 iterations. There is no `break` or `continue` statement in this build; make the loop condition reflect when the loop should stop. For example:

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
| `def` | `def` defines calculations; `spell` defines world-changing spells (`spldef` is a compatible legacy alias). |
| `True`, `False` | `true`, `false` (lowercase). |
| `if`, `elif`, `else`, `while`, `for`, `in`, `and`, `or`, `not` | These control-flow and boolean words are supported in MANA. |
| `None`, `lambda`, `class`, `try`, `except`, `with`, `yield`, `raise`, `global`, `del`, `assert`, `break`, `continue` | Not identified as MANA constructs. |

Any word that is not in the MANA keyword table is not identified as a keyword. A word can still be a valid user-defined name unless it is reserved by the runtime.

### Native summoning expression

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

`appraise` records a trial without committing the new instance; `cast` commits the successful summon. A valid route and a known being record are required. `conjure` creates physical matter and does not read the being catalogue. See the [Summoning Library](../libraries/SUMMONING_LIBRARY.md) for route requirements, position and condition options.
