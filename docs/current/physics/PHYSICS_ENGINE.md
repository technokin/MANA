# MANA Physics Engine — v1.0.0

**Page kind:** Explanation  

This document describes the primary **2D world engine**. MANA's separate 3D vector calculations remain available as library-style math; they do not make the simulated world three-dimensional. The engine is headless: graphics display its results but never decide them.

## 1. World dimensions and 3D library calculations

The primary world is the x-y plane. Position, velocity, acceleration, force, object direction, and supplied world gravity must have `z = 0`. A vector with non-zero z can still be created and used for standalone vector calculations, but it cannot move a world object or be used as world gravity.

```mana
load geometry2d
stone = create Earth
velocity(stone, geometry2d.direction(1, 0) * 10 m/s)
advance_time(1 s, timestep=0.01 s, gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
show stone.pos
show stone.vel
```

Expected output:

```text
Vector3(10, -4.905, 0) [m]
Vector3(10, -9.81, 0) [m/s]
```

`geometry2d.direction(x, y)` is available after `load geometry2d` for explicit world vectors. `vector3d.direction(x, y, z)` is available after `load vector3d` for 3D calculations such as `vector3d.magnitude(vector3d.direction(1, 2, 3))`. A non-zero z vector used with `velocity`, `accelerate`, `move`, `geometry2d.aim`, `reflect`, `anchor`, direct world-vector assignments, or `advance_time(..., gravity=...)` raises `PhysicsErrorML` instead of being silently flattened.

The underlying calculation utilities retain their 3D capabilities through the optional `vector3d` namespace. MANA source supports `load geometry2d` and `load vector3d`; user-authored `.manalib` packages can be built using the [Library Builder](../libraries/LIBRARY_BUILDER.md).

## 2. The physics clock

`advance_time(duration, timestep=..., gravity=...)` advances virtual time in deterministic substeps and then advances timers/event handlers.

| Setting | Current behaviour |
|---|---|
| Default step | `1/60 s` |
| Maximum step | `0.1 s` |
| Maximum steps per call | `100,000` |
| Maximum collision-pair checks per call | `20,000,000` |
| Default gravity | Zero; no planet is assumed |
| Failure handling | A failed advance restores the state from before the call |

The final substep may be shorter than the requested timestep so the requested duration is reached within floating-point tolerance. Smaller steps improve timing resolution but increase cost. Collision checks are pairwise; exceeding the pair-check budget raises an error and rolls back the entire `advance_time` call.

Gravity is an explicit 2D acceleration vector:

```mana
load geometry2d
advance_time(1 s, timestep=0.01 s, gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
```

Expected output:

```text
(no output)
```

Gravity applies only to that call. It is not stored as a global planetary field. The speed limit `c` is checked as velocities are integrated.

## 3. Motion and forces

World object properties are `pos` in metres, `vel` in m/s, and `acc` in m/s², all constrained to the x-y plane.

- `velocity(object, scalar)` sets speed along positive x by default. Inside `tgset(target):`, the selected target is used to calculate the direction automatically; a vector remains available for explicit low-level control.
- `accelerate(object, scalar_or_vector)` configures persistent acceleration.
- `decelerate(object, scalar_or_vector)` configures acceleration opposite the supplied vector.
- Direct assignment to `object.acc` configures persistent acceleration.
- `push` and `pull` are one-second action impulses. Their stored acceleration is a record of the action and is not integrated again on later clock steps.
- `move` directly displaces an object; it is not a force simulation.
- `anchor` makes an object immovable to the motion and collision solvers.
- `rotate` currently stores a planar angle in radians; it does not yet couple rotation to torque or collision response.

The integrator uses constant acceleration over each substep: position is updated from the prior velocity and acceleration, then velocity is updated. The engine recalculates energy and momentum readouts from the new state. Energy changes caused by configured acceleration and explicit gravity are recorded in the energy ledger.

## 4. 2D collision bounds

The primary world uses **circles**, not spheres. Current shape labels such as `wall`, `cone`, `polygon`, and `circle` are semantic labels; they do not create exact geometry yet.

Each object has a projected `area` in square metres, defaulting to `1 m2`. If `collision_radius` is zero, the engine derives the circle radius from equal projected area:

\[
r = \sqrt{\frac{A}{\pi}}
\]

For example:

```mana
stone = create Earth
stone.area = 3.141592653589793 m2  # equivalent circle radius: 1 m
stone.collision_radius = 0 m       # use area-derived bound
```

Expected output:

```text
(no output)
```

A positive `collision_radius` in metres explicitly overrides `area`. An area of zero and no explicit radius produces a non-colliding point. `collidable = false` disables contact checks without disabling movement. Area determines the 2D collider footprint; volume remains a material property for density/energy and for 3D library calculations.

The detector sweeps each circle's relative path across the time step and estimates the first contact time, reducing high-speed tunnelling. Response uses a Newtonian normal impulse with mass, anchored status, and restitution. A one-pass overlap correction separates intersecting circles, but this is not a full constraint solver.

## 5. Impact energy, heat, and target damage

At impact, the solver calculates the effective contact mass and normal impact energy. The kinetic energy lost by the response is transferred to the objects as thermal energy, split by mass share using the current prototype specific heat of `1000 J/(kg·K)`.

Collision records include both object labels, estimated normal impact energy, energy converted to heat, and estimated contact time. `last_collisions()` returns recent summaries; the runtime retains up to 1,000 records.

Only a collision with exactly one target profile produces automatic HP damage. The prototype formula is:

```text
base_damage = impact_energy_j / 100
resisted_damage = base_damage * (1 - elemental_resistance)
final_damage = max(0, resisted_damage - defence)
```

Resistance is clamped to `[0, 1]`. `defence` is a flat HP-like reduction. `100 J per HP` is a tunable balance constant, not a universal physical law. HP never drops below zero. Contacts emit `impact` and `collision`; positive HP damage also emits `damaged`.

## 6. Targeted casting, `post`, and `release`

Target choice belongs outside a spell definition. A block such as `tgset(npc): release(fireball)` temporarily selects a target for the casting action. The spell itself only defines its own behaviour; it does not contain target-selection logic.

Inside this block, `velocity(projectile, 300 m/s)` uses the selected target's position to calculate the direction automatically. `post(spell)` runs the spell and targeted flight in an isolated trial, reports movement/collision/damage, then restores the world. `release(spell)` runs the same logic and commits the world changes. Both accept the spell name only. Neither requires the programmer to calculate direction vectors or travel time for ordinary targeted projectiles.

A target profile that defines only `distance` is positioned along the default forward (+X) axis in this headless prototype; explicit `pos` takes precedence. A future world engine should supply real target positions. An explicitly provided velocity vector overrides automatic target direction.

## 7. Current limitations

1. **2D only for world motion and collisions.** Non-zero z world movement is rejected. Three-dimensional vector calculations remain available in the physics library layer.
2. **Approximate circle geometry.** There are no exact polygon edges, wall colliders, or mesh-based contacts yet.
3. **Newtonian collision response.** Kinetic energy and momentum readouts have relativistic formulas, but collisions near `c` are not handled by a relativistic collision solver.
4. **No friction, air resistance, fluid simulation, rolling, torque, or angular-momentum solver.** Rotation is not coupled to impacts.
5. **No combustion, pressure-wave simulation, or complete phase-change model.** Operations such as `compress`, `expand`, and `transform` are not yet full material solvers.
6. **Prototype damage rule.** The joules-per-HP constant, defence and resistance formula need future tuning.
7. **Integrity and breakage remain unimplemented.** Stabilizers and uncontrolled collapse must be designed separately.
8. **Gravity is caller-supplied.** Automatic planetary/orbital gravity is not implemented.

Any future renderer must display the state calculated here; it must not decide whether physics succeeds. Projectile motion uses `velocity()`; target selection remains outside the spell in `tgset(target):`. `geometry2d` provides optional calculation and direction helpers, not a separate launch operation.
