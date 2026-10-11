# MANA Glossary and Design Terms

**Page kind:** Explanation  

**Current source version:** v1.0.0
**Status:** Current terminology reference

This glossary keeps words that sound similar from being used interchangeably. Entries marked **design** describe the intended model; entries marked **implemented** describe current code where relevant.

## Language and execution

| Term | Meaning |
|---|---|
| **MANA** | The language, runtime, and world-engine project. |
| **`.mana` program** | Source code parsed by MANA's lexer, parser, and runtime. It is not a Python file. |
| **`def`** | An ordinary function definition for reusable calculations and helpers. It must not silently mutate the world when called directly. |
| **`spldef`** | A spell definition for world-changing behaviour. Execute it with `post(...)` or `release(...)`. |
| **`incant`** | The MANA statement used to supply a value from a definition and exit that definition. It exits the current definition and can provide the value supplied to the caller. |
| **`tgset`** | A target-profile/context construct. Target choice is performed outside the spell body. It is also used to define named material/target records. |
| **`load`** | Loads a built-in or packaged library namespace. It loads a built-in or packaged MANA library into the current program. |
| **`post`** | Runs a spell as a trial and restores world state after collecting the execution report. |
| **`release`** | Runs a spell and commits its world-state changes. |
| **Runtime** | The component that evaluates parsed MANA statements and expressions and applies their semantics. |
| **World Engine** | Runtime world state plus physical calculations, motion, collision handling, and energy bookkeeping. The current simulated world is 2D. |

## Mana, energy, and elements

| Term | Meaning |
|---|---|
| **Mana** | The underlying magical medium in the design. It is not one of the four base elements and is not a finite stored player resource. |
| **`Mana`** | Uppercase type selector used where the language creates pure-mana objects. |
| **`mana`** | Lowercase built-in namespace for pure-mana effects and universal object controls. |
| **Mana-equivalent readout** | A reported amount associated with an operation. It is not a remaining mana balance that can run out. |
| **Physical energy** | Tracked energy of world objects and transfers: thermal, kinetic, released, and other accounted contributions. |
| **Energy ledger** | Records energy input/output, internal transfer, and provenance. A transfer must not count as a net creation or destruction. |
| **Fundamental element** | One of Fire, Water, Earth, Air. There are exactly four in the established model. |
| **Conceptual entry** | A catalogue concept such as Life, Death, Light, Order, or Time. Its presence in a catalogue does not mean every associated ability exists. |
| **Derived/specialised entry** | A catalogue entry such as Lightning, Sound, Metal, or Nature. It is not a fifth base element. |
| **Invocation** | Permission to use a registered non-base elemental/special channel. Invocation is not a resource payment. |
| **Null versus Void** | Null is a worldbuilding concept of absence/opposition to mana. `Void` is the current code/plane label. They are not declared exact synonyms. |

## Cosmology and beings

| Term | Meaning |
|---|---|
| **Plane** | A separately identified location in the cosmology. Plane metadata does not secretly change unrelated language or physics behaviour. |
| **Region** | A named subdivision registered under a parent plane, such as `Hell.Naraka`. It is not a separate top-level plane. |
| **Pathway** | A directed or bidirectional connection between two plane/region endpoints, with an open/closed state. |
| **Plane data library** | A separately loaded module containing details such as elemental spirits, regions, and beings. |
| **Being record** | Data describing a species/entity, its home plane, kind, optional element tie, requirements, and stats. It is not itself an active world object. |
| **World object** | An active simulation object with physical state such as mass, position, velocity, temperature, and energy. A manifested being becomes a world object. |
| **Cross-plane summoning** | Bringing a defined being through an open route using `summoning.bring`. `planes` alone transports energy, not beings. |
| **Taming** | Current instance-level naming/recall support for a brought being. It is not a complete obedience or AI system. |
| **Reanimation** | Animating existing bones/corpse/remains in the Mortal Plane with `necromancy.reanimate`. It does not create the body. |
| **Constructed undead spell** | User-written MANA code that creates/assembles an undead-like construct; it is not a special built-in `summon_skeleton` function. |
| **Necro channel** | An invocation/accounting label mapped to Underworld permission. It is not an additional fundamental element or a separate top-level plane. |

## Geometry and tools

| Term | Meaning |
|---|---|
| **`geometry2d`** | A library of 2D geometry calculations. It does not replace or independently run world physics. |
| **`vector3d`** | A library of 3D vector/math helpers. It does not enable 3D world simulation. |
| **VS Code extension** | Optional syntax highlighting, snippets, and language-editor support. It is not the runtime. |

## Status vocabulary used in the handbook

- **Established design:** explicitly decided by the project owner.
- **Implemented:** present in the current source and covered by tests.
- **Partial:** some operations work but the complete intended capability does not yet exist.
- **Planned:** direction for future implementation only.
- **Calibration value:** a prototype number used by the current simulation, not a permanent real-world constant.

When in doubt, check [Implementation Status](IMPLEMENTATION_STATUS.md) and then the exact current API guide. An archived audit is not the current interface definition.
