# MANA Implementation Component Reference

**Page kind:** Explanation  

**Version:** 2.0.0
**Purpose:** map the implementation to the language behaviours it provides. This guide is for people auditing or extending MANA; spell authors normally need the [Language Guide](../getting_started/LANGUAGE_GUIDE.md) and [Built-in Reference](../reference/FUNCTION_REFERENCE.md), not the internals described here.

## 1. How a program runs

```text
source.mana
   │
   ▼
Lexer ──► Token stream
   │
   ▼
Parser ──► AST (program structure)
   │
   ▼
Runtime ──► language values, scopes, definitions and loads
   │
   ├──► element interaction rules
   ├──► quantities and unit checks
   ├──► energy ledger and cost readouts
   └──► 2D world physics, collisions and target damage
```

The 2D world engine operates without an explicit library load. `geometry2d` and `vector3d` expose calculation helpers, `planes` provides identity and pathway operations, and the built-in `mana` namespace provides pure-mana effects and universal control. These namespaces do not replace or turn on the world engine. The display layer is not part of the execution pipeline and must not decide whether a spell succeeds.

## 2. Source files and responsibilities

| File or folder | Responsibility | What it should not decide |
|---|---|---|
| `mana.py` | Command-line entry point; validates the requested `.mana` path and reports MANA errors. | Language syntax or physics rules. |
| `magiclang/__init__.py` | Declares the implementation package version (`2.0.0`). | Runtime setup or program execution. |
| `magiclang/runner.py` | Reads a source file, tokenizes and parses it, creates a project-aware runtime, then runs the program. | The semantics of an individual physics operation. |
| `magiclang/tokens.py` | Defines token kinds, reserved keyword mapping, and the token record with source location. | Whether a parsed spell is physically possible. |
| `magiclang/lexer.py` | Converts source characters into tokens, including strings, numbers, comments, indentation and punctuation. | Program execution. |
| `magiclang/parser.py` | Enforces MANA grammar and builds AST nodes; produces syntax errors with file/line context. | Running spells or mutating world objects. |
| `magiclang/ast_nodes.py` | Data structures representing parsed expressions and statements. | Lexing, grammar validation or execution. |
| `magiclang/runtime.py` | Scopes, names, values, built-ins, configured spell instances, `tune`, target context, library loads, `post`/`release`, event/timer dispatch and execution records. | Drawing the world. |
| `magiclang/elements.py` | Element catalogue, domain ownership and the explicit interaction-rule evaluator. | General language parsing or collision simulation. |
| `magiclang/units.py` | Quantities, dimensions, recognized unit names and dimensional arithmetic. | Deciding whether an elemental reaction is allowed. |
| `magiclang/physics.py` | Vector and physical calculation helpers such as speed enforcement, momentum, kinetic energy, force, pressure and displacement. | The world clock and pairwise collision search. |
| `magiclang/physics_engine.py` | 2D time-step integration, swept-circle contact detection, impact response, collision heat and prototype target damage. | UI rendering or library namespace selection. |
| `magiclang/libraries/__init__.py` | Documents and exports the built-in library package surface. | Selecting which library a program loads. |
| `magiclang/libraries/geometry2d.py` | Optional advanced planar geometry calculations and explicit-angle trajectory control. | Enabling normal 2D world physics; that is already active. |
| `magiclang/libraries/drafter.py` | Creates custom plane definitions, regions, custom values and beings. |
| `magiclang/libraries/summoning.py` | Resolves being records and manifests beings through `planes` pathways. |
| `magiclang/libraries/necromancy.py` | Reanimates declared local corpse/bone objects or animates solid constructs; `Necro` usage is recorded through `planes` without adding physical energy. |
| `magiclang/libraries/three_d.py` | Optional 3D vector and calculation functions. | Turning the 2D world into a 3D simulator. |
| `magiclang/libraries/mana.py` | Pure-mana constructs, bursts and beams; universal control (toward, away, lift, hold, stop, collect); source-aware defaults and effect energy accounting. | Element-specific operations or a separate physics implementation. |
| `magiclang/libraries/planes.py` | Plane identification/existence, categories and regions, pathway operations, deterministic shortest routes, energy transfers/channels, and elemental invocation. | Creating plane definitions or transferring beings. |
| `magiclang/libraries/planar_registry.py` | Runtime-scoped compact identity records, region records, explicit pathway records, aliases and invocation permissions; provides the identity-registration hook used by `drafter`. | Exposing a plane-creation function through `planes`. |
| `magiclang/libraries/plane_data/` | Independent data modules for the 13 elemental planes and spirits, Hell's current regions, and currently specified beings. | Changing the semantics of MANA execution. |
| `tools/library_builder.py` | Creates library projects, validates MANA library source/manifest, and packages `.manalib` archives. | Executing arbitrary Python code from a library package. |
| `tools/vscode-extension/` | VS Code syntax definition, snippets, comment/indent rules and extension metadata. | Interpreting or simulating MANA programs. |

For execution semantics, the existing rules remain unchanged: `show` prints; `post(spell)` runs a trial and restores world state; `release(spell)` commits the same spell execution. Their records are available to host tools and tests, not as assignable MANA expressions. See [Spell Modes in the Language Specification](../language/LANGUAGE_SPEC.md#4-statements-and-expression-behaviour).

## 3. Tokens: what the lexer produces

Tokens have four fields: kind, value, source line, and source column. The parser consumes token kinds; the value and source location help it build AST nodes and report errors.

### Values and layout

| Token kinds | Meaning |
|---|---|
| `NUMBER`, `STRING`, `IDENT` | A number, quoted text, or identifier. Numeric literals may use decimal and exponent notation. |
| `NEWLINE` | End of a non-blank source line. |
| `INDENT`, `DEDENT` | Enter or leave an indentation block. Tabs are normalized to four spaces before tokenization. |
| `EOF` | End of input. |

### Delimiters and operators

| Token kinds | Source spellings |
|---|---|
| `LPAREN`, `RPAREN` | `(`, `)` |
| `LBRACKET`, `RBRACKET` | `[`, `]` |
| `COMMA`, `DOT`, `COLON` | `,`, `.`, `:` |
| `PLUS`, `MINUS`, `STAR`, `SLASH`, `PERCENT`, `POWER` | `+`, `-`, `*`, `/`, `%`, `**` |
| `EQ`, `EQEQ`, `NE` | `=`, `==`, `!=` |
| `LT`, `LE`, `GT`, `GE` | `<`, `<=`, `>`, `>=` |

### Keyword tokens

The lexer maps these reserved source words to keyword token kinds:

| Token kind | Source spelling | Role |
|---|---|---|
| `KW_DEF` | `def` | Define an ordinary calculation/helper function. It may accept parameters and supplies its result with `incant`. |
| `KW_SPLDEF` | `spldef` | Legacy spell-declaration token retained for compatibility. The preferred `spell name(...):` form is parsed contextually. |
| `KW_LOAD` | `load` | Load a library into its own namespace. |
| `KW_INCANT` | `incant` | Supply a definition's value and immediately exit the current definition. |
| `KW_TGSET` | `tgset` | Define a target profile or open a temporary target context, depending on syntax. |
| `KW_IF`, `KW_ELIF`, `KW_ELSE` | `if`, `elif`, `else` | Conditional control flow. |
| `KW_WHILE`, `KW_FOR`, `KW_IN` | `while`, `for`, `in` | Repetition and sequence iteration. |
| `KW_AND`, `KW_OR`, `KW_NOT` | `and`, `or`, `not` | Boolean operations. |
| `KW_TRUE`, `KW_FALSE` | `true`, `false` | Boolean values. |
| `KW_CREATE`, `KW_WEAVE` | `create` | Create a magical object; the result must be assigned directly. |
| `KW_SIMUL` | `simul` | Begin a validated source-order simultaneous-operation block. |
| `KW_WAIT`, `KW_AFTER`, `KW_EVERY` | `wait`, `after`, `every` | Advance time or schedule work in virtual time. |
| `KW_WHEN` | `when` | Register an event handler. |
| `KW_SKIP` | `skip` | An intentional no-operation statement. |

`load` and `skip` are MANA keywords. `span()` and `length()` are built-ins. Use `incant` to finish a definition and optionally supply its result. Words not listed in the MANA keyword table are not identified as keywords.

The token kinds are implementation details, not extra words that programmers need to type. For example, a source word `def` becomes `KW_DEF`; users write `def`, never `KW_DEF`.

## 4. Parser and grammar responsibilities

The parser reads the token stream and creates a tree of intent. It checks syntax and important statement-shape constraints before the runtime executes anything.

| Source construct | Parser/runtime result | Important rule |
|---|---|---|
| `a = 4`, `object.temp = 500 K` | `Assignment` | Variable/property assignment is different from invoking a standalone command. Runtime-managed properties cannot be overwritten arbitrarily. |
| `def calculate(value):` | `FunctionDef(is_spell=False)` | Ordinary calculation function; supports parameters and uses `incant` to supply a value. |
| `spell e_ball(element):` | `FunctionDef(is_spell=True)` configured as an element template | Spell definitions accept no parameters or exactly one `element` selector for a base element. |
| `spell_instance = e_ball(Fire)` | `Call` followed by assignment; creates `SpellInstance` | Configuration only; does not execute the spell body. |
| `tune(spell.velocity) = ball, 300 m/s` | `TuneAssignment` | Exactly one existing operation/target pair must match. |
| `show value` or `show(value)` | `ExpressionStatement` using output | Output command, not an expression value. |
| `post(spell[, text|visual])` / `release(spell)` | `SpellModeStatement` | Standalone commands. Text is the default; visual records a non-committing scene preview. Not assignable or nestable. |
| `name = create Fire` | `Assignment` whose value is a `Create` node | Creation must be assigned directly; nested/unassigned creation is rejected. |
| `target = tgset:` | `TargetSet`, `WeaveMana` | Creates a target profile outside the spell. |
| `tgset(target):` | `TargetContext` | Temporarily selects an existing target for the enclosed cast operation. |
| `if` / `elif` / `else`, `while`, `for` | Conditional or loop AST nodes | Indented body is required. Runtime caps guard loops. |
| `simul:`, `wait`, `after`, `every`, `when` | Scheduling, event or concurrent AST nodes | These use virtual time/runtime safeguards; `simul` validates write conflicts, then runs statements in source order with rollback on failure. |
| `load geometry2d` | `LoadLibrary` | The namespace becomes available only after load. Global operations are not replaced. |
| `load planes` | `LoadLibrary` | The runtime exposes plane identities and pathway navigation through a separate namespace. |
| `[a, b, c]` | `ListLiteral` | Lists are the only general collection literal in this prototype. |

The parser implements MANA’s defined grammar. General tuple/set/dictionary literals, anonymous functions, class declarations, decorators, and arbitrary multi-parameter spell definitions are not part of the current language. Packaged library source has a controlled exception: helper definitions may take parameters so they can calculate and supply values through `incant`.

## 5. AST node inventory

Every syntactic form is represented by a node from `magiclang/ast_nodes.py`. Nodes are plain data records; the runtime assigns behaviour to them.

| Node | Represents |
|---|---|
| `Program`, `Block` | Whole parsed program and an ordered group of statements. |
| `LoadLibrary` | Library loading. |
| `Literal`, `Name`, `ListLiteral`, `Attribute`, `Subscript` | Literal value, name lookup, list value, dotted property/namespace access, and indexed sequence access. |
| `Unary`, `Binary`, `Call` | Unary operator, binary expression, and a callable expression with arguments. |
| `Create`, `Assignment`, `ExpressionStatement` | Object-creation request, assignment, and a standalone expression/command. |
| `FunctionDef`, `Incant`, `SkipStatement` | Ordinary/spell definition, value supplied by a definition, and deliberate no-op (`skip`). |
| `TargetSet`, `WeaveMana`, `TargetContext` | Target-profile creation and temporary selected-target context. |
| `If`, `While`, `For`, `Simul` | Conditional, loop, and source-order `simul` statements. |
| `Wait`, `After`, `Every`, `Event` | Virtual-time and event constructs. |
| `SpellModeStatement` | Standalone `post`/`release` command. |
| `TuneAssignment` | Replaces the value of one existing operation in one configured spell instance. |

If a new source-language feature is added, it normally needs changes in at least the lexer (if it introduces tokens), parser, AST representation, runtime implementation, tests, documentation, and VS Code syntax support. Not every feature needs a new token or a new AST class; reuse existing structures when doing so keeps the grammar clear.

## 6. Runtime values and execution records

| Runtime value | Purpose |
|---|---|
| `MagicObject` | A world object with an element/material identity and physical/magical properties. World motion is limited to x-y coordinates. |
| `ElementTypeValue` | A reference to a registered type such as `Fire`, not a created world object. |
| `FunctionValue` | A definition plus its captured environment and parameter rules. |
| `SpellInstance` | An element template configured for one base element, with tuning isolated from other instances. |
| `SpellChange` | One before/after property change recorded during a spell execution. |
| `SpellResult` | Host-side record containing mode, success/commit status, `incant` value, created/affected objects, changes, hits, cost readouts, energy transfers, fired rules, errors and trace. |
| `LibraryNamespace` | A namespaced collection of explicit exports from a built-in or `.manalib` package. |
| `Environment` | A name-to-value mapping with an optional parent scope. |
| `IncantSignal` | Internal control flow for exiting a definition with a value. |
| `TimerRegistration`, `EventRegistration` | Internal records used by virtual-time scheduling and events. |

`post` and `release` share the same spell execution path. The difference is the state policy afterward: a successful or failed trial restores world changes, while a successful release commits its changes and a failed release restores the previous state. Importantly, trial output is not a separate, approximate simulation.

## 7. Units and physics layers

`magiclang/units.py` represents a quantity as a numeric value plus a dimension vector, including an absolute-temperature marker for Celsius literals. The five base dimensions are `kg`, `m`, `s`, `K`, and `mana`; derived units include `m2`, `m3`, `m/s`, `m/s2`, `N`, `J`, `Pa`, `W`, `kg/m3`, `kg*m/s`, and `mana/s`. Addition/subtraction require matching dimensions. Multiplication/division compose dimensions.

`magiclang/physics.py` contains reusable vector and mechanics calculations. `magiclang/physics_engine.py` integrates the always-on 2D world: movement, configurable gravity, spatial-hash swept-AABB broad phase, swept equivalent-circle contacts, basic impulse response, collision heat, HP loss, and collision/event history. Continuous physics energy transfers are aggregated per `advance_time` call so ledger size stays bounded for long simulations. Shape names are currently labels; they are not exact polygon colliders. The optional `vector3d` namespace provides 3D mathematics only, `geometry2d` provides advanced planar calculations, and `planes` manages pathway references and internal transfer ledger entries.

## 8. Elements and rules

`magiclang/elements.py` owns the registered catalogue and its primary domain map. The four fundamental types are exactly `Fire`, `Water`, `Earth`, and `Air`. Conceptual entries include `Light`, `Darkness`, `Life`, `Death`, `Order`, `Entropy`, `Spirit`, `Soul`, `Space`, `Time`, and `Void`; specialized/derived entries include `Lightning`, `Sound`, `Metal`, and `Nature`.

`can_influence(element, domain)` answers a catalogue/domain question. `interaction(a, a_mana, b, b_mana, available_heat=...)` returns an `InteractionResult` and does not itself execute the physics engine. Current reactions and their limitations are listed in [Elements and Rules](../reference/ELEMENTS_AND_RULES.md).

## 9. Libraries and the Library Builder

The main 2D engine is always active; importing `geometry2d` only makes advanced tools visible through the `geometry2d` namespace. It includes angles, coordinates, intersections, vector calculations, and an explicit `aim` helper. Projectile motion uses `velocity()`; target selection remains outside spell definitions in `tgset(target):`.

`planes` is loaded only after `load planes`; its runtime-scoped registry contains compact plane/region identity records and pathway records with endpoints, directionality, and open/closed state. Elemental attributes and being records live in independent built-in data libraries loaded on demand. Pathway, permission, channel, ledger, and newly loaded data-library state are included in transaction rollback. Internal energy transport is recorded in the runtime ledger with equal and opposite source/target deltas and does not increment external energy input/output. The public API includes identity lookup, `exists`, category operations, region lookup, one-way or bidirectional paths, shortest-route lookup, energy transfer/channels, and elemental invocation. Plane contents do not modify unrelated execution rules.

`vector3d` is loaded only after `load vector3d`. It includes 3D vectors, dot/cross products, projections, reflections, lengths, angle comparisons, and physical calculation helpers. These functions coexist with `geometry2d` because calls remain namespaced; importing one does not overwrite names from the other or core MANA operations.

A user library is a MANA `.manalib` ZIP package. `tools/library_builder.py` supports `init`, `validate`, and `build`. The manifest declares the package name, version, description, entry source and exported helpers. Library top level may contain only `def` declarations, loads and `skip`. General parameters are available to library helper definitions only, not to ordinary spell definitions. The loader validates archive integrity, manifest identity, entry path, grammar, exports and cycles. The package does not run embedded Python. Current format supports a single entry source plus an optional README; multi-file source trees and dependency version resolution are not yet supported.

## 10. Error types

All user-facing language errors use `MagicLangError` subclasses and include source context where available.

| Error | Meaning |
|---|---|
| `SyntaxErrorML` | The code does not match MANA grammar or uses disallowed syntax. |
| `TypeErrorML` | A value has the wrong type or an operation/property is invalid. |
| `UnitErrorML` | Quantity dimensions or unit requirements do not match. |
| `RuntimeErrorML` | A name, library load, call or runtime safety limit is invalid. |
| `MagicErrorML` | A magical rule or guarded state transition rejects the operation. |
| `PhysicsErrorML` | A physical constraint is violated. |

The CLI prints MANA errors without exposing a Python traceback. Host developers should test features both at module level and by running representative `.mana` programs through the public entry point.

