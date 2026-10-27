# Building Your First Spells

**Page kind:** Practical guide  
**Level:** Beginner to intermediate

This guide is meant to be followed with a copy of the MANA project open. Each program below is complete: paste it into a `.mana` file or save it under a new name in the project folder, then run it.

## Before you begin

MANA source files use the `.mana` extension. The interpreter is included in this folder, so you do not need to install a separate game engine or Python package to try the examples.

```powershell
python mana.py --check examples/standalone_release.mana
python mana.py examples/standalone_release.mana
```

On Windows, `py` can replace `python` if that is the launcher installed on your computer. `--check` parses a file without running its statements. It will not catch every runtime error.

## 1. Make an object and cast a spell

An object is created with `create` followed by a supported element or type. A spell definition keeps its actions together. `incant` supplies the result of the definition; it is not a separate casting command.

```mana
spell ember():
    flame = create Fire
    shape(flame, circle)
    velocity(flame, 20 m/s)
    incant flame

post(ember)
release(ember)
show "Objects after the cast:", active_objects()
```

Expected output:

```text
[POST ember] inputs: no parameters
[POST ember] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST ember] created Fire (Fire, 1 kg; create Fire)
[POST ember] flame.shape: 'point' -> 'circle' (shape)
[POST ember] energy input: 200 J (velocity; spell work)
[POST ember] flame.energy: 1e+06 J -> 1.0002e+06 J (velocity)
[POST ember] flame.integrity: 0.992062994740159 -> 0.9920624656417467 (velocity)
[POST ember] flame.integrity_effective_energy_j: 1000000.0 -> 1000200.0 (velocity)
[POST ember] flame.integrity_energy: 1e+06 J -> 1.0002e+06 J (velocity)
[POST ember] flame.integrity_last_score_j: 1000000.0 -> 1000200.0 (velocity)
[POST ember] flame.kinetic_energy: 0 J -> 200 J (velocity)
[POST ember] flame.mana_cost: 0.1 -> 200.10000000000065 (velocity)
[POST ember] flame.mana_used: 0.1 -> 200.10000000000065 (velocity)
[POST ember] flame.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(20, 0, 0) [kg*m/s] (velocity)
[POST ember] flame.vel: Vector3(0, 0, 0) [m/s] -> Vector3(20, 0, 0) [m/s] (velocity)
[POST ember] spell completed
[POST ember] mana appraisal: 200.1 mana
[POST ember] created: flame (Fire, 1 kg)
Objects after the cast: [<element:flame#2>]
```

`post(ember)` tries the spell and restores the world afterward. `release(ember)` runs the spell and commits its successful changes. A release can fail; a failure is not a successful cast just because the definition exists.

## 2. Shape ambient mana

Mana is not made from nothing or stored as a personal fuel bar. Use `weave mana` when you need a pure-mana construct. Write optional settings below it in an indented block.

```mana
load geometry2d

spell ward():
    shield = weave mana:
        shape = barrier
        radius = 0.8 m
        energy = 1800 J
        position = geometry2d.point(2 m, 0 m)
    incant shield

post(ward, visual)
release(ward)
```

Expected output:

```text
[POST ward] inputs: no parameters
[POST ward] shield takes shape
[POST ward] mana.form: 1800 J from ambient mana
[POST ward] spell completed
[POST ward] mana appraisal: 1800 mana
[POST ward] created: shield (Mana, 0 kg)
[POST ward] visual replay was requested, but no Visualiser recording is active; click the Visual button in VS Code or run with --record to view this non-committing preview
```

The setting names accepted by `weave mana` are `shape`, `radius`, `energy`, `position`, `collidable`, and `anchored`. The `shape` value must be one of MANA's supported shape labels. A shape label chooses an appearance and some default behaviour; it does not mean the physics engine has an exact collider with that geometry.

The visual preview is optional. Run the program in a terminal and it will still execute, but you need the Visualiser recording enabled to see the hypothetical cast as a scene.

## 3. Choose a target outside the spell

The target is selected when you cast, not hidden inside the spell definition. That lets you reuse the same spell with different targets.

```mana
load geometry2d

training_dummy = tgset:
    hp = 100
    max_hp = 100
    defence = 0
    pos = geometry2d.point(4 m, 0 m)
    collision_radius = 0.45 m

spell small_bolt():
    bolt = create Fire
    bolt.collision_radius = 0.2 m
    velocity(bolt, 60 m/s)
    incant bolt

tgset(training_dummy):
    post(small_bolt)
    release(small_bolt)

show "Dummy health:", training_dummy.hp
```

Expected output:

```text
[POST small_bolt] inputs: no parameters
[POST small_bolt] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST small_bolt] created Fire (Fire, 1 kg; create Fire)
[POST small_bolt] energy input: 1800 J (velocity; spell work)
[POST small_bolt] bolt.energy: 1e+06 J -> 1.0018e+06 J (velocity)
[POST small_bolt] bolt.integrity: 0.992062994740159 -> 0.9920582353914711 (velocity)
[POST small_bolt] bolt.integrity_effective_energy_j: 1000000.0 -> 1001800.0 (velocity)
[POST small_bolt] bolt.integrity_energy: 1e+06 J -> 1.0018e+06 J (velocity)
[POST small_bolt] bolt.integrity_last_score_j: 1000000.0 -> 1001800.0 (velocity)
[POST small_bolt] bolt.kinetic_energy: 0 J -> 1800 J (velocity)
[POST small_bolt] bolt.mana_cost: 0.1 -> 1800.1000000000538 (velocity)
[POST small_bolt] bolt.mana_used: 0.1 -> 1800.1000000000538 (velocity)
[POST small_bolt] bolt.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(60, 0, 0) [kg*m/s] (velocity)
[POST small_bolt] bolt.vel: Vector3(0, 0, 0) [m/s] -> Vector3(60, 0, 0) [m/s] (velocity)
[POST small_bolt] target selected: training_dummy; simulating targeted motion for 0.0833333 s
[POST small_bolt] collision: training_dummy ↔ bolt; impact energy 1800 J; 1728 J converted to heat
[POST small_bolt] hit: bolt hit training_dummy; 18 HP damage; HP 82
[POST small_bolt] spell completed
[POST small_bolt] mana appraisal: 1800.1 mana
[POST small_bolt] created: bolt (Fire, 1 kg)
[POST small_bolt] hits: training_dummy
Dummy health: 82.0
```

This uses the current 2D world solver. If the runtime reports a contact, that contact is real for this simulation. The Visualiser does not decide that two objects touched merely because their drawings overlap.

## 4. Combine elements

The four fundamental elements are Fire, Water, Earth and Air. Other entries may require invocation first, and not every possible pair has a special rule implemented.

```mana
water = create Water
earth = create Earth
mud = combine(water, earth)
show "Combined result:", mud
show "Material label:", mud.material
```

Expected output:

```text
Combined result: <material:mud#10>
Material label: Mud
```

Water and Earth currently combine into Mud. Read [Elements and Implemented Rules](../reference/ELEMENTS_AND_RULES.md) before assuming that another pair behaves the same way.

## 5. Make an area effect

An area effect is a single runtime operation. The Visualiser can draw a ring or expanding flash around it, but the radius and affected objects are decided by the runtime.

```mana
load geometry2d

practice_target = tgset:
    pos = geometry2d.point(4 m, 0 m)
    collision_radius = 0.35 m

spell pulse():
    result = mana.burst(
        energy = 900 J,
        radius = 1.2 m,
        position = geometry2d.point(4 m, 0 m)
    )
    incant result

release(pulse)
show "Target temperature:", practice_target.temp
```

Expected output:

```text
Target temperature: 294.05 K
```

## 6. React to a contact event

MANA event handlers run when the runtime emits the named event. For example, `impact` is raised by the current collision solver, not by a visual animation.

```mana
load geometry2d

when impact:
    show "MANA reported an impact."

projectile = create Fire
projectile.collision_radius = 0.2 m
velocity(projectile, 30 m/s)

target = tgset:
    hp = 100
    max_hp = 100
    defence = 0
    pos = geometry2d.point(1 m, 0 m)
    collision_radius = 0.2 m

advance_time(0.1 s, timestep=0.01 s)
show "Target health:", target.hp
```

Expected output:

```text
MANA reported an impact.
Target health: 95.5
```

Handlers execute as part of the MANA runtime. They are useful for reactions and simple sequencing, but they are not a parallel game loop.

## 7. Summon a known being

Summoning uses the plane and being records. The path must be open; if no valid route exists, the spell must not pretend the summon succeeded.

```mana
load planes
load summoning

planes.open_path("Wild Realm", "Mortal Plane")
griffin = summoning.bring("Griffin")
summoning.tame(griffin, "Ashwing")
show "Summoned being:", griffin.tame_name
summoning.send_back(griffin)
```

Expected output:

```text
Summoned being: Ashwing
```

This is a library operation, not a visual portal. The Visualiser may show a local summoning sigil, gathered light or mist. It does not show a portal or a map of the planes.

## 8. Run and watch it

Use the ordinary Run triangle in VS Code to execute a `.mana` file without a debugger. Use the eye-shaped **MANA: Visual** button only when you want to record and replay the spell. The Visualiser is a separate, optional extension.

For command-line replay, use:

```powershell
python mana.py --record fireball.jsonl examples/fireball_contact.mana
```

Then choose **MANA: Open Visualiser Recording**. The recording file is an internal replay format for the current viewer. It is not yet a public API for a game engine.

## Where to go next

- [Example index](../../../examples/README.md) — a list of the runnable programs by topic.
- [Language guide](LANGUAGE_GUIDE.md) — the language's syntax and conventions.
- [Function reference](../reference/FUNCTION_REFERENCE.md) — signatures, inputs and errors for built-ins.
- [Magic Visualiser guide](../tooling/MAGIC_VISUALISER.md) — installation, replay, limitations and troubleshooting.
- [Where MANA could be used](../foundations/FUTURE_USES_AND_ROADMAP.md) — what it can do now and possible future applications.
