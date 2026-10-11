# MANA Troubleshooting

**Page kind:** How-to  

**Version:** 1.0.0
This page lists common mistakes and how to correct them. It describes the current prototype; it does not promise behaviour that is not implemented.

## 1. A template call runs no magic

This is expected:

```mana
spldef e_ball(element):
    ball = create element
    shape(ball, circle)
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
```

Expected output:

```text
(no output)
```

`e_ball(Fire)` creates a configured spell instance. It does not create `ball` yet. Use `post(fire_ball)` to preview or `release(fire_ball)` to commit the spell's effects.

## 2. A template accepts only `element`

Valid:

```mana
spldef elemental_ball(element):
    ball = create element
    velocity(ball, 300 m/s)
    incant ball
```

Expected output:

```text
(no output)
```

**Expected failure (intentionally invalid):** this demonstrates the unsupported two-parameter spell-template syntax.

```mana
spldef elemental_ball(element, speed):
    skip
```

Put settings such as velocity, shape, temperature change, and duration in the definition body. Change an existing operation using `tune`.

## 3. Tuning reports that an operation does not exist

`tune` must match an operation call that already exists in the definition, including the internal target variable.

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

The operation is `velocity`, and its target variable is `ball`. Tuning `flame` instead of `ball`, or tuning an operation absent from the definition, raises an error.

## 4. Tuning reports ambiguity

If the definition contains two `velocity(ball, ...)` calls, MANA cannot know which one you intend to change. It raises an ambiguity error. Use different target variables when operations should be independently tunable, or keep only one such operation for that target.

## 5. `post` or `release` rejects an assignment

They are execution commands, not value-producing expressions in MANA source.

Correct, standalone example:

```mana
spldef e_ball(element):
    ball = create element
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
[POST fire_ball] energy input: 45000 J (velocity; spell work)
[POST fire_ball] ball.energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fire_ball] ball.integrity: 0.992062994740159 -> 0.9919456821384532 (velocity)
[POST fire_ball] ball.integrity_effective_energy_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fire_ball] ball.integrity_energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fire_ball] ball.integrity_last_score_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fire_ball] ball.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fire_ball] ball.mana_cost: 0.1 -> 45000.10000003379 (velocity)
[POST fire_ball] ball.mana_used: 0.1 -> 45000.10000003379 (velocity)
[POST fire_ball] ball.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fire_ball] ball.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fire_ball] spell completed
[POST fire_ball] mana cost: 45000.1 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

**Expected failure (intentionally invalid):** `release` is a command and cannot be assigned.

```mana
result = release(fire_ball)
```

`post` prints the trial report. The host runtime can inspect its `SpellResult` record in tests and tools, but MANA code cannot assign that record.

## 6. `show` does not display a spell trace

`show` prints its arguments. Use `post(spell)` when you want the step-by-step preview trace.

```mana
spldef e_ball(element):
    ball = create element
    velocity(ball, 300 m/s)
    incant ball

fire_ball = e_ball(Fire)
show fire_ball
post(fire_ball)
```

Expected output:

```text
<spell-instance:fire_ball (Fire)>
[POST fire_ball] inputs: element=Fire
[POST fire_ball] energy input: 1e+06 J (create Fire; matter creation (initial state))
[POST fire_ball] created Fire (Fire, 1 kg; create Fire)
[POST fire_ball] energy input: 45000 J (velocity; spell work)
[POST fire_ball] ball.energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fire_ball] ball.integrity: 0.992062994740159 -> 0.9919456821384532 (velocity)
[POST fire_ball] ball.integrity_effective_energy_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fire_ball] ball.integrity_energy: 1e+06 J -> 1.045e+06 J (velocity)
[POST fire_ball] ball.integrity_last_score_j: 1000000.0 -> 1045000.0000000338 (velocity)
[POST fire_ball] ball.kinetic_energy: 0 J -> 45000 J (velocity)
[POST fire_ball] ball.mana_cost: 0.1 -> 45000.10000003379 (velocity)
[POST fire_ball] ball.mana_used: 0.1 -> 45000.10000003379 (velocity)
[POST fire_ball] ball.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(300, 0, 0) [kg*m/s] (velocity)
[POST fire_ball] ball.vel: Vector3(0, 0, 0) [m/s] -> Vector3(300, 0, 0) [m/s] (velocity)
[POST fire_ball] spell completed
[POST fire_ball] mana cost: 45000.1 mana
[POST fire_ball] created: ball (Fire, 1 kg)
```

The first line prints the value/reference; the second runs a trial and displays what happens.

## 7. `skip` and `incant`

- `skip` does nothing and is useful for a placeholder block. Write `skip`, not `skip()`.
- `incant value` supplies a value to the caller and exits the current definition.
- Use `incant value` to finish a definition and supply its result. A word outside the MANA keyword table is not identified as a keyword; it does not gain special control-flow behaviour.

## 8. Units or physics values are rejected

MANA checks dimensions. Use a velocity such as `300 m/s`, a temperature increment such as `500 K`, and a distance such as `20 m`. A temperature is not a speed, and a scalar speed is not the same thing as a direction vector.

## 9. Run a file or the test suite

From the project root:

```powershell
python mana.py examples\fireball.mana
python -m pytest -q
```

If `python` does not resolve on Windows, use the installed Python executable's full path or the Python launcher (`py`) if available. Python is required for this prototype unless you build the optional standalone executable.

## 10. VS Code extension is not the interpreter

Install `installers/vscode/mana-language-1.0.0.vsix` through **Extensions → Install from VSIX**. The extension supplies editor support; run MANA using the command in Section 9 or the project task. The root `.vscode/tasks.json` is workspace configuration, not part of the VSIX extension.
