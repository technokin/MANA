# MANA v0.9.0 — Release Audit

**Status:** packaged candidate verified in the development environment  
**Scope:** element spell templates, instance-local tuning, `pass`, examples, documentation, and VS Code language support.

## Summary of changes

- A parameterized spell definition may use only the reserved template parameter `element`.
- `instance = template(Fire)` creates a configured spell instance. It does not execute the spell body.
- `create element` creates the object when the instance is run, using the selected base element.
- Element templates accept only `Fire`, `Water`, `Earth`, or `Air`.
- `tune(instance.operation) = target, value` replaces the value of one existing operation call selected by operation name and source-level target variable.
- Tuning is stored on the selected instance. It neither modifies the template nor other instances created from that template.
- A missing operation/target match or more than one matching call raises an error rather than silently guessing.
- `pass` is a reserved no-operation statement and is written without parentheses.
- Public examples, syntax snippets, the language guide, specification, and built-in reference were updated. Historical v0.8.0 audit material remains under `docs/archive/v0.8/`.

## Verification performed

The checks below were run against the v0.9.0 working tree before release packaging:

| Check | Result |
|---|---:|
| Automated test suite (`python -m pytest -q`) | 79 passed |
| Public `.mana` examples | 7 of 7 exited successfully |
| Python bytecode compilation | Passed |
| VS Code extension JSON files | Valid JSON |
| VSIX package integrity and manifest checks | Passed in the test suite |
| Current version metadata | `0.9.0` across project and extension metadata |

## Behaviour covered by regression tests

- Calling `template(Fire)` creates an instance without creating world objects or running operations.
- Separate Fire and Earth instances retain independent configurations.
- A tuned velocity or heat increment is used by later `post` and `release` runs of that instance.
- `post` rolls back world state but preserves the configured tuning.
- Tuning errors for missing targets, missing operations, and ambiguous matches.
- Rejection of non-element template parameters and non-base element types.
- `pass` is accepted as a statement and rejected as an identifier or function call.
- `show`, `post`, and `release` remain standalone commands, and `post`/`release` accept exactly one named spell.

## Important current limitations

- `tune` currently edits the second argument of an existing operation call selected by its operation name and first target variable. It is not a general AST editor and cannot add operations or create new properties.
- If the same operation/target pair appears more than once in a definition, tuning is considered ambiguous.
- Element templates are currently restricted to one parameter named `element`. Arbitrary user parameters are not supported by this template mechanism.
- Configured instances and their tuning persist for the current program run; durable saving of tuned settings is not implemented.
- The VS Code extension provides syntax highlighting, editor configuration, and snippets. It does not provide semantic diagnostics, a debugger UI, or the full Grimoire IDE.
- Windows Explorer registry association still needs testing on the target Windows machine.

## Release note

This is a language feature release, **v0.9.0**. The v0.8.0 source archive is not modified. Under the project's current convention, further bug fixes should use the v0.9.x patch line, and the next major language change should move to v0.10.0.
