# MANA, Mana, Matter, and Energy

**Page kind:** Explanation  

**Current source version:** v1.0.0

This document separates MANA's intended cosmology from the numerical model used by the current prototype. These are related, but they are not interchangeable descriptions.

## 1. The worldbuilding model of mana

**Established design:** mana is the omnipresent medium from which usable magical energy arises. Casters manipulate the mana that is present; they do not carry a finite, rechargeable mana battery. Matter and magical effects can be treated as configurations of mana, while MANA code determines how those configurations are changed.

Mana is not one of the four fundamental elements. Fire, Water, Earth, and Air are elemental modes/constituents; mana is the underlying medium used by magic. It therefore makes sense to use pure mana for a barrier, force pulse, or directed beam without assigning the effect a Fire/Water/Earth/Air identity.

The user's design also distinguishes Null from ordinary matter and energy: Null represents absence/opposition to mana, compared conceptually to anti-matter only as an analogy. **Null has not been implemented as a complete physical model.** The current element catalogue has `Void`, which must not silently be treated as an exact synonym for Null.

## 2. No finite stored mana pool

MANA does not ask a caster to enter a remaining-mana value before every spell. There is no general operation that subtracts a spell's cost from a stored personal reserve. A complex spell may have a greater mana-use *readout* than a simple spell, but that readout is not a finite resource bar and does not make the spell fail when it crosses a threshold.

Special channels such as a non-base elemental plane or the Underworld have an invocation/permission rule. Invocation is permission to draw or use the channel, not a charge paid from a finite mana pool.

## 3. Numerical conventions in the prototype

The prototype currently uses two independent conversion conventions:

| Operation | Current convention | Meaning |
|---|---|---|
| Matter manifestation | `1 mana` corresponds to `10 kg` of matter | A project-defined conversion used when reporting manifestation cost. |
| Explicit mana-to-energy mapping | `1 mana` corresponds to `1 J` | A separate conversion for operations that explicitly map mana to energy. |

These multipliers are not derived from each other. In particular, the prototype does not infer rest-mass energy through `E = mc²`. They are implementation rules, not claims about SI physics.

Creating an object may report a manifestation cost based on its mass. The initial thermal and kinetic state is tracked separately. Changes such as heating or changing velocity can produce an equivalent mana-cost readout based on the energy change, but do not spend a stored resource pool.

## 4. Physical energy bookkeeping

The world engine tracks energy in an internal ledger. The runtime keeps input/output entries and per-object derived quantities. The central object readout is currently:

`energy = thermal_energy + kinetic_energy + released_energy`

Thermal energy is currently calculated from mass, the prototype's default specific heat, and absolute temperature. Kinetic energy and momentum are calculated from mass and velocity through the physics helpers. These values are derived/read-only through the language rather than arbitrary numbers that can be assigned without validation.

The ledger distinguishes energy entering the simulated world, leaving it, changing form, and being transferred internally. A transfer should have matching source/destination accounting; it must not appear as new energy on both ends. Unabsorbed pure-mana effect energy is recorded as environmental/unabsorbed energy rather than silently discarded.

### Creation and composition

- `create Fire`, `create Water`, `create Earth`, and `create Air` create objects of the four base types.
- `create Mana` creates a pure-mana object/construct type where allowed by the current runtime.
- Creating a non-base plane element requires the appropriate `planes` permission.
- `combine(a, b)` marks source objects inactive and creates a composite whose energy derives from its sources, so the same source energy is not counted twice.
- `separate(composite)` restores the original source objects.
- `split(object, parts)` divides the object's mass, thermal/kinetic state, released energy, and provenance across the resulting pieces.
- Element interactions such as Fire/Water cancellation can produce a `ThermalRelease` carrier. This is an energy-bearing record, not energy destruction.

There is no implemented general matter-destruction operator that converts arbitrary matter directly into energy. `Null`-based erasure is not a substitute for this missing operation.

## 5. Temperature rules

The current defaults are:

| Base type | Starting temperature |
|---|---:|
| Fire | 1000 K |
| Water | 273.15 K |
| Earth | 293.15 K |
| Air | 288.15 K |

The current default specific heat is `1000 J/(kg·K)` for all objects. It is not yet material-specific.

`heat(object, delta)` adds a non-negative temperature change; `cool(object, delta)` subtracts one and does not go below absolute zero. Celsius is accepted only as an absolute-temperature literal converted to kelvin. For example, `20 C` represents `293.15 K`; it is not a temperature increment for `heat()` or `cool()`.

Heating a combustible object may move its state to `burning` when its configured ignition threshold is crossed. This is currently a state transition plus an event, not a full combustion simulation with smoke, consumed fuel, flame spread, and generated heat over time.

## 6. Pure-mana effects and universal control

The built-in lowercase `mana` namespace exposes three pure-mana effects:

- `mana.form(...)` creates a temporary pure-mana construct with recorded effect energy and collision properties.
- `mana.burst(...)` applies a radial pulse to eligible nearby objects, sharing effect energy and recording any unabsorbed remainder.
- `mana.emit(...)` sends an energy ray through a direction/range and applies heat to eligible objects in the beam.

Default values exist to make basic uses concise. Their exact parameters and units are in [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md); do not infer that every shape has full mesh/collision support from the `shape` label.

The same namespace also offers element-independent object control. `toward`, `away`, `lift`, `hold`, `stop`, `release_control`, and `collect` use the shared runtime and physics properties. They are not elemental conversions. A one-time lift force is not the same thing as a sustained altitude controller; current `levitate`/`hold` behaviour is an anchored-position abstraction.

## 7. Planar energy versus spell consumption

`planes.send_energy(...)` records an energy transfer across an open pathway. The number measured in joules is necessary for a ledger entry, but the transfer is not a finite mana budget. The `kind` label classifies what is being recorded, such as an elemental channel or a `Necro:` accounting entry.

The current necromancy implementation records a fixed internal marker of `100 J` per reanimation. This value is an accounting marker, not a claim that an animated skeleton literally needs only 100 J of physical energy, nor an input the caster must supply. It does not add the marker to the corpse's physical energy. This number is an implementation choice that can be revised separately from the mana cosmology.

For a custom spell such as a skeleton-summoning spell or army-creation spell, spell logic should express which constructs are made and controlled. A built-in library must not demand a user-entered mana budget just because the spell is complex.

## 8. Limits and unresolved physical work

The current physics model uses finite floating-point quantities, a 2D world, simplified material defaults, circle-based contact, and Newtonian collision impulses. Relativistic energy/momentum helper functions are available, but near-light collision response is not a validated relativistic simulation. Integrity thresholds and stabilizer strengths are calibration constants. Environmental propagation of a released energy carrier is not a complete field simulation.

See [Energy Model](../physics/ENERGY_MODEL.md), [Physics Engine](../physics/PHYSICS_ENGINE.md), and [Implementation Status](IMPLEMENTATION_STATUS.md) for implementation-level detail.
