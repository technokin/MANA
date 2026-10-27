# Where MANA Could Be Used

**Page kind:** Planning guide  
**Status:** Ideas and next steps, not promises for a finished product.

MANA is useful today for writing spells, checking how the current rules behave, and replaying supported effects in the optional Visualiser. It is not yet a game engine, a complete physics simulator, or a ready-made plugin for another game.

This page describes where the project could go without treating future ideas as implemented features.

## Areas worth exploring

### Spell prototyping for games

A developer could describe an ability in MANA, try different speeds or shapes, and see how the current 2D runtime handles a shot, barrier, impact, or area effect. This can help answer design questions before a game-specific implementation exists.

**Available now:** the interpreter, limited 2D movement and collision, spell preview/release, and the optional record-and-replay Visualiser.  
**Not available yet:** an official Unity, Godot, Unreal, or custom-engine plugin; live synchronization with a game scene; or an engine-independent contract that is ready to support production gameplay.

### RPG abilities and combat rules

MANA's spell definitions, target profiles, elemental combinations, summoning records, and necromancy library could support early experiments with RPG abilities. A future project might use those rules to prototype attacks, resistances, summons, barriers, status effects, or spell progression.

The current creature statistics and impact-to-health conversion are prototype values. They should not be treated as final balance rules.

### Visual effects planning

A Visualiser recording can help a developer think through the sequence of a spell: when a construct appears, when it moves, and when a real contact happens. A later version could offer more reusable effect profiles and export options for artists, but the current Visualiser is a viewer, not an asset exporter.

### Interactive fiction and tabletop preparation

The language can also be used to test magic-system rules away from a game engine. For example, a spell can be composed from reusable operations, and the result can be checked in a small controlled scene. It could become a tool for drafting consistent abilities for a tabletop campaign or interactive story.

### Learning and experimentation

MANA's custom syntax and interpreter make it possible to explore language implementation, runtime design, dimensional quantities, deterministic simulation, and test-driven development through a small domain-specific language.

## What MANA outputs today

Without recording enabled, MANA executes a `.mana` file and prints the program's `show` output, spell-preview text, and diagnostics. The Python API can also inspect runtime objects and spell results.

When the Visualiser is explicitly launched—or when a developer uses `--record`—the runtime writes a local JSON Lines recording. That file is an internal replay format for the current Visualiser. It is not a supported public game-integration API, and no external engine needs to read it to use MANA today.

## Roadmap

The sequence below favours a reliable core before adding more integrations.

### 1. Make the current toolchain dependable

- Keep the interpreter, grammar, snippets, examples, tests, and documentation in sync.
- Improve performance for repeated object creation without changing world results or sharing mutable object state.
- Make syntax errors and editor help easier to understand.
- Keep normal command-line execution independent of either VS Code extension.

### 2. Improve the spell authoring experience

- Add completion, hover help, document outline, useful snippets, and one-click Run/Check actions.
- Keep `weave mana` as the clear way to shape ambient mana; do not revive `create Mana`.
- Add complete, small, runnable examples for the most common spell patterns.
- Document limits next to the feature they affect.

### 3. Improve the magic-first Visualiser

- Keep it opt-in and record-and-replay based for the initial design.
- Improve elemental appearances, abstract spell effects, object naming, and real-contact reactions.
- Add safeguards for large scenes and recordings, and keep preview objects visibly separate from committed objects.
- Do not add portals or a plane view unless the project owner explicitly reopens that decision.

### 4. Make the world model more capable

Potential work includes better broad-phase collision handling, clearer material profiles, better object lifecycle rules, and more collision shapes. These changes need independent tests and measured performance; visual approximations must not be presented as implemented physics.

MANA 2.0 deliberately keeps its world simulation 2D. A full 3D world is not a planned requirement for polishing this release; `vector3d` remains a standalone calculation library. A fluid solver, terrain destruction, continuing combustion, and complete creature AI are also outside the current release scope.

### 5. Consider external applications later

External game-engine integration is deliberately out of scope for the current release. The Visualiser recording is a private replay format; do not build third-party systems against it. If the owner chooses to pursue integrations later, first design a separate versioned public API, define which system owns state and collisions, and test a single host before promising support for others.

## How to judge progress

A feature is ready when it has a clear language/runtime contract, automated tests, a runnable example, accurate documentation, and a known statement of its limits. A name in a catalogue or a visual effect in the viewer is not by itself proof that the underlying simulation exists.

For current capabilities, see [Implementation Status](IMPLEMENTATION_STATUS.md) and [Not Supported Yet](NOT_SUPPORTED_YET.md). For runnable starting points, see [Examples](../../../examples/README.md).


## A more concrete path toward game use

The Reddit feedback raised a fair point: a language is much easier to judge when it is clear what someone can make with it and what comes out of the interpreter. MANA now has runnable examples for projectiles, a target hit, barriers, area bursts, summoning, reanimation, and the local Visualiser. Those examples demonstrate a small prototype workflow; they do not mean an outside game can call MANA as a production plugin today.

If external game use becomes a priority, the useful challenge is to define the stable *meaning* of an effect before choosing an engine. A game adapter would need to map high-level results—such as an entity appearing, a movement request, a genuine contact, a shield being raised, a target taking an effect, or a summon failing—to the host game's objects and rules. The game would need clear authority over who owns positions, collisions, health and persistence. Otherwise MANA and the host engine could both apply the same change and produce contradictory results.

That adapter contract is a future design task. The current Visualiser recording is intentionally private to the viewer; do not make Unity, Godot, Unreal or another application depend on its current JSON Lines shape.

## Suggested milestones

These are checkpoints, not release dates.

### Milestone A — Dependable language and examples

- Every public example parses and runs from the documented command line.
- The parser, runtime, language grammar, snippets and reference all agree on keywords and settings.
- Large spell runs have documented resource limits and measurable performance targets.
- The source distribution keeps interpreter use independent from release automation and optional editor packaging.

### Milestone B — A useful editor and Visualiser

- A new user can open an example, click Run, and see output without configuring a debugger.
- The Visual action is separate, opt-in and does not add recording overhead to normal runs.
- Previews are visibly hypothetical; releases are visibly committed; touch reactions come from runtime contact events.
- The viewer identifies what is being shown, limits huge scenes safely, and shows a readable warning when it omits content.
- Installing neither extension still leaves the interpreter usable from the terminal.

### Milestone C — Engine-agnostic effect contract

Before publishing an integration API, define a versioned vocabulary for what MANA reports, which fields are stable, how failures and cancellation are represented, and whether the host or MANA owns simulation state. Include a sample adapter that turns a spell result into host-side actions, without making the viewer file format the contract.

A first proof should be deliberately small: one projectile, one target, one contact, and one resulting effect. It should compare MANA's expected event sequence with the host game's result, handle a host-side rejection, and prove that a failed operation does not leave half-created objects behind. Only after this works should more effects or other engines be considered.

### Milestone D — Scale the simulation where needed

Better broad-phase collision detection, contact lifecycle events, more accurate physical shapes, object limits and group simulation may be needed for large battles. This work belongs in the world engine, not as cosmetic tricks in the Visualiser. Profiling must come before promising a large entity count.

## How to measure progress

For each milestone, record:

- the commit being tested and the test command;
- the examples exercised and the relevant outputs;
- benchmark setup, object count, run duration and memory usage where measured;
- what remains unsupported and any known failure boundaries.

A feature is ready when its behaviour is documented, its edge cases are tested, and a new user has a runnable example. A colourful animation alone is not enough.
