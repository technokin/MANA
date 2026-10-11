# MANA Documentation — v1.0.0

**Page kind:** Reference  

This is the current documentation entry point for MANA. Read the foundations handbook first to understand what the language is designed to express, then use the language guide and references for exact syntax and function signatures.

Start with the short repository-level [MANA Introduction](../../MANA_INTRO.md) if you want the overall idea before the detailed handbook.

> **Version rule:** `docs/current/` describes v1.0.0. Historical audits and superseded decisions are under [`../archive/`](../archive/README.md) and are not current API references.

## Start with the foundations

- [Foundations Handbook](foundations/README.md) — reading order and status labels.
- [What MANA Is](foundations/MANA_OVERVIEW.md) — purpose, architecture, and core boundaries.
- [Mana, Matter, and Energy](foundations/MANA_AND_ENERGY.md) — the mana concept, physical-energy bookkeeping, and conversion readouts.
- [Elements and Concepts](foundations/ELEMENTS_AND_CONCEPTS.md)
- [Conceptual Domains and Specialised Categories](foundations/CONCEPTUAL_DOMAINS.md) — four base elements, conceptual entries, derived entries, plane channels, and interactions.
- [Programming and Spells](foundations/PROGRAMMING_AND_SPELLS.md) — `def`, `spldef`, `tgset`, `incant`, `load`, execution modes, time, and events.
- [Universal Control and Pure Mana](foundations/UNIVERSAL_CONTROL_AND_PURE_MANA.md) — force, motion, object manipulation, mana constructs, bursts, and beams.
- [Planes and Pathways](foundations/PLANES_AND_PATHWAYS.md)
- [MANA Plane Catalogue](foundations/PLANE_CATALOGUE.md) — identities, regions, pathways, energy transfer, and invocation.
- [Beings and Summoning](foundations/BEINGS_AND_SUMMONING.md)
- [Built-in Being and Creature Catalogue](foundations/CREATURE_CATALOGUE.md) — data records, built-in beings, cross-plane movement, taming, return, and recall.
- [Necromancy and Undead](foundations/NECROMANCY_AND_UNDEAD.md) — reanimation, constructed undead spells, and control boundaries.
- [Objects, Materials, and State](foundations/OBJECTS_MATERIALS_AND_STATE.md) — world objects, `tgset`, properties, material states, and object lifecycle.
- [World Engine: 2D and 3D](foundations/WORLD_ENGINE_2D_3D.md) — simulation physics versus 2D/3D calculations.
- [Libraries and Extension Model](foundations/LIBRARIES_AND_EXTENSION_MODEL.md) — core/runtime boundaries, built-ins, data libraries, and user packages.
- [Python Runtime and Development Tools](foundations/PYTHON_RUNTIME_AND_TOOLING.md) — source execution, editor support, and project structure.
- [Implementation Status](foundations/IMPLEMENTATION_STATUS.md) — implemented, partial, and planned features.
- [Glossary and Design Terms](foundations/GLOSSARY_AND_DESIGN_TERMS.md) — consistent terminology used throughout the docs.

## Quick lookup and diagnostics

- [MANA Cheat Sheet](reference/MANA_CHEAT_SHEET.md) — keywords, operators, units, reserved names, events, and errors.
- [Error Catalogue](reference/ERROR_CATALOGUE.md) — error families, diagnostic format, common causes, and fixes.
- [Error Message Index](reference/ERROR_MESSAGE_INDEX.md) — generated inventory of error-constructor messages and source locations.
- [Generated API Index](reference/API_INDEX.md) — functions, language constructs, events, and error classes.
- [Glossary Usage Index](foundations/GLOSSARY_USAGE_INDEX.md) — pages mentioning each glossary term.
- [Not Supported Yet](foundations/NOT_SUPPORTED_YET.md) — current limits in one place.
- [Release Checklist](RELEASE_CHECKLIST.md) — repeatable verification before a release.

## Learn the actual language

- [Getting Started: Language Guide](getting_started/LANGUAGE_GUIDE.md)
- [Ten-Minute Tutorial](getting_started/TEN_MINUTE_TUTORIAL.md)
- [Recipes](getting_started/RECIPES.md)
- [Language Specification](language/LANGUAGE_SPEC.md)
- [Keyword Design and Migration](language/KEYWORD_MIGRATION.md)
- [Spell Templates and Tuning](language/SPELL_TEMPLATES_AND_TUNING.md)
- [Built-in Function Reference](reference/FUNCTION_REFERENCE.md)
- [Elements and Implemented Rules](reference/ELEMENTS_AND_RULES.md)

## Physics and execution

- [Physics Engine](physics/PHYSICS_ENGINE.md)
- [Energy Model](physics/ENERGY_MODEL.md)
- [Interpreter Architecture](internals/INTERPRETER_ARCHITECTURE.md)
- [Component Reference](internals/COMPONENT_REFERENCE.md)

## Built-in libraries

- [Pure Mana and Universal Control](libraries/MANA_LIBRARY.md)
- [2D Geometry](libraries/GEOMETRY2D_LIBRARY.md)
- [3D Vector Calculations](libraries/VECTOR3D_LIBRARY.md)
- [Planes](libraries/PLANES_LIBRARY.md)
- [Plane Creation (`drafter`)](libraries/DRAFTER_LIBRARY.md)
- [Cross-Plane Summoning](libraries/SUMMONING_LIBRARY.md)
- [Necromancy](libraries/NECROMANCY_LIBRARY.md)
- [User Library Builder](libraries/LIBRARY_BUILDER.md)

## Tools and support

- [Python Setup and VS Code](tooling/PYTHON_AND_VSCODE.md)
- [Troubleshooting](troubleshooting/TROUBLESHOOTING.md)

## Scope boundary

The language interpreter and world engine decide program semantics. VS Code provides optional editing support. `geometry2d` and `vector3d` are calculation libraries; only the 2D world solver currently advances world objects and resolves their collisions. A catalogue record, example, or future-design section is not proof of full implementation; consult [Implementation Status](foundations/IMPLEMENTATION_STATUS.md).
