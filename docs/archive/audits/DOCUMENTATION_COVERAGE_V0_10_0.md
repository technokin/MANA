# MANA v0.10.0 — Documentation Coverage Audit

**Purpose:** verify that the documentation describes the implemented language and the current built-in libraries. This audit is checked by `tests/test_libraries.py`; it does not claim that future or unfinished systems are implemented.

## Coverage summary

| Area | Current coverage | Canonical document |
|---|---|---|
| Source syntax and spelling rules | Definitions, element templates, tuning, statements vs expressions, control flow, units and imports | [Language Specification](../../current/language/LANGUAGE_SPEC.md) |
| Beginner usage | Running files, common source constructs and targeted casting | [Language Guide](../../current/getting_started/LANGUAGE_GUIDE.md) |
| Global built-ins and statement commands | The complete reserved core name catalogue is cross-checked against the built-in reference; geometry labels and constants are called out separately from executable operations | [Built-in Reference](../../current/reference/FUNCTION_REFERENCE.md) |
| Element catalogue | Every currently registered catalogue entry is cross-checked against the element reference | [Elements and Rules](../../current/reference/ELEMENTS_AND_RULES.md) |
| Tokenizer | All `TokenType` members, keyword spellings, comments, line/column metadata and indentation behaviour | [Implementation Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| Parser and AST | Accepted grammar, important syntax restrictions, every AST node class, and how a feature moves from syntax to runtime | [Implementation Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| Runtime and result data | World objects, element type values, definitions, spell instances, trial/firing result records, scopes, timers, events and library namespaces | [Implementation Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| Units and energy | Base dimensions, derived units, matter/mana multiplier and cost readouts | [Energy Model](../../current/physics/ENERGY_MODEL.md) and [Implementation Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| Default world physics | 2D time steps, movement, target-directed speed, circle contacts, response, damage, events, safety limits and omissions | [Physics Engine](../../current/physics/PHYSICS_ENGINE.md) |
| Optional 2D library | Every exported API, including advanced geometry, angles, intersections, aiming and explicit-angle `launch` | [2D Geometry Library](../../current/libraries/GEOMETRY2D_LIBRARY.md) |
| Optional 3D library | Every exported calculation and both exported constants; no 3D world simulation | [3D Vector Library](../../current/libraries/VECTOR3D_LIBRARY.md) |
| User library system | Project creation, manifest, validation, building, export rules, package safety and limitations | [Library Builder](../../current/libraries/LIBRARY_BUILDER.md) |
| Error recovery | Common error families and troubleshooting | [Troubleshooting](../../current/troubleshooting/TROUBLESHOOTING.md) |
| IDE tooling | Syntax highlighting, snippets, Windows runner and file association | [Windows and VS Code](../../current/tooling/PYTHON_AND_VSCODE.md) |

## Source-derived inventory checked

The current implementation inventory is:

- **50 token kinds** declared by `magiclang/tokens.py`.
- **28 AST node classes** declared by `magiclang/ast_nodes.py`.
- **19 registered element types**: four fundamental elements, eleven provisional conceptual entries, and four derived/specialized entries.
- **68 globally reserved/built-in names** in the runtime catalogue. These include operations, statement command names, constants, namespace names and shape labels; they are not all callable functions.
- **29 exports** in `geometry2d`, including advanced calculations and an explicit-angle trajectory helper.
- **25 exports** in `vector3d`, including 23 calculation helpers and two constants.

The tests check that every declared token kind and AST node appears in the component reference, every catalogue element appears in the element guide, every global built-in name is referenced in the built-in guide, and every exported library name is documented in its library guide.

## Code/data boundaries

- `post(spell)` and `release(spell)` are not being redesigned in this documentation/library work. `post` runs the real execution path in a trial and restores world state; `release` commits successful changes. Their host-side `SpellResult` is not a value assignable by MANA source.
- The default 2D world engine remains active without imports. `geometry2d` exposes additional calculations only through that namespace, including `geometry2d.launch(...)` for a manual angle. `vector3d` is calculation-only; importing it does not modify the world's dimensionality.
- The library builder packages MANA source in `.manalib`; it does not load Python payloads. The current format supports a single entry file and optional README, not a general multi-file dependency resolver.
- Documented limitations remain limitations: exact polygon collision, fluids, friction, torque/angular response, combustion, pressure waves, material breakage, graphical rendering, the Grimoire IDE and 3D world simulation are not asserted to exist.

## Verification approach

Run from the project root:

```powershell
python -m pytest -q
python -m compileall -q magiclang mana.py tools\library_builder.py
```

The coverage assertions live in `tests/test_libraries.py`. Local Markdown-link checks are also run before packaging the release archive.
