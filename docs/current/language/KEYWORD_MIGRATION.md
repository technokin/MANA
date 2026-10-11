# MANA Keyword Design and Migration — v1.0.0

**Page kind:** Explanation  

This document records the decisions for MANA's source syntax. MANA is a standalone source language. Its source files use MANA syntax and do not require users to write host-language code.

## Current syntax decisions

| MANA word | Meaning | Notes |
|---|---|---|
| `def` | Ordinary computational helper | Used for calculations such as `square(value)`. The result is supplied with `incant`. |
| `spldef` | Spell definition | Used for world-changing spell behaviour. Spell execution remains through `post(...)` or `release(...)`. |
| `tgset` | Target profile/context | Selects or defines target context; it is not a definition keyword. |
| `incant` | Definition result | The statement that exits a definition and can supply its result. |
| `load` | Load a library namespace | Loads a library namespace into the current program. |
| `skip` | No-operation statement | Marks an intentional no-operation statement. |
| `span(...)` | Integer iteration span | Used as `for i in span(...)` to provide an integer iteration span. |
| `length(value)` | Supported sequence length | Returns the supported length of lists, strings and spans. |

The language retains `if`, `elif`, `else`, `while`, `for`, and `in`, as well as the boolean operators `and`, `or`, and `not`. These are deliberate, explicit exceptions to the goal of using distinctive vocabulary. `round` is retained as a geometry shape label with its own MANA meaning.

## Unknown words

A word absent from the MANA keyword table is not identified as a keyword. A name may still be used as an identifier where the grammar permits it; using an unbound name produces a MANA diagnostic with its source location.

## Definitions are intentionally categorized

```mana
def square(value):
    incant value * value

spldef warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

answer = square(9)
show answer
post(warm_stone)
```

Expected output:

```text
81
[POST warm_stone] inputs: no parameters
[POST warm_stone] energy input: 293150 J (create Earth; matter creation (initial state))
[POST warm_stone] created Earth (Earth, 1 kg; create Earth)
[POST warm_stone] energy input: 100000 J (heat; spell energy input; mana-equivalent is readout only)
[POST warm_stone] stone.energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity: 0.9953940111610206 -> 0.9949206008522664 (heat)
[POST warm_stone] stone.integrity_effective_energy_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.integrity_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity_last_score_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.mana_cost: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.mana_used: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.temp: 293.15 K -> 393.15 K (heat)
[POST warm_stone] stone.thermal_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] spell completed
[POST warm_stone] mana cost: 100000 mana
[POST warm_stone] created: stone (Earth, 1 kg)
```

`def` enables ordinary programming use outside magic. `spldef` indicates a spell intended for MANA's spell execution model. This lets MANA support general computation while keeping spell execution distinct from ordinary function evaluation. `tgset` remains independent so target selection can stay outside a spell's body.

## Migration checklist

When the language surface changes, update these together:

1. Lexer token table and parser statement handling.
2. Runtime built-ins and reserved-name lists.
3. VS Code grammar/snippet vocabulary.
4. VS Code TextMate grammar, language configuration and snippets.
5. Current documentation and every runnable `.mana` example.
6. Regression tests for old forms failing and new forms working.
7. Function reference coverage and the versioned VSIX package.

The runtime may use internal implementation helpers to implement `span()` and `length()`. Those helpers do not become MANA built-ins.
