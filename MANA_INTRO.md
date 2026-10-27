# MANA — An Introduction to the Magic System

**Edition:** MANA 2.0.0 foundations  
**Purpose:** explain the magic before explaining the programming language.

The foundational concepts are mana, the four base elements, spells, targets, matter, world laws, planes, pathways, beings, summoning, and necromancy. This introduction explains what those ideas mean in the magical world before describing their source-language counterparts.

MANA is a magic system built around a simple premise: **magic is the deliberate shaping of an ever-present medium into changes in matter, motion, living beings, and the relationships between worlds.** A spell is not merely a special word that causes a hard-coded animation. It is a deliberate magical operation with a target, an intended effect, constraints, and consequences in the world.

The system is designed so that a firebolt, a ward, a gust of wind, a conjured iron guardian, or the arrival of a creature from another plane can be understood through the same connected foundations. The visible effects may differ enormously, but they still act through a shared world: mana is the magical medium; elemental modes describe fundamental kinds of interaction; objects and beings carry state; world laws determine physical outcomes; planes describe where a being or source belongs; and pathways describe which connections are available.

This is a guide to that model. It deliberately begins with the meaning of magic, not syntax. MANA is also implemented as a programming language, but code is the way a practitioner describes magic to the runtime—not the definition of magic itself.

## 1. The shape of magic in MANA

Magic in MANA is easiest to understand as several layers working together.

1. **Mana is the underlying medium.** It is present throughout the world and is not treated as a private battery carried by each caster.
2. **An operation gives mana a purpose.** It may push, pull, protect, illuminate, heat, cool, shape, form a construct, or influence an existing target.
3. **A target gives the operation somewhere to act.** It may be an object, a region, a physical material, a living being, or a world-state property.
4. **Elemental modes and specialised channels describe the nature or source of an effect.** Fire, Water, Earth, and Air are the four fundamental elements. Other concepts and plane channels have separate meanings.
5. **The world determines the result.** Motion, collision, matter state, temperature, and energy bookkeeping are decided by runtime rules, not by the illustration shown on screen.
6. **A spell composes operations into one intention.** It can be simple or combine many operations, checks, and effects.

These layers should not be confused. Fire is not mana itself. A plane is not a spell. Summoning is not conjuring metal. A shape is not a living creature. A spell's name is not proof that the implementation contains every behaviour associated with that name.

## 2. What is mana?

Mana is the general magical medium from which magical work is expressed. The established MANA model treats it as omnipresent and inexhaustible at the worldbuilding level: a caster does not begin a scene with a personal tank of mana, spend the last unit, and then need to recharge it before casting again.

That does **not** mean every result is free of consequence. Physical energy and material properties still matter. Moving a massive object is different from moving a feather. Heating iron is different from heating air. A barrier must resist the force applied to it if it is intended to act as a physical barrier. A conjured object occupies space and participates in the world model. The runtime records energy input, output, and transfer so that effects cannot silently bypass all accounting just because mana is inexhaustible.

Think of mana as the medium that allows an operation to be performed, not as an excuse to ignore the result of that operation. A spell can be possible and still be poorly designed, physically ineffective, out of range, blocked, invalid for its target, or limited by a currently unsupported rule.

### Mana and physical energy are different concepts

MANA records quantities such as joules, watts, mass, velocity, and temperature when they are relevant to the current simulation. Those values are numerical bookkeeping and simplified physical state. They are not a declaration that mana itself is stored in joules or that the caster owns a finite quantity of those joules. Plane-channel accounting likewise records transfers; it is not a battery meter.

The prototype does not implement a complete field theory of magic. Its energy ledger is an auditable model of supported operations, not a scientific claim that all magical phenomena have been explained.

Further reading: [Mana, Matter, and Energy](docs/current/foundations/MANA_AND_ENERGY.md).

## 3. The four fundamental elements

MANA has exactly four fundamental base elements: **Fire, Water, Earth, and Air**. These are the base set; Ice, Metal, Lightning, Life, Death, Shadow, and Void are not additional base elements merely because they appear in catalogues or stories.

The four elements are best understood as foundational modes of interaction, not simply colours or damage labels. They can influence which material or behaviour an effect expresses, but they do not replace the operation itself: an elemental effect still needs to do something.

### Fire

Fire is associated with heat, temperature change, combustion, ignition, reaction, expansion, and radiance. It is a natural mode for heating, starting a burning state, releasing heat, and producing a visible flame-like effect. In the current world engine, a material can ignite when a heat operation crosses its supported ignition threshold. That is a state change, not a full simulation of fuel consumption, spreading flame fronts, smoke chemistry, or fire-driven structural collapse.

### Water

Water is associated with flow, fluidity, absorption, cooling, pressure, adaptability, and purification. It gives a conceptual basis for moisture, wet surfaces, cooling interactions, and fluid-like behaviour. The current model supports wetting and selected material interactions, but it is not a complete fluid solver: it does not calculate all fluid pressure, turbulence, splashing, buoyancy, or liquid volume movement.

### Earth

Earth is associated with solidity, structure, density, stability, strength, and resistance to change. It is the foundational mode most naturally associated with stone-like material, solid forms, and defensive structures. Earth does not automatically mean every rock, metal, or wall has fully simulated geology or fracture mechanics; physical materials have their own profiles and supported behaviours.

### Air

Air is associated with movement, gas, speed, pressure, vibration, flow, and manipulation. It is a natural foundation for pushes, gusts, motion-related effects, and atmosphere. MANA's world engine can use wind as an environmental input to drag, but the current engine is not a full aerodynamics or computational-fluid-dynamics simulator.

### Elemental interaction

Elements can interact, combine, reinforce one another, or cancel under defined rules. The implementation contains a limited, explicit interaction table. For example, Water with Earth can produce Mud; Water and Air can produce Ice when the required heat-removal condition is supplied; Fire and Water have a cancellation/thermal-release outcome; and other pairings may become a generic compound rather than a specialised product.

These rules are deliberately explicit. An unlisted pairing should not be assumed to have a sophisticated hidden reaction. See [Elements and Implemented Rules](docs/current/reference/ELEMENTS_AND_RULES.md) for the exact current behaviour.

## 4. Concepts, derived entries, and special channels

A concept is an area of magical meaning, not automatically a new fundamental element. Light, Darkness, Life, Death, Order, Entropy, Spirit, Soul, Space, Time, and Void appear in the conceptual catalogue. Lightning, Sound, Metal, and Nature appear as derived or specialised catalogue entries. The exact catalogue is described in [Elements and Concepts](docs/current/foundations/ELEMENTS_AND_CONCEPTS.md).

The distinction matters:

- **Element:** one of the four fixed foundational modes.
- **Conceptual domain:** an area of magical meaning, such as light, identity, life, or temporal sequence.
- **Derived/specialised entry:** a catalogue identity associated with a combination or specialised field; it is not automatically a fully general derivation system.
- **Plane or channel:** a source or cosmological location that may be relevant to specialised magic.
- **Operation:** what the magic does, such as pushing, binding, heating, or changing a material.
- **Effect:** the resulting state or event, such as a barrier forming or an object becoming wet.

For example, a record named “Time” does not grant arbitrary time travel. The runtime has time advancement and scheduled events, but this is not equivalent to unrestricted temporal rewriting. Likewise, a Life entry does not mean every form of healing, growth, biological repair, and resurrection is implemented. Null is a separate worldbuilding concept and must not be silently equated with the current Void entry.

Certain non-base elemental/special channels require invocation permission before direct use. The invocation is an access rule for a channel, not a mana payment. Supported direct creation rules and exceptions are documented in the element reference.

## 5. What is a spell?

A **spell** is a named, reusable arrangement of magical operations that expresses an intention. A spell may have a single effect, or it may coordinate many effects, checks, target rules, and timing decisions. It can be simple—produce a burst of force—or complex—select a target, create a protective field, change the environment, conjure material, and then apply a physical operation to the resulting object.

The spell is not necessarily an ancient word with a fixed immutable effect. In MANA, named spell definitions are reusable authored procedures. One spell can be adapted, and distinct spells can share the same underlying operations. This is why MANA avoids requiring a separate hard-coded engine function for every fantasy ability.

A spell commonly has these conceptual parts:

- **Intent:** the desired outcome—push, bind, guard, illuminate, cool, transmute, summon, and so on.
- **Target:** the object, being, or state that will be affected.
- **Method:** the operations used to produce the result.
- **Parameters:** magnitude, direction, shape, duration, material, or other supported properties.
- **Conditions:** circumstances that must hold for the operation to be valid.
- **Consequences:** resulting changes to the object, environment, world state, or energy ledger.
- **Execution decision:** whether the spell is being previewed or committed.

A spoken incantation, gesture, wand motion, rune, or ritual may exist in a fictional setting as the means by which a caster focuses intent. Those are presentation and worldbuilding ideas. The MANA runtime does not require spoken audio, gesture-recognition, or a particular wand animation for its spell logic.

### A spell is more than its visual effect

A fireball graphic does not prove a target was hit. A glowing shield does not prove it absorbed an impulse. A summon animation does not prove the being exists in the world state. The runtime's records and physics rules establish whether an object was created, a spell committed, or contact occurred. The Visualiser should show these events faithfully instead of deciding the result by appearance.

### Preview and release

MANA provides two important execution intentions:

- **`post(spell)`** previews a spell in an isolated trial. It can produce a trace or hypothetical visual events, but those trial changes must not become committed world state.
- **`release(spell)`** commits a successful spell's supported effects to the world. If validation or execution fails, the runtime uses the supported transaction/rollback rules so partial changes are not mistakenly treated as a successful release.

This division permits experimentation: test the idea, inspect the proposed result, then release it when the spell is ready. Preview is not a weaker kind of release; it has a different state-commit rule.

## 6. Caster, target, and target context

A caster is the source of intent in a spell. In the current Visualiser the caster is a drawn scene actor, not necessarily a full runtime-controlled physical being. The spell system and world engine are responsible for recorded effects and contacts.

A target is the entity or world property an operation intends to affect. Targeting should be separated from the inner mechanics of a spell so that a spell can be reused against different objects. MANA uses `tgset` for target/profile context, with selection context placed outside the spell body. Target profiles are anchored by default in the current design, which is useful for a stationary training dummy or guard; movement must be explicitly enabled or applied where supported.

Targeting and collision are different:

- **Target selection** answers which entity the spell is directed toward.
- **Trajectory** describes where a travelling effect moves.
- **Collision** is a world-engine event when the moving effect actually reaches a surface or target.
- **Impact response** is the physical or magical result of that contact.

A spell can target an entity and still miss. An effect can collide with a barrier before reaching its intended target. The visualiser therefore stops the recorded projectile at its recorded contact point rather than making every target-directed effect pass through the scene.

## 7. Pure mana and universal manipulation

Not every operation requires an element. Pure mana and universal control describe effects that manipulate an object or manifest an abstract construct without treating Fire, Water, Earth, or Air as an obligatory label.

Current pure-mana primitives include prototype operations for:

- forming a supported mana construct;
- producing a burst or pulse;
- emitting a directed energy/beam-like effect;
- controlling motion or changing velocity;
- pulling, pushing, or applying other supported universal manipulations;
- establishing a barrier or a geometry-like mana form where the supported primitive allows it.

This is a compositional foundation. The same control idea can be used against a stone, a conjured metal object, or a being, subject to the target and the operation's validations. The runtime does not yet model every persistent control effect as a full controller or solve every possible magical field interaction.

For the exact functions and limitations, see [Universal Control and Pure Mana](docs/current/foundations/UNIVERSAL_CONTROL_AND_PURE_MANA.md) and [the Mana Library](docs/current/libraries/MANA_LIBRARY.md).

## 8. Matter: existing objects and conjured material

MANA distinguishes between using an existing object and bringing a new material object into existence in the local world.

A physical world object has state. Depending on its type and supported properties, this may include position, velocity, mass, volume, density, temperature, material, collision data, integrity, and lifecycle state. The engine can advance the object's motion and check contact against other objects. Profiles and catalogues describe data; only an active world object participates in simulated motion and collision.

### Conjuration

**Conjuration creates physical material.** It can produce a supported material object such as iron, steel, gold, copper, stone, wood, glass, crystal, ice, or water. A conjured object has physical properties rather than being only a drawing. Its mass and material data influence the world's representation and accounting.

Conjuration does not create a creature from a plane. That is summoning. A conjured golem-shaped metal body is initially matter; it is not automatically a living golem, a being record, or an intelligent actor. Its represented form, behaviour, and biological status are distinct questions.

### Transmutation

**Transmutation changes composition.** It may turn a supported iron object into gold or change a supported material to another registered composition. MANA's current prototype preserves mass by default and recalculates supported derived properties such as volume, density, and collision size. This is a simplified material conversion model, not atomic-level chemistry, isotope physics, metallurgy, or nuclear transmutation.

### Shape

**Shape changes geometry.** It can change the represented outline or primitive form of an existing supported object—for example, to a wall, ring, disc, beam-like segment, or other recognised geometry. Shaping an ordinary object is not the same as turning it into a living creature.

### Transfiguration

**Transfiguration changes represented form.** Under the established MANA design boundary, it is intended for living entities or matter explicitly created through conjuration. It can change the represented form family—such as a humanoid, knight, bird, serpent, beast, or golem-like shape—without replacing the underlying entity identity. It does not mean a normal existing wall can be declared a living bird merely by changing a string. The current implementation is a prototype: form graphics and scale are supported, but biological viability, anatomy, consciousness, reproduction, and complete organ systems are not simulated.

The four concepts stay separate:

| Operation | Main question | Example outcome |
|---|---|---|
| `conjure` | What new material object appears? | A mass-bearing iron block appears. |
| `transmute` | What is the object's composition? | The iron object becomes gold while following mass rules. |
| `shape` | What geometry does this object have? | The block becomes a ring or wall-like form. |
| `transfigure` | What supported living or conjured form does it represent? | A conjured metal body takes a knight-like form. |

The [World Weather and Matter reference](docs/current/libraries/WORLD_WEATHER_AND_MATTER.md) details the supported material operations and their limits.

## 9. Weather is an environmental state, not a catalogue of spells

MANA does not need one dedicated spell definition for rain, a second for wind, a third for fog, and another for clouds. Weather is a **parameterised world state**. A program can configure and combine atmospheric properties—precipitation, intensity, wind speed and direction, temperature, humidity, cloud cover, fog, heat factor, lightning intensity, and duration—without inventing a separate spell for every possible combination.

The `weather` library's job is to configure that state. A spell may choose to alter the weather as part of its behaviour, but rain itself is not inherently a spell. A scene may begin rainy; a wind may alter the motion of supported objects; precipitation may affect wetness; temperature and material properties may influence supported phase changes. The weather renderer then visualises recorded parameters.

Keep the responsibilities separate:

- **Weather controls** define environmental parameters.
- **World laws** define how those parameters interact with simulated matter and motion.
- **Spells** may change weather, but they are not the only way the environment can be described.
- **The visualiser** draws what the recording reports; it does not generate the physical truth.

Weather features such as cloud layers, fog density and lightning visuals are only partly physical in the current prototype. They should not be mistaken for a fully simulated atmosphere.

## 10. What is a being?

A being is a creature or entity with a recognisable identity, species or form, and potentially a home plane and supported properties. The catalogue may describe its kind, home plane, attributes, and initial stats. A **being record is data**: it describes a being but is not itself a moving creature in the simulated world. A being becomes an active scene object when a supported operation manifests it.

The current built-in records include various elemental/special-plane spirits and a smaller set of other species. Their numerical statistics are prototype values, not canonical universal laws. The project does not yet provide a complete general creature-AI system, strategic behaviour solver, ecology simulator, or comprehensive combat engine. A being can appear in the world without automatically knowing how to fight, navigate, reproduce, or make independent choices.

## 11. What is summoning?

**Summoning brings a defined being into the current world from a known source or plane through an available route.** It answers a different question from conjuration:

- Conjuration manifests physical matter.
- Summoning manifests a being described by the creature/plane data and supported by a route.
- Reanimation changes the state of existing remains.

Summoning therefore depends on identity and origin. The runtime needs to find a being record, identify the source plane, and check whether an appropriate open pathway is available. A plane name by itself is not a creature, and a creature name without a matching record is not enough to manufacture a valid summon.

The `summoning` library performs the supported cross-plane bringing operation. In the current implementation, the general `bring()` operation manifests the being in the Mortal Plane. This is a starter framework for identity, route and arrival; it is not a full population simulator or creature AI. Other interactions—naming, taming, recalling, or sending a being back—have their own support and limits.

A user-authored spell may coordinate a summoning operation, but “summon a skeleton” is not a magic built into every version of the language as a dedicated hard-coded keyword. The user's spell defines the sequence and calls the relevant operation.

Read [Beings and Summoning](docs/current/foundations/BEINGS_AND_SUMMONING.md) and [the Summoning Library](docs/current/libraries/SUMMONING_LIBRARY.md).

## 12. What is a plane?

A **plane is a distinct cosmological place or domain**. It can be associated with a fundamental element, a specialised channel, a realm of beings, or another named region of the setting. A plane has identity: it can be named, categorised, located in the registry, associated with beings, and connected to other planes through pathways.

A plane is not the same as:

- an element (Fire as a base elemental mode versus the Fire Plane as a location/channel);
- a creature (an elemental spirit may be recorded as living in a plane, but is a separate being record);
- a pathway (a route connects locations, but does not define either endpoint);
- an effect (summoning, invocation, or energy transfer is an operation involving a plane);
- a portal visual (the Visualiser does not present a portal-based map or a plane-travel editor).

The plane registry tracks identities, categories, regions, and pathway relationships. Pathways can have properties such as direction/open state and can be considered for reachability. The planes library handles identification, routes, invocation permissions and energy-transfer bookkeeping. The summoning library uses the supported route and being data to bring an entity into the local simulation. These responsibilities are separate so that defining a place does not secretly define its physics or all of the inhabitants' behaviour.

The `drafter` library can define custom plane data during a runtime session, including properties, regions and beings. That data is not automatically a persisted world editor project after the session ends. A plane catalogue entry also does not mean that every associated power is implemented. The current project is a 2D world engine; plane cosmology is data and route logic, not a fully visualised multidimensional simulator.

Read [Planes and Pathways](docs/current/foundations/PLANES_AND_PATHWAYS.md) and the [Plane Catalogue](docs/current/foundations/PLANE_CATALOGUE.md).

## 13. What is a pathway?

A pathway is a defined connection between plane records or supported regions. It records that a route exists and may express whether movement is directional, whether the connection is open, and which route is available. A pathway is a relationship in the registry; it is not automatically a physical tunnel with geometry in the 2D arena.

The route system can identify reachability and choose supported paths. The planes library also records energy transfer along a pathway. That accounting should not be confused with summoning a creature: energy transfer and being movement are related cosmologically, but the runtime uses separate operations for them.

A closed or unavailable route should block operations that require it. Being records also matter: the existence of a road between two locations does not create a being that has never been defined.

## 14. Necromancy and reanimation

Necromancy has a strict boundary: **reanimation acts on existing remains**. A corpse, bones, skeleton or other accepted remains object must already exist and be identified by the runtime as a body. Merely renaming a rock to “corpse” must not turn it into valid remains. Reanimation changes the object's animation/being state and records the relevant Necro/Underworld channel accounting.

Reanimation is not summoning. Summoning brings a defined being through a route. Reanimation animates an existing body. A constructed undead creature may be described by an ordinary spell composed from supported primitives, but there is no magic shortcut that makes a missing corpse appear from nothing just by calling it “undead.”

The current necromancy library does not implement a universal soul metaphysics system, restoration of a person's complete memories, moral alignment, afterlife simulation, or autonomous undead intelligence. Those are possible worldbuilding questions; they should not be claimed as engine capabilities.

See [Necromancy and Undead](docs/current/foundations/NECROMANCY_AND_UNDEAD.md).

## 15. Magic and the laws of the world

MANA attempts to make the world respond consistently to supported actions. The current 2D engine contains simplified laws for motion and contact: gravity, mass-aware acceleration, swept collision checks, restitution, tangential friction, wind drag, thermal exchange, material phase changes and surface wetting/dust effects. It also tracks selected state changes and physical-energy bookkeeping.

The rules are not complete natural science. They are an explicit, evolving simulation model. Collision geometry is simplified; the world is 2D; object integrity is calibrated; pressure-dependent chemistry, combustion propagation, full fluid motion, spin and rolling friction, detailed biological simulation, and a fully coupled electromagnetic or magical field solver are not present as complete general systems.

A spell can be conceptually powerful while its implementation remains partial. MANA's documentation should distinguish three statements:

- **Worldbuilding rule:** what the magic system is intended to mean.
- **Runtime rule:** what the current engine validates and calculates.
- **Visual convention:** how the optional Visualiser depicts a recorded event.

These are connected, but never interchangeable.

## 16. Examples as magical ideas

The following are conceptual descriptions rather than promises about every current implementation detail.

### A firebolt

The caster directs a fire-associated effect toward a selected target. The spell expresses a trajectory and impact intent. The world engine advances the projectile and determines whether it reaches a target, barrier, or surface. If contact occurs, the supported impact response changes the world state. A graphic of flame alone is not the hit test.

### A ward

The caster establishes a defensive construct or protection state. The result should be evaluated by the type and strength of the supported barrier and by the incoming interaction. A convincing blue bubble is only the presentation; recorded blocking, absorption or collision is the physical result.

### A wind change

The atmosphere is configured with wind speed and direction. It does not require a dedicated “wind spell” function. If drag is enabled and the material/object has supported area and movement state, the world engine can use relative wind in the force calculation. The visualiser may draw drifting streaks, but they do not cause the motion.

### A forged guardian

A spell may conjure a metal object with mass, position and material properties. It may then transfigure the conjured matter into a supported guardian-like form. The result is a physical object with an appearance; animation as a creature, cognition and independent behaviour are separate features and are not implied solely by the form label.

### A summoned spirit

The program identifies a being record and its home plane, checks the route, and asks the summoning library to bring the being into the world. The being's identity originates from the catalogue, not from material creation. Its later actions still require supported behaviour or authored spell logic.

### A reanimated skeleton

The world already contains remains accepted by the necromancy rules. Reanimation changes that object's supported state and records the channel bookkeeping. The process is distinct from bringing a new being from a plane.

## 17. How the programming language expresses magic

Only after understanding the system does the source language become easier to read. `spell` defines a reusable spell in MANA's primary syntax (with `spldef` retained as a legacy alias); ordinary `def` defines a reusable helper; `tgset` sets a target context or profile; `appraise` records a non-committing trial; `cast` commits it; `incant` supplies a definition's result. The older `post(spell)` and `release(spell)` forms remain supported. `load` makes a supported library available. `shape`, `conjure`, `transmute`, and `transfigure` each have different responsibilities.

The language is custom: MANA programs are stored as `.mana` files and use MANA syntax and semantics, even though the present interpreter is implemented in Python. Python is the implementation language, not the language the practitioner writes spells in. The Visualiser is optional and replays a recording; it is not required to run a MANA source file.

Start with [the Magic System Compendium](docs/current/foundations/MAGIC_SYSTEM_COMPENDIUM.md) for the conceptual reference, then the [Language Guide](docs/current/getting_started/LANGUAGE_GUIDE.md) for syntax and [Building Your First Spells](docs/current/getting_started/BUILDING_FIRST_SPELLS.md) for executable examples.

## 18. Quick glossary

| Term | Meaning in MANA |
|---|---|
| **Mana** | Omnipresent magical medium; not a finite personal pool or one of the four base elements. |
| **Element** | One of the four fundamental modes: Fire, Water, Earth, Air. |
| **Conceptual domain** | A field of meaning such as Life, Light or Time; not automatically a base element or complete power system. |
| **Spell** | A reusable arrangement of supported magical operations. |
| **Caster** | The source of a spell's intent; not necessarily a simulated physical actor in every runtime. |
| **Target** | The object, being or world state the operation intends to affect. |
| **Effect** | A resulting change or manifestation produced by an operation. |
| **Conjure** | Manifest a new physical material object. |
| **Transmute** | Change an object's material composition under defined rules. |
| **Shape** | Change supported geometry. |
| **Transfigure** | Change the represented form of a living entity or eligible conjured matter. |
| **Summon** | Bring a defined being into the current world using supported plane and route logic. |
| **Reanimate** | Animate existing accepted remains; not the same as summoning or conjuration. |
| **Plane** | A named cosmological location/domain in the registry. |
| **Pathway** | A registered connection used for route/reachability and supported energy transfer. |
| **Invocation** | Permission to use a supported special channel; not a finite mana payment. |
| **World law** | A physical default or rule that affects supported runtime behaviour. |
| **Preview (`post`)** | Trial execution whose hypothetical changes do not commit as world state. |
| **Release** | Successful committed execution of a spell. |
| **Visualiser** | Optional renderer for recorded events; not the authority that decides physics. |

## 19. What exists now and what remains incomplete

MANA 2.0.0 includes a custom interpreter, spell execution modes, a 2D world engine, a limited set of elemental interactions, pure-mana primitives, target/object profiles, a material and periodic-data catalogue, parameter-driven weather controls, a plane registry/pathway system, built-in being data, cross-plane summoning, limited necromancy, 2D geometry and 3D vector calculation libraries, recordings, tests and optional VS Code support.

MANA is intentionally a 2D world simulation; `vector3d` supplies separate calculation helpers and does not imply 3D world movement or collisions. Other boundaries include a real-time interactive multiplayer world, complete creature intelligence, exhaustive elemental reaction graphs, a molecular chemistry engine, realistic fluid simulation, automatic biological viability, an unrestricted time/space magic solver, and a persisted visual plane editor. These limits keep the documentation aligned with behaviour the runtime actually supports.

The detailed source of truth for current capability is [Implementation Status](docs/current/foundations/IMPLEMENTATION_STATUS.md), backed by the function references, runtime code, examples and tests. The [Magic System Compendium](docs/current/foundations/MAGIC_SYSTEM_COMPENDIUM.md) expands the conceptual system without pretending that every piece of fantasy lore is already executable.


## The language's native magic syntax

MANA uses indentation and colons for blocks; it does not use curly braces. New code should declare magical behaviour with `spell name():`, while existing `spldef name():` programs remain valid. The statement `weather rain, intensity=0.8, radius=80 m, duration=30 s` expresses an area-local climate effect directly. Omitting `radius` affects global world climate; supplying a radius confines environmental effects to objects within that region. `name = conjure steel, mass=5 kg, shape=sphere` is the readable native form for manifesting ordinary matter.

MANA's role is to define, execute, record, and appraise magical operations. The `appraise spell` mode previews and records the changes without committing them; `cast spell` commits them. The legacy `post(spell)` and `release(spell)` forms remain valid. Mana-related output is a calculated cost/appraisal readout, not a consumable personal battery required before each cast. Physical energy, material identity, object limits, environmental effects, and world-law outcomes remain recorded and validated.


## MANA's native spell verbs

MANA's primary surface is not intended to be a thin wrapper around a library. A spell can be written with an indented declaration, environment statements, direct matter statements, and a clear appraisal/cast boundary:

```mana
spell rain_circle():
    weather rain, intensity=0.8, wind_speed=8 m/s, duration=30 s, radius=80 m
    iron = conjure steel, mass=5 kg, shape=sphere
    shape iron into ring
    transmute iron into bronze
    incant iron

appraise rain_circle
cast rain_circle
```

`appraise` runs the spell as a recorded trial and restores the hypothetical world changes. `cast` commits a successful execution. Mana values in the resulting record are an appraisal of effort, not a finite personal battery used up to unlock casting. The environment, matter, energy, motion, collisions, and world laws determine the real outcomes.

The direct transformation statements are `shape object into geometry`, `transmute object into material`, `transform object into phase`, and `transfigure object into form`. Bare destinations are names from the relevant catalogue; put a calculated destination in parentheses, e.g. `transmute ingot into (chosen_material)`. These are real parser forms, not special text preprocessed by the editor. The traditional call syntax stays available when a spell needs operation-specific options.


## Native language: summoning is not conjuration

MANA keeps the distinction between creating matter and bringing a being into the world. `conjure` defines physical material, mass, geometry, state and contact behaviour. `summon` refers to an existing being record and requires a valid pathway from its home plane. This prevents a named creature from being manufactured accidentally out of an arbitrary material description.

```mana
load planes
planes.open_path("Wild Realm", "Mortal Plane")

spell call_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    incant griffin

appraise call_griffin
cast call_griffin
```

`appraise call_griffin` records a hypothetical execution without keeping its world changes. `cast call_griffin` commits the successful summon. Use `summon (chosen_being) from (chosen_plane)` when a name comes from a variable. The `summoning.bring(...)` form remains available for lower-level library work, but native MANA source should prefer the language verb. A conjured metal griffin remains matter unless the relevant form, living status, behaviour, and transformation rules explicitly establish more.

## Further reading: matter and living forms

For practical material, metal, weapon, armour and periodic-table behaviour, see [Materials and Forging](docs/current/libraries/MATERIALS_AND_ARMORY.md), [Anatomy and Comparative Biology](docs/current/libraries/ANATOMY_LIBRARY.md), [Comparative Anatomy Research](docs/current/libraries/COMPARATIVE_ANATOMY_RESEARCH.md), and [Arcana: Magical Disciplines](docs/current/libraries/ARCANA_LIBRARY.md). For organs, body systems, blood control, transformation, death, revival and lich states, see [Physiology and Body Magic](docs/current/libraries/PHYSIOLOGY_LIBRARY.md). For a separate design catalogue of original magical concepts inspired by broad MCU/DC themes, see [MANA Magic Inspiration Catalogue](MANA_MAGIC_INSPIRATION_CATALOGUE.md). Those inspired concepts are marked by implementation status so design ideas are not confused with available runtime features.
