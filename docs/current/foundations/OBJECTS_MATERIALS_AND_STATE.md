# World Objects, Material Profiles, and State

**Page kind:** Explanation  

**Current source version:** v2.0.0
**Related references:** [Function Reference](../reference/FUNCTION_REFERENCE.md), [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md), [World Weather and Matter](../libraries/WORLD_WEATHER_AND_MATTER.md), [Physics Engine](../physics/PHYSICS_ENGINE.md)

This document explains what MANA manipulates. A world object is not simply a material label: it carries physical properties, derived quantities, active/inactive status, and bookkeeping provenance.

## 1. World object versus descriptive record

A **world object** participates in the active simulation. It can have mass, volume, material, position, velocity, temperature, shape label, collision settings, physical energy, integrity, and optional behaviour/combat fields. The physics engine advances eligible objects and resolves contacts.

A **profile/record** provides data for a system. A `tgset` declaration may define an object or target profile depending on the supplied fields and use. A **being record** is a catalogue entry with a name and home plane; it does not move until `summoning.bring()` manifests it as a world object. A **plane record** has identity/category/path relationships; it is not a physical object in the world solver.

## 2. Creating and configuring an object

The central creation statement uses a type selector:

```mana
stone = create Earth
```

The four base element selectors are Fire, Water, Earth, and Air. Creating a non-base plane-backed type requires the relevant invocation permission in the current implementation. Pure mana is selected through uppercase `Mana` where supported; lowercase `mana` is the operation namespace.

An object may be configured with supported properties, but fields controlled by the engine should not be assigned arbitrarily if doing so would skip energy, integrity, unit, or lifecycle validation. Use physical operations such as `heat`, `cool`, `velocity`, `move`, `transform`, and the `mana` control operations when they represent the requested change.

## 3. `tgset` material definitions

A material profile can be written as:

```mana
load geometry2d
stick = tgset:
    kind = "stick"
    material = "Wood"
    shape = line
    state = "solid"
    mass = 0.5 kg
    volume = 0.001 m3
    pos = geometry2d.point(2 m, 0 m)

rock = tgset:
    kind = "rock"
    material = "Rock"
    shape = circle
    state = "solid"
    mass = 2 kg
    volume = 0.001 m3
    pos = geometry2d.point(4 m, 0 m)

heat(stick, 300 K)
transform(rock, "powder")
show stick.state
show rock.state
```

Expected output:

```text
burning
powder
```

The exact accepted fields and validations are part of the language/runtime reference. Important fields include mass, volume, area, density (derived), position, velocity/acceleration, temperature, material, state, kind, shape, collision radius, restitution, anchoring, combustible, powderable, ignition temperature, integrity-related values, and optional being/combat values. Not every property is directly writable.

## 4. Material behaviour in the current prototype

Material names can infer some defaults. Common combustible labels (including Wood and related plant/fabric materials) may receive `combustible = true` unless explicitly overridden. A default ignition threshold exists. When a heat operation crosses the threshold, the material may change to the `burning` state and emit `object_ignited`.

Powdering a supported solid changes its state and preserves the represented mass and tracked energy on the aggregate object. It does not yet create a spatial cloud of individual powder particles. Material changes are not a full chemistry or phase-equilibrium solver. When `world.phase_changes_enabled` is true, known catalogue materials can switch their `state` as temperature crosses registered melting/boiling points; latent heat, fractional phases, pressure-dependent phase diagrams and reaction kinetics are not yet modelled. Wind drag, world gravity, contact friction, wetting and thermal exchange use configurable world laws; see [World Weather and Matter](../libraries/WORLD_WEATHER_AND_MATTER.md).

## 5. Physical fields and derived quantities

| Field | Role | Common unit/meaning |
|---|---|---|
| `mass` | Inertial/gravitational mass value | kg |
| `volume` | Occupied volume | m3 |
| `area` | Exposed/projected area for selected calculations | m2 |
| `density` | Derived from mass and volume where available | kg/m3 |
| `pos` | 2D world position represented with a vector | m |
| `vel` | Velocity | m/s |
| `acc` | Acceleration | m/s2 |
| `temp` | Absolute temperature | K |
| `force` | Force state/readout | N |
| `pressure` | Pressure state/readout | Pa |
| `energy` | Read-only tracked physical-energy total | J |
| `integrity` | Current stability/integrity readout | 0–1 style value in current calibration |
| `collapsed_into` | Collapse carrier reference | `None` until the object collapses |
| `state` | Text label for physical/material state | e.g. `solid`, `burning`, `powder` |

Quantities carry dimensions. MANA does not silently treat metres, seconds, joules, and newtons as interchangeable. Managed values are updated through runtime operations; attempting to bypass that machinery with direct assignment can be rejected.


## 5.1 Conjured matter and the periodic catalogue

`conjure(material, ...)` creates a new physical matter object with stored mass, volume, density, state, temperature and creation provenance. `transmute(target, material, preserve_mass=true)` changes composition/material while keeping the same object ID and preserving mass by default. The built-in `periodic` catalogue contains 118 element records and can provide reference density, standard state, atomic number/symbol, and available transition points. Unknown and estimated values are not silently treated as measured precision. Common alloy compositions such as generic steel, brass, and bronze are explicitly approximate. The catalogue does not implement arbitrary chemical reaction equations or nuclear transmutation.

`shape()` remains the operation for ordinary geometric forms. `transfigure()` is restricted to living objects and matter originally created by `conjure()`; it changes the object's represented form (for example, conjured iron into a knight-like form) rather than changing chemical composition.

## 6. Lifecycle: active, inactive, released, combined, and collapsed

Objects have a lifecycle. An operation may create a new active object, change an existing object's state, mark an input inactive as part of a composite operation, release an object from active simulation, or collapse a failing object into a `ThermalRelease` carrier. Energy provenance is retained so that the same physical energy is not simultaneously counted in inactive input and active output objects.

- `combine(a, b)` combines distinct eligible sources; self-combination is rejected to avoid duplicating mass/energy.
- `separate(composite)` uses stored provenance where available to restore source objects.
- `split(object, count)` divides source quantities and provenance among output parts according to the current implementation.
- `dispel`/release-like behaviour marks an object inactive and accounts for tracked energy leaving the active world; it does not implement a full environmental destination model.
- Collapse transfers the original object's tracked energy to a carrier. `collapsed_into` is `None` before the event and refers to the resulting carrier after collapse.

These lifecycle rules are critical to conservation; removing an object from a host-side collection is not a valid substitute for a MANA world operation.

## 7. Object profiles versus target selection

`tgset` target data and `tgset(target):` context are used to supply target identity/fields and to select a target for execution. The spell itself should define the behaviour; the context tells the engine what object/position is currently selected. This supports reusable projectile spells and target-directed operations without writing target-selection logic into each `spell` declaration.

A target profile may contain HP, max HP, defence, attack, distance, resistance values, position, or other supported properties. That does not yet implement a full creature AI, path-finding, or game-like combat engine.

## 8. Matter source boundaries

Creating `Earth` creates an elemental object in the current model; it does not extract a piece of a continuous terrain mesh. Manipulating an already-represented Rock or Wood object is possible without invoking Earth merely because of the material. Cutting stone from a ground surface requires destructible terrain/material-volume support, which is not implemented in the current 2D prototype.

## 9. Related systems

- [Energy Model](../physics/ENERGY_MODEL.md) explains derived/ledger energy.
- [Physics Engine](../physics/PHYSICS_ENGINE.md) explains how motion/collision applies.
- [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md) explains common manipulation controls.
- [Beings and Summoning](BEINGS_AND_SUMMONING.md) distinguishes a record from a manifested body.
- [Necromancy and Undead](NECROMANCY_AND_UNDEAD.md) explains the body-present rule for reanimation.
