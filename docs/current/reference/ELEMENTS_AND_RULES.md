# MANA Elements and Interaction Rules

**Page kind:** Reference  

**Version:** 2.0.0

This page documents the element catalogue currently in the code. The catalogue categorises concepts; it does not claim every listed pairing has a fully implemented magical reaction.

## Four fundamental elements

These are the only fundamental base elements. They are locked types, not variables to redefine, and one base element cannot be converted into another by simply renaming it.


### Availability and invocation

The four base element types can be used directly with `create` without invoking a plane. The registered non-base elemental-plane types (`Ice`, `Metal`, `Thunder`, `Life`, `Death`, `Underworld`, `Holy`, `Shadow`, and `Void`) require `load planes` and `planes.invoke("PlaneName")` before direct creation, because their energy is taken from the corresponding plane. This permission does not spend or store a finite mana pool. A derived result formed by a valid combination of base elements does not need the derived plane to be invoked; for example, Water and Air can produce Ice under the documented heat-removal condition. Catalogue concepts such as `Light` or `Order` are not automatically directly creatable object types merely because they appear in the domain catalogue.

| Element | Primary domains in the catalogue | How to read this |
|---|---|---|
| `Fire` | Heat, temperature, thermal change, combustion, anger, passion | Primarily governs heat and thermal change; light and expansion are recorded as related involvement. |
| `Water` | Fluidity, flow, adaptability, coldness, absorption, purification | Primarily governs flow and adaptability; vitality, pressure and cooling are recorded as related involvement. |
| `Earth` | Strength, defence, stability, structure, density, solidity, gravity effect | Primarily governs structure, stability and strength; gravity is an effect/domain association, not a fifth element. |
| `Air` | Manipulation, gas, movement, speed, vibration, pressure | Primarily governs movement, gases, and pressure-like effects. |

## Provisional conceptual catalogue

These names exist in the current catalogue but are not additional fundamental elements. Their full spell libraries and laws remain incomplete.

| Name | Current catalogue domains |
|---|---|
| `Light` | Light, illumination, radiation, visibility, reflection |
| `Darkness` | Occlusion, concealment, light absorption |
| `Life` | Growth, vitality, regeneration, biological structure |
| `Death` | Cessation, degradation, corpse state, decay association |
| `Order` | Organization, regularity, pattern, structure association |
| `Entropy` | Dispersion, disorder, decay |
| `Spirit` | Spirit, will, possession, manifestation |
| `Soul` | Identity, essence, memory, self |
| `Space` | Position, distance, spatial relation |
| `Time` | Duration, sequence, rate, temporal relation |
| `Void` | Separation, absence, vacuum-like behaviour |

## Derived/specialized catalogue entries

`Lightning`, `Sound`, `Metal`, and `Nature` are listed as derived/specialized concepts. They are not part of the four-element base set. A complete derivation/crafting system for these types remains future work.

## Implemented interaction rules

| Inputs | Current result | Conditions and important details |
|---|---|---|
| Same element + same element | Same element reinforced | Quantities are added. |
| Fire + Water | Cancellation result | Close quantities produce `ThermalRelease`; if one side dominates, the unmatched amount leaves the dominant element. Matched mana is reported as released energy. |
| Light + Darkness | Cancellation result | Uses the same cancellation rule as Fire/Water in the current implementation. |
| Water + Earth | `Mud` material | The result is labelled a material with both component names. |
| Mud + Life | `Wood` material | The documented staged interaction is Water + Earth → Mud, then Mud + Life → Wood. |
| Earth + Life | `EarthLifeCompound` | Not Wood; the water/mud stage is required by the current rule. |
| Water + Air | `Ice` material | Only when `available_heat=True`, representing heat removed from the target. |
| Fire + Air | Fire with propagation effect | Uses the specific energy/readout rule defined in `elements.py`; argument order does not change the rule. |
| Other pairings | Generic `Compound` | No special reaction is currently defined. |

The cancellation tolerance is currently 1% of the larger input. This tolerance is an implementation constant, not an assertion that the input energies are physically equivalent in ordinary SI terms.

## Domain ownership

The engine maps each known domain to one primary owner and may record other involved elements separately. Examples include `temperature` → Fire, `pressure` → Air, `strength` → Earth, `vitality` → Life and `flow` → Water. `has_domain(object_or_element, "domain")` queries that catalogue; it does not perform the corresponding magic or guarantee a full library is implemented.

## Where to learn more

- [Built-in Reference](FUNCTION_REFERENCE.md): available commands and object operations.
- [Energy Model](../physics/ENERGY_MODEL.md): matter, mana, thermal state and energy readouts.
- [Interpreter Architecture](../internals/INTERPRETER_ARCHITECTURE.md): where element profiles and interaction rules live in the implementation.
