# MANA v0.10.1 — Documentation Coverage

This page records the source-derived inventory for the current release. It is distinct from the historical v0.10.0 coverage audit. Coverage tests live in `tests/`; they verify declared language structures and public library APIs against current documentation.

## Inventory

| Component | Current inventory | Canonical documentation |
|---|---:|---|
| Token kinds | 50 `TokenType` members | [Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| AST classes | 29 classes, including the `Subscript` expression node | [Component Reference](../../current/internals/COMPONENT_REFERENCE.md) |
| Registered element selectors | 19 | [Elements and Rules](../../current/reference/ELEMENTS_AND_RULES.md) |
| Runtime `BUILTIN_NAMES` catalogue | 69 names, including shape labels, constants and namespaces as well as callable operations | [Function Reference](../../current/reference/FUNCTION_REFERENCE.md) and [Language Specification](../../current/language/LANGUAGE_SPEC.md) |
| Language keywords | 24 | [Language Specification](../../current/language/LANGUAGE_SPEC.md) |
| Reserved object property identifiers | 30 | [Language Specification](../../current/language/LANGUAGE_SPEC.md) |
| `geometry2d` public exports | 28; no `launch` export | [2D Geometry Library](../../current/libraries/GEOMETRY2D_LIBRARY.md) |
| `vector3d` public exports | 25, including 2 constants | [3D Vector Library](../../current/libraries/VECTOR3D_LIBRARY.md) |
| User `.manalib` package flow | `init`, `validate`, `build`, import and namespace checks | [Library Builder](../../current/libraries/LIBRARY_BUILDER.md) |

The counts are not additive: the reserved sets overlap (for example, `force` is both an operation name and a property name). The language guide documents reserved categories separately to make their purposes clear.

## Feature coverage

- The language specification covers syntax, scope, list indexing and assignment, `len()`, Celsius, SI prefixes, events, tracing, loop limits, errors, reserved identifiers and direct-call semantics.
- The energy model covers conversion rules, the ledger, integrity baselines, stabilizer behaviour and collapse carrier limitations.
- The physics guide documents motion, collision response, targets, safety limits and known 2D/relativistic limitations.
- The 2D and 3D library guides are cross-checked against their exported API mappings.
- The function reference's MANA code blocks are executed individually by `test_function_reference_examples_are_runnable_individually` in `tests/test_audit_regressions.py`.

## Verification commands

```powershell
python -m pytest -q
python -m compileall -q magiclang mana.py tools\library_builder.py
```
