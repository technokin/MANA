# MANA Magic System Compendium

**Page kind:** Conceptual reference  
**Edition:** MANA 2.0.0 foundations  
**Purpose:** a magic-first reference that defines the central terms, relationships, and limits of the MANA world before the reader studies syntax.

This compendium describes the conceptual system and marks where the current runtime is narrower. A name in a fantasy catalogue is not, by itself, an implemented power. For exact code signatures, consult the function and library references linked throughout.

## 1. A compact model of the magical world

MANA treats magic as controlled interaction with an omnipresent medium. Its system can be described in six layers:

1. **Medium:** mana is present throughout the world and is available for magical work.
2. **Mode:** the four foundational elemental modes are Fire, Water, Earth and Air. Specialised or conceptual categories add vocabulary but do not change the fundamental set.
3. **Operation:** a caster or spell chooses what the magic should do—form, push, pull, protect, heat, cool, bind, conjure, change a material, alter a supported form, or call a being through a route.
4. **Subject:** the operation acts on a world object, being, material, or environmental state.
5. **Law:** the world runtime validates state and calculates supported physical consequences.
6. **Record:** events can be logged and visualised so that what happened is distinguishable from what was merely intended.

The same framework handles different scenes without turning every effect into a separate engine subsystem. A rock projectile and a metal projectile need not have unrelated movement code; they can share a motion operation while their material profiles remain different. A rainstorm and a fog bank need not be separate hard-coded spells; they can be atmospheric configurations with different parameter values.

## 2. Mana, energy, matter, and consequence

### Mana

Mana is the omnipresent medium used by magic. It is neither the fifth element nor a personal resource pool. The design does not give every caster a finite reserve that is depleted with each operation.

### Physical energy

The engine tracks selected physical energy values and provenance. These values help make changes inspectable: a transfer should be visible in the ledger; a material's temperature should affect supported phase transitions; motion depends on mass and forces. This is an accounting model for the current simulation, not an exhaustive explanation of magical energy in nature.

### Matter

Matter is represented by world objects and material profiles. Objects can have mass, volume, density, position, velocity, temperature, material/composition, shape, collision settings, integrity, and state. A data record without active world-object state is descriptive only. A plane record, for example, is not a boulder in the physics scene; a creature record is not a creature walking around until a supported manifestation operation creates an active object.

### Consequence

An inexhaustible medium does not eliminate constraints. A spell's target may be invalid, a pathway may be unavailable, an interaction may not be implemented, a barrier may fail under a supported contact rule, or a numerical state may be outside the allowed limits. The system aims to validate intent against available mechanisms instead of assuming that naming an effect forces it to happen.

## 3. The four base elements in detail

The base elemental set is fixed. A custom library or plane record cannot silently redefine it.

### Fire — heat, reaction, combustion

Fire corresponds to thermal change, ignition, combustion association, radiance, expansion and reaction. Its strongest current world-engine relationship is with temperature and ignition. Where a target has a supported ignition threshold, heating it past that threshold may mark it as burning. Continuous fuel consumption, advancing flame fronts, smoke transport, realistic heat transfer through arbitrary geometry and complete combustion chemistry are not implemented as a full simulation.

Fire can be combined with ordinary object-control operations. A Fire-associated projectile still needs a trajectory. A Fire barrier still needs to be represented and checked against incoming contact. A spell name does not bypass collision or material rules.

### Water — flow, moisture, adaptation

Water relates to fluidity, absorption, moisture, cooling, pressure and purification associations. The current model records environmental precipitation and supported surface wetting. Materials can carry wetness and respond to selected interactions. It does not calculate realistic fluid volumes, surface tension, turbulence, buoyancy, splash geometry or hydraulic systems.

Water is one component of the explicit elemental-interaction table. Certain reactions, like Water plus Earth producing Mud, are implemented. Other imagined reactions should remain a design proposal until they have a defined rule, tests and runtime support.

### Earth — structure, solidity, density

Earth relates to stability, strength, density, solidity and defensive construction. It is associated with solid matter and structural shapes. The world engine uses material profiles and geometry to represent objects; it does not provide a universal geology model, terrain excavation system, granular mechanics engine, or a complete fracture solver.

### Air — motion, pressure, vibration

Air relates to movement, gas, flow, speed, vibration and pressure. In the world engine, wind is an environmental state that can affect supported objects through relative-velocity drag when drag is enabled. Air-associated actions may also use universal motion operations. A gust represented visually is not the source of physics unless the runtime recorded the environmental change or force.

### Explicit rules and generic outcomes

MANA keeps elemental reactions explicit. Same-element inputs may reinforce; selected pairs have special reactions or cancellation; unlisted pairs may become a generic compound. This prevents undocumented reactions from appearing automatically. The exact implemented table belongs in [Elements and Implemented Rules](../reference/ELEMENTS_AND_RULES.md).

## 4. Concepts, derived types, planes, and channels

Magic vocabulary contains several categories. They are connected, but they are not synonyms.

| Category | Definition | What it does not imply |
|---|---|---|
| Fundamental element | Fire, Water, Earth or Air. | It does not automatically grant every power associated with the word. |
| Conceptual domain | An idea such as Life, Light, Darkness, Order, Entropy, Spirit, Soul, Space, Time or Void. | The domain label is not a fully implemented independent physics system. |
| Derived/specialised catalogue entry | Examples include Lightning, Sound, Metal or Nature. | The existence of the label does not mean a complete derivation graph exists. |
| Plane | A cosmological location or realm identified by the registry. | It is not a creature, effect, portal graphic or material element. |
| Channel | A permitted magical source/discipline associated with a plane or operation. | It is not a separate base element or a finite mana tank. |
| Operation | A specific action such as push, form, heat, conjure or transmute. | It is not a whole domain of power. |

The worldbuilding model places some principles outside the four-element set. Null is one such separate concept. It is not safe to treat Null as a synonym for the current Void entry: Void is a catalogue term in the runtime, while a complete independent Null model remains unimplemented.

## 5. What qualifies as a spell?

A spell is a reusable authored plan for magical change. It can combine conditions, selection, supported operations and a result. It is not limited to a pre-packaged database of fantasy spell names. A spell called “Ember Lance” could be expressed through a target, a Fire-associated object/effect, velocity and an impact response. A protective spell may create or configure a supported shield and then rely on the runtime's collision response. A disarming spell may manipulate an existing object rather than need an entirely separate physics engine.

A named spell must be understood at three levels:

- **Definition:** the actions the spell author asks to perform.
- **Execution:** whether the runtime accepts and commits those actions.
- **Outcome:** the state and events produced by the runtime/world engine.

The visual effect is a fourth, separate layer. It represents the event to the viewer; it is not itself proof the event occurred.

### Ingredients of a spell

- **Intent:** what the caster wants.
- **Target context:** which entity or profile receives the action.
- **Operation sequence:** the supported primitives to execute.
- **Parameters:** direction, magnitude, duration, material, shape, and so on.
- **Preconditions:** a valid target, available channel, defined being record, route, compatible material, or valid numeric range.
- **Commit behaviour:** whether this is a preview or an actual release.
- **Result:** success, failure, state changes and recorded effects.

A spell may be short and direct or composed of several subordinate functions. Ordinary helper functions are useful for computation and reusable preparation; a spell definition is where world-changing behaviour is grouped for spell execution.

## 6. Preview and commit are different magical acts

MANA defines the trial/commit distinction explicitly.

### `post(spell)`

A post runs the spell in a trial context. It may emit preview output and hypothetical events for inspection. The trial's proposed changes are not committed to the persistent world state. The Visualiser can show a dashed or preview-marked result to make that distinction visible.

### `release(spell)`

A release attempts to commit the spell's supported world changes. A successful release records committed effects. A failed release should not leave behind a half-committed world state for effects covered by the runtime's transaction mechanism.

This distinction matters when developing magic. It gives the practitioner a way to test trajectories, transformations, weather combinations or a summoning sequence without treating every experiment as an irreversible world event.

## 7. Targeting, target profiles, and contact

A **target profile** is the description/context for an object or selected target. `tgset` is the language construct used for this profile/context. In the established design, target context is external to a spell definition so the same spell can operate on different targets.

Target profiles are stationary/anchored by default in the current world model. This suits a test target, a fixed wall, or a stationary NPC used to exercise collision. A target intended to move must be given supported movable state or explicitly configured. The default is not a claim that every being in a real setting is immobile.

The engine distinguishes a target from the trajectory and collision:

1. A spell selects a target.
2. The effect is launched or the operation is applied.
3. A moving object follows a trajectory derived from the recorded state.
4. The physics engine detects actual contact.
5. A contact response is calculated and recorded.
6. The Visualiser draws the recorded result.

An effect does not hit merely because its name mentions a target. An effect may hit an intervening surface. A preview may show a hypothetical hit without committing it. The record and runtime outcome remain authoritative.

## 8. Pure-mana effects and universal control

Pure mana is not one of the four fundamental elements. It provides a way to express generic magical constructs and manipulations without choosing an elemental material mode for every action.

The mana library includes prototype primitives such as `form`, `burst`, `emit`, and universal controls. They express families of action rather than one named spell apiece:

- a formed construct can provide a supported shape or barrier-like object;
- a burst expresses outward propagation from a point;
- an emitted effect expresses a directed beam-like action;
- control operations can change an object's motion, move it toward a destination or apply a supported pull/push-like effect;
- geometry helpers can calculate direction, points and distances for 2D operations.

These capabilities share a common set of target and world rules. They do not yet comprise a complete field solver for every sustained beam, magnetic force, levitation, fine steering, or arbitrary magical force field.

## 9. Objects and their life cycle

World objects are active entities in the simulated world. They have an identity that persists through certain changes. Material and form may change while the ID remains the same; an object may become inactive, be collapsed into another object, or be represented by a different state. The exact fields are documented in [Objects, Materials, and State](OBJECTS_MATERIALS_AND_STATE.md).

The key distinction is between **an object, its material, its shape, its form, and its behaviour**:

- Material says what the object is made of.
- Shape says which supported geometry represents it.
- Form says which supported display/being family represents it.
- State says whether it is present, inactive, burning, powdered, wet, reanimated, or otherwise marked.
- Behaviour is what supported operations or a creature system cause it to do.

A `form` label or visual family must not be taken as proof of a complete creature body, AI, or anatomy simulation.

## 10. Conjuration, transmutation, shaping, and transfiguration

These names define separate jobs.

### Conjuration: create a material object

`conjure()` creates a physical material object from a supported material catalogue. The created object has an identity and physical properties such as mass, volume, density, position, temperature and collision data as available. Known reference materials include metals and common physical materials. The periodic data library provides 118 chemical element records for reference; this is a data catalogue, not an atomic-scale solver.

Fantasy materials may need explicit properties, particularly density. Unavailable material data should remain an explicit unknown or estimate instead of fabricating authoritative values.

Conjuring matter is not the same as:
- creating a being record;
- bringing a being through a plane pathway;
- animating existing bones;
- drawing a decorative model that has no world properties.

### Transmutation: change composition

`transmute()` changes the material/composition while preserving the entity's identity. It conserves mass by default and recalculates supported derived properties. The optional volume-preserving mode changes the accounting rule. This is intentionally a simplified model: it does not calculate atoms, chemical bonding, nuclear reaction yields, alloy phase diagrams or the real energetic feasibility of arbitrarily converting elements.

### Shaping: change geometry

`shape()` changes supported geometric representation: examples include rings, walls, arcs, discs, beams/segments and other listed forms. Shaping does not create an organism or turn ordinary rock into a new species.

### Transfiguration: change supported form

`transfigure()` changes the represented form of living entities or matter created by conjuration under the MANA design boundary. Supported forms currently include humanoid/wizard, knight, bird, serpent, beast and golem-like families. It preserves the entity identity and may scale the representation. It does not simulate all biological requirements, organ function, cognition, heredity, or a complete living creature's physiology.

### Why not merge them?

If all four were one operation, the runtime would have no clear way to distinguish a composition change from a geometry change or an entity becoming a represented being. The separation makes validation, conservation rules, visualisation and documentation understandable.

## 11. The periodic table's role

The periodic library is a reference for element symbols, atomic numbers and supported material values such as density and transition temperatures where available. Its role is to make conjured and transmuted material data inspectable and consistent.

The table is not yet a chemistry engine. It cannot independently calculate all alloy compositions, molecular structure, reaction rates, isotope mixtures, nuclear stability or pressure-dependent states. When a compound or alloy has estimated data, that status should travel with the object and appear as an estimate in the inspector.

## 12. Weather and the atmosphere

Weather is configured through the `weather` namespace. It is a world/environment state rather than a list of dedicated spells. The supported parameter family includes:

- a preset/configuration kind such as clear, rain, snow, storm, heatwave, sandstorm, fog, wind, ashfall, aurora, blizzard or custom;
- intensity and precipitation type;
- wind speed and direction;
- ambient temperature;
- relative humidity;
- cloud cover and fog;
- a normalised heat factor;
- lightning intensity;
- duration or indefinite state.

`weather.configure()` can set several properties together. `weather.wind()`, `weather.precipitation()`, `weather.ambient_temperature()`, `weather.humidity()`, `weather.fog()`, `weather.clouds()`, `weather.heat()` and `weather.lightning()` allow a program to modify a subset of the atmosphere while retaining other values. `weather.clear()` restores the calm/clear profile. Exact signatures belong in the library reference.

This design supports combinations without a new function per combination: heavy rain with crosswind, a dry high wind with dust, cold fog, a humid still atmosphere, or a storm with lightning. The library validates parameter ranges. The world engine applies supported environmental interactions; the renderer visualises the saved environment record.

The model remains partial. Wind drag, wetting and limited thermal exchange interact with objects, while cloud appearance, fog layers and much lightning appearance are primarily visual. There is no comprehensive cloud microphysics, global climate solver, precipitation accumulation on terrain, or fluid atmosphere.

## 13. World laws and physical consistency

The `world` library exposes the configured rule set. The current 2D simulation has defaults and optional controls for:

- gravity;
- air density and relative wind drag;
- collision restitution;
- tangential contact friction;
- thermal exchange with ambient temperature;
- material phase changes using reference transition points;
- surface wetting and drying/dust behaviours.

The solver also records object creation/change and contact events. Swept collision helps prevent a fast object passing through another between integration steps. The renderer does not infer an impact from the visual intersection of two sprites; it consumes the recorded contact event.

Important exclusions remain: no 3D collision world, spin or rolling-resistance solver, complete fluids, fully coupled thermal field, high-pressure phase diagrams, all-reaction chemistry, destructive terrain volume or complete material fracture solver. World laws are a calibrated prototype simulation, not a claim of scientific-grade fidelity.

## 14. Planes: identity and cosmology

A plane is a named cosmological place/domain. The registry stores its identity and classification, may link plane-specific data, can record regions, and relates planes through pathways. The catalogue includes top-level planes and special/elemental plane entries. The presence of a catalogue entry does not guarantee that every power of that plane exists in executable form.

Separate these concepts:

- **Plane identity:** which realm is being named.
- **Plane data:** the metadata and possible beings associated with that realm.
- **Region:** a sub-area represented in supported registry data.
- **Pathway:** a connection with route properties and availability.
- **Invocation:** permission to use a supported non-base channel.
- **Energy transfer:** a ledger/accounting operation through a route.
- **Summoning:** manifestation of a defined being using the supported plane/route logic.

The `planes` library focuses on identification, location/category metadata, routes, reachability, channel invocation and energy-transfer bookkeeping. `drafter` creates custom plane records during a session. The plane registry is not an editor for a plane's internal landscape, terrain, culture or hazards. No portal visualization or plane-map view is promised by this project.

## 15. Pathways and invocation

A pathway connects records. It may be one-way or bidirectional and can be open or closed. Route selection checks available connections. A route can support reachability and energy-transfer accounting, but it is not automatically a physical tunnel present in the 2D world.

Invocation makes a supported special channel available. It is not a payment taken from a finite mana pool. The four base elements are directly available; certain non-base plane-backed types need the corresponding channel invoked. The direct-use rules and special cases are listed in the element docs.

A valid pathway is not enough to summon an unknown creature. The target being must be defined and associated with a valid home plane. The route operation also does not create the plane itself.

## 16. Beings, summoning, and return

A `BeingRecord` is catalogue data: name/species, home-plane association, and supported descriptive attributes. It is not an active world object until brought into the simulation.

`summoning.bring()` uses that record and route logic to manifest a being in the Mortal Plane in the current implementation. The module includes supported ways to identify beings and some follow-up operations, such as taming, sending back, or recalling where the applicable record and route are available. It does not provide a full creature intelligence system.

A group summon is still constrained by runtime object/batch limits. The implementation has finite safety ceilings to prevent a single cast from creating unbounded numbers of active beings. The current world engine is 2D, so being records can contain lore about an origin without implying that full simulation of the home realm exists.

## 17. Necromancy and the existing-body rule

Necromancy reanimates existing remains. The runtime verifies body markers and the fact that the object was introduced as remains; labels alone cannot change an arbitrary object into a corpse. Reanimation preserves object identity while changing supported state to a reanimated/undead being representation. The Necro label corresponds to Underworld channel accounting in the current model; those accounting amounts are markers and not a fuel pool.

This is separate from summoning a pre-defined being and separate from conjuring material. Reanimated skeletons do not automatically acquire memories, intelligence, independent motives or full biological motion. An authored spell may give an undead construct additional supported behaviours, but the runtime does not hide a complete undead AI under the reanimation function.

## 18. Protection, harm, and conditions

MANA's supported operations can be composed into offensive and defensive patterns. Examples include barriers, movement disruption, material-state changes, heat, wetness, selected status effects and dispelling/cleansing-like operations where exposed by the current library and runtime. The exact catalogue of effects and values is implemented behaviour, not universal lore.

A complete magic system would also define compatibility between conditions: whether wetness improves conductivity, whether freezing alters restitution, whether a ward blocks a beam, how many layers of protection stack, whether a condition can be refreshed, and how a creature resists a transformation. These are good candidates for explicit shared rules. They must be implemented centrally and tested instead of duplicated in separate spell-name handlers.

The present prototype has selected interactions, such as elemental combinations and world-state material effects, but it is not a fully balanced battle simulator. Damage curves, creature AI, status stacking and a comprehensive counterspell graph remain incomplete or outside the current world engine.

## 19. Families of magic and what makes them different

Fantasy labels are useful for describing intent, but the system should classify effects by the operation and world state they require. Two spells with different names may be the same kind of operation with different parameters; two spells that look alike may require different rules.

### Direct and travelling effects

A **projectile** is a moving object or effect with a launch state and a trajectory. It should use movement and contact rules. A **beam** is a directed effect represented across a line or path; whether it is continuous or instantaneous must be specified rather than guessed from its appearance. A **burst** expands outward from an origin. Its affected region, duration and strength distribution are separate design choices. A beam that looks as if it passed through a target must not count as a hit if the runtime has no corresponding contact or valid effect event.

### Fields, wards, and barriers

A **field** describes an effect that applies within a region or while a condition holds. A **ward** is a protective rule or state; its meaning must specify what it blocks, how it is consumed, whether it can be penetrated, and how long it lasts. A **barrier** is an object/construct or collision boundary with supported physical behaviour. A decorative ring around a character is not automatically a barrier. Visual appearance, magical protection and physical collision are separate concerns.

### Control and alteration

**Control** alters motion or behaviour under defined authority. **Binding** restricts permitted movement. **Disruption** interferes with an operation or state. **Cleansing/dispel** removes selected supported effects; it should name which conditions can be removed and whether the caster, target or surrounding objects are affected. **Healing** would require a specified repair model; a label such as Life or Restoration alone does not define tissue repair or restore any arbitrary state.

### Conjuration and transformation

These families have distinct state transitions. Conjuration introduces a newly manifested physical object; transmutation changes its composition; shaping changes geometric representation; transfiguration changes an eligible entity's supported form. Summoning manifests a defined being using plane and route rules; necromancy reanimates accepted existing remains. A spell may compose several of these, but each stage has its own preconditions and results.

### Environmental magic

Wind, rainfall, fog, snow, cloud cover, temperature and lightning belong to environment configuration. They are not separate mandatory spell functions. A spell may configure the atmosphere, but the `weather` controls should be reusable outside any spell named after a weather type. That permits rain combined with wind, fog under cold conditions, or high heat with dry air without inventing a unique built-in function for every combination.

### Information, time, space, and other conceptual arts

Some fantasy systems include divination, illusions, teleportation, time reversal, memory alteration, or spatial folding. MANA's conceptual catalogue may contain related terms, but a catalogue entry is not a complete operational system. Each such power needs a defined observable input, allowed state transition, error model, and testable outcome before it should be described as implemented. In particular, virtual-time scheduling is not arbitrary time travel, 3D vector math is not a 3D world, and a plane record is not a teleportation implementation.

## 20. Resistance, opposition, and failure

Magic should not succeed merely because the author wrote a powerful name. Its outcome depends on supported preconditions and the relevant world rule. A valid spell may fail because its target is missing, its route is closed, a required channel has not been invoked, the requested material or shape is unsupported, a parameter is invalid, a target cannot accept that transition, or the execution fails before commit.

A mature resistance framework should distinguish at least the following ideas:

- **Physical resistance:** mass, inertia, contact, friction, structural integrity, temperature and material properties influence supported physical changes.
- **Elemental interaction:** explicit interaction rules govern listed combinations. Unlisted combinations must not receive imaginary outcomes by convention.
- **Protection/warding:** a state that blocks or modifies a known class of effect. It needs a scope, strength/uses, expiry and a clear response to stronger or incompatible effects.
- **Immunity:** an explicit rule that a named class of effect cannot affect a target. A display category, species name or elemental association is not automatic proof of immunity.
- **Interruption:** a cast may be prevented or a sequence may fail before commit. Interruption timing and rollback behaviour must be explicit.
- **Dispelling:** an operation removes selected effects. It should not erase unrelated world state or undo arbitrary history unless such a capability is deliberately specified and implemented.
- **Counteraction:** one effect changes the conditions relevant to another, such as cooling a burning object or freezing a wet surface. It is a rule-based interaction, not a special-case visual collision.

The current implementation covers only parts of this framework. It has world collisions, material states, selected elemental interactions, and a limited number of protective or control effects. It does not yet have a universal resistance stat, a fully general ward-priority system, a complete immunity schema, or a balanced counterspell graph. Those should remain explicit gaps rather than being implied by descriptive text.

Failure should be legible. A failed precondition should report the cause when possible. A failed release should not leave partially committed effects in any state covered by transactions. A failed preview should not leave changes in the committed world. An animation should communicate the recorded failure, not quietly turn it into success.

## 21. A checklist for defining a new magical principle

When designing a new effect, plane property, being ability, or world interaction, write its definition using the following checklist before implementing it.

1. **Meaning:** what does the phenomenon mean in-world? Is it an operation, material, element, concept, being, plane, or environmental condition?
2. **Classification:** does it belong to a base element, conceptual domain, derived catalogue entry, special plane channel, or no elemental category? Do not create a fifth base element by accident.
3. **Subject:** what can it affect—an existing object, living being, conjured matter, a region, an environment property, a pathway, or a defined being record?
4. **Preconditions:** what needs to exist? Is the target active? Is the pathway open? Is invocation required? Is the target's body/state eligible? Are the parameters valid?
5. **State transition:** what exact fields or world state change when it succeeds? Which fields remain unchanged?
6. **Conservation and cost:** does it transfer energy, exchange heat, change material composition, add or remove matter, or only change representation? Explain how the world ledger handles it. Do not use an arbitrary mana price to hide an undefined physical result.
7. **Timing and range:** is the effect instantaneous, travelling, sustained, scheduled, or persistent? Which time source determines expiry? Does range matter, and how is it measured?
8. **Failure and opposition:** what makes it fail? What blocks it? Which conditions can counter it? What is rolled back on failure?
9. **Observation:** which records describe the intent, outcome and world changes? Which parts are preview-only? What must a visualiser never infer?
10. **Testing:** cover a normal case, boundary values, invalid target, invalid parameters, conflicting effects, time expiry, rollback, recording output, and stress/resource limits.
11. **Documentation status:** mark the capability as implemented, partial, data-only or planned. Link to code, reference signatures and runnable examples.

This method keeps the system extensible without hard-coding a different physics rule for every named spell. It also preserves a useful divide: the magic system describes what a phenomenon means; the runtime implements the operations that make that phenomenon happen; the world engine decides supported physical consequences; the Visualiser explains the resulting record to a person.

## 22. Time and magical duration

A duration is not the same as a permanent property. Weather may have a duration or be configured as indefinite. Timed events use virtual time and execution order; this is not arbitrary time manipulation. An object may remain in a changed state after the operation that caused the change ends, while an aura, weather profile, status, or temporary field may expire according to its own recorded lifetime.

The runtime's `simul` and event/timer subset is deterministic source-order scheduling, not general parallel execution. Time-related concepts in the catalogue must not be interpreted as the ability to rewind arbitrary state, travel to any moment or bypass the engine's transaction and ordering rules.

## 23. Visualisation: truth before spectacle

The Visualiser is an optional reader of local event recordings. It can show the caster, active entities, material and element colours, projectile tracks, collision flashes, atmospheric layers, object details and recorded world settings. It can replay, scrub, jump between impacts, search/filter objects and inspect an object's recorded properties.

Its obligations are:

1. **Do not invent hits.** Contacts come from the physics record.
2. **Do not invent weather.** Weather effects come from environment/world-state records, not from matching a spell's name.
3. **Do not convert preview into release.** Preview events remain identified as trial output.
4. **Do not imply data equals simulation.** A being record or material catalogue is not an active object by itself.
5. **Do not misrepresent dimensionality.** The world scene is 2D even though 3D vector math is available.

Visual quality is important, but it must be attached to a real result. The renderer may approximate shape, material appearance or atmosphere artistically; it must not decide the physics.

## 24. Safety and resource boundaries

The interpreter, world engine and package tooling enforce input, parser, execution, object, event, recording and library limits. Those protect the MANA process from malformed inputs and accidental resource explosions. They do not make running a hostile program under a normal OS account safe. MANA is not a substitute for an OS-level sandbox when code is untrusted.

The Visualiser reads bounded local JSON Lines recordings and uses a restrictive webview Content Security Policy. It has no intended network dependency during replay. The recorder and extension should treat program-produced events as untrusted data: validate sizes, nesting, timestamps and field shapes, then use text insertion rather than interpreting event text as HTML.

## 25. Working examples and study route

The existing source tree includes illustrative examples for pure mana, world objects, weather, material transformation, collisions, planes, summoning and necromancy. Run only the examples whose dependencies and limitations are clear. Start with the plain-language example cookbook; use individual library guides when you want to compose an actual program.

Suggested reading route:

1. This compendium and the [MANA Introduction](../../../MANA_INTRO.md).
2. [Mana and Energy](MANA_AND_ENERGY.md) and [Elements and Concepts](ELEMENTS_AND_CONCEPTS.md).
3. [Objects, Materials and State](OBJECTS_MATERIALS_AND_STATE.md) and [Universal Control](UNIVERSAL_CONTROL_AND_PURE_MANA.md).
4. [Planes and Pathways](PLANES_AND_PATHWAYS.md), [Beings and Summoning](BEINGS_AND_SUMMONING.md), and [Necromancy](NECROMANCY_AND_UNDEAD.md).
5. [World Weather and Matter](../libraries/WORLD_WEATHER_AND_MATTER.md) and [World Engine](WORLD_ENGINE_2D_3D.md).
6. [Programming and Spells](PROGRAMMING_AND_SPELLS.md), then the language specification and function reference.

## 26. Reference status policy

Whenever a new power is considered, document it in four parts:

1. **Meaning:** what the effect means in the worldbuilding system.
2. **Preconditions:** what must be available, identified or true.
3. **World rule:** which state transition or law determines success/failure.
4. **Visual convention:** how the optional viewer renders the recorded event.

Then mark its status as **implemented**, **partial**, **data-only**, or **planned** and ensure that reference docs, code and tests agree. A function name is not proof of complete world behaviour. A catalogue entry is not proof of a working spell. A polished animation is not proof of a physical outcome.
