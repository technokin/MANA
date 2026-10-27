# MANA Physics Engine — v2.0.0

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

`advance_time(duration, timestep=..., gravity=...)` advances virtual time in deterministic substeps and then advances timers/event handlers. The built-in `world` namespace stores the global gravity, restitution, friction, air density, drag, thermal-exchange, phase-change and wetting defaults used by the engine.

| Setting | Current behaviour |
|---|---|
| Default step | `1/60 s` |
| Maximum step | `0.1 s` |
| Maximum steps per call | `100,000` |
| Maximum swept-AABB candidate-pair checks per call | `20,000,000` |
| Broad-phase cells per collider | `2,048` before large-sweep fallback |
| Total cell memberships per substep | `2,000,000` |
| Default gravity | Configurable through `world.configure`; zero initially |
| Default restitution | `0.2`, unless overridden on an object |
| Default contact friction | `0.35`, unless overridden on an object |
| Default air density | `1.225 kg/m3` |
| Failure handling | A failed advance restores the state from before the call |

The final substep may be shorter than the requested timestep so the requested duration is reached within floating-point tolerance. Smaller steps improve timing resolution but increase cost. The broad phase indexes each collider's swept bounds in a spatial hash, then runs the swept-circle narrow phase only for candidate pairs whose bounds overlap. This avoids testing every pair in a sparse scene, while dense scenes remain potentially quadratic. Large swept bounds use a scene-scan fallback rather than expanding into unbounded grid cells. Exceeding the candidate-work or cell-index budget raises a MANA runtime error and rolls back the entire `advance_time` call.

Global gravity is an explicit 2D acceleration vector. Configure it once with `world.configure(gravity=...)`; a `gravity=...` argument to `advance_time` overrides it for that call:

```mana
load geometry2d
advance_time(1 s, timestep=0.01 s, gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
```

Expected output:

```text
(no output)
```

The global setting persists until `world.configure()` changes it or `world.reset()` restores defaults. A per-call `gravity=` argument does not overwrite the global setting. The speed limit `c` is checked as velocities are integrated.

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

The integrator uses constant acceleration over each substep: position is updated from the prior velocity and acceleration, then velocity is updated. The engine recalculates energy and momentum readouts from the new state. Energy changes caused by configured acceleration and explicit gravity are recorded in the energy ledger. Wind work and atmospheric thermal exchange are also external energy transfers. During `advance_time`, continuous per-object transfers are accumulated exactly in the input/output counters and represented by compact per-operation ledger summaries, preventing a long-running world from retaining one ledger dictionary per object per tick. Discrete spell work and collision events remain individually traceable.

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

The broad phase indexes conservative swept AABBs (start-to-end bounds expanded by each collision radius), so fast projectiles are considered along their entire path. The narrow phase sweeps each circle's relative path across the timestep and estimates the first contact time, reducing high-speed tunnelling. Response uses a Newtonian normal impulse with mass, anchored status, and restitution, followed by a Coulomb-style tangential friction impulse capped by `mu * normal_impulse`. A one-pass overlap correction separates intersecting circles, but this is not a full constraint solver. Translational kinetic-energy loss from contact is added to thermal energy; spin and rolling friction are not modelled.

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

Inside this block, `velocity(projectile, 300 m/s)` uses the selected target's position to calculate the direction automatically. `post(spell)` runs the spell and targeted flight in an isolated trial, reports movement/collision/damage, then restores the world. `post(spell, visual)` records that hypothetical performance for the Visualiser without committing it; `post(spell)` remains the text default. `release(spell)` runs the same logic and commits the world changes. Neither requires the programmer to calculate direction vectors or travel time for ordinary targeted projectiles.

A target profile that defines only `distance` is positioned along the default forward (+X) axis in this headless prototype; explicit `pos` takes precedence. A future world engine should supply real target positions. An explicitly provided velocity vector overrides automatic target direction.

## 7. Current limitations

1. **2D only for world motion and collisions.** Non-zero z world movement is rejected. Three-dimensional vector calculations remain available in the physics library layer.
2. **Approximate circle geometry.** There are no exact polygon edges, wall colliders, or mesh-based contacts yet.
3. **Newtonian collision response.** Kinetic energy and momentum readouts have relativistic formulas, but collisions near `c` are not handled by a relativistic collision solver.
4. **Simplified contact friction and air drag.** Coulomb-style sliding friction and wind-relative air drag are implemented, but there is no rolling resistance, torque/angular-momentum solver, full fluid flow, or lift model. The spatial hash improves sparse-scene scaling; scenes with many overlapping swept bounds can still approach quadratic collision work and will hit configured safety budgets.
5. **Limited thermal and material laws.** Ambient heat exchange and catalogue-driven melting/boiling state changes are implemented; combustion, pressure waves, latent heat, partial melting, chemical reactions and full phase equilibrium are not.
6. **Prototype damage rule.** The joules-per-HP constant, defence and resistance formula need future tuning.
7. **Integrity and breakage remain unimplemented.** Stabilizers and uncontrolled collapse must be designed separately.
8. **Gravity is configured, not astronomical.** Uniform 2D gravity can be persisted globally or overridden per advance; there is no planetary field, orbital mechanics or spatially varying gravity.

Global settings and the actual implemented law set are inspectable with `world.current()` and `world.laws()`. Any future renderer must display the state calculated here; it must not decide whether physics succeeds. Projectile motion uses `velocity()`; target selection remains outside the spell in `tgset(target):`. `geometry2d` provides optional calculation and direction helpers, not a separate launch operation.
