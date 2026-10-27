# Spell Execution, Transactions, Time, and Events

**Page kind:** Explanation  

**Current source version:** v2.0.0
**Related references:** [Language Specification](../language/LANGUAGE_SPEC.md), [Physics Engine](../physics/PHYSICS_ENGINE.md), [Function Reference](../reference/FUNCTION_REFERENCE.md)

This chapter describes when code runs and when its world changes become permanent. A spell's source code, a trial execution, and a committed release are three different things.

## 1. Definitions do not execute just by being written

MANA parses a program into statements and definitions. A `def` declaration defines an ordinary reusable helper. A `spell` declaration defines a spell body; `spldef` remains a backward-compatible alias. Neither declaration means the spell's world-changing effects have already happened.

`def` is meant for calculations and reusable logic that does not secretly mutate the world when directly called. World-changing actions belong in a `spell` declaration, executed with `appraise` or `cast` (legacy `post(...)` and `release(...)` remain supported). This separation lets a caller know whether it is asking for a value or asking the world to change.

## 2. Trial and committed execution: `appraise` and `cast`

| Form | Intent | Resulting world state |
|---|---|---|
| `appraise my_spell` | Trial a spell and record its report | World changes are rolled back after the trial. |
| `post(my_spell)` / `post(my_spell, text)` | Legacy trial forms | World changes are rolled back after the trial. Text is the default. |
| `post(my_spell, visual)` | Legacy visual trial form | World changes are rolled back; a viewer is shown only when recording is enabled and opened. |
| `cast my_spell` | Execute a spell for real | Valid changes are committed. |
| `release(my_spell)` | Legacy committed-execution form | Valid changes are committed. |

The engine records step/operation information so the report can show what was created and changed. A `post` result is not a permanent object spawn: returned values may be detached/represented for reporting so the trial does not leave active objects behind. A failed `release` rolls back its transaction rather than partially committing whatever happened before the error.

A directly called pure `def` cannot be used to get around this execution boundary. If its body tries to perform a world-changing operation, the runtime raises a MANA error. This protects the difference between computation and execution.

## 3. Target context

The target context is selected outside the spell body:

```mana
npc = tgset:
    hp = 100
    max_hp = 100
    distance = 10 m

load geometry2d
spell pulse():
    projectile = weave mana:
        shape = projectile
        radius = 0.15 m
        energy = 750 J
        position = geometry2d.point(0 m, 0 m)
    velocity(projectile, 100 m/s)
    incant projectile

tgset(npc):
    release(pulse)
```

Expected output:

```text
(no output)
```

The target context supplies a selected entity or target profile to engine operations that use it. It can support target-directed flight and optional default destinations for control functions. The spell body defines what happens; target selection does not belong inside every spell.

## 4. Rollback and state snapshots

Operations such as plane creation, opening pathways, invoking a channel, bringing a being, and reanimating remains can modify more than one object or registry. The transaction layer snapshots the runtime state that is relevant to an execution mode. If a trial completes, or a committed operation fails, the runtime restores the appropriate state so a half-applied event or library action does not leave inconsistent data behind.

Rollback is not a guarantee that every external side effect can be undone: output already printed to a terminal, external files deliberately written by an operation, or other operating-system actions are outside the simulated-world snapshot. Built-in libraries should keep their mutations inside the runtime state where possible and use runtime transaction hooks for any registries they modify.

## 5. Deterministic `simul`

`simul` is intended to group operations whose conflicts need to be checked before they run. In the current prototype, it does **not** start parallel threads. The runtime validates conflicts and executes statements in source order against the transaction state, preserving deterministic output and reproducible errors.

A source-order implementation is a deliberate prototype choice. If a future version implements physically simultaneous resolution, it must specify a stable read snapshot, a conflict-resolution model, and deterministic commit semantics rather than letting thread scheduling choose results.

## 6. Time statements

The runtime includes:

- `wait(duration)` — advance virtual execution by a duration according to the current scheduler model;
- `after(duration):` — schedule/execute a block after a delay;
- `every(interval):` — register a repeated timer callback;
- `advance_time(duration, ...)` — explicitly step the virtual world/scheduler;
- `when event_name:` — register a handler for a recognised event.

These are virtual-time features of the prototype, not operating-system real-time guarantees. Events are processed through the runtime's scheduling/physics loop. `for` and `while` have an iteration safety limit so a runaway source file cannot loop forever without bound.

## 7. Events

Physics and libraries may emit events such as `impact`, `collision`, and `damaged`, along with library events for pathways, energy arrival, object ignition, being arrival/return, and reanimation. Exact event names are owned by the event registry/runtime source; use that registry rather than inventing spelling variants.

An unknown event name produces a MANA-format warning with source location and remains inert. It is not silently treated as a new event, nor should the interpreter show a raw Python `RuntimeWarning` as its public diagnostic.

## 8. Error reporting

MANA errors should identify the source file, line, and column wherever a statement location is available. The public error categories include syntax, type, unit, runtime, magic, and physics errors. A raw Python exception is an interpreter bug or an unhandled edge case, not a language-level error users should have to understand.

The CLI uses a non-zero exit code for language/runtime failure and keeps tracebacks for unexpected internal exceptions so development defects can be diagnosed. The command-line runner reports program output and language diagnostics; editors should not reinterpret them as a separate execution engine.

## 9. Important boundaries

- `incant` supplies a definition result and exits that definition; it is not a function call.
- A second `incant` in an already exited path is unreachable and receives a warning where detected.
- MANA has no `return`, `break`, or `continue` statement in the current source grammar.
- `simul` is deterministic source-order execution with conflict checking, not multi-threaded concurrency.
- A trial should not leave active world changes; release failures should not commit partial world state.
- The editor displays actual runtime output; UI code must not determine whether the spell succeeds.
