# MANA — Introduction to the Language and Its Foundations

**Version:** 1.0.0  
**Audience:** anyone trying to understand what MANA is before reading syntax or implementation details.

## The central idea

MANA treats magic as programmable operations rather than a catalogue of unrelated, hard-coded spell names. A spell is code. It can create or affect objects, use elemental properties, manipulate motion, invoke a special energy channel, use a plane pathway, or combine several capabilities. The programmer expresses the behaviour; the runtime enforces the supported language and physics rules.

MANA is also intended to work for ordinary computation. A language that can express magic but cannot express basic calculations, reusable helpers, conditions, lists, or ordinary program flow would be unnecessarily limited. That is why MANA has ordinary `def` functions as well as `spldef` spells.

## The foundational concepts

### Mana

Mana is the general medium used by magic. It is not a fifth element and it is not a finite personal battery that must be depleted by each spell. A caster uses the mana available to the system. Some channels—such as non-base elemental planes and the Underworld/Necro channel—require explicit invocation permission. That permission is not a mana payment.

The runtime still records physical energy and transfers for consistency. A joule value in the ledger is an accounting value, not a claim that the caster has a finite pool of joules to spend. The numerical model is a prototype, and the detailed energy rules are documented separately.

### The four fundamental elements

The four base elements are **Fire, Water, Earth, and Air**. They are not merely four colours or four interchangeable damage types; they represent different modes of magical interaction. MANA's intended rules include controlled combinations and cancellations, but an interaction is only executable to the extent it is implemented in the current element rules.

Other labels—such as Ice, Metal, Thunder, Life, Death, Holy, Shadow, Underworld, and Void—are not additional base elements. Some are specialised/derived entries, some are conceptual domains, and some have corresponding planes or channels. The categories must not be collapsed into one another: a conceptual label is not automatically a new fundamental element, and a plane name is not automatically a usable operation.

### Pure mana and universal control

Not every effect needs an elemental label. A force pulse, barrier, beam, object pull, collection effect, or movement instruction can be expressed through pure mana or universal object-control operations. Elemental manipulation and general control are complementary tools: elements describe the magical mode or material interaction, while control operations describe what happens to an object.

### Objects and physical behaviour

MANA programs work with objects and their properties. The runtime tracks supported quantities such as mass, temperature, position, velocity, and energy. Operations change those values through validated procedures rather than allowing arbitrary assignments to bypass the physical model. The current World Engine is 2D; the `vector3d` library performs three-dimensional mathematics but does not turn the world simulation into a 3D engine.

### Planes and pathways

A plane is an identified place in the cosmology. The `planes` library identifies planes and regions, records explicit pathways, checks reachability, and records energy transfer. It does not define a plane's internal laws or move beings. `drafter` creates custom plane records; plane data libraries store plane-specific data; `summoning` brings a defined being across an available route.

### Beings and necromancy

Being records describe a species/entity and its home plane. Bringing a being from another plane is different from creating an undead construct. `summoning.bring(...)` is a cross-plane library operation, not a general spell keyword. A user-written spell such as `summon_skeleton` is ordinary MANA code. Reanimation is different again: `necromancy.reanimate(...)` requires existing remains, bones, or a corpse. Necromancy uses the Necro/Underworld channel and mana manipulation, but it cannot make an absent corpse exist by relabelling an ordinary object.

### Ordinary functions, spells, and targets

- `def` defines an ordinary reusable function, primarily for calculations and general program logic.
- `spldef` defines a spell whose effects are executed through MANA's spell execution modes.
- `tgset` establishes target context outside the spell body. Target selection is not embedded into every spell.
- `incant` is MANA's result statement. MANA does not use `return`.
- `load` loads a library and checks dependencies.
- `span`, `length`, and `skip` are MANA's chosen vocabulary for iteration ranges, sequence length, and an intentionally empty statement.

The formal syntax and edge cases belong in the [Language Specification](docs/current/language/LANGUAGE_SPEC.md), not this introduction.

## How to read this project

1. **Foundations** explain the concepts and intended separation of systems.
2. **Getting Started** teaches actual syntax through runnable programs.
3. **Language Specification** defines grammar and semantics.
4. **Function Reference** lists implemented functions and signatures.
5. **Library guides** explain each namespace and its dependencies.
6. **Physics and internals** describe the numerical implementation and runtime architecture.
7. **Implementation Status** marks what is implemented, partial, or planned.

## Design versus implementation

MANA 1.0.0 is the first public 1.0 release of the current implementation. The foundation documents describe the intended conceptual model; reference pages describe the current code. Where they differ, the implementation-status page should make the gap explicit. Do not infer a complete system from a name alone: a plane, conceptual domain, element profile, creature record, or example may exist as data without a full simulator for its behaviour.

MANA programs are stored as `.mana` source files and executed by the Python implementation in `mana.py` and `magiclang/`. The project includes optional VS Code language support for highlighting and editing, but the extension does not execute programs. Any editor capable of editing text can be used; Python 3.12 or newer is required to run the current source implementation.
