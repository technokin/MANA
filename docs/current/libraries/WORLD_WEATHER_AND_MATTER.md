# World Weather and Matter Controls

**Page kind:** Reference guide  
**Status:** Available in the current Python-hosted runtime

MANA's weather and ordinary-material operations are **world functions**, not a list of one-off weather spells. `weather` is available as a built-in namespace. Its functions change the environment parameters consumed by the runtime, and the optional Visualiser reads those same recorded parameters. The world engine applies configurable gravity, swept-circle collision response, restitution, tangential contact friction, wind drag, ambient-temperature exchange, curated material phase changes, surface wetting/drying, dust/ash coating, and rain extinguishing burning surfaces. Cloud cover, fog, humidity, heat shimmer and lightning intensity also feed scene presentation; they are not yet full fluid, cloud-microphysics, or electrical simulations.

## World laws are configurable rules

`world` is the built-in namespace for global physical defaults. It does not cast magic: it configures the rules used by the physics and material steps. An omitted option keeps its previous value. Gravity defaults to zero so a project can choose its own world; contact restitution defaults to `0.2`, contact friction to `0.35`, and air density to `1.225 kg/m3`. Individual objects may override the default `restitution` and `friction`.

```mana
load geometry2d
world.configure(
    gravity=geometry2d.direction(0, -1) * 9.81 m/s2,
    air_density=1.225 kg/m3,
    restitution=0.2, friction=0.35,
    drag=true, thermal_exchange=true,
    phase_changes=true, wetting=true
)
show world.current()
show world.laws()
```

Expected output:

```text
{'gravity_m_s2': [0.0, -9.81], 'air_density_kg_m3': 1.225, 'default_restitution': 0.2, 'friction_coefficient': 0.35, 'drag_enabled': True, 'thermal_exchange_enabled': True, 'phase_changes_enabled': True, 'wetting_enabled': True}
[{'name': "Newton's second law", 'rule': 'F = m a', 'active': True, 'detail': 'Forces change velocity according to mass.'}, {'name': 'Swept collision', 'rule': 'first contact along the integration step', 'active': True, 'detail': 'Projectile/object contact is resolved before an object can pass through a target.'}, {'name': 'Restitution', 'rule': 'e = 0.2 by default', 'active': True, 'detail': 'Objects may override restitution individually.'}, {'name': 'Contact friction', 'rule': 'mu = 0.35 by default', 'active': True, 'detail': 'Coulomb-style tangential impulse is capped by friction coefficient times the normal impulse; spin/rolling friction are not modelled.'}, {'name': 'Gravity', 'rule': 'g = (0, -9.81) m/s²', 'active': True}, {'name': 'Aerodynamic drag', 'rule': 'rho = 1.225 kg/m³', 'active': True, 'detail': 'Wind drag uses relative velocity, area, mass, air density and drag coefficient.'}, {'name': 'Material phase', 'rule': 'temperature crosses material transition points', 'active': True, 'detail': "Known melting/boiling points apply at the catalogue's reference pressure."}, {'name': 'Thermal exchange', 'rule': 'object temperature approaches ambient temperature', 'active': True}, {'name': 'Wetness exchange', 'rule': 'precipitation wets and dry weather dries surfaces', 'active': True}, {'name': 'Matter conservation', 'rule': 'transmute() preserves mass by default', 'active': True, 'detail': 'Use preserve_mass=false only when you explicitly want volume preserved instead.'}, {'name': 'Identity conservation', 'rule': 'shape/transmute/transfigure keep the same entity ID', 'active': True}]
```

Supported controls are `world.current()`, `world.laws()`, `world.configure(...)`, `world.reset()`, `world.set_gravity(...)`, `world.set_air_density(...)`, `world.set_restitution(...)`, and `world.set_friction(...)`. Gravity is a 2D acceleration vector. Air density must be between 0 and 100 kg/m³, restitution between 0 and 1, and friction between 0 and 2. The `world.laws()` report describes the active implementation, including what is intentionally simplified.

Implemented world rules include:

- **Motion:** Newtonian integration with configured persistent acceleration and global gravity.
- **Contacts:** swept-circle detection to reduce fast-object tunnelling; restitution controls bounce, and Coulomb-style tangential friction reduces sliding. Lost translational kinetic energy from an impact is added to thermal energy. Spin, rolling resistance, polygon-edge contacts, and iterative multi-contact constraints are not implemented.
- **Air and weather:** wind drag depends on relative velocity, exposed area, mass, air density and a drag coefficient. Wet and dry precipitation update surface wetness or dust coating; wet surfaces can extinguish supported burning objects.
- **Heat and phase:** ambient temperature exchange and catalogue-driven melting/boiling state changes are enabled by default. These are simplified reference-pressure transitions, not a chemistry or full thermodynamics solver.
- **Matter and identity:** `transmute()` preserves mass by default and updates volume/density; shape and transfiguration keep the same object identity.

`world.configure()` changes simulation state, so call it in a spell executed via `post()` or `release()` when running spell code. `world.reset()` restores the defaults above.

## Periodic table

`periodic` is a built-in read-only reference containing all 118 recognised elements in the runtime catalogue. It is a source of material properties for conjuration/transmutation, not a full chemical-reaction solver. The recorded density and phase points are reference values; unknown, superheavy, or estimated entries are marked where appropriate.

```mana
iron_data = periodic.lookup("Fe")
show iron_data
show periodic.melting_point("iron")
show periodic.search("noble gas")
```

Expected output:

```text
{'atomic_number': 26, 'symbol': 'Fe', 'name': 'Iron', 'density_kg_m3': 7874.0, 'standard_state': 'solid', 'category': 'transition metal', 'estimated_density': False, 'atomic_mass_u': 55.845, 'estimated_atomic_mass': False, 'melting_point_k': 1811, 'boiling_point_k': 3134, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}
1811 K
[{'atomic_number': 2, 'symbol': 'He', 'name': 'Helium', 'density_kg_m3': 0.1785, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 4.002602, 'estimated_atomic_mass': False, 'melting_point_k': 0.95, 'boiling_point_k': 4.22, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 10, 'symbol': 'Ne', 'name': 'Neon', 'density_kg_m3': 0.9002, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 20.1797, 'estimated_atomic_mass': False, 'melting_point_k': 24.56, 'boiling_point_k': 27.07, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 18, 'symbol': 'Ar', 'name': 'Argon', 'density_kg_m3': 1.784, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 39.948, 'estimated_atomic_mass': False, 'melting_point_k': 83.8, 'boiling_point_k': 87.3, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 36, 'symbol': 'Kr', 'name': 'Krypton', 'density_kg_m3': 3.75, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 83.798, 'estimated_atomic_mass': False, 'melting_point_k': None, 'boiling_point_k': None, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 54, 'symbol': 'Xe', 'name': 'Xenon', 'density_kg_m3': 5.894, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 131.293, 'estimated_atomic_mass': False, 'melting_point_k': None, 'boiling_point_k': None, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 86, 'symbol': 'Rn', 'name': 'Radon', 'density_kg_m3': 9.73, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': False, 'atomic_mass_u': 222.0, 'estimated_atomic_mass': True, 'melting_point_k': None, 'boiling_point_k': None, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}, {'atomic_number': 118, 'symbol': 'Og', 'name': 'Oganesson', 'density_kg_m3': 7000.0, 'standard_state': 'gas', 'category': 'noble gas', 'estimated_density': True, 'atomic_mass_u': 294.0, 'estimated_atomic_mass': True, 'melting_point_k': None, 'boiling_point_k': None, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}]
```

The API includes `periodic.lookup(name_or_symbol)`, `periodic.by_number(atomic_number)`, `periodic.all()`, `periodic.search(query)`, `periodic.density(value)`, `periodic.melting_point(value)`, `periodic.boiling_point(value)`, `periodic.symbol(value)`, `periodic.name(value)`, and `periodic.count` (118). Densities and phase points are available only where the data catalogue has them.

## Compose weather from parameters

```mana
weather.configure("storm", intensity=0.8, wind_speed=14 m/s,
                  wind_direction="northwest", duration=20 s)
weather.precipitation("snow", intensity=0.65)
weather.clouds(0.95)
weather.fog(0.25)
show weather.current()
```

Expected output:

```text
{'kind': 'custom', 'intensity': 0.65, 'precipitation': 'snow', 'wind_speed_mps': 14.0, 'wind_x_mps': -9.899494936611665, 'wind_y_mps': 9.899494936611665, 'wind_direction_name': 'northwest', 'wind': 0.7, 'wind_direction': -0.7071067811865476, 'temperature_k': 280.15, 'humidity': 0.95, 'clouds': 0.95, 'fog': 0.25, 'heat': -0.25, 'lightning': 0.85, 'started_at': 0.0, 'until': 20.0, 'duration': 20.0, 'indefinite': False}
```

Presets include `clear`, `rain`, `snow`, `storm`, `blizzard`, `heatwave`, `sandstorm`, `fog`, `wind`, `ashfall`, `aurora`, and `custom`. A custom profile starts from current settings and changes only named parameters. Modifying a timed profile keeps its remaining duration; a fresh profile without `duration` lasts until replaced or cleared.

Common controls:

- `weather.configure(kind, ...)` or `weather.set(kind, ...)`: set several parameters together.
- `weather.wind(speed, direction, intensity=..., duration=...)`: alter wind without defining a named spell.
- `weather.precipitation(kind, intensity=..., duration=...)`: choose `none`, `rain`, `snow`, `dust`, `ash`, or `hail`.
- `weather.temperature(value, duration=...)`: set ambient temperature in kelvin.
- `weather.humidity(value, duration=...)`, `weather.clouds(coverage, duration=...)`, `weather.fog(density, duration=...)`, `weather.heat(value, duration=...)`, and `weather.lightning(intensity, duration=...)`: tune individual atmospheric properties. Normalized values are between 0 and 1 except heat, which is between -1 and 1.
- `weather.clear()` and `weather.current()`: reset the weather or retrieve a copy of its parameters.

Rain, wind, fog and snow are not spell names. They are parameters and reusable environment controls; a program can compose them however it needs. The first version has a simplified environmental solver, not a full real-world climate or fluid simulator.

## Conjure ordinary matter

`conjure()` creates physical matter. Native assignment syntax is also accepted: `ore = conjure steel, mass=5 kg, shape=sphere`. It is intentionally different from `create` for elemental manifestations and `summoning` for beings. Materials with a registered density can be conjured directly; unknown fantasy materials require an explicit density. Supported registered examples include metal, iron, steel, gold, copper, aluminium, stone, wood, glass, crystal, ice, and water.

```mana
load geometry2d
spell forge_warden():
    warden = conjure("metal", mass=4 kg,
                     position=geometry2d.point(3 m, 0 m),
                     shape=sphere, name="Forged Warden")
    transfigure(warden, "knight", scale=1.25)
    incant warden

release(forge_warden)
```

Material mass, density, volume, collision size, and temperature become world properties. Conjuring a large object therefore has a physical cost in the runtime's material/mana accounting rather than being only a drawing.

## Shape, conjure, transmute, and transfigure

These operations have separate jobs:

- `shape(object, geometry)` changes ordinary object geometry, such as `circle`, `polygon`, `wall`, `shield`, `ring`, or `beam`. It does not turn an object into a living creature.
- `conjure(material, ...)` manifests a new physical material object such as iron, steel, gold, wood, glass, water, or stone. It is not `summoning`: summoning manifests a being; conjuration manifests matter. The runtime charges material-creation cost and stores mass, volume, density, material provenance, composition and available periodic-table data. Fantasy materials without reference density require an explicit density.
- `transmute(target, material, preserve_mass=true)` changes the material/composition of an existing object while retaining its identity. By default, mass is conserved while volume, density and collision size are updated; `preserve_mass=false` instead keeps volume and recalculates mass. Registered elements accept either their name or symbol. This is a material conversion rule, not nuclear chemistry: the periodic data is a catalogue, and alloy/compound composition may be explicitly marked as an estimate.
- `transfigure(target, form, scale=1.0)` changes the represented form of a living entity or matter created by `conjure()`, while preserving that entity's identity. Supported form families include humanoid/wizard, knight, bird, serpent, beast and golem. Ordinary objects created through `create` or `tgset` cannot be transfigured; use `shape()` for their geometric forms.

```mana
load geometry2d
steel = conjure("steel", mass=4 kg, position=geometry2d.point(3 m, 0 m))
transmute(steel, "gold")
transfigure(steel, "knight", scale=1.25)
ordinary_wall = create Earth
shape(ordinary_wall, wall)
```

Expected output:

```text
(no output)
```

Transfiguration is a first-stage entity-form operation, not a full anatomical, genetic, molecular, or autonomous-creature simulation.

## World-engine boundary

The runtime is the authority for object properties, world-law configuration, weather controls, physics, contacts, material transitions, and spell results. The Visualiser is a renderer/replayer: it must not invent hits, infer weather from spell names, or independently decide physical outcomes. The current physics world remains two-dimensional, and some material/atmospheric behavior is intentionally simplified. More detailed local simulation can be added later without coupling the language semantics to the editor UI.


## Area weather and the native statement

The language accepts an indented, brace-free climate statement:

```mana
spell rain_ring():
    weather rain, intensity=0.8, wind_speed=12 m/s, wind_direction=north, duration=30 s, radius=80 m

post(rain_ring)
release(rain_ring)
```

Expected output:

```text
[POST rain_ring] inputs: no parameters
[POST rain_ring] local weather configured: rain (radius 80 m, intensity 0.8)
[POST rain_ring] spell completed
[POST rain_ring] mana appraisal: 0 mana
```

With no `radius`, the statement configures the world-wide climate. With `radius`, it creates or updates an area zone centred on the caster's world position. Supply `center=some_position` (a 2D position in metres or a positioned object) to centre the area elsewhere. The most recently configured overlapping zone wins for an object. Area weather affects physical objects only while they are within the zone; on expiry, the zone is removed and the global weather becomes the fallback. `weather.areas()` returns copies of active area zones for inspection.

A `post(spell)` call is an appraisal/trial: it records the hypothetical climate and object changes then rolls them back. `release(spell)` commits these changes to world state. The `mana_cost_readout`/mana usage fields are calculated appraisal values; MANA does not require a finite personal mana pool to permit a cast.

`conjure` currently accepts mass up to 1e12 kg per object. This raises the previous per-object ceiling; cumulative object and per-run resource budgets remain in force to protect the interpreter and world engine. Supported additional creation options are velocity, anchored state, collidable state, restitution, friction, and drag coefficient.


## Native spell-language forms

Area weather may be authored as part of a spell without explicitly calling a namespace API:

```mana
spell rain_circle():
    weather rain, intensity=0.8, wind_speed=8 m/s, duration=30 s, radius=80 m

appraise rain_circle
cast rain_circle
```

Expected output:

```text
[APPRAISAL rain_circle] inputs: no parameters
[APPRAISAL rain_circle] local weather configured: rain (radius 80 m, intensity 0.8)
[APPRAISAL rain_circle] spell completed
[APPRAISAL rain_circle] mana appraisal: 0 mana
[CAST rain_circle] spell committed
[CAST rain_circle] mana appraisal: 0 mana
```

Use `appraise` for the non-committing, recorded trial and `cast` to commit supported changes. The compatible `post(spell)` / `release(spell)` forms remain available. Native object statements such as `shape ring into sphere`, `transmute ingot into silver`, `transform water into gas`, and `transfigure conjured_iron into knight` express common operations directly. The corresponding function forms remain available for advanced parameters.
