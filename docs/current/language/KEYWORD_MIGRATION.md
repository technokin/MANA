# MANA Keyword Design and Migration — v2.0.0

**Page kind:** Explanation  

This document records the decisions for MANA's source syntax. MANA is a standalone source language. Its source files use MANA syntax and do not require users to write host-language code.

## Current syntax decisions

| MANA word | Meaning | Notes |
|---|---|---|
| `def` | Ordinary computational helper | Used for calculations such as `square(value)`. The result is supplied with `incant`. |
| `spell` | Primary spell declaration | Preferred spelling for world-changing spell behaviour, using the standard indented block grammar. Execute with native `appraise spell_name` or `cast spell_name`. |
| `spldef` | Legacy spell declaration alias | Fully supported for older projects; no migration is required. |
| `appraise` | Non-committing spell trial | Records an appraisal and rolls back hypothetical world changes; legacy `post(spell)` is retained. |
| `cast` | Commit a spell | Executes and commits the spell's supported world effects; legacy `release(spell)` is retained. |
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

spell warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

answer = square(9)
show answer
appraise warm_stone
```

Expected output:

```text
81
[APPRAISAL warm_stone] inputs: no parameters
[APPRAISAL warm_stone] energy input: 293150 J (create Earth; matter creation (initial state))
[APPRAISAL warm_stone] created Earth (Earth, 1 kg; create Earth)
[APPRAISAL warm_stone] energy input: 100000 J (heat; spell energy input; mana-equivalent is readout only)
[APPRAISAL warm_stone] stone.energy: 293150 J -> 393150 J (heat)
[APPRAISAL warm_stone] stone.integrity: 0.9953940111610206 -> 0.9949206008522664 (heat)
[APPRAISAL warm_stone] stone.integrity_effective_energy_j: 293150.0 -> 393150.0 (heat)
[APPRAISAL warm_stone] stone.integrity_energy: 293150 J -> 393150 J (heat)
[APPRAISAL warm_stone] stone.integrity_last_score_j: 293150.0 -> 393150.0 (heat)
[APPRAISAL warm_stone] stone.mana_cost: 0.1 -> 100000.1 (heat)
[APPRAISAL warm_stone] stone.mana_used: 0.1 -> 100000.1 (heat)
[APPRAISAL warm_stone] stone.temp: 293.15 K -> 393.15 K (heat)
[APPRAISAL warm_stone] stone.thermal_energy: 293150 J -> 393150 J (heat)
[APPRAISAL warm_stone] spell completed
[APPRAISAL warm_stone] mana appraisal: 100000 mana
[APPRAISAL warm_stone] created: stone (Earth, 1 kg)
```

`def` enables ordinary programming outside magic. `spell` declares a reusable spell; `spldef` remains a backward-compatible alias. `appraise` records a hypothetical run without committing it, while `cast` commits a successful run. The older `post(spell)` and `release(spell)` forms remain supported. This keeps general calculation distinct from a world-changing spell while making normal spell source read like MANA rather than a library API.

## Migrating v1 source to v2

New or updated code should use `spell name():` for spell declarations, `appraise spell_name` for a non-committing trial, and `cast spell_name` to commit supported effects. Existing `spldef name():`, `post(spell_name)`, and `release(spell_name)` forms remain accepted for backward compatibility, so a v1 project can migrate gradually. The v2 runtime does not require a rewrite just to parse legacy `spldef` declarations.

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

## Pure-mana constructs

`create Mana` is no longer supported. Mana is not created as matter; a spell shapes ambient mana into a construct. Use the named `weave mana` operation instead:

```mana
orb = weave mana:
    shape = projectile
    radius = 0.15 m
    energy = 750 J
```

Expected output:

```text
(no output)
```

Every setting is optional. Supported settings are `shape`, `radius`, `energy`, `position`, `collidable`, and `anchored`. The shape name must be one of MANA's documented shape labels. The `mana.form(...)` helper remains available and uses the same validation and constructor.

When migrating an older program, replace a bare `create Mana` with `weave mana`. If that old program relied on its zero-energy default, choose an explicit effect `energy` to preserve the intended behaviour.
