# Libraries and Extension Boundaries

**Page kind:** Explanation  

**Current source version:** v2.0.0

MANA separates core rules from optional/domain-specific features. A library is a namespace of related functions and data. Importing one makes that namespace available; it should not alter unrelated language semantics simply because its data was loaded.

## 1. `load` and namespace access

The source keyword is `load`, not `import`. A program can write:

```mana
load geometry2d
load vector3d
load planes

sample_point = geometry2d.point(2 m, 5 m)
position = vector3d.position(2 m, 5 m, 0 m)
show planes.category_of("Mortal Plane")
```

Expected output:

```text
mortal
```

The library namespace is accessed through a dot, and this keeps APIs separated. `geometry2d.distance(...)` and `vector3d.distance(...)` are distinct functions, so one library cannot accidentally overwrite the other.

Built-in dependencies are checked explicitly. The plane-data modules and `drafter`, `summoning`, and `necromancy` depend on the plane registry and require `load planes` before their explicit load. Internal lazy data loads from an already-loaded library do not require a new source-level `load` line.

## 2. Core versus library responsibilities

The core language owns syntax and evaluation, ordinary/spell definitions, target context, object creation/operations, world time/physics, units, energy accounting, errors, and shared runtime state. It also installs the basic `mana` namespace because pure-mana effects and universal control are foundational operations.

Libraries own additional calculation APIs, plane registry behaviour, plane creation/data registration, cross-plane being access, and death-related reanimation. A library must reuse core objects, physics, and ledger conventions instead of building a competing simulation.

## 3. Current built-in libraries

| Library | Main responsibility | Does not do |
|---|---|---|
| `mana` | Pure-mana constructs, radial bursts, beams, element-independent object control | It does not define a separate finite mana pool. |
| `geometry2d` | 2D geometry calculations and aiming helpers | It is not the world physics/collision solver. |
| `vector3d` | 3D vector/maths/physical calculations | It does not enable 3D world physics. |
| `planes` | Plane identity/categories/regions, pathways/routes, energy transfer ledger, invocation permissions | It does not create planes or move beings. |
| `drafter` | Create custom plane records, custom values, regions and beings | It is not a general editor for rewriting established built-in planes. |
| `summoning` | Find a being record, bring it through a route, tame, send back and recall | It is not a user spell named `summon_skeleton`, nor a generic body reanimation function. |
| `necromancy` | Reanimate existing local bodies and identify undead state | It does not create a corpse from nothing or implement full skeleton AI. |
| `elemental_planes` | Data for thirteen individual elemental/special planes and their spirits | It does not merge those planes into one place or make them all base elements. |
| `atlantis` | Atlantis being data | It does not move a Mermaid by itself. |
| `fae_paradise` | Fae Paradise being data | It does not provide a full Fae behaviour system. |
| `wild_realm` | Wild Realm species records | It does not automatically import every creature into the world. |
| `hell` | Hell regions data | It does not build all sixteen future Naraka subregions or a full afterlife simulation. |
| `heaven` | Heaven data module | Its current built-in being list is empty. |
| `lineage_halls` | Lineage Halls data module | Its current built-in being list is empty. |

## 4. Plane creation and arbitrary data

`drafter` allows a program to create a custom plane and attach safe data values, regions, and being records. This is important because plane data can contain many user-defined properties, and a hardcoded Python property for every possible field would be unmaintainable. The generic data mechanism should still validate the shapes/types of records and prevent those values from executing arbitrary Python.

A custom plane's properties have no automatic side effects on MANA physics. If a user defines `wind_strength = 20`, that value affects the world only if a MANA spell/library explicitly reads and interprets it.

## 5. Plane data loading

The identity registry is small and always available after `load planes`. Plane data loads on demand. For example, elemental spirit data is grouped into `elemental_planes`; Atlantis, Fae Paradise, Wild Realm, Hell, Heaven, and Lineage Halls each have distinct data modules. This arrangement is chosen to keep the common registry small and prevent importing one plane from loading every being in the catalogue.

## 6. The Library Builder

`tools/library_builder.py` is a developer command-line tool for user-authored MANA libraries. Its operations initialise a starter library, validate its manifest/source and build a `.manalib` package. It is not a plane creator, not a World Engine content editor, and not part of runtime magic semantics. The future IDE may provide a GUI for this workflow without requiring a second packaging implementation.

The current builder supports a small source-package format; it is not yet a full dependency resolver or multi-module package manager. The language runtime imports user library packages from the project `libraries/` folder. Library names are validated against reserved language/built-in names.

## 7. How to extend without coupling everything

When adding a new library:

1. Decide whether the behaviour must be a core invariant or can be isolated behind a namespace.
2. Keep APIs deterministic and unit-aware.
3. Use existing `MagicObject`, `Quantity`, physics, ledger, and error classes when applicable.
4. Validate all arguments and return MANA errors rather than leaking raw host-language exceptions.
5. If a library depends on `planes` or another library, declare/validate that dependency explicitly.
6. Add tests for normal behaviour, malformed inputs, rollback, and interactions with existing libraries.
7. Update the exact function reference, library guide, examples, VS Code grammar/snippets, and current implementation-status table.

## 8. API status

Function names in current library guides are the public names for this prototype revision. The worldbuilding concept and library responsibility can be final even when a function is a prototype interface; public APIs must nevertheless be treated as implementation contracts within a release. Do not silently reintroduce removed names such as `summoning.summon` or `necromancy.animate_construct`; historical audits may mention those as removed/old ideas but are not current references.
