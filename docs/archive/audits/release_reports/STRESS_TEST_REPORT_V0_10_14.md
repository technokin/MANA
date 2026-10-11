# MANA v0.10.14 Pre-Release Stress Test

**Date:** 2026-10-11  
**Scope:** Current MANA lexer, parser, runtime, numeric helpers, target-profile fields, geometry/vector APIs, planes/drafter helpers, CLI syntax-check mode, and Grimoire version metadata.  
**Release status:** Stress hardening applied; this is not a claim of exhaustive verification.

## Results

- **327 automated tests passed** in the final full-suite run (28.90 seconds).
- The stress regression module contains 17 tests covering numeric bounds, parser/evaluator nesting, complex arithmetic, result-size bounds, failed-operation rollback, seeded arithmetic fuzzing, and malformed-source fuzzing.
- Deterministic fuzz cases: 1,200 arithmetic expressions and 1,500 malformed source strings. No raw host-language exception escaped these tests.
- Target-field matrix: 74 cases across HP, maximum HP, defence, resistances, mass, volume, area, temperatures, collision radius, restitution, position, state/material text, and boolean fields. 30 values were accepted and 44 rejected with MANA errors; zero raw Python exceptions.
- Direct operation matrix: 16 extreme-value cases covering rotation, scaling, heat/cool, acceleration, velocity, movement, compression/expansion, splitting, pressure, square root, and direction construction. Six succeeded and ten were rejected with MANA errors; zero raw Python exceptions.
- Manual probes also covered 5,000-digit integer literals, non-finite numeric literals, 1,500-deep input nesting, huge unit conversions, power towers, huge geometry/vector values, and a rejected targeted velocity above `c`.

## Defects found and addressed

1. Extremely long integer literals could leak Python's decimal-conversion `ValueError`; numeric-literal conversion now returns a source-located MANA syntax diagnostic.
2. Floating-point literals such as `1e999` could become infinity; non-finite literals are now rejected.
3. Deeply nested input could leak `RecursionError`; the parser reports a MANA nesting-limit error, and runtime evaluation separately bounds expression depth.
4. Numeric conversions in target fields, timers, quantities, vectors, geometry helpers, and custom plane/being helpers could leak `OverflowError`; these paths now reject unsupported numeric values with MANA diagnostics.
5. Fractional powers of negative numbers could produce complex values that reached `show`; complex arithmetic results are now rejected because MANA numeric physics is real-valued.
6. An exponent cap alone did not bound integer-result allocation; integer powers now preflight estimated result size. String/list concatenation and repetition have a one-million-character/item operation limit to prevent accidental or hostile giant allocations.
7. A failed mass assignment could leave related object fields and accounting state changed; property assignment now restores its snapshot after failure.
8. Scaling previously calculated some derived values after beginning state updates; it now validates the scaled geometry and density before committing the new values.
9. A targeted `velocity()` call that exceeded the speed-of-light limit could mutate the aim direction before rejection; aim state is now committed only after velocity validation succeeds.

## Current numeric/complexity guards

- Expression evaluation depth: 256.
- Exponent magnitude: 100,000.
- Estimated integer-power result size: 1,000,000 bits.
- String/list operation result size: 1,000,000 characters/items.

These are runtime safeguards, not a formal sandbox. A source file can still consume memory proportional to its input size, and users should not treat these limits as a security boundary for untrusted code.

## Verification performed

- `python -m pytest -vv -x`: **327 passed** in 28.90 seconds.
- `python -m compileall -q magiclang grimoire mana.py tools`: passed.
- Version synchronization, example-output snapshot, API-index, and error-catalogue checks: passed.
- `python mana.py --check examples/fireball.mana`: passed without executing the file.
- `python grimoire.py --version`: `Grimoire 0.10.14 (MANA 0.10.14)`.

The Windows Grimoire executable workflow was not run in this Linux environment. Ruff and pyflakes were not available in the offline environment, so those lint checks remain unverified. Do not treat this stress pass as a substitute for testing the actual Windows release artifact and a clean-install end-to-end smoke test.
