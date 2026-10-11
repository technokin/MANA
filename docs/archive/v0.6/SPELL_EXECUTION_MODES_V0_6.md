# Spell execution and value flow — updated v0.6.2 design

A spell is defined once with `def`. Use `post(spell)` for a trial with a report and rollback, or `release(spell)` to execute and commit changes. If a spell needs inputs, give its parameters defaults so it can be previewed by name. Explicit overrides remain available for testing other values.

`post(spell)` prints the resolved input values first, then each recorded operation/change as it occurs, followed by a summary of the mana-cost readout, created objects, hits and errors. It does not require `show` calls to build that report. Pre-existing runtime state is restored after the trial.

`show value` is ordinary output, like `print()`. It prints the value you give it; it is not a spell report. `show(value)` remains accepted.

`incant value` immediately ends the current definition and passes `value` to its caller. Its behavior is the same as `return value` in another language; only the keyword spelling differs. `return` is not valid in Mana source, and `incant(value)` is invalid.

```mana
stone = create Earth

def warm_stone(target=stone, heat_change=1200 K):
    heat(target, heat_change)
    incant target

post(warm_stone)       # trial report; state is restored afterward
release(warm_stone)    # same configured spell, changes are committed
show stone.temp        # optional ordinary output after release
```
