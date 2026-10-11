# Pure Mana and Universal Control — MANA v1.0.0

**Page kind:** Reference  

The lowercase `mana` namespace provides pure-mana effects and element-independent control operations. It is installed by the runtime automatically; `load mana` is also accepted. Uppercase `Mana` is the type selector recognized by `create Mana`. The namespace and the type selector have different jobs.

The main world simulation is 2D in the x-y plane. Positions and directions must follow MANA's unit rules. All numeric effect defaults are defaults, not a mana-storage limit; the runtime records energy and mana-equivalent use in its readouts and ledger.

## Defaults

| Operation | Default | Meaning |
|---|---:|---|
| `mana.form()` | `sphere`, `1000 J`, `1 m` radius | Forms a pure-mana construct. Position defaults to 10 m along +X from the runtime caster position. The terminal runtime currently initializes that position to (0 m, 0 m); a future interactive engine can supply an actor position. |
| `mana.burst()` | `1000 J`, `1 m` radius | Radial pulse centred 10 m along +X from the caster position. |
| `mana.emit()` | `1000 W`, `1 s`, `10 m` range, `1 m` beam radius | Energy beam. Power × duration gives total emitted energy. Direction defaults to +X, or automatically aims at the selected `tgset` target. Position defaults to 10 m along +X. |
| `mana.control(...)` | `100 N`, `1 s` | Default force magnitude and action duration for `toward`, `away`, and `lift`. |
| `mana.collect(...)` | `100 N`, `1 s` | Collects one object or a list of objects toward the selected `tgset` target, or to the caster position if no target block is active. |

The optional `position` parameter is last for `form`, `burst`, and `emit`. Omit it for the default location or use a named argument to set it without filling other optional arguments. For example, `mana.emit(power=250 W, duration=2 s, position=geometry2d.point(4 m, 3 m))`.

## Form, burst, and emit

### `mana.form(shape, energy, radius, collidable, anchored, position)`

Creates a finite-energy, zero-material-mass pure-mana construct. Common shape labels include `sphere`, `ball`, `projectile`, `barrier`, `wall`, `shield`, and `disc`. Projectile-like labels are collidable by default; barrier-like labels are collidable and anchored by default. Optional overrides are `collidable` and `anchored`. The current 2D physics engine still represents collision bounds as circles; these labels do not create arbitrary wall/disc geometry by themselves.

```mana
orb = mana.form("sphere", energy=750 J, radius=0.15 m)
velocity(orb, 25 m/s)
```

Expected output:

```text
(no output)
```

A projectile transfers its stored mana energy to a struck object as heat and then becomes inactive. The transfer is recorded internally in the energy ledger. Creating a construct records ambient-mana energy input; it does not draw from a stored mana pool.

### `mana.burst(energy, radius, position)`

Applies a radial energy pulse to objects inside the radius. Energy is divided equally among eligible objects. Any portion not absorbed by objects is recorded as unabsorbed environmental energy, not as lost or destroyed energy.

```mana
result = mana.burst(energy=2000 J, radius=2 m)
show result
```

Expected output:

```text
{'effect': 'burst', 'energy_j': 2000.0, 'radius_m': 2.0, 'position_m': [10.0, 0.0], 'affected': 0, 'delivered_j': 0.0, 'unabsorbed_j': 2000.0}
```

### `mana.emit(power, duration, direction, range, beam_radius, position)`

Emits a directed pure-mana ray. `power` has units of watts, `duration` seconds, and `span`/`beam_radius` metres. The emitted energy is `power × duration`. If `direction` is omitted within `tgset(target):`, the target's position determines the direction; otherwise the default is +X.

```mana
load geometry2d
result = mana.emit(power=500 W, duration=2 s, position=geometry2d.point(3 m, 0 m))
show result.energy_j
```

Expected output:

```text
1000.0
```

Eligible objects in the beam receive the energy as heat. A combustible target changes to `burning` when a heat operation leaves it at or above its ignition threshold and it is not already burning. The prototype models ignition as a state change; it does not yet simulate continuing fuel consumption, smoke, or flame spread.

## Element-independent control

These functions use the shared runtime and physics properties. They do not require Fire, Water, Earth, Air, or another element.

- `mana.toward(object, destination, strength, duration)` applies force toward a position vector or positioned object. Inside `tgset(target):`, omit `destination` to use the selected target.
- `mana.away(object, source, strength, duration)` applies force away from a source. Inside `tgset(target):`, omit `source` to use the selected target.
- `mana.lift(object, strength, duration)` applies an upward force impulse. Its default is 100 N for one second; it sets motion, not a sustained altitude constraint.
- `mana.hold(object, position)` stops the object and anchors it at the current position, or at the optional position supplied.
- `mana.levitate(object, position)` is the accessible fixed-position form of `hold`; the object remains anchored independently of elemental type.
- `mana.stop(object)` stops motion and converts the object's kinetic energy into its thermal energy. Total energy is conserved.
- `mana.release_control(object)` releases a held object from its anchor; it does not delete its energy.
- `mana.collect(objects, destination, strength, duration)` applies toward-control to one object or a list. Destination defaults to the selected `tgset` target, or to the caster position when no target block is active.
- `mana.control(object, action, strength, duration, destination)` exposes the underlying action set: `toward`, `away`, `lift`, `hold`, `stop`, and `release`.

Example using `tgset` context to avoid repeating a target position:

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

`mana.toward` and `mana.away` require an explicit destination/source outside `tgset(target):`. Force values must be finite and non-negative; control durations must be between 0 and 60 seconds. Positions are 2D world positions in metres. Errors use the normal MANA error classes and acquire the source location of the calling statement.

## Defining material objects with `tgset`

`name = tgset:` can define ordinary manipulable material objects as well as combat-oriented target profiles. The fields describe the object; they do not create a new language construct or a specialist library.

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

The runtime infers `combustible = true` for common combustible materials such as wood, timber, paper, cardboard, straw, dry grass, leaves, cloth, cotton, bark, and cane when the author has not specified `combustible`. The default ignition threshold is 573.15 K, and `heat()` raises temperature by a change in kelvin. Crossing the threshold changes a combustible object's `state` to `burning` and emits `object_ignited`.

A material can override the inferred setting explicitly, for example `combustible = false`. The `powderable` field defaults to true for solid material profiles, except non-solid base types such as Fire, Water, and Air. `transform(object, "powder")` rejects an object explicitly marked `powderable = false`. Powder is currently represented as one aggregate object: its mass and tracked energy remain on that object. This operation does not yet generate separate individual dust particles.

Known physical fields such as `mass`, `volume`, `area`, `temp`, `pos`, `state`, `material`, `kind`, `combustible`, `powderable`, `ignition_temp`, `shape`, `collision_radius`, and `restitution` are validated. Density is derived from mass and volume. Values such as mass must have consistent units; mass must be positive and temperature cannot fall below 0 K.

## Energy, errors, and limits

Pure-mana effects take their effect energy from ambient mana. Energy input is recorded in the runtime ledger, and the mana-equivalent use is a readout, not a stored/spendable pool. Internal projectile-to-object transfer is recorded as an internal transfer with matching source and target deltas. Burst energy that no object absorbs is accounted for as unabsorbed environmental energy.

The implementation is part of the current 2D physics prototype. It does not provide a 3D world simulation, material terrain extraction, continuing fire simulation, or automatic path planning for moving objects. Barrier-style constructs currently use anchored circular collision bounds and do not yet have energy-based durability or maintenance costs. For physical movement, use universal control plus the existing motion and physics operations; for a fixed position, use `mana.hold`/`mana.levitate`.
