# MANA Documentation — v2.0.0

**Page kind:** Reference  

> **Current source snapshot:** [MANA 2.0.0 Source Snapshot Notes](RELEASE_V2_0_0_REPORT.md) describes what this package contains. The [MANA 2.0.0 Release Log](../../MANA_v2.0.0_RELEASE_LOG.md) summarizes the earlier development history. The older [pre-release audit notes](../archive/audits/release_reports/MANA_V2_PRE_RELEASE_AUDIT.md) and [consolidation audit](../archive/audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md) are retained as historical records.


This is the current documentation entry point for MANA. Read the foundations handbook first to understand what the language is designed to express, then use the language guide and references for exact syntax and function signatures.

Start with the short repository-level [MANA Introduction](../../MANA_INTRO.md) if you want the overall idea before the detailed handbook.

> **Version rule:** `docs/current/` describes v2.0.0. Historical audits and superseded decisions are under [`../archive/`](../archive/README.md) and are not current API references.

## Start with the foundations

- [MANA Magic System Compendium](foundations/MAGIC_SYSTEM_COMPENDIUM.md) — magic-first explanations of mana, spells, elements, targeting, pure mana, conjuration, transformation, weather, beings, summoning, planes, pathways, necromancy, world laws, and the boundary between design and implementation.
- [Foundations Handbook](foundations/README.md) — reading order and status labels.
- [What MANA Is](foundations/MANA_OVERVIEW.md) — purpose, architecture, and core boundaries.
- [Mana, Matter, and Energy](foundations/MANA_AND_ENERGY.md) — the mana concept, physical-energy bookkeeping, and conversion readouts.
- [Elements and Concepts](foundations/ELEMENTS_AND_CONCEPTS.md)
- [Conceptual Domains and Specialised Categories](foundations/CONCEPTUAL_DOMAINS.md) — four base elements, conceptual entries, derived entries, plane channels, and interactions.
- [Programming and Spells](foundations/PROGRAMMING_AND_SPELLS.md) — `def`, `spell` (legacy alias `spldef`), `tgset`, `incant`, `load`, and execution modes.
- [Execution, Time, and Events](foundations/EXECUTION_TIME_AND_EVENTS.md) — scheduled statements, event handlers, world time, and recorded outcomes.
- [Universal Control and Pure Mana](foundations/UNIVERSAL_CONTROL_AND_PURE_MANA.md) — force, motion, object manipulation, mana constructs, bursts, and beams.
- [Planes and Pathways](foundations/PLANES_AND_PATHWAYS.md)
- [MANA Plane Catalogue](foundations/PLANE_CATALOGUE.md) — identities, regions, pathways, energy transfer, and invocation.
- [Beings and Summoning](foundations/BEINGS_AND_SUMMONING.md)
- [Built-in Being and Creature Catalogue](foundations/CREATURE_CATALOGUE.md) — data records, built-in beings, cross-plane movement, taming, return, and recall.
- [Necromancy and Undead](foundations/NECROMANCY_AND_UNDEAD.md) — reanimation, constructed undead spells, and control boundaries.
- [Objects, Materials, and State](foundations/OBJECTS_MATERIALS_AND_STATE.md) — world objects, `tgset`, properties, material states, and object lifecycle.
- [Library Compatibility and Naming Leeway](libraries/LIBRARY_COMPATIBILITY.md) — shared data boundaries, naming aliases, and cross-library checks.
- [Materials and Forging](libraries/MATERIALS_AND_ARMORY.md) — periodic data, alloys, conjuration, equipment blueprints, armour, arrows, metal fields and transmutation.
- [Anatomy and Comparative Biology](libraries/ANATOMY_LIBRARY.md) — species profiles, individually catalogued typical adult human bones, tissues, cells, organs, clade-specific structures and custom species.
- [Comparative Anatomy Research and Model Design](libraries/COMPARATIVE_ANATOMY_RESEARCH.md) — research-backed comparison of human, mammal, bird, snake, earthworm and fictional body plans, with explicit simulation limits.
- [Physiology and Body Magic](libraries/PHYSIOLOGY_LIBRARY.md) — active injuries, blood-state operations, body changes, death, revival and undead states.
- [Arcana: Magical Disciplines](libraries/ARCANA_LIBRARY.md) — world-local catalogue of magic schools, domains, methods, limits and counters.
- [World Engine: 2D and 3D](foundations/WORLD_ENGINE_2D_3D.md) — simulation physics versus 2D/3D calculations.
- [Libraries and Extension Model](foundations/LIBRARIES_AND_EXTENSION_MODEL.md) — core/runtime boundaries, built-ins, data libraries, and user packages.
- [Python Runtime and Development Tools](foundations/PYTHON_RUNTIME_AND_TOOLING.md) — source execution, editor support, and project structure.
- [Implementation Status](foundations/IMPLEMENTATION_STATUS.md) — implemented, partial, and planned features.
- [Glossary and Design Terms](foundations/GLOSSARY_AND_DESIGN_TERMS.md) — consistent terminology used throughout the docs.

## Source snapshot

- [MANA 2.0.0 Source Snapshot Notes](RELEASE_V2_0_0_REPORT.md) — included components and package boundaries.

## Quick lookup and diagnostics

- [MANA Cheat Sheet](reference/MANA_CHEAT_SHEET.md) — keywords, operators, units, reserved names, events, and errors.
- [Error Catalogue](reference/ERROR_CATALOGUE.md) — error families, diagnostic format, common causes, and fixes.
- [Error Message Index](reference/ERROR_MESSAGE_INDEX.md) — generated inventory of error-constructor messages and source locations.
- [Generated API Index](reference/API_INDEX.md) — functions, language constructs, events, and error classes.
- [Glossary Usage Index](foundations/GLOSSARY_USAGE_INDEX.md) — pages mentioning each glossary term.
- [Not Supported Yet](foundations/NOT_SUPPORTED_YET.md) — current limits in one place.
- [Project Changelog](../../CHANGELOG.md) — historical version notes and source changes.
- [Earlier Project Audit](../archive/audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md) — historical pre-release snapshot; do not use its test counts as current.

## Learn the actual language

- [Getting Started: Language Guide](getting_started/LANGUAGE_GUIDE.md)
- [Ten-Minute Tutorial](getting_started/TEN_MINUTE_TUTORIAL.md)
- [Building Your First Spells](getting_started/BUILDING_FIRST_SPELLS.md) — a practical path from an object to a complete spell.
- [Recipes](getting_started/RECIPES.md)
- [Example Cookbook](getting_started/EXAMPLE_COOKBOOK.md) — a topic-based guide to the runnable example files.
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
- [World Weather, Conjuration, and Transformation](libraries/WORLD_WEATHER_AND_MATTER.md) — parameter-based climate controls, material conjuration, transmutation, and transfiguration.
- [2D Geometry](libraries/GEOMETRY2D_LIBRARY.md)
- [3D Vector Calculations](libraries/VECTOR3D_LIBRARY.md)
- [Planes](libraries/PLANES_LIBRARY.md)
- [Plane Creation (`drafter`)](libraries/DRAFTER_LIBRARY.md)
- [Cross-Plane Summoning](libraries/SUMMONING_LIBRARY.md)
- [Necromancy](libraries/NECROMANCY_LIBRARY.md)
- [User Library Builder](libraries/LIBRARY_BUILDER.md)

## Separate magic-design catalogue

- [MANA Magic Inspiration Catalogue](../../MANA_MAGIC_INSPIRATION_CATALOGUE.md) — original spell and discipline concepts inspired by broad MCU/DC themes. Each entry distinguishes current primitives from partial foundations and future design targets. This is not a changelog or an implementation promise.

## Tools and support

- [Python Setup and VS Code](tooling/PYTHON_AND_VSCODE.md)
- [VS Code Extension Guide](tooling/VSCODE_EXTENSION_GUIDE.md) — Run, inline completion, and Visualiser installation.
- [Project File Layout](tooling/PROJECT_LAYOUT.md) — where source, docs, examples, extensions, and installers belong.
- [Magic Visualiser](tooling/MAGIC_VISUALISER.md) — optional magical scene replay.
- [Where MANA Could Be Used](foundations/FUTURE_USES_AND_ROADMAP.md) — current application areas and a practical future roadmap.
- [Troubleshooting](troubleshooting/TROUBLESHOOTING.md)

## Scope boundary

The language interpreter and world engine decide program semantics. VS Code provides optional editing support. `geometry2d` and `vector3d` are calculation libraries; the 2D world solver advances world objects, resolves swept-circle collisions with restitution and tangential friction, applies global gravity and wind drag, and processes configured thermal exchange, catalogue phase changes, wetting and dust coating. `world.laws()` reports the active rule set. The engine also provides a reference periodic table for conjured/transmuted matter. This remains a prototype world engine, not a complete weather, chemistry, or material-science solver. A catalogue record, example, or future-design section is not proof of full implementation; consult [Implementation Status](foundations/IMPLEMENTATION_STATUS.md).
