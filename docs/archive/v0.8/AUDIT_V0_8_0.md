# MANA v0.8.0 — Command Semantics and Spell Tuning Audit

## Scope

Audited the current parser/runtime path, all seven public `.mana` examples, execution-mode tests, direct-object removal tests, current documentation, and the packaged VS Code extension. This is a code-only audit; it does not test Windows Explorer registry integration.

## Rules enforced in v0.8.0

1. **`show` is output-only.** `show value` and `show(value)` print values. The command cannot be assigned to a variable or nested inside another expression.
2. **`post` is a standalone trial command.** `post(spell_name)` takes exactly one named spell, prints resolved inputs and a step trace, then rolls back world changes. Its `SpellResult` remains available to the host runtime/test harness, not as a MANA-source expression.
3. **`release` is a standalone firing command.** `release(spell_name)` takes exactly one named spell and commits changes. It cannot be assigned or nested in another expression. Inline parameter overrides are rejected.
4. **Object deactivation is not `release`.** The old `release(object)` overload was removed so that `release` has one meaning: firing a spell. Use object-specific operations such as `dispel(object)` when removing an object from the active runtime.
5. **`spell_name.tune = parameter: value` updates stored spell parameters.** The parameter must exist in the `def` signature. Tuned values apply to subsequent `post` and `release` commands for the current program run; include the tune statement in the source file to reapply it each time the file runs.
6. **`create Element` must be assigned directly.** The accepted form is `fire = create Fire`; a bare or nested create expression is rejected so objects are not created and lost accidentally.
7. **Normal value-returning calls remain expressions.** For example, `answer = identity(42)` remains valid. `incant value` is still a statement that passes a value back to a normal direct caller.

## Example

```mana
def fireball(speed=250 m/s, heat_change=4500 K):
    fire = create Fire
    heat(fire, heat_change)
    velocity(fire, speed)
    show("Fireball temperature:", fire.temp)
    show("Fireball velocity:", fire.vel)
    incant fire

fireball.tune = speed: 300 m/s
fireball.tune = heat_change: 5000 K
post(fireball)
release(fireball)
```

`post` displays the trial report itself; extra `show` calls are only needed when the spell author wants ordinary output from values inside the spell. `release` fires the same saved configuration and commits the world changes.

## Explicitly unchanged

- Element reactions, physics formulas, energy multipliers and the open integrity/breakage design were not redesigned.
- Direct invocation of an ordinary user-defined `def` remains a normal function call; this release does not add an auto-detection rule that tries to guess which definitions are spells versus helper functions. To run a spell through the trial/commit modes, use `post` or `release`.
- Tuning is runtime state, not a file-writing feature. It persists during the current run but does not rewrite source or save settings to a separate configuration file.
- The Grimoire IDE and graphical world viewer remain future work.

## Verification

The v0.8.0 package test suite is run with `python -m pytest -q`. The coverage includes command-only execution modes, exact argument count, tune application, tune validation, rollback/commit semantics, create assignment rules, all public examples and VS Code package integrity.
