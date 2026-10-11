# What MANA Is

**Page kind:** Explanation  

**Current source version:** v1.0.0

MANA is a programming language designed around programmable magic. A MANA program can perform ordinary computation, define reusable functions, compose spells, create and manipulate objects, apply physical operations, and use libraries for specialised systems such as planar pathways, summoning, and necromancy.

MANA is not a story format and its plane catalogue is not a narrative requirement. Plane and being records are structured data. A program can use them to identify a home plane, find a route, move energy through a pathway, or bring a being into the simulated world. The data does not alter how unrelated statements execute.

## The core idea

A caster is a programmer. The spell is the program. The world engine is the execution environment.

The language should allow complex results to be composed from smaller operations. A stone projectile, for example, does not need its own hardcoded `stone_bullet` command. A program can obtain a stone object, shape or split it, set its velocity, and let the engine handle motion and collision. A skeleton-control spell should reuse ordinary movement and control operations rather than defining a different movement system for each species.

The same principle applies to beams, barriers, shockwaves, levitation, collecting objects, summoning groups, and other effects: provide general primitives, then let MANA code compose them.

## Four connected parts

### 1. Language

The language defines syntax, values, functions, spell definitions, library loading, control flow, units, diagnostics, and execution modes. The current interpreter implementation uses Python internally; `.mana` files follow MANA's own grammar and runtime rules.

### 2. Runtime and world engine

The runtime parses and executes MANA programs. The world model stores objects and their properties. The physics engine advances time, calculates motion and energy, handles 2D collisions, and records changes. It decides the actual result of a spell; an editor must not substitute its own simulation.

### 3. Libraries

The core provides rules every MANA program must obey, such as syntax, dimensional units, world execution, and energy bookkeeping. Libraries group specialist operations. `geometry2d` supplies planar calculations; `vector3d` supplies 3D mathematics; `planes` handles plane identity and pathways; `drafter` creates custom plane definitions; `summoning` brings defined beings across pathways; `necromancy` reanimates existing bodies and records the required Necro channel usage; `mana` exposes pure-mana effects and universal object control.

### 4. Development tools

The VS Code extension is optional syntax support; it does not define language semantics or execute programs. MANA source can be edited in any text editor and is executed by the Python implementation.

## Design boundaries

- There are exactly **four fundamental base elements**: Fire, Water, Earth, and Air.
- MANA itself is not a fifth element. `Mana` is the element/object type selector for pure mana; lowercase `mana` is the namespace of pure-mana effects and universal control.
- Conceptual domains do not automatically become extra fundamental elements.
- Pure-mana and universal-control primitives should work without requiring an element for every action.
- Existing matter may be manipulated without invoking an element merely because the matter is associated with that element. Using a non-base plane's elemental mana is a separate operation that requires the relevant invocation.
- Mana is not modelled as a stored, finite player pool. Displayed mana-equivalent cost is a readout, not a resource balance that can run out.
- Energy bookkeeping still matters. A spell cannot silently create, duplicate, or delete tracked physical energy simply because mana is inexhaustible.
- A pathway in `planes` carries energy only. Moving a being across it belongs to `summoning`.
- Plane identity and plane data are not world physics. Adding a record cannot silently change the language or engine's behaviour.
- The main world is currently 2D. The 3D library does not turn the world engine into a 3D simulator.

## What's implemented today

The project currently includes a working interpreter, lexer/parser/AST, 2D object simulation, units, an energy ledger, pure-mana controls, element interaction rules, plane registry and pathways, plane data modules, custom plane creation through `drafter`, cross-plane entity access through `summoning`, local corpse/bone reanimation through `necromancy`, 2D geometry and 3D vector-calculation libraries, tests, examples, documentation, and optional VS Code syntax support.

Several larger pieces remain incomplete: a graphical World Engine viewport, a genuinely 3D world, real terrain extraction, continued fire simulation, a general creature AI/behaviour framework, and final calibration of all physical and combat values. See [Implementation Status](IMPLEMENTATION_STATUS.md).

## How to navigate the project

- Start with [Getting Started](../getting_started/LANGUAGE_GUIDE.md) to learn syntax.
- Use [Function Reference](../reference/FUNCTION_REFERENCE.md) when you know the operation you want.
- Use the foundations handbook to understand the underlying rules before extending them.
- Use [Interpreter Architecture](../internals/INTERPRETER_ARCHITECTURE.md) and [Component Reference](../internals/COMPONENT_REFERENCE.md) when working on implementation code.
- Historical reports are under `docs/archive/`; they explain earlier revisions and must not be treated as the current API reference.
