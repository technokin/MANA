# Conceptual Domains and Specialised Magical Categories

**Page kind:** Explanation  

**Version:** 2.0.0
**Purpose:** keep four base elements, conceptual domains, specialised labels, and plane/channel names distinct.

## 1. The categories are different

MANA uses several kinds of names. They are not interchangeable.

| Category | Meaning | Example | What the name alone does not guarantee |
|---|---|---|---|
| Base element | One of the four foundational elemental modes | Fire, Water, Earth, Air | It does not mean every imagined effect is already implemented. |
| Derived/specialised element label | A result or specialised mode represented in the current catalogue/rules | Ice, Metal, Thunder | It does not establish a complete general derivation system. |
| Conceptual domain | An abstract principle or area of effect associated with one or more elemental/domain owners | Life, Death, temperature, flow, pressure | It is not automatically a fifth base element or a plane. |
| Plane/channel | A named source/place in the cosmology, possibly with an invocation rule | Underworld, Life Plane, Ice Plane | It is not a spell function and does not automatically grant permission. |
| Pure mana operation | An effect expressed without requiring an elemental identity | burst, beam, barrier/construct, pull | It still obeys runtime limits and supported physics. |

## 2. Four base elements

### Fire

Fire is the base mode associated in MANA's design with heat/temperature and certain light or ignition effects. Fire is not a universal label for all energy: a pure-mana beam is not automatically Fire, and a temperature change must still use the supported thermal operations.

### Water

Water is associated with fluidity, adaptation, cooling/vitality themes, and material interactions such as the Water/Earth mud result. These associations are design semantics; each concrete operation must still be defined by code.

### Earth

Earth is associated with solid material, strength, defence, and material construction. It can represent an object or elemental mode, but the presence of Earth does not automatically provide destructible terrain extraction or arbitrary object creation from the environment.

### Air

Air is associated with gases, manipulation, pressure, and motion-related effects. Universal push/pull and object control remain available without an Air label; Air is used when the effect specifically relies on its elemental role.

## 3. Current explicit elemental interactions

The executable interaction function currently documents these important cases:

| Inputs | Current implementation outcome | Qualification |
|---|---|---|
| Same element + same element | Reinforced instance of the same element | Input amounts are added. |
| Fire + Water | Cancellation/thermal-release outcome | Uses a tolerance and dominant-element logic; not all pairs use this rule. |
| Light + Darkness | Cancellation helper | These names are catalogue labels, not base elements. |
| Water + Earth | Mud | A defined material result. |
| Mud + Life | Wood | Requires the staged Mud result first. |
| Earth + Life | Earth/Life compound | Does not silently become Wood. |
| Water + Air | Ice | Current rule requires `available_heat=True` to represent heat removed from the target. |
| Fire + Air | Fire-propagation interaction | Current implementation records the Air portion as released energy. |
| Other pairs | Generic compound result | No special reaction is implied. |

See [Elements and Implemented Rules](../reference/ELEMENTS_AND_RULES.md) for the actual code-level catalogue. Do not infer that every two-domain combination has a bespoke transformation.

## 4. Specialised and conceptual labels

The current catalogue includes specialised entries such as Ice, Metal, Thunder, and Nature, plus concepts including Life, Death, Holy, Shadow, Underworld, and Void. Their presence supports lookup, ownership, plane data, or particular operations where implemented. It does not mean they all derive from the four base elements through one universal algorithm.

The intended design permits Life and Death as important conceptual principles while preserving the four-element foundation. Other conceptual principles can be introduced as the language's conceptual model is refined, but they should not be silently promoted to base elements.

`Void` and `Null` must remain distinct. `Void` currently appears as a registered special/plane label. `Null` is the design concept of absence/opposition to mana and does not yet have a complete physical model.

## 5. Domain ownership

The element module associates domains with primary owners and may identify participating elements. Examples include temperature with Fire, pressure with Air, strength with Earth, vitality with Life, and flow with Water. Domain lookup is descriptive metadata: it does not create a spell, grant plane access, convert one element into another, or imply that a dedicated library exists.

## 6. Invocation and planes

The four base elements do not require invocation. Accessing a non-base plane/channel may require `load planes` followed by `planes.invoke(...)`. Invocation is permission, not a finite mana cost. For Necro, `planes.invoke("Necro")` grants access to the Underworld-associated channel; the bookkeeping source remains the Underworld. Invocation does not summon the Underworld spirit or move a being.

A derived effect can be produced by base-element operations where the rules support it without invoking the similarly named plane. For example, the current Ice interaction can be reached through Water + Air under its defined conditions; directly taking energy from the Ice Plane is a separate action.

## 7. Design checklist for adding a new name

Before adding a magical category, answer these questions explicitly:

1. Is it a base element, a derived/specialised label, a conceptual domain, a plane/channel, or just a function/effect name?
2. Does it have a distinct energy/source rule, or is it only a semantic tag?
3. Does it need invocation permission?
4. What existing operation actually uses it?
5. What happens when it interacts with each base element?
6. Which properties and units are changed?
7. What ledger entries or physical-energy changes occur?
8. What tests define its normal case, invalid use, and edge cases?

A label should not be added to every layer automatically. In particular, a concept does not require its own plane unless the cosmology defines one, and a plane does not require a new syntax keyword.

## 8. Related references

- [Elements and Concepts](ELEMENTS_AND_CONCEPTS.md)
- [Mana and Energy](MANA_AND_ENERGY.md)
- [Planes and Pathways](PLANES_AND_PATHWAYS.md)
- [Elements and Implemented Rules](../reference/ELEMENTS_AND_RULES.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
