# MANA Interpreter Architecture

**Page kind:** Explanation  

**Version:** 2.0.0
**Audience:** readers who want to understand how source code becomes a simulated spell.

MANA is a standalone source language implemented in Python at present. The interpreter is implemented in Python; `.mana` files are parsed and executed according to MANA’s own grammar and runtime rules. The interpreter has a small language front end, a runtime, and specialised element, unit, energy and physics modules.

## Execution pipeline

```text
.mana source
   ↓
Lexer → Tokens
   ↓
Parser → AST (program structure)
   ↓
Runtime evaluates statements and expressions
   ├─ language values and scope
   ├─ element rules
   ├─ quantities and units
   ├─ energy accounting
   ├─ 2D world physics
   └─ imported library namespaces
   ↓
SpellResult / printed trace / committed world state
```

The visualiser is deliberately outside this pipeline. It may display calculated state, but it must not decide whether an effect succeeds.

## 1. Source reader and lexer

The lexer reads lines of `.mana` text and converts characters into ordered tokens. It tracks line and column information for error messages, recognises quoted strings and numeric literals, treats `#` as a comment marker, and emits `INDENT`/`DEDENT` tokens for block boundaries. This is how indentation can represent `def`, `if`, `tgset`, `simul`, and other blocks without braces.

The token categories currently include:

| Category | Examples | Purpose |
|---|---|---|
| Values/names | `NUMBER`, `STRING`, `IDENT` | Numeric literal, text literal, or identifier. |
| Layout | `NEWLINE`, `INDENT`, `DEDENT`, `EOF` | Lines and nested blocks. |
| Grouping | parentheses, brackets, comma, dot, colon | Calls, lists, attributes, and block headers. |
| Operators | `+`, `-`, `*`, `/`, `%`, `**`, comparisons | Arithmetic and comparisons. |
| Declarations and keywords | `def`, legacy token `spldef`, contextual `spell`, `load`, `incant`, `tgset`, `if`, `while`, `for`, `create`, `skip`, `simul`, timer/event words | `spell name(...):` is recognized contextually; `spldef` remains reserved for compatibility. |

`load` and `skip` are MANA keywords. Use `incant value` to supply a definition result, `load` to load libraries, and `skip` as a no-operation statement. A definition exits with `incant`, optionally supplying a value.

## 2. Parser and AST

The parser checks the token sequence against the MANA grammar. It does not perform the spell simulation. Instead it creates an abstract syntax tree (AST): objects that represent what the source requests. AST node families include:

- **Program and Block:** ordered statements and indented statement groups.
- **Literal, Name, ListLiteral, Attribute:** values, variable references, lists, and dot access.
- **Unary, Binary, Call:** expression operations and calls.
- **Assignment and ExpressionStatement:** storing a value or executing a standalone statement.
- **FunctionDef, Incant and Pass:** definition bodies, supplying a definition's result, and an intentional no-op.
- **Create, TuneAssignment, SpellModeStatement:** object creation, editing an existing spell operation, and non-expression `post`/`release` commands.
- **TargetSet and TargetContext:** defining a target profile separately from selecting a target for a casting block.
- **If, While, For, Simul, Wait, After, Every, Event and ImportLibrary:** control flow, scheduling/events, concurrent operation blocks, and library loading.

The MANA grammar defines the available expression forms. Tuple, set and dictionary literals are not general MANA data types. Ordinary spell definitions support zero parameters, or the single `element` selector for a reusable element template. General parameterized helper definitions are allowed only inside validated library entry files.

## 3. Runtime and scope

The runtime evaluates the AST and owns the mutable simulation state. An environment maps names to values and links to a parent environment for lexical lookup. A definition captures its environment. An element template call creates a configured `SpellInstance`; it does not execute the spell body. An ordinary `post` or `release` resolves a spell name and uses its saved settings.

The distinction among commands is important:

- `show` prints values; it does not execute a spell or create a trace.
- `post(spell)` runs the spell through the actual runtime, records a `SpellResult` and trace, then rolls world mutations back.
- `release(spell)` runs the same execution logic and commits world changes.
- `incant value` supplies a value from a definition. It is a statement, not a callable function.
- `tune(spell.operation) = target, value` changes one existing operation on one configured instance. It is configuration, not spell execution.

The complete host-side result record carries success state, the `incant` value, trace steps, created/changed objects, collision/hit details, cost readouts and errors. MANA source cannot assign `post` or `release` to a variable; IDE and tests may inspect the record through host APIs.

## 4. Built-ins and library namespaces

Core operations are installed by the runtime and available without imports. Examples include creating/shaping objects, changing temperature, setting velocity, advancing virtual time, querying collisions, and displaying output. Global names are kept separate from optional helpers.

`load geometry2d` exposes advanced planar calculations under the `geometry2d` namespace. `load vector3d` exposes 3D vector calculations under `vector3d`. Importing a module does not change the world to 3D. Namespaced helpers are not copied into the global scope, so `geometry2d.distance` and `vector3d.distance` remain distinct.

A custom `.manalib` package contains a JSON manifest and MANA source. The loader validates the manifest, entry path, syntax and exports; only top-level `def` declarations, nested `load` statements and `skip` are accepted. The package cannot contain arbitrary Python that the loader executes. The Library Builder guide documents how to make these packages.

## 5. Element catalogue and magical interactions

`elements.py` stores registered `ElementProfile` entries and categorises them as fundamental, conceptual or derived. Exactly Fire, Water, Earth and Air are fundamental. A profile describes its domains and any explicitly recorded secondary involvement. The domain table lets `has_domain` answer catalogue questions.

The `interaction()` rule evaluator is independent of display. It returns a structured result describing the produced kind/name, mana quantity, component names, released mana, note, and (where applicable) energy origin. Implemented special cases include Fire/Water cancellation, Light/Darkness cancellation, Water/Earth → Mud, Mud/Life → Wood, Earth/Life → a compound, Water/Air → Ice when heat can be removed, and Fire/Air → Fire propagation behaviour. Other pairings currently produce a generic compound rather than pretending a special rule is implemented. See [Elements and Rules](../reference/ELEMENTS_AND_RULES.md).

## 6. Quantities and units

The quantity system stores a numeric value plus a dimension. Base dimensions are kilograms, metres, seconds, kelvin and mana. Addition/subtraction require matching dimensions; multiplication/division compose dimensions. Aliases include velocity, acceleration, force, energy, pressure, density, momentum and power units. This stops physically incompatible operations, such as adding a speed to a temperature, from silently succeeding.

The parser/runtime support unit-bearing literals such as `300 m/s`, `500 K` and `12 m`. Units are engine rules, not text decorations. Read [Language Specification](../language/LANGUAGE_SPEC.md) and [Energy Model](../physics/ENERGY_MODEL.md) for supported dimensions and conversion assumptions.

## 7. Physics engine

World objects live in a 2D x-y plane. `advance_time` integrates motion in deterministic substeps and handles timers/events and collision checks. Collision boundaries are currently circles derived from projected area or an explicit collision radius. Collision response applies a Newtonian normal impulse; impact energy lost to the response is transferred into thermal energy, and collisions can produce prototype HP damage/events.

The engine rejects nonzero-z world movement. `vector3d` is calculation-only. Current limits—such as missing exact polygon collision, friction, fluids and angular dynamics—are described in [Physics Engine](../physics/PHYSICS_ENGINE.md).

## 8. Errors and failure boundaries

All user-facing errors inherit from `MagicLangError` and include a filename and optionally a line number:

| Error | Meaning |
|---|---|
| `SyntaxErrorML` | Invalid grammar, malformed blocks or unsupported syntax. |
| `TypeErrorML` | An operation received an unsupported kind of value or an invalid property. |
| `UnitErrorML` | Quantity dimensions or units do not agree. |
| `RuntimeErrorML` | A name/call/load is invalid or a runtime safety cap was reached. |
| `MagicErrorML` | A magical rule or guarded state transition failed. |
| `PhysicsErrorML` | A physical constraint was violated, such as impossible speed or invalid geometry. |

`post` restores trial world state after success or failure. `release` commits successful changes and restores the previous state when the execution fails. A failed `advance_time` call is atomic and restores state to before that time advance.

## 9. Observing program behaviour

Run a public example from the repository root with `python mana.py examples	argeted_fireball.mana`. Runtime messages and the Error Catalogue describe the interpreter behaviour exposed to MANA programs. Keep the relevant language guide and runnable examples aligned with intentional behaviour changes.
