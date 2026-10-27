# Library Compatibility and Naming Leeway

**Page kind:** Reference  
**Status:** Current v2.0.0 compatibility contract

MANA's built-in libraries are optional namespaces, but several share runtime data. Loading one library does not mean every other library must be loaded, and a catalogue record does not automatically enable a simulation mechanic.

## Naming leeway

For custom material and equipment lookup, spaces, underscores, and hyphens are interchangeable. For example, `Moon-Metal`, `moon metal`, and `MOON_METAL` refer to the same custom material. A custom name is stored once; aliases do not create duplicate records.

The displayed name remains the name originally registered. Search results and profile lookups return canonical records. A custom material must still have valid density and state data; flexible spelling does not bypass validation.

## Compatibility map

| Library / feature | Shared data or dependency | Compatibility boundary |
|---|---|---|
| `materials` | Periodic-table and physical-material records; runtime-local custom materials | Custom material profiles are available to world conjuration, transmutation, and `armory` blueprints. |
| `armory` | Runtime-local custom material and equipment records | Equipment blueprints reference material profiles; they do not create matter until conjured. Name separators are flexible for custom blueprint lookup. |
| `anatomy` | Species, organs, systems, tissues, and body-structure records | These records describe body models; they do not alone implement a unique solver for every structure. |
| `physiology` | Anatomy records plus per-entity tracked state | A structure is usable when the selected body's profile provides it or a compatible custom structure is defined. Species differences remain meaningful; absent organs are not silently treated as universal. |
| `planes`, `drafter`, `summoning`, `necromancy` | Plane registry and pathway/being data | Plane-data libraries require the plane system. Loading order and pathway permissions still apply; naming leeway does not bypass access rules. |
| `geometry2d`, `vector3d` | Standalone calculation APIs | Vector calculations do not turn the world engine into a 3D simulator. |
| `arcana`, `mana`, `world`, `weather` | Runtime world state and/or spell execution | They compose through runtime primitives; a label or catalogue entry is not a new spell-specific engine operation. |

## Known limits and intended leeway

- Stock library records are read-only through public lookup results; custom definitions are scoped to the current runtime/world.
- `materials.by_category("all")` includes both stock and runtime-defined materials.
- A custom material can be referenced by `materials.profile()`, `armory.define()`, `conjure`, and `transmute` using equivalent separators.
- Library load dependencies are not removed by spelling flexibility. If a plane library declares a prerequisite, load that prerequisite first in MANA source.
- Anatomy/physiology combinations are not assumed biologically universal. A composite or fictional species can use custom components, but missing life-support dependencies may still produce warnings or limited behaviour.
- Unknown names, invalid units, invalid state values, and unsafe numeric ranges remain errors. Leeway is for equivalent names and compatible data access, not for silently accepting invalid inputs.

## Recommended compatibility checks for new library data

1. Resolve a stock record by canonical name and alias.
2. Define a custom record, then retrieve it using spaces, underscores, and hyphens.
3. Pass the record into every intended consumer library (for materials: armory, conjuration, and transmutation).
4. Check `all`, `search`, `by_category`, and `exists` results for consistency.
5. Test rollback and runtime isolation when a definition is made inside a trial/post operation.
6. Keep reference-only data clearly distinguished from mechanics implemented by the world engine.
