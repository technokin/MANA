# Physiology and Body Magic

**Page kind:** Runtime library reference  
**Status:** Implemented game-state model with deliberately simplified biology

The `physiology` library makes a being's body a structured object rather than a single hit-point number. A spell can inspect a body, alter an organ's integrity, influence a whole system, change blood state, enhance a trait for a limited duration, change an eligible form, cause death, attempt revival, or hand off to the necromancy library for an undead state. This is the foundation for self-magic, body morphing, blood manipulation, regeneration, and lich-like persistence.

**Important boundary:** MANA's body model is a fictional simulation interface, not a medical simulator. Integrity, oxygen saturation, blood volume and organ dependencies are game parameters. They should not be used to make real medical decisions.

## 1. A living being is still a world object

Bodies participate in world rules like other objects. A creature generally has a world-object identity and position, plus properties such as `living`, `is_being`, `is_summoned`, `life_state`, `hp`, `max_hp`, `species`, `body_form`, and `anatomy`. The physiology library creates missing anatomy fields on first use, preserving existing injuries and compatible species data. A dead body remains a physical object so it may be inspected, revived if eligible, or used by necromancy. An undead object is not the same state as a living object with low health.

Use `physiology.profile(target)` to inspect a compact body-state snapshot. `physiology.organs()` enumerates the defined organ catalogue, and `physiology.systems()` returns the mapping from named systems to the organs represented in each system. Snapshots are copies for inspection; change state through the supported operations rather than editing an arbitrary returned dictionary and expecting the world to update.

```mana
load planes
planes.open_path("Wild Realm", "Mortal Plane")
spell call_beast():
    beast = summon "Griffin" from "Wild Realm"
    physiology.profile(beast)
    incant beast

cast call_beast
```

Expected output:

```text
[CAST call_beast] ERROR: RuntimeErrorML: docs/current/libraries/PHYSIOLOGY_LIBRARY.md:16:5:5: 'physiology' is not identified
```

Summons have route and catalogue requirements. For a project-owned entity, pass the actual world object that is marked as living/being/targetable; a decorative canvas sprite is not a body.

## 2. The organ model

Every tracked organ has a name, a system, a role and an integrity from 0 to 1. Integrity is an abstract availability/condition factor, not a literal percentage of anatomical tissue remaining. Lower integrity can reduce a connected trait or system's effective performance; a value near zero means the corresponding function is severely impaired under the current model.

### Nervous system

- `brain`: awareness, memory hooks, and reflex integration.
- `brainstem`: breathing, wakefulness, and autonomic reflexes.
- `cerebellum`: coordination, balance, and motor learning.
- `spinal_cord`: signal relay between brain and body.
- `peripheral_nerves`: voluntary motion and sensory signalling.
- `autonomic_nerves`: automatic circulation, breathing, and digestion control.

These parts let magic target awareness, reflexes, sensory throughput or movement as a defined body operation. The current model does not simulate individual neurons, memory contents or detailed neural circuits.

### Circulatory and blood model

- `heart` and `heart_valves`: pump/flow availability and one-way circulation.
- `arteries`, `veins`, and `capillaries`: delivery, return and tissue exchange.
- `blood` and `blood_plasma`: circulating transport medium and fluid volume.
- `red_blood_cells`: abstract oxygen-carrying capacity.
- `spleen`, `bone_marrow`, and `stem_cells`: filtering, blood-cell production and a bounded repair reserve.

Separate body fields track blood volume in litres, maximum modelled volume, externalised blood, ongoing blood-loss rate, clot state and oxygen saturation. These values make spells such as `Blood Bind`, `Draw the Red Thread`, `Clot`, `Restore Blood`, and `Purge` composable from a small set of state transitions. They do not simulate blood as a per-particle fluid.

### Respiratory system

`lungs`, `diaphragm`, `air_sacs` and `gills` model compatible gas-exchange organs. Oxygen saturation changes with the supported model and can lead to an abstract oxygen-debt effect during world advancement. Morphing into an aquatic or avian form must not be treated as a simple skin swap: the target form's anatomy and movement profile determine whether gills, air sacs, wings or fins are present, while the current solver remains simplified.

### Metabolism and waste handling

`liver`, `kidneys`, `bladder`, `stomach`, `intestines`, `pancreas`, `endocrine_system`, `thyroid` and `adrenal_glands` represent metabolism, filtering, digestion and slow regulation. Toxicity is a normalised fictional burden. Liver/kidney availability influences its rate of reduction during simulation. This is a roleplay/game-state abstraction, not a chemistry model of a real organism.

### Structure and movement

`skeleton`, `skeletal_muscles`, `cartilage`, `tendons`, `ligaments` and `connective_tissue` contribute to the musculoskeletal group. The current world is 2D, so body traits adjust supported movement/damage properties rather than simulating full skeletal articulation, gait, inverse kinematics or 3D balance. Movement capabilities also have explicit form tags such as terrestrial, flight-capable, swim-capable, slither-capable, amphibious and stationary.

### Protection, senses, immunity and specialised parts

`skin` represents the outer interface and protection. `eyes`, `ears`, `inner_ear` and `tongue` are sensory organs. `immune_system`, `lymphatic_system` and `lymph_nodes` are abstract defence/recovery components. `wings`, `tail`, `gills`, `fins`, `venom_gland` and `reproductive_system` are optional or species-specific organs. An organ's inclusion gives the runtime a place to attach effects; it does not automatically implement a full independent biological process for every named organ.

## 3. Body systems and cascading effects

`physiology.systems()` maps organs into named groups such as `nervous`, `circulatory`, `respiratory`, `digestive`, `excretory`, `musculoskeletal`, `integumentary`, `sensory`, `immune`, `lymphatic`, `endocrine`, `blood_production`, `locomotion` and `reproductive`.

`physiology.injure(target, "heart", 0.4)` reduces one organ's integrity. `physiology.injure_system(target, "circulatory", 0.25)` reduces integrity across the organs assigned to that system. `heal` and `heal_system` restore integrity up to 1.0, but ordinary healing cannot revive a dead body; use `revive` for that explicit transition or the necromancy library for undead animation. Each operation updates derived traits and records an entity/magic event, so a spell can use event handlers and the Visualiser to inspect consequences.

The current system uses explicit, bounded dependencies rather than a complete biochemical network. For instance, severe circulatory impairment can worsen oxygen supply; respiratory impairment can contribute to oxygen debt; blood loss can reduce HP and consciousness; and sustained bleeding can eventually cause death during time advancement. It does not yet simulate all emergent disease, immunity, hormones, organ feedback loops, detailed wounds, or long-term ageing.

## 4. Self-magic and trait enhancement

A body does not have to be transformed into a different creature to be magically changed. The library supports temporary enhancement of:

- `strength`: multiplier applied to supported force-related body properties.
- `speed`: movement-speed multiplier.
- `endurance`: longer sustained activity in the model.
- `durability`: body damage reduction.
- `senses`: abstract perception enhancement.
- `reflexes`: abstract response multiplier.
- `regeneration`: passive modelled HP recovery.
- `recovery`: how quickly selected states recover.

An enhancement is time-limited and bounded. The current interface permits a factor from 1 to 5 and a duration no greater than 60 seconds, with a limited number of simultaneous enhancement records. Repeated casting does not grant an infinite stack: concurrent effects are bounded and effective properties are recalculated from their base values. A spell still has to perform supported operations; an effect name such as “Titan Strength” does not create strength by itself.

```mana
load planes
load physiology
planes.open_path("Wild Realm", "Mortal Plane")
spell giant_stride():
    target = summon "Griffin" from "Wild Realm"
    physiology.enhance(target, "strength", factor=2.5, duration=12 s)
    physiology.enhance(target, "durability", factor=1.8, duration=12 s)
    physiology.enhance(target, "endurance", factor=2.0, duration=12 s)
    incant target
cast giant_stride
```

Expected output:

```text
[CAST giant_stride] spell committed
[CAST giant_stride] mana appraisal: 0 mana
```

The trait multipliers affect only properties and calculations that the engine already connects to those traits; they are not a blanket override of every action in the world.

### General body propulsion

`physiology.propel(target, direction, speed, mode="physical")` is a shared movement operation. It is not a built-in jump spell, sprint spell, or anime-specific speed ability. A user-defined spell can use it to launch, run, take off, swim, or move in another direction that the 2D world supports. Direction is a dimensionless 2D vector; speed must have velocity units. The body's enhancement traits can affect the applied speed.

- `mode="physical"` checks the proposed motion against the body's current integrity-energy threshold before changing its velocity.
- `mode="arcane"` explicitly treats the movement as magically supported, allowing high-speed movement without the carrier collapsing from its own bulk translational-energy stress. Normal world collisions and the remaining engine rules still apply. This is not a complete relativistic collision model.
- For a massive body, the applied speed is capped strictly below the speed of light, even when the spell requests a value at or beyond that boundary. It does not implement a physically ordinary run at exactly `c` or faster-than-light motion.

A multi-storey leap can be composed from an anatomy-bound body, temporary enhancement, an upward propulsion operation, gravity, and world time advancement. No dedicated `multi_story_jump()` operation is needed:

```mana
load planes
load anatomy
load physiology
load geometry2d
planes.open_path("Wild Realm", "Mortal Plane")
world.configure(gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
spell multistory_leap():
    body = summon "Griffin" from "Wild Realm"
    anatomy.bind(body, "griffin")
    physiology.enhance(body, "strength", factor=2.0, duration=10 s)
    physiology.propel(body, geometry2d.direction(0, 1), 20 m/s, mode="arcane")
    incant body
cast multistory_leap
advance_time(0.5 s, timestep=0.01 s)
```

Expected output:

```text
[CAST multistory_leap] spell committed
[CAST multistory_leap] mana appraisal: 324000 mana
```

This example demonstrates vertical launch under gravity; it does not prove that MANA has a full humanoid skeletal gait solver or a 3D multilevel collision world. A user-authored spell can combine propulsion with `impulse`, velocity, acceleration, landing checks, body enhancement, and additional validation as those mechanics are available.

## 5. Blood magic

`physiology.blood_state(target)` reports the current blood-state subset. `physiology.manipulate_blood(target, mode, intensity=..., duration=..., amount_l=...)` supports a bounded group of state changes:

- `bind`: records a temporary blood-control effect and may strain consciousness at high intensity; it does not let a spell author bypass object validation.
- `draw`: removes a bounded amount from the modelled blood volume, records it as an externalised pool, and may injure or kill if the body's remaining state crosses critical limits.
- `clot`: stops the supported ongoing blood-loss rate and clears the current binding state.
- `restore`: returns a bounded amount from the externalised pool and improves the supported volume/oxygen fields.
- `purge`: reduces the abstract toxicity burden by the requested intensity.

`physiology.set_bleeding(target, rate_lps)` sets a capped ongoing bleed rate. During `advance_time`, bleeding is progressed in small world steps; low blood volume or zero HP can cause the runtime's death transition. All these actions are fictional mechanics for MANA's internal world, not an instruction for real-world harm or medical treatment.

A “blood puppet” or “blood whip” spell is not a separate magical engine. It combines `manipulate_blood` with target/force restrictions and possibly a conjured externalised-blood material effect. If you want those effects to be persistent physical objects, the conjuration/material model needs to represent their mass, stability, and expiry rather than drawing a decorative line and treating it as physics.

## 6. Morphing and transfiguration

MANA distinguishes three transformations:

1. `shape(object, geometry)` changes geometry, for example a ring-shaped object into a shield-like geometry. It is the right choice for a normal sword or plate.
2. `transmute(object, material)` changes composition and refreshes material-derived density/volume/strength/conductivity fields while preserving the object's identity.
3. `transfigure(object, form)` changes supported represented form for a living body or eligible conjured matter. This is the form-changing path for self-morphing and constructed creatures.

`physiology.define_form(name, organs=[...], movement_mode=..., vital_structures=..., strength=..., speed=..., endurance=..., durability=..., senses=..., reflexes=..., regeneration=..., recovery=..., label=...)` registers a reusable body-form template for `transfigure`. The organ list accepts 3–1024 known structure names, and a runtime can register up to 128 custom forms. A typical living form must include a nervous/control structure and a circulation/transport structure or an appropriate clade-specific equivalent (for example earthworm cerebral ganglia with aortic arches or hemolymph). Fictional life-support models can explicitly supply `vital_structures=[...]`; those structures must be included in `organs`. The form validator no longer assumes every creature must literally possess a vertebrate brain and heart. In MANA source, define trait multipliers through named parameters such as `speed=1.6` and `senses=1.3`; MANA does not require Python-style dictionary literals. The legacy `trait_factors` mapping remains available to Python callers. A form template does not automatically implement all its listed organs or movement mechanics: it declares structure and trait priors which must be supported by runtime rules.

```mana
load physiology
load planes
planes.open_path("Wild Realm", "Mortal Plane")

spell register_winged_humanoid():
    physiology.define_form("Winged Humanoid",
        organs=["brain", "brainstem", "heart", "blood", "lungs", "skeleton",
                "skeletal_muscles", "skin", "eyes", "wings", "air_sacs"],
        movement_mode="flight-capable",
        strength=1.2, speed=1.6, endurance=1.2, senses=1.3)
    griffin = summon "Griffin" from "Wild Realm"
    transfigure(griffin, "Winged Humanoid")
    incant griffin

cast register_winged_humanoid
```

Expected output:

```text
[CAST register_winged_humanoid] spell committed
[CAST register_winged_humanoid] mana appraisal: 0 mana
```

That code registers the form template; it does not transform a person or generate flight physics on its own. To apply it, a spell must target a valid living body and call `transfigure(target, "Winged Humanoid")` within the supported runtime rules. The physics engine is 2D and the visual form is not a complete 3D skeletal mesh.

The body system retains a bounded anatomy archive across form changes so that supported injuries are not automatically erased when the visual shape changes back. There is no molecular/genetic model, and the runtime does not currently provide complete organ growth, pregnancy, complex species reproduction or independent organ simulation.

## 7. Injury, instant death and resurrection

`physiology.kill(target, cause="spell")` performs an immediate life-state transition for a valid living target. It marks the target dead, records the cause/time/count, sets HP to zero, preserves the body object, clears voluntary blood control and emits `being_died`. Lethal damage from supported combat paths can also trigger the death transition. A spell that requests instant death should explicitly invoke an accepted effect or call this operation inside the executed spell context; a flashy green particle is not a death rule.

`physiology.revive(target, vitality=0.35, restore_organs=0.1)` can return an eligible existing dead body to the living state when its body remains and its soul state is reachable. The current implementation allows at most three physiological revivals. It restores a bounded portion of HP, blood volume, oxygen saturation and organ integrity, and emits `being_revived`. This is a design restriction to keep resurrection consequential and predictable, not a universal rule for all magical systems.

For spell design, separate the stages:

- **Lethal effect:** marks a living entity dead according to the selected rule.
- **Recovery or revival:** restores a recoverable body and reachable soul to the living state.
- **Reanimation:** moves an existing corpse/bone/skeleton into an animated undead state; it does not make the target alive again.
- **Lichification:** binds the lich's persistent soul state to a phylactery/anchor, subject to the necromancy library's checks.
- **Reconstitution:** attempts to rebuild a lich after the supported body is destroyed, using its registered phylactery and route rules.

The distinctions matter. `physiology.revive` rejects a soul marked destroyed, consumed or bound to a phylactery. `necromancy.reanimate` requires actual existing corpse/remains markers. `necromancy.lichify` is a separate state transition, and `necromancy.reconstitute` is not equivalent to healing an ordinary living body. Consult [Necromancy Library](NECROMANCY_LIBRARY.md) for its full requirements and limits.

## 8. Soul and identity are not just organs

Body state and soul state are deliberately separate. A body can be intact while its soul is unreachable; a lich can persist with a destroyed body; an animated skeleton can move while not being alive; and a living body can be enhanced without changing its species. These statuses should not be collapsed into a single `alive=true` flag.

Relevant values include `life_state`, `is_dead`, `is_undead`, `body_present`, `body_condition`, `soul_state`, `revival_count`, `death_cause`, `death_time`, `necromantic_mana_type`, and the phylactery binding metadata used by the necromancy library. Some of these are internal properties maintained by the library; spells should prefer the documented library methods and use snapshots for inspection.

## 9. Events and reactivity

Body operations emit events such as `being_died`, `being_revived`, `being_lichified`, `being_reconstituted`, and `blood_changed`, alongside general entity and magic-effect observations. A spell system can subscribe to these to implement reactions: a ward might trigger on death, a curse might activate on blood-state change, or a phylactery ward might react when a lich's body is destroyed. Event handlers must remain bounded and should avoid recursively producing the same event forever; use explicit conditions and one-shot flags for chain reactions.

The event is an observation of a real state transition, not an automatic magical effect. MANA will not infer that every dead entity should revive or that every blood change should create a weapon. The spell author defines those reactions.

## 10. Recommended conventions for body-magic spells

- Validate that the target is a living body before applying living-only magic.
- Use a form template instead of assigning arbitrary species strings to `body_form`.
- Use organ and system names consistently, in snake_case.
- Treat body trait factors as multipliers on supported calculations, not as infinite overrides.
- Use a death/revival/reanimation/lichification state transition appropriate to the intended result.
- Keep persistent conjured matter separate from biological anatomy.
- Decide whether an effect expires, remains until countered, or requires an anchor. Give sustained effects a bounded duration or a clear release rule.
- Test a spell at partial organ integrity, low blood volume, dead-state, unreachable-soul and already-undead conditions—not only on a healthy default target.

## 11. Known limits and future work

The current body model already offers organs, named systems, injury/healing, body traits, forms, blood state, oxygen, temperature, toxicity, death/revival, and integration with lich/reanimation mechanics. It does not yet have a full biomechanical solver, detailed wound shapes, complete cardiovascular flow, genetic inheritance, organ transplant compatibility, cellular regeneration, immune pathogen dynamics, species life-cycle simulation, or anatomically precise hit zones. Those should be introduced as shared, tested state models—not as isolated “superpower” functions. The visualiser may display anatomy/effects, but it must never decide whether an organ failed or a body died; the runtime is authoritative.
