# MANA Error Catalogue

**Page kind:** Reference

MANA errors are grouped by cause. The runtime's messages may include the name, value, unit, operation, or file involved, so this catalogue documents the stable diagnostic families and the action to take. The source remains authoritative for exact, context-specific wording; use the codes and classes to identify the category.

## Diagnostic format

Command-line errors use `CODE ErrorClass: file:line:column: message`. A hint may follow on a separate line. Each error object also exposes `code`, `message`, `filename`, `line`, `column`, `hint`, `severity`, and `to_diagnostic()` for IDE integration.

| Error class | Default code family | Common cause | What to do |
|---|---|---|---|
| `SyntaxErrorML` | `M1000` | Malformed expression, missing delimiter, invalid indentation, unknown word used in invalid syntax | Check the highlighted source location and compare the construct with the Language Specification. |
| `TypeErrorML` | `M2000` | Wrong argument type, invalid property value, unsupported operand | Pass the documented type and inspect the function's argument requirements. |
| `UnitErrorML` | `M2100` | Incompatible dimensions or unknown unit | Use supported units and compatible dimensions. |
| `RuntimeErrorML` | `M3000` | Unidentified name, invalid call, invalid index, invalid execution state, span step of zero | Check spelling, scope, bounds, and operation preconditions. |
| `MagicErrorML` | `M4000` | Forbidden magical interaction, invalid element invocation, managed-state write, invalid pathway operation | Check element/plane access and the operation's magical constraints. |
| `PhysicsErrorML` | `M5000` | Non-finite or unsupported physical value, speed-limit violation, invalid physical state | Check dimensions, numeric range, and physical constraints. |
| Internal failure | `M9000` | An unexpected defect in the interpreter or one of its dependencies | Preserve the source file and reproduction. Developers can rerun with `MANA_DEBUG=1`. |

## Common messages and fixes

| Message family | Cause | Fix |
|---|---|---|
| `'<name>' is not identified` | The name is not in scope or is not a MANA construct | Correct the spelling, define the name, or load its library. A close match may be suggested. |
| `span step must not be zero` | A span would have a zero increment | Use a nonzero step. |
| `index ... is out of range` | A list/string index is outside its valid range | Check the collection length and index. |
| incompatible/unknown unit | The unit is not registered or dimensions do not match | Use supported SI units and valid dimensions. |
| unknown MANA event | An event name is not registered | Use an event listed in the Cheat Sheet. |
| library dependency cycle | Libraries load one another in a cycle | Break the cycle or move shared definitions into a third library. |
| invalid plane pathway | An endpoint is unknown, inaccessible, or the operation conflicts with route state | Verify endpoint names, route direction, and access conditions. |
| internal MANA error | A host exception escaped expected error conversion | Report it as a bug; developers can enable `MANA_DEBUG=1` to capture the traceback. |

## Complete source-message inventory

The [generated error message index](ERROR_MESSAGE_INDEX.md) inventories direct error-constructor messages and source locations. Use it alongside this cause-and-fix guide; dynamic message values vary by input.

## Error classes in code

Importable classes are `MagicLangError`, `SyntaxErrorML`, `TypeErrorML`, `UnitErrorML`, `RuntimeErrorML`, `MagicErrorML`, and `PhysicsErrorML`, all defined in `magiclang/errors.py`. The class name is retained for compatibility; the `code` field provides a stable diagnostic family.

## Validation without execution

Run `python mana.py --check path/to/file.mana`. This tokenizes and parses the file without running spell bodies or changing world state. It catches lexical and syntactic errors; runtime-only problems can still occur when the program executes.
