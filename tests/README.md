# MANA Test Suite

The tests here verify the current Python implementation of MANA. They are regression checks for the actual source behaviour; documentation examples and catalogue entries alone do not count as proof that a feature works.

## Run the suite

From the project root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

To run a focused group:

```powershell
python -m pytest tests/test_language.py -q
python -m pytest tests/test_physics_engine.py tests/test_energy_model.py tests/test_energy_consistency.py -q
python -m pytest tests/test_libraries.py tests/test_planes_library.py tests/test_drafter_summoning_necromancy.py -q
python -m pytest tests/test_stress_boundaries.py tests/test_audit_regressions.py -q
python -m pytest tests/test_documentation_examples.py tests/test_project_layout.py tests/test_editor_tooling.py -q
```

## What the test modules cover

| Test module | Main coverage |
|---|---|
| `test_basic.py`, `test_language.py`, `test_keyword_migration.py`, `test_v0101_features.py` | Lexer/parser basics, language syntax, keywords, ordinary functions, spell definitions, and established language vocabulary. |
| `test_engine.py`, `test_spell_modes.py`, `test_mana_control.py` | Runtime execution, `post`/`release`, target context, control operations, and state changes. |
| `test_physics_engine.py`, `test_energy_model.py`, `test_energy_consistency.py` | Motion/collision behaviour, energy accounting, and consistency invariants. |
| `test_libraries.py`, `test_planes_library.py`, `test_drafter_summoning_necromancy.py` | Built-in libraries, plane/pathway records, transfers, summoning, and necromancy. |
| `test_audit_regressions.py`, `test_stress_boundaries.py` | Regression cases, malformed inputs, boundary values, and invalid built-in calls. |
| `test_examples_smoke.py`, `test_documentation_examples.py` | Runnable examples and documented output versus actual output. |
| `test_editor_tooling.py` | VS Code extension metadata, grammar, snippets/package integrity, and current workspace tasks. |
| `test_project_layout.py` | README/intro separation, project organisation, version consistency, generated indexes, local documentation links, and source-check mode. |

`release_failure_test.mana` is a targeted source fixture for release-failure behaviour. Examples intended for users live in `examples/`; fixtures and regression scenarios live in `tests/`.

## Interpreting a green run

A passing suite means that the covered cases passed on the Python version and platform used to run it. It is not a mathematical proof that every possible program is correct. New bugs should receive a minimal regression test, and changes to output should update the expected-output block only when the behaviour change is intentional.
