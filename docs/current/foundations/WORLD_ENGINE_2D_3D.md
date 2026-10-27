# World Engine, Physics, 2D Geometry, and 3D Mathematics

**Page kind:** Explanation  

**Current source version:** v2.0.0

MANA has one primary world simulation and separate geometry/math libraries. The primary world runtime is 2D. The existence of a `vector3d` library does not change collision, motion, terrain, targeting, or gravity into three-dimensional simulation.

## 1. The simulated object

A world object is created through MANA syntax and managed by the runtime. It has runtime identity and a property dictionary. Common properties include:

| Property | Meaning |
|---|---|
| `mass` | Mass as a quantity, normally kg. |
| `volume` | Volume, normally m3. |
| `area` | Projected/contact area, normally m2. |
| `density` | Derived density based on mass/volume. |
| `pos` | 2D world position stored using a vector with z=0. |
| `vel` | Velocity, normally m/s. |
| `acc` | Acceleration, normally m/s2. |
| `force` | Recorded/applied force information, depending on operation. |
| `energy` | Derived physical-energy readout. |
| `temp` | Absolute temperature in kelvin. |
| `state` | State/material status such as `solid`, `powder`, or `burning`, where supported. |
| `material`, `kind` | Descriptive material/kind labels used by profiles and specialist libraries. |
| `anchored`, `anchor_pos` | Whether the object is held at a fixed position and the anchor coordinate. |
| `collision_radius`, `collidable`, `restitution` | Current 2D contact settings. |
| `hp`, `max_hp`, `defence`, `attack` | Optional combat/profile fields when set. |
| `integrity`, `integrity_break_energy`, `integrity_energy`, `stabilizers`, `collapsed_into` | Stability/collapse tracking in the current physics prototype. |
| `active`, `released`, `bound` | Runtime-managed state flags. |

Some values are read-only/runtime managed. Direct assignment to managed properties is rejected so that changes cannot bypass the ledger, integrity update, or other invariants. Use operations such as `heat`, `velocity`, `move`, `transform`, or the appropriate library controls.

## 2. World dimensions

Positions, velocities and acceleration used by the main runtime must have z=0. The core engine interprets x and y as the world plane. A vector with nonzero z is not accepted as a valid world movement/position vector. The target system and default physical motion use this same 2D model.

`geometry2d` is an optional calculation library for point/vector construction, direction, angles, intersections, closest points, polygon membership, line/segment intersection, circle calculations, and explicit aiming helpers. It gives more geometry functions to MANA programs but does not replace the world collision engine.

`vector3d` is an optional three-dimensional mathematics/physical-calculation library. It supports vectors, positions, velocities, accelerations, dot/cross products, projection/reflection, distances, angles, displacement, relativistic energy/momentum helpers, force/pressure calculations, z-planarity checks, and reading vector-valued object fields. It is useful for 3D calculations alongside the 2D world, not for 3D world motion.

## 3. Time advancement

`advance_time(duration[, timestep=..., gravity=...])` advances virtual time through substeps. The current defaults and safety limits are documented in the Physics Engine reference; the implementation currently uses a nominal 1/60 s step, limits individual substeps, caps total step count and estimated collision-pair checks, integrates persistent acceleration and optional gravity, resolves collisions, and processes timed/event callbacks.

Gravity defaults to zero unless supplied. An object does not fall simply because `advance_time` is called if no gravity/acceleration has been configured. This is intentional for a controllable simulation prototype.

## 4. Motion operations

Core operations include `move`, `velocity`, `accelerate`, `decelerate`, `push`, `pull`, `rotate`, `scale`, `reflect`, `anchor`, `unanchor`, `bind`, `dispel`, and universal controls under `mana`. These represent different behaviours:

- Position/displacement changes where an object is.
- Velocity sets its current motion.
- Acceleration/push/pull changes motion through the runtime's physics state.
- Anchoring holds a position; it is not the same as a force.
- Universal control expresses common intent such as toward, away, lift, hold, stop, or collect without requiring an element.

A single upward impulse is not a sustained levitation constraint. The current `mana.hold`/`mana.levitate` semantics rely on anchoring rather than a full continuous controller that calculates gravity compensation every step. This difference should remain explicit until a persistent control solver exists.

## 5. Collision model

Current world collision uses swept circle contacts in the x-y plane. Objects have a collision radius; if it is zero the runtime can derive an equivalent circle from projected area. A positive radius overrides that derivation. The `collidable` flag can turn contacts off without necessarily disabling movement, and `restitution` controls bounce behaviour within the implemented model.

The engine records `last_collisions()` and emits events such as `impact`, `collision`, and, for positive target HP damage, `damaged`. Impact damage is a prototype rule, not a complete combat system. Collision impulses are Newtonian while energy/momentum helper calculations can be relativistic, so collisions at near-light speed are not a validated relativistic regime.

The collision solver does not currently support arbitrary exact polygon terrain collision even though `geometry2d` can calculate polygon relationships. The geometry library and world solver have separate responsibilities.

## 6. Target-directed flight

Targeting is selected outside a spell using `tgset(...)` or `tgset: ...`. The spell body defines its behaviour; the world engine resolves target geometry and flight. Current targeted flight remains limited: it primarily handles eligible objects created by the spell, uses the innermost target context, has a documented fallback direction when the target is distance-only, and limits estimated flight duration. Check `PHYSICS_ENGINE.md` for the currently coded limits before relying on long-distance projectile behaviour.

These are current prototype restrictions, not a reason to place target-selection logic inside every `spell` declaration.

## 7. Integrity and collapse

The prototype calculates an integrity readout from effective stress energy and a material/element-specific breaking-energy threshold. The thresholds are tunable calibration constants. Stabilizers can raise the threshold or reduce relevant stress components, with duplicate labels counted once and diminishing benefits. Entropy and Death can reduce stability through the current rules.

At zero integrity the object becomes inactive and its tracked physical energy is transferred to a `ThermalRelease` carrier. `collapsed_into` exists on every world object and is `None` until collapse. This maintains energy provenance rather than deleting the object's energy. A full environmental propagation/damage model for released energy is not implemented.

## 8. 3D library: what it does and does not do

The `vector3d` library is namespaced so it can live alongside `geometry2d`. Its `position`, `velocity_vector`, and `acceleration_vector` constructors enforce appropriate dimensions; vector operations preserve/combine dimensions according to their math. For example, the dot product composes the input dimensions, and cross products return a vector with the multiplied dimensions.

`vector3d.planar(v)` returns a copy with z=0; it does not silently modify the original vector or move an object. `vector3d.is_planar(v)` checks the z component against tolerance. `vector3d.object_vector(object, field)` reads a vector-valued field like position or velocity from a world object. These bridge functions make 3D calculation results usable when they are genuinely planar, while preserving the rule that world positions and motions remain 2D.

## 9. Numerical and unit boundaries

Physics operations reject values that are dimensionally inconsistent, negative where positivity is required, or non-finite. A metre is not interchangeable with a second, an energy quantity with a force, or a Celsius absolute-temperature literal with a kelvin temperature increment. Vector normalisation of the zero vector is undefined and raises an error. Floating-point geometry is robust against avoidable intermediate overflow but is not arbitrary-precision mathematics.

## 10. Future engine work, not current promises

The optional Visualiser can replay JSONL records, but it is not a live world viewport or editor. Future engine work may add live observation, destructible terrain, persistent steering controllers, ongoing combustion, more material-specific thermal properties, richer creature behaviour, and a relativistically consistent collision solver. A full 3D world is not a goal for MANA 2.0; `vector3d` remains a calculation library. Do not describe any future capability as implemented until code and tests support it.
