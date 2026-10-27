# Materials, Forging, Equipment, and Metal Magic

**Page kind:** Runtime library guide  
**Status:** Available in the current Python-hosted runtime

MANA's material model is shared by conjuration, transformations, world physics, equipment, and the Visualiser. A material is not simply a display name or a coloured effect. Its density and other registered properties shape how the world engine handles it. The implementation is a game simulation with selected physical rules—not a universal chemistry or fracture-mechanics solver.

## 1. Four different operations

| Operation | What changes | What should remain the same |
|---|---|---|
| `conjure` | Creates new physical matter, with mass, material, shape, position, and world properties. | No existing object's identity is reused. |
| `shape` | Changes the geometry label of an existing object, such as `ring`, `shield`, `wall`, `sphere`, or `polygon`. | Material composition and object identity. |
| `transmute` | Changes an object's material/composition and refreshes material-derived physics properties. | Object identity and position; mass is preserved by default. |
| `transform` | Changes a supported physical state such as `solid`, `liquid`, `gas`, `plasma`, or `powder`. | The aggregate object's identity and its total mass in the supported model. |
| `transfigure` | Changes the represented form of a living being or eligible conjured matter, such as iron becoming a knight-shaped construct. | The entity's identity. This is not equivalent to a geometry change or to summoning a new being. |

The name alone does not guarantee a successful operation: the target must be eligible, input properties must be valid, and the runtime's supported model determines the result.

## 2. The periodic table is a reference catalogue

The built-in `periodic` namespace exposes 118 element records:

```mana
iron_record = periodic.lookup("Fe")
carbon_record = periodic.lookup("carbon")
show iron_record
show periodic.by_number(26)
```

Expected output:

```text
{'atomic_number': 26, 'symbol': 'Fe', 'name': 'Iron', 'density_kg_m3': 7874.0, 'standard_state': 'solid', 'category': 'transition metal', 'estimated_density': False, 'atomic_mass_u': 55.845, 'estimated_atomic_mass': False, 'melting_point_k': 1811, 'boiling_point_k': 3134, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}
{'atomic_number': 26, 'symbol': 'Fe', 'name': 'Iron', 'density_kg_m3': 7874.0, 'standard_state': 'solid', 'category': 'transition metal', 'estimated_density': False, 'atomic_mass_u': 55.845, 'estimated_atomic_mass': False, 'melting_point_k': 1811, 'boiling_point_k': 3134, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}
```

Useful operations include `periodic.lookup(name_or_symbol)`, `periodic.by_number(atomic_number)`, `periodic.search(text)`, `periodic.all()`, `periodic.density(element)`, `periodic.melting_point(element)`, `periodic.boiling_point(element)`, `periodic.symbol(element)`, `periodic.name(element)`, and `periodic.count`.

Each record may include atomic number, symbol, name, category, density, standard state, atomic mass, melting/boiling points, reference conditions, and flags identifying estimated values. The superheavy elements and some physical properties use estimates. Missing data is represented as missing data; it should not be silently treated as an exact measurement.

The periodic table is not itself a chemistry engine. It does not calculate molecular bonds, chemical reaction kinetics, nuclear reaction feasibility, toxicity, corrosion rates, or exact alloy microstructure. MANA's composition ledger is a structured game-world record.

## 2.1 Consolidated material catalogue

The current stock catalogue consolidates **407 unique canonical material profiles**: the 118 periodic-table elements plus named profiles for alloys, rocks and terrain, glasses and ceramics, polymers and composites, biological and organic materials, fibres and textiles, fluids and gases, powders, fictional materials and other specialist substances. Aliases (such as aluminium/aluminum spellings or canonical fantasy-material names) resolve to a single profile instead of creating duplicate catalogue rows.

Every stock profile is normalised to a common schema covering state, density, hardness/toughness/strength indices, thermal and electrical properties, thermal expansion, porosity, toxicity, optical transparency, magical resonance, intended uses, tags, microstructure/subcategory, broad `family`, and a `property_scope` note. Missing phase-transition data remains missing; estimated values are gameplay coefficients, not certified engineering data.

Use `materials.categories()` for the ten consolidated top-level families, `materials.summary()` for counts by family/subcategory/state, `materials.by_category("metals and alloys")` for family filtering, `materials.by_state("liquid")` for phase filtering, `materials.compare(first, second)` for property differences, and `materials.recommend(...)` for a constrained material shortlist. Stock search/category indexes are built once per runtime, while public APIs return copies so query results cannot mutate the shared catalogue.

Representative additions include specialist steels and alloys (tool steel, spring steel, Inconel 718, Hastelloy C276, Monel 400, titanium alloy), geological and terrain materials (basalt, laterite, obsidian, silica sand, gravel and snow), optical/refractory materials (borosilicate glass, fused silica, sapphire and zirconia ceramic), engineering polymers/composites (PEEK-family polymers, PTFE, aramid fibre and carbon-fibre composite), organic/textile feedstocks, process fluids, and fictional substances such as demonsteel, dragonhide, aetherite, voidglass and stormglass. The numeric properties remain approximate simulation coefficients; material names do not imply chemistry, manufacturing, or fracture mechanics are fully simulated.

## 3. Material profiles and custom alloys

`materials.profile(name)` returns a copy of a material's physical profile. `materials.search(query)` finds registered materials by name, category or symbol; `materials.all()` lists the built-in and world-local custom profiles; `materials.exists(name)` checks known material names. A custom profile belongs to one `Runtime`, so it does not leak into other worlds or projects.

Define a reusable material in a spell or other executable world-changing context:

```mana
load materials
spell define_moonsteel():
    materials.define("Moonsteel", density=7900 kg/m3,
                     state="solid", category="custom alloy",
                     hardness=0.82, toughness=0.78, strength=1100,
                     magnetic_response=0.25,
                     electrical_conductivity=0.55,
                     thermal_conductivity=0.48,
                     corrosion_resistance=0.9,
                     composition="Fe:0.94,C:0.04,Ni:0.02")
    incant "Moonsteel registered"

cast define_moonsteel
```

Expected output:

```text
[CAST define_moonsteel] spell committed
[CAST define_moonsteel] mana appraisal: 0 mana
```

Composition entries use element symbols or names and **mass fractions**. Fractions must be positive, include no duplicate element, and total approximately 1.0. MANA normalises the accepted fractions and derives atomic fractions from the representative atomic masses in the table. At most 20 elements can be supplied in one custom composition. A missing formula is normal for an alloy with a variable composition; the runtime records the formula as unknown instead of inventing one.

The following custom profile fields are supported:

- `density`: physical density with density units.
- `state`: `solid`, `liquid`, `gas`, `plasma`, or `powder`.
- `category`: a descriptive string such as `custom alloy`, `ceramic`, or `fantasy crystal`.
- `hardness`, `toughness`, `strength`: simulation coefficients and strength in MPa.
- `magnetic_response`: coupling factor used by metal manipulation, from 0 to 1.
- `electrical_conductivity`, `thermal_conductivity`: normalised coefficients from 0 to 1.
- `combustible`, `brittle`: booleans used by selected world rules.
- `corrosion_resistance`: normalised coefficient from 0 to 1.
- `composition`: optional elemental composition ledger.

These properties are intentionally explicit. Defining Moonsteel with high strength does not automatically make it unbreakable; damage, object scale, temperature, impact energy, and other supported rules still matter. The profile is not a certified material database.

## 4. Conjuration creates physical objects

Conjuration should be used to create matter that persists as an object in the simulated world:

```mana
load materials
load armory
sword = conjure "sword", material=steel, name="Gatewatcher", mass=2.4 kg
arrow = conjure "arrow", material=steel, mass=0.045 kg
plate = conjure "body armour", material=steel, mass=8 kg
ore = conjure copper, mass=20 kg, shape=sphere
show sword.material
show plate.equipment_slot
```

Expected output:

```text
steel
body_armour
```

Examples are valid when the named blueprint/material is registered, and a custom material must first be defined in the same world. The engine supports larger physical objects than the old small-object demos, but per-object and cumulative runtime limits still apply; large quantities can be physically expensive and should be tested incrementally. The current per-object conjuration ceiling is 1e12 kg, not an unlimited resource promise.

Options can include `mass`, `material`, `position`, `shape`, `name`, `temperature`, explicit `density` for data that is not registered, `state`, `velocity`, `anchored`, `collidable`, `restitution`, `friction`, `drag_coefficient`, and blueprint dimensions. Unit-bearing values must use compatible units. `anchored=true` makes an object fixed in the 2D world; `collidable=false` disables collision participation. These affect real runtime properties, not merely the view.

Conjured objects retain material provenance and physical properties. They enter the same object, collision, environmental, and event systems as other physical objects. Conjuration is not summoning: it does not look up or transport an existing creature.

## 5. Equipment blueprints are recipes, not unique functions

`armory.blueprints()` lists reusable item designs; `armory.inspect(name_or_object)` reports their properties. The catalogue covers melee weapons, ranged launchers, ammunition, shields, armour slots, tools, and resource forms. It includes patterns such as swords, greatswords, daggers, axes, hammers, maces, spears, javelins, staves, bows, crossbows, bucklers, shields, body armour, head/hand/leg armour, ingots, rods, chains and payload arrows.

Create a blueprint item with `conjure`. For example:

```mana
load planes
load armory
planes.open_path("Wild Realm", "Mortal Plane")
spell forge_guard():
    guard = summon "Griffin" from "Wild Realm"
    blade = conjure "sword", material=steel, mass=1.8 kg
    shield = conjure "shield", material=iron, mass=5 kg
    armory.equip(guard, blade)
    armory.equip(guard, shield)
    incant guard
cast forge_guard
```

Expected output:

```text
[CAST forge_guard] spell committed
[CAST forge_guard] mana appraisal: 0.68 mana
```

A real project must have the correct plane route for the chosen being and use supported equipment slots. A blueprint doesn't create a physical object until conjured. Equipment is attached to a wearer by `armory.equip(wearer, item)` and detached with `armory.unequip(wearer, item)`. One item per slot can be equipped at once. Current combat resolves equipped armour through a simplified armour-rating mitigation model, not a detailed per-body-part hitbox simulation.

### Define your own blueprint

`armory.define(...)` registers a reusable blueprint, subject to name, shape, slot, material, coefficient and resource limits. It does not create the item immediately.

```mana
load planes
load materials
load armory
planes.open_path("Wild Realm", "Mortal Plane")
spell register_siege_bolt():
    armory.define("Siege Bolt", slot="projectile", material="steel",
                  mass=0.8 kg, shape="segment",
                  length=0.75 m, width=0.045 m, thickness=0.045 m,
                  damage_multiplier=1.8, durability=180,
                  payload="anchor", attack_style="ranged",
                  launch_speed=65 m/s,
                  description="Heavy anchor-headed bolt")
    bolt = conjure "Siege Bolt", material="steel"
    incant bolt

cast register_siege_bolt
```

Expected output:

```text
[CAST register_siege_bolt] spell committed
[CAST register_siege_bolt] mana appraisal: 0.08 mana
```

Blueprint properties may include slot, material, mass, shape, length, width, thickness, damage multiplier, armour rating, durability, payload and ranged launch speed. A projectile blueprint can use supported payloads such as binding, net, shock, smoke, flare, anchor, burst and acid. Payload resolution is deliberately bounded; defining a payload is not the same as simulating arbitrary chemistry or electronics.

## 6. Weapons, armour and arrows

MANA should support equipment through data and shared operations, not one hard-coded spell per weapon. A sword and an axe are different blueprints with different mass, dimensions, damage coefficients and handling metadata. A shield is equipment with a defensive slot and armour properties. Arrows are physical projectile objects whose payload can vary, while the launcher's configured speed provides the initial velocity.

Typical operations:

- `armory.inspect("longbow")` — inspect the design.
- `armory.define(...)` — register a user-created design.
- `conjure "longbow"` — create the physical item.
- `armory.equip(wielder, item)` / `armory.unequip(wielder, item)` — equip or remove the item.
- `armory.imbue(arrow, "shock")` — set a supported payload on a conjured projectile.
- `armory.launch(wielder, arrow, target, launcher=bow)` — launch the projectile through the physics world.
- `armory.strike(wielder, target, weapon, force=...)` — resolve a bounded melee strike when the weapon is equipped.

Not every visual equipment profile currently has full animation or a unique attack move. Equipment should get new behaviour by implementing shared world rules and fields, not by adding cosmetic if-statements to the Visualiser.

## 7. Metal manipulation

`metals` applies a bounded magnetic-response model to physical matter. Its two modes are distinct:

- `metals.control(target, direction, strength, duration=...)` applies a directional force to a supported metallic target.
- `metals.field(center, strength, radius, polarity="attract", duration=...)` registers a temporary magnetic field. `metals.active_fields()` returns a snapshot of active fields.

Force is scaled by the target's material profile, including `magnetic_response`. Ordinary steel and iron respond more than copper, aluminium, gold or nonmetallic objects unless a custom profile says otherwise. A profile with magnetic response 0 is effectively unaffected. Field strength, radius, duration and resulting work are bounded; the simulation is not atom-by-atom magnetism and does not guarantee that a complex metal structure moves without breaking or colliding.

```mana
spell draw_iron_gate():
    gate = conjure steel, mass=80 kg, position=geometry2d.point(8 m, 0 m), shape=wall
    metals.control(gate, geometry2d.direction(-1, 0), 5000 N, duration=2 s)
    incant gate
```

Expected output:

```text
(no output)
```

The chosen direction, distance, collisions, anchoring and world constraints determine the result. An anchored target may not be moved as expected; use object properties deliberately rather than assuming a named "metal magic" effect overrides physics.

## 8. Transmutation changes the material, not its identity

```mana
ore = conjure iron, mass=12 kg
transmute ore into silver
```

Expected output:

```text
(no output)
```

By default the operation preserves mass and updates volume and collision scale from the destination density. A volume-preserving conversion can be requested with the function form `transmute(ore, "silver", preserve_mass=false)`. Custom densities may be supplied when no profile exists. Transmutation updates the composition record, atomic-number metadata when applicable, state defaults, hardness, toughness, strength, magnetic response, conductivity, heat conduction, combustion/brittleness and corrosion-resistance fields. It also adjusts equipment durability in the supported model.

There are important boundaries:

1. Converting a material does not create additional material mass by default.
2. Periodic-table metadata is descriptive data. The runtime does not solve real chemical or nuclear reactions.
3. The engine records work/energy changes but does not claim an experimentally accurate energy budget for arbitrary transmutation.
4. A change of shape is `shape`; a change of phase is `transform`; a change of living/conjured represented form is `transfigure`.
5. Material transformations are not a way to turn an ordinary target profile into a genuine body or being.

## 9. Practical patterns

### Forge and appraise before committing

```mana
spell create_aegis():
    core = conjure steel, mass=7 kg, shape=shield, name="Aegis Core"
    shape core into shield
    incant core

appraise create_aegis
cast create_aegis
```

Expected output:

```text
[APPRAISAL create_aegis] inputs: no parameters
[APPRAISAL create_aegis] energy input: 2.05205e+06 J (conjure steel; matter manifestation)
[APPRAISAL create_aegis] created Aegis Core (Compound, 7 kg; conjured material steel)
[APPRAISAL create_aegis] executed conjure('steel')
[APPRAISAL create_aegis] executed shape(Aegis Core, 'shield')
[APPRAISAL create_aegis] spell completed
[APPRAISAL create_aegis] mana appraisal: 0.7 mana
[APPRAISAL create_aegis] created: Aegis Core (Compound, 7 kg)
[CAST create_aegis] spell committed
[CAST create_aegis] mana appraisal: 0.7 mana
```

`appraise` records a non-committing trial of supported world changes; `cast` commits the result. A trial is useful before material-heavy or high-impact operations. Read the resulting recording and object properties to confirm the actual output.

### Register a custom alloy and then a tool

```mana
load materials
load armory
load periodic
spell make_silverglass():
    materials.define("Silverglass", density=2600 kg/m3,
                     state="solid", category="fantasy composite",
                     hardness=0.65, toughness=0.62, strength=420,
                     magnetic_response=0.05,
                     electrical_conductivity=0.7,
                     thermal_conductivity=0.6,
                     corrosion_resistance=0.92,
                     brittle=false,
                     composition="Si:0.45,O:0.35,Ag:0.20")
    armory.define("Silverglass Wand", slot="tool", material="Silverglass",
                  mass=0.35 kg, shape="segment", length=0.3 m,
                  width=0.02 m, thickness=0.02 m,
                  durability=60, description="A light composite wand")
    wand = conjure "Silverglass Wand", material="Silverglass"
    incant wand

cast make_silverglass
show materials.profile("Silverglass")
show armory.inspect("Silverglass Wand")
show periodic.lookup("Ag")
```

Expected output:

```text
[CAST make_silverglass] spell committed
[CAST make_silverglass] mana appraisal: 0.035 mana
{'name': 'Silverglass', 'density_kg_m3': 2600.0, 'state': 'solid', 'category': 'fantasy composite', 'hardness_index': 0.65, 'toughness_index': 0.62, 'strength_mpa': 420.0, 'magnetic_response': 0.05, 'electrical_conductivity': 0.7, 'thermal_conductivity': 0.6, 'corrosion_resistance': 0.92, 'elastic_modulus_gpa': 0.1, 'specific_heat_j_kg_k': 1000.0, 'thermal_expansion_per_k': 2e-05, 'porosity_index': 0.0, 'toxicity_index': 0.0, 'optical_transparency_index': 0.0, 'magical_resonance_index': 0.0, 'melting_point_k': None, 'boiling_point_k': None, 'combustible': False, 'brittle': False, 'estimated': True, 'source': 'runtime-defined-game-material', 'microstructure': 'fantasy composite', 'property_scope': 'user-defined gameplay coefficient; not certified engineering data', 'tags': ['fantasy composite', 'solid'], 'common_uses': ['user-defined crafting', 'world simulation'], 'subcategory': 'fantasy composite', 'family': 'polymers and composites', 'composition_record': {'kind': 'custom_alloy', 'name': 'Silverglass', 'formula': None, 'proportion_basis': 'mass_fraction_input; atomic_fraction_derived', 'elements': [{'symbol': 'Si', 'atomic_number': 14, 'atomic_mass_u': 28.085, 'estimated_atomic_mass': False, 'mass_fraction': 0.45, 'atomic_fraction': 0.40305585042878533}, {'symbol': 'O', 'atomic_number': 8, 'atomic_mass_u': 15.999, 'estimated_atomic_mass': False, 'mass_fraction': 0.35, 'atomic_fraction': 0.5503035947736111}, {'symbol': 'Ag', 'atomic_number': 47, 'atomic_mass_u': 107.8682, 'estimated_atomic_mass': False, 'mass_fraction': 0.2, 'atomic_fraction': 0.04664055479760356}], 'estimated': True}}
{'name': 'silverglass wand', 'material': 'Silverglass', 'slot': 'tool', 'shape': 'segment', 'mass_kg': 0.35, 'length_m': 0.3, 'width_m': 0.02, 'thickness_m': 0.02, 'damage_multiplier': 1.0, 'armour_rating': 0.0, 'durability': 60.0, 'payload': 'none', 'launch_speed_m_s': None, 'custom': True, 'description': 'A light composite wand'}
{'atomic_number': 47, 'symbol': 'Ag', 'name': 'Silver', 'density_kg_m3': 10490.0, 'standard_state': 'solid', 'category': 'transition metal', 'estimated_density': False, 'atomic_mass_u': 107.8682, 'estimated_atomic_mass': False, 'melting_point_k': 1234.93, 'boiling_point_k': 2435, 'reference_temperature_k': 293.15, 'reference_pressure_pa': 101325.0}
```

These examples show catalogue and object fields. Custom numeric coefficients are game balance inputs and should be tested against the target's expected use.

## 10. Boundaries and future directions

The current implementation provides a single 2D world simulation, simplified contact geometry, a material property table, mass/volume bookkeeping, selected phase and environmental rules, a bounded magnetic-force model and equipment-based combat. It does not yet have full 3D shapes, metallurgy grain structure, chemical kinetics, detailed wear, per-body-part armour coverage, finite-element fracture, a fluid solver, or unrestricted energy transmutation. New functionality should extend shared material and physics behaviour before introducing additional convenience names.
