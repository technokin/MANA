# Fundamental, Conceptual, and Derived Elements

**Page kind:** Explanation  

**Current source version:** v1.0.0

MANA distinguishes the four fundamental elements from conceptual domains and derived/specialised entries. This distinction is essential: the presence of a name in a catalogue does not mean that it is a fifth fundamental constituent or that every spell involving it is already implemented.

## 1. The four fundamental elements

These four are the fixed base set. They are not variables that a program can redefine, and one base element is not converted into another merely by renaming it.

### Fire

Primary catalogue domains are heat, temperature, thermal change, combustion, anger, and passion. Related associations in the implementation include light, expansion, and reaction. In code, Fire is a type with a defined starting temperature and interaction rules; its other conceptual associations do not automatically implement full light manipulation or emotional influence.

### Water

Primary domains are fluidity, flow, adaptability, coldness, absorption, and purification. Related associations include vitality, pressure, and cooling. The implemented interaction table includes Water + Earth → Mud. Water + Air can produce Ice when the required heat-removal condition is available.

### Earth

Primary domains are strength, defence, stability, structure, density, solidity, and a gravity effect. Related associations include vitality and pressure. Earth is the base type commonly associated with solid matter and structural operations; ordinary existing stone/wood/rock material profiles can be manipulated without treating the action itself as an invocation of an elemental plane.

### Air

Primary domains are manipulation, gas, movement, speed, vibration, and pressure. Related associations include flow and sound. Air is associated with motion and gas behaviour. It also participates in the Water + Air → Ice interaction when heat is removed from the target.

## 2. Conceptual catalogue in the current code

The current `magiclang/elements.py` assigns these entries the category `conceptual`. That categorisation is part of the prototype registry; it does not mean each has a separate fully developed spell library.

| Concept | Catalogue domains | Boundary in MANA |
|---|---|---|
| Light | Illumination, radiation, visibility, reflection | Currently has a defined interaction with Darkness; complete light physics is not provided. |
| Darkness | Occlusion, concealment, light absorption | A conceptual entry, not an additional base element. |
| Life | Growth, vitality, regeneration, biological structure | Relevant to life-related operations; also has an associated plane/data channel. |
| Death | Cessation, degradation, corpse state, decay association | Relevant to death-related states and Necro design; not equivalent to the Underworld plane itself. |
| Order | Organization, regularity, pattern, structure association | Used as a conceptual association, including in stability/stabilizer logic. |
| Entropy | Dispersion, disorder, decay | Conceptual association; not a general entropy simulation. |
| Spirit | Spirit, will, possession, manifestation | Conceptual category; contacting a spirit from another plane is still a summoning concern. |
| Soul | Identity, essence, memory, self | Catalogue concept; complete soul-state mechanics are not implemented. |
| Space | Position, distance, spatial relation | Spatial mathematics already exists, but this entry does not provide free-form dimension manipulation. |
| Time | Duration, sequence, rate, temporal relation | The engine has virtual time and scheduling; that is not arbitrary time manipulation. |
| Void | Separation, absence, vacuum-like behaviour | Existing registry name. Do not conflate it automatically with the planned Null concept. |

The user's worldbuilding design places some principles—such as causality, fate, karma, and the rules above mana—outside the four elemental constituents. Those must not be added as base elements simply because they can influence a magical situation. A fully defined conceptual-element system remains distinct from the base four.

## 3. Derived or specialised catalogue entries

The runtime currently labels `Lightning`, `Sound`, `Metal`, and `Nature` as `derived`. They are not additional fundamental elements. Their conceptual domains are charge/current/discharge for Lightning; sound waves/resonance for Sound; conductivity related to strength/density/structure for Metal; and ecosystem/biological interaction for Nature.

The prototype does not yet provide a complete universal derivation tree that can construct every derived type from other types. The domain map is a catalogue of ownership/association, not a promise that each domain has a full spell implementation.

## 4. Elemental planes and special channels

The plane-data catalogue contains thirteen individual elemental/special-channel plane entries:

`Fire`, `Water`, `Earth`, `Air`, `Ice`, `Metal`, `Thunder`, `Life`, `Death`, `Underworld`, `Holy`, `Shadow`, and `Void`.

These are **thirteen separate plane records**, not thirteen fundamental elements. The fixed fundamental set remains Fire, Water, Earth, and Air. Some plane entries are special or conceptual channels in the worldbuilding model, and some names do not have a one-to-one counterpart in `ELEMENTS` (for example, the planar label `Thunder` versus the code's derived `Lightning`). Do not silently merge those terms without an explicit design decision.

Each built-in elemental/special plane currently has a data record for its elemental spirit. The data library includes initial combat numbers for those records; those values are prototype data rather than established cosmological constants. See [Beings and Cross-Plane Summoning](BEINGS_AND_SUMMONING.md).

## 5. Invocation rule

The four base elements are usable directly. Directly creating a registered non-base plane type requires loading `planes` and invoking the corresponding channel first, for example:

```mana
load planes
planes.invoke("Ice")
ice_object = create Ice
show ice_object
```

Expected output:

```text
<element:ice_object#3>
```

This example uses an existing plane channel. It does not mean that every possible derived combination must be invoked. The design permits derived material/effects created by valid combinations of base elements without separately invoking a derived plane—for example, Water + Air → Ice under the heat-removal rule.

Invocation is a permission flag/channel operation; it does not drain an inexhaustible mana pool. A permission can be revoked. Revoke also stops continuous energy channels sourced from that plane. `planes.invoke("Necro")` maps the Necro mana-channel name to the Underworld's permission state; Necro is the channel label, not another one of the four base elements.

A catalogue concept does not become a directly creatable object type only because it is listed in `elements.py`. The runtime validates which names are registered as directly available plane types.

## 6. Implemented element interactions

The current interaction function includes the following explicit rules. Unlisted pairings produce a generic `Compound` result rather than a fabricated specialised reaction.

| Inputs | Current result | Important condition |
|---|---|---|
| Same element + same element | The same element, reinforced | The input amounts are added. |
| Fire + Water | Cancellation outcome | Within a 1% tolerance, a `ThermalRelease` is made. Otherwise the dominant element remains and matched energy is recorded as released. |
| Light + Darkness | Cancellation outcome | Uses the same cancellation helper in current code. |
| Water + Earth | Mud | A material result. |
| Mud + Life | Wood | Wood is staged: Water + Earth first produces Mud, then Mud + Life produces Wood. |
| Earth + Life | `EarthLifeCompound` | It is not Wood; the Mud stage has been omitted. |
| Water + Air | Ice | Requires `available_heat=True` to represent heat removed from the target. |
| Fire + Air | Fire propagation interaction | The current code adds a Fire-weighted portion of Air and records the consumed Air portion as released energy. |
| Other pairs | `Compound` | No special reaction is defined by the current rule function. |

The cancellation tolerance is an implementation constant at 1% of the larger input. It is not a universal law that all similarly sized elemental amounts cancel in the same way outside this implemented function.

## 7. Domain ownership versus actual capability

The code records one primary owner for each named domain and may list other elements as involved. Examples include temperature → Fire, pressure → Air, strength → Earth, vitality → Life, and flow → Water. `has_domain(...)` reads this catalogue. It does not automatically execute a spell, convert one element into another, or guarantee that a specialist library exists.

## 8. Design rules to preserve

1. Keep exactly four fundamental base elements.
2. Keep mana conceptually separate from elements.
3. Keep direct use of non-base plane energy behind invocation, while allowing valid base-element combinations without that invocation.
4. Do not turn conceptual domains into extra base elements by convenience.
5. Do not equate Null with the current `Void` code entry without defining the relationship.
6. Do not document a reaction as implemented unless `elements.py`, the runtime and tests actually implement it.
