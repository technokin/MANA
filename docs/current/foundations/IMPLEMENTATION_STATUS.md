# MANA v1.0.0 Implementation Status

**Page kind:** Explanation  

This page separates established design from current code. It is the fastest way to check whether a concept below is already executable, partially represented, or still planned.

## Language and runtime

| System | Status | Notes |
|---|---|---|
| `.mana` source language | Implemented | Custom lexer, parser, AST, runtime, MANA errors, units, source locations and tests. Implemented in Python; Python is the implementation language, not the language used to write `.mana` programs. |
| Ordinary `def` helpers | Implemented | Intended for pure computation; world-changing effects belong in a spell. |
| `spldef` spells | Implemented | Execute through `post` or `release`. |
| `tgset` target profiles/context | Implemented | Target selection remains outside a spell body. |
| `incant` result statement | Implemented | No `return` statement exists in the MANA source grammar. |
| `load` library keyword | Implemented | Dependency checks are enforced for built-in library/data namespaces. |
| `skip`, `span`, `length` | Implemented | MANA-specific language vocabulary. |
| List indexing and assignment | Implemented | Lists support indexing/length and nested list mutation under runtime rules. |
| Events, timers and `simul` | Partial/implemented subset | Deterministic source-order execution, registered event names, virtual-time callbacks, and safety limits. Not a parallel execution engine. |

## Magic and energy

| System | Status | Notes |
|---|---|---|
| Four fundamental elements | Implemented | Fire, Water, Earth, Air object types and profiles. |
| Conceptual domain catalogue | Implemented as catalogue | Catalogue membership does not imply every domain spell exists. |
| Derived/specialised catalogue | Partial | Lightning, Sound, Metal, Nature profiles; no complete general derivation graph. |
| Element interactions | Partial | Explicit pairings in `elements.py`; others return a generic compound. |
| Invocation of non-base plane energy | Implemented | Uses `planes` permission state; invocation is not a finite mana pool. |
| Pure-mana `form`, `burst`, `emit` | Implemented prototype | Energy ledger and simplified geometry; construct durability/mesh effects are limited. |
| Universal object control | Implemented prototype | Shared controls exist but persistent steering/levitation control is not a full controller solver. |
| Material object profiles via `tgset` | Implemented subset | Supported properties, combustible defaults, ignition state, powder aggregate state. No terrain extraction or dust-particle simulation. |
| Energy ledger | Implemented prototype | Tracks input/output/transfer/provenance. Not a complete field-based environmental energy solver. |
| Integrity and collapse | Implemented calibration model | Per-label break-energy baselines and stabilizers are configurable starting values; environmental propagation of collapse energy is incomplete. |
| Null | Worldbuilding concept / planned | Not implemented as a complete separate physical model; do not equate automatically with `Void`. |

## Cosmology and beings

| System | Status | Notes |
|---|---|---|
| Plane registry | Implemented | Twenty top-level references and three built-in Hell regions. |
| Pathways and shortest routes | Implemented | One-way/bidirectional direct records, open/closed status, deterministic shortest routes. |
| Planar energy transfer/channels | Implemented accounting subset | Joules/watts recorded via ledger; not a finite pool. |
| Elemental spirit data | Implemented data | Thirteen separate elemental/special plane records grouped in one data library. |
| Built-in non-elemental beings | Implemented data subset | Mermaid, Elf, Griffin, Werewolf, Vampire, Chimera, Giant, Orc. Other plane modules may have empty being lists. |
| Built-in combat stats | Implemented prototype values | See creature catalogue and source data modules; do not present as final balance. |
| `drafter` custom planes | Implemented | In-memory/runtime custom records, data properties, regions and beings. Persistence across runtime sessions is not automatic. |
| `summoning.bring` | Implemented | Uses a being record and valid route to manifest in Mortal Plane. |
| Taming / send back / call | Implemented subset | Instance naming and return/recall via routes; not a general creature AI. |
| `necromancy.reanimate` | Implemented subset | Requires previously marked corpse/bones/remains; records a fixed ledger marker; does not create a body. |
| User-authored summon-undead spells | Composable with current primitives | A spell is MANA code, not a built-in `summon_skeleton` function. Automated Necro accounting across every arbitrary custom spell is still incomplete. |
| Creature AI/combat behaviour | Partial/planned | Stats exist but no complete behaviour/strategy system or final combat solver. |
| Plane-creation persistence/UI | Planned | `drafter` creates runtime data; a persistent world/project asset workflow is future work. |
| Beings physically crossing to planes other than Mortal Plane | Not implemented as general world simulation | Current `summoning` destination is the Mortal Plane. |

## Geometry and World Engine

| System | Status | Notes |
|---|---|---|
| 2D motion and circle-based contacts | Implemented prototype | World objects must have z=0; collision geometry is simplified. |
| `geometry2d` | Implemented | Calculation library; not a replacement collision engine. |
| `vector3d` | Implemented calculations | Vector/math/physical-helper functions only; no 3D world. |
| 3D collisions/world gravity/3D targeting | Not implemented | Would require a separate expansion of engine state and physics. |
| Terrain material removal | Not implemented | A solid ground is not automatically a destructible matter volume. |
| Ongoing fire propagation/fuel consumption | Not implemented | Current ignition is a state/event, not combustion progression. |
| Graphical World Engine viewport | Planned | The current source project is a language/runtime with no live graphical world viewport. |

## Developer tooling

| System | Status | Notes |
|---|---|---|
| VS Code grammar/snippets | Implemented | Optional editing support for `.mana` files; execution remains in `mana.py`. |
| Library Builder | Implemented starter CLI | Initialises/validates/packages `.manalib`; not a full package manager. |
| GPL-3.0-only licensing | Present | See root `LICENSE` and `tools/vscode-extension/LICENSE.txt`. |

## Rules for keeping this page trustworthy

Update this table whenever a feature moves status. An example in documentation does not itself mean the feature is implemented; a function name in a catalogue does not prove that its complete behaviour exists. A feature should be marked implemented only when the source, tests, examples, and public reference agree.
