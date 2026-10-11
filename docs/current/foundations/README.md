# MANA Foundations Handbook

**Page kind:** Explanation  

**Documentation edition:** v1.0.0
**Purpose:** explain the design that the language, libraries, and world runtime are intended to implement.

This handbook is the conceptual starting point. The language guide and function reference define exact syntax. These chapters explain why the systems are separated, how their concepts relate, which rules have been established, and where current code differs from the intended model.

## Recommended reading order

1. [What MANA Is](MANA_OVERVIEW.md) — project purpose, architecture, and non-negotiable boundaries.
2. [Mana, Matter, and Energy](MANA_AND_ENERGY.md) — omnipresent mana, no finite caster pool, ledger bookkeeping, and prototype conversion conventions.
3. [Fundamental, Conceptual, and Derived Elements](ELEMENTS_AND_CONCEPTS.md) — four base elements, conceptual catalogue, specialised entries, invocation, and implemented interactions.
4. [Programming Model and Spell Execution](PROGRAMMING_AND_SPELLS.md) — helper functions, spell definitions, target contexts, language vocabulary, and composition.
5. [Execution, Time, Events, and Transactions](EXECUTION_TIME_AND_EVENTS.md) — `post`, `release`, rollback, `simul`, time, and errors.
6. [Universal Control and Pure Mana](UNIVERSAL_CONTROL_AND_PURE_MANA.md) — moving existing objects, constructing pure mana, beams, bursts, and multi-object control.
7. [Objects, Materials, and State](OBJECTS_MATERIALS_AND_STATE.md) — object properties, `tgset`, lifecycle, material state, and energy provenance.
8. [Planes, Pathways, and Cosmology](PLANES_AND_PATHWAYS.md) — identities, regions, connections, energy transfer, data modules, and invocation.
9. [Beings and Cross-Plane Summoning](BEINGS_AND_SUMMONING.md) — being records, home planes, current stats, routes, taming, return, and recall.
10. [Necromancy and Undead Control](NECROMANCY_AND_UNDEAD.md) — existing-body reanimation, constructed-undead spells, and Necro-channel bookkeeping.
11. [World Engine, 2D, and 3D](WORLD_ENGINE_2D_3D.md) — physical state, motion, collisions, integrity, and the boundary between 3D math and the 2D world.
12. [Libraries and Extension Boundaries](LIBRARIES_AND_EXTENSION_MODEL.md) — built-in libraries, plane-data modules, and user `.manalib` packages.
13. [Python Runtime and Development Tools](PYTHON_RUNTIME_AND_TOOLING.md) — source execution, VS Code support, and project structure.
14. [Glossary and Design Terms](GLOSSARY_AND_DESIGN_TERMS.md) — consistent definitions for MANA terminology.
15. [Implementation Status](IMPLEMENTATION_STATUS.md) — implemented, partial, and planned systems at a glance.

## Status labels

- **Established design:** an owner decision or core project rule.
- **Implemented:** present in the source and exercised by tests.
- **Partial:** some behaviour works, but the whole planned system is not present.
- **Planned:** future direction only.
- **Calibration value:** a prototype constant that may change as physics and tests improve.

An element or plane appearing in a catalogue does not prove that every associated ability exists. A spell example demonstrates only what its operations actually perform. Archived audits explain the release in their filenames and must not override current source/reference documentation.

## Dedicated catalogues

- [Conceptual Domains and Specialised Categories](CONCEPTUAL_DOMAINS.md)
- [MANA Plane Catalogue](PLANE_CATALOGUE.md)
- [Built-in Being and Creature Catalogue](CREATURE_CATALOGUE.md)
