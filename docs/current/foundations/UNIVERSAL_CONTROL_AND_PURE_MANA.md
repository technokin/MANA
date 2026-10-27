# Universal Control and Pure-Mana Effects

**Page kind:** Explanation  

**Current source version:** v2.0.0
**Related reference:** [Pure Mana and Universal Control API](../libraries/MANA_LIBRARY.md)

This chapter explains the model behind the lowercase `mana` library. It is about *how to think about* the operations; use the library reference for exact signatures, defaults, optional parameters, and errors.

## 1. Universal control is not an element

A caster should not need Air mana simply to move an object, Earth mana to push a rock, or Fire mana to give an object velocity. Existing matter is already present in the world. Manipulating it is a general operation, separate from producing or drawing elemental mana.

The runtime already includes operations such as `move`, `velocity`, `accelerate`, `decelerate`, `push`, `pull`, `aim`, `anchor`, `unanchor`, `transform`, `compress`, `expand`, `split`, `combine`, and `separate`. The `mana` namespace adds a more accessible control surface around shared motion/physics state. It should not create a second unrelated physics model.

## 2. Three motion concepts

These are different actions and must not be confused:

1. **Position change:** `move` changes where an object is.
2. **Force/motion change:** `push`, `pull`, `velocity`, acceleration, `mana.toward`, `mana.away`, or `mana.lift` affect movement through the current physics model.
3. **Maintained control:** `mana.hold` and `mana.levitate` use an anchored position abstraction. They are not yet a general feedback-controller solver that calculates a force against gravity at every timestep.

`mana.stop(object)` sets motion to zero and converts the object's kinetic energy to thermal energy, preserving the tracked total. `mana.release_control(object)` releases the hold/anchor; it does not erase energy. These operations exist for any eligible object, not only magical constructs.

## 3. Automatic destinations and `tgset`

When a mana control function accepts an optional destination, the runtime may use the active `tgset(target):` context. This keeps target selection out of the spell body. Some operations can fall back to the caster/runtime origin if no target context is active; exact behaviour differs by operation and is documented in the library reference.

A default origin is a usability default, not proof that an in-game caster object or camera currently exists. In the terminal prototype the caster origin starts at the coordinate origin unless provided by the host runtime. The default effect position may therefore be a predictable offset along +X.

## 4. Pure-mana constructs

The current lowercase namespace exposes three core effects:

- **`mana.form(...)`** creates a temporary energy-bearing pure-mana object. The construct can be given velocity and interact with world objects using the current collision engine.
- **`mana.burst(...)`** applies a radial pulse to eligible nearby objects. Available energy is distributed according to the current implementation; unabsorbed energy is recorded rather than silently deleted.
- **`mana.emit(...)`** sends an energy beam/ray along a direction and range. It applies effects to eligible objects intersecting its simplified beam bounds.

Pure mana does not acquire a Fire, Water, Earth, or Air label simply because it has a visible shape. A mana sphere can be a projectile; a barrier can use an anchored collision bound; a radial burst can model a shockwave-like impulse/energy event. These are composable primitives, not separate hard-coded commands for every possible named spell.

## 5. Energy is accounted for, not charged to a finite caster pool

Pure-mana effects record input energy and equivalent usage in the runtime ledger. This records what the effect does. It does not mean the caster has a finite inventory that runs out after a fixed number of spells. When a projectile strikes a target, the current implementation records the transfer to the target as heat. When a burst does not transfer all energy to eligible objects, the remainder is recorded as unabsorbed/environmental energy.

The exact physical solver remains a prototype. Energy bookkeeping helps keep cause and effect inspectable, but it does not make the model a complete electromagnetic field solver or a general-purpose heat-flow simulation.

## 6. Composition examples

### A pure-mana projectile

```mana
orb = mana.form("sphere", energy=750 J, radius=0.15 m)
velocity(orb, 25 m/s)
show orb.energy
```

Expected output:

```text
750 J
```

### A directed beam

```mana
load geometry2d
beam_result = mana.emit(power=500 W, duration=2 s, position=geometry2d.point(3 m, 0 m))
show beam_result.energy_j
```

Expected output:

```text
1000.0
```

### Pulling an existing object using the selected target

```mana
load geometry2d
stone = tgset:
    material = "Rock"
    mass = 2 kg
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

### Moving a set of objects together

Collection is a multi-object operation. A program can build a list of already-known objects and then call the collection function once, subject to its argument and duration rules. It does not discover arbitrary terrain matter; terrain extraction is not implemented.

## 7. Material profiles, not special-case spell names

`tgset` records can describe wood, rock, powderable solids, combustion settings, mass, volume, position, shape, and other supported fields. This is a way to configure a world object or target profile, not a new programming-language type for every physical material.

A wooden object can be heated and enter the `burning` state if its material settings and ignition threshold allow it. The current engine does not continue a combustion simulation: there is no full fuel-consumption, smoke, propagation, or fire-spread model. `transform(object, "powder")` currently retains the material's mass and tracked energy on an aggregate powder object rather than spawning thousands of individual particles.

## 8. Limits to preserve

- World object positions and collisions remain 2D.
- `shape` labels do not create exact arbitrary mesh collision geometry.
- Barriers do not yet have a durability/maintenance model based on their stored energy.
- `hold`/`levitate` are anchored-position abstractions, not a full force-control loop.
- Material terrain extraction is not implemented.
- Pure-mana output and ledger readouts do not provide a finite-mana resource bar.

For exact API semantics and all argument errors, use the [MANA library reference](../libraries/MANA_LIBRARY.md) and [Function Reference](../reference/FUNCTION_REFERENCE.md).
