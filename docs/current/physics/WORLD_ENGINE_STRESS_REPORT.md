# World Engine Hardening and Stress Report

**Page kind:** Report  
**Status:** Unreleased working-copy verification  
**Date:** 2026-10-14  
**Scope:** 2D world physics, swept collision broad phase, world-law configuration, continuous energy exchange, and rollback.

## Results

- Full regression suite: **374 passed in 19.18 s**.
- Spatial broad-phase property test: a seeded set of 180 moving colliders produces exactly the same swept-AABB candidate-pair set as a brute-force reference calculation.
- Sparse-scene regression: 1,500 colliders complete a physics step with a 500-candidate budget. A naive all-pairs scan would consider 1,124,250 pairs for that scene before removing distant pairs.
- High-speed projectile regression: a fast projectile still contacts its target across the full swept path.
- Numeric stress: finite coordinates near `1e200` no longer overflow while calculating the swept-contact quadratic; invalid non-finite swept bounds fail with a MANA physics error.
- Transaction regression: a `world.configure()` call with a valid early argument and invalid later argument leaves all prior settings unchanged. A failed `advance_time()` restores the time, world state, ledger counters, and continuous-energy accumulator.
- Long-run accounting regression: **5,000 physics ticks** produce a bounded number of aggregate continuous-physics ledger records rather than one record per object per tick.
- Weather energy regression: wind work and atmospheric thermal exchange are included in world energy input/output accounting and remain aggregated over long advances.
- VSIX packaging and JavaScript syntax checks pass; generated documentation indexes are current.

## Manual benchmark

Measured in the current Linux/Python 3.13 container. These timings are indicative, not a promise about other machines; the 5,000-object measurement includes `tracemalloc` overhead.

| Workload | Observed result |
|---|---|
| 5,000 sparse objects, one 1/60 s step | 2.006 s; 23.16 MiB peak traced Python allocation; 0 collisions |
| 5,000 physics ticks for one object | 2.341 s; one aggregated physics-integration ledger entry |

The broad phase uses a deterministic spatial hash over conservative swept bounds, followed by local sweep-and-prune and the existing swept-circle narrow phase. Fast projectiles therefore remain candidates along their entire step. Large swept boxes use a bounded scene-scan fallback instead of being expanded into unbounded numbers of cells.

## Safety limits and known gaps

- One simulation advance is capped at 100,000 substeps and 20,000,000 candidate-pair checks.
- One object is indexed into at most 2,048 grid cells before using the fallback; the broad-phase index is capped at 2,000,000 cell memberships per substep.
- Dense scenes whose swept bounds overlap heavily can still have quadratic work. The engine reports a MANA runtime error and rolls back instead of continuing unbounded work.
- Continuous physics, wind, and thermal transfers retain exact aggregate energy counters but are grouped by operation and direction in the readable ledger. Discrete spell/collision events remain individually traceable.
- The world remains 2D with approximate circular collider bounds. The broad phase does not add exact polygons, rigid-body rotation, a full fluid solver, or scientifically complete material chemistry.
- Ruff and pyflakes could not be installed because this environment has no network access. Python compile checks, JS syntax checks, generated-doc validation, package verification and the full test suite were run instead.

## Reproduction

From the repository root:

```bash
python -m pytest -q
python tools/generate_reference_index.py --check
python tools/generate_error_catalogue.py --check
python tools/sync_documentation_outputs.py --check
python tools/vscode/build_mana_vsix.py
python tools/vscode/build_mana_visualiser_vsix.py
node --check tools/vscode-extension/extension.js
node --check tools/mana-visualiser-extension/extension.js
node --check tools/mana-visualiser-extension/media/viewer.js
```
