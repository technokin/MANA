# Spell Templates, Instances, and Tuning

**Page kind:** Explanation  

**MANA v2.0.0 — focused reference**

This document explains the difference between defining a spell, creating a configured spell instance, changing a spell's settings, and firing it.

## 1. Define the reusable behaviour

```mana
spell e_ball(element):
    ball = create element
    shape(ball, circle)
    heat(ball, 500 K)
    velocity(ball, 300 m/s)
    incant ball
```

Expected output:

```text
(no output)
```

The parameter is only for element selection. It can be one of `Fire`, `Water`, `Earth`, or `Air`. Speed, temperature change, shape, duration, and other settings are written in the body and later changed with `tune`.

`create element` resolves the selected element type at runtime. It creates the object only when the spell body actually runs.

## 2. Create separate configured instances

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

This does not run the spell body. It creates four separate configured instances based on the same definition. Each instance has its own settings.

`e_ball(Fire)` must take exactly one fundamental element and should be assigned to a name. Calls such as `e_ball(Fire, 300 m/s)` are invalid because operation settings are not parameters.

## 3. Change one existing operation

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

Read the first statement as: inside the `fire_ball` template instance's definition, find the `velocity` operation that targets the source variable `ball` and replace its second argument with `600 m/s`.

The selected instance uses 600 m/s and a 1500 K temperature increment on later executions. Other instances, such as `earth_ball`, keep their original values.

### How targeting works

The second part of the left-hand side identifies the operation name. The first item on the right identifies the variable used as the operation's first argument. MANA requires exactly one match in the spell definition.

```mana
spell twin_orb(element):
    near = create element
    far = create element
    velocity(near, 100 m/s)
    velocity(far, 200 m/s)
    incant near

orbs = twin_orb(Fire)
tune(orbs.velocity) = far, 900 m/s
tune(orbs.velocity) = near, 500 m/s
```

Expected output:

```text
(no output)
```

This is unambiguous because `near` and `far` identify separate source-level targets. If the same operation and target pair appears more than once in the definition, MANA reports an ambiguity error rather than guessing.

## 4. Preview and fire

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

- `post` executes a trial and prints the execution trace. The trial's world mutations are rolled back.
- `release` executes and commits the spell's changes.
- Both commands take only one argument: the name of a definition with no parameters, or a configured spell instance.
- Neither command can be assigned to a variable in MANA source. The execution record is available to the interpreter's host API and automated tests.

Tuning is configuration, not world state. Therefore `post` does not undo tuning.

## 5. `show`, `incant`, and `skip`

```mana
spell e_ball(element):
    ball = create element
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
show "Chosen instance:", fire_ball
```

Expected output:

```text
Chosen instance: <spell-instance:fire_ball (Fire)>
```

`show` prints its values; it does not fire spells or print a trace. `post` is responsible for the execution report.

Inside a definition, `incant ball` supplies the `ball` object as the definition's result and exits the body. It is not a function call and supplies the value without a separate return keyword.

`skip` does nothing and is useful for an unfinished block:

```mana
spell placeholder():
    skip
```

Expected output:

```text
(no output)
```

## 6. Errors you should expect

| Example problem | Expected response |
|---|---|
| `e_ball(Fire, 300 m/s)` | Wrong number of template arguments |
| `e_ball(Life)` | `MagicErrorML`: element selector must be one of the four base elements |
| `tune(fire_ball.gravity) = ball, 9` | `TypeErrorML`: operation does not exist in this spell |
| `tune(fire_ball.velocity) = flame, 900 m/s` | `TypeErrorML`: no matching target/operation |
| Same operation/target pair appears multiple times | `TypeErrorML`: tuning is ambiguous |
| `tune(e_ball.velocity) = ball, 900 m/s` before creating an instance | `TypeErrorML`: tune requires a configured spell instance |
| Wrong units supplied to an existing operation | `UnitErrorML` when the tuned spell executes |

## 7. Current boundaries

The first implementation tunes the second positional argument of a built-in operation call. The target is identified by the source-level name used as that operation's first positional argument. Named-argument operations, property-path tuning, and visual tuning controls are not part of this version.
