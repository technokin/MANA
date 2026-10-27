> **Historical pre-release snapshot:** This document records the working copy before MANA 2.0.0. Its version numbers and test counts describe that earlier snapshot. Use the [current MANA 2.0.0 verification report](../../../current/RELEASE_V2_0_0_REPORT.md) for the present checks.

# Consolidated Project Audit — MANA

**Page kind:** Audit  
**Status:** Local source audit completed; release publication not performed  
**Audit date:** 2026-10-23  
**Source baseline:** latest supplied working ZIP, version `1.0.0` with unreleased working-tree changes

## Summary

The consolidated source passed the full Python regression suite and the project's generated-documentation, version-sync, runnable-example, and package-integrity checks in this environment. This audit records the checks actually run and the limitations that remain. It does not claim that every catalogue entry has a dedicated simulation model or that a GitHub release was published.

## Test results

| Check | Result | Notes |
|---|---|---|
| Full regression suite | **468 passed** | Latest run after the adversarial Visualiser, editor-completion, settings, and documentation regressions were added. |
| Documentation examples and example smoke tests | **9 passed** | Focused run of `tests/test_documentation_examples.py` and `tests/test_examples_smoke.py`. |
| Python compilation | **Passed** | `python -m compileall -q magiclang mana.py tools`. |
| All shipped example parsing | **61/61 passed** | Lexed and parsed every `examples/*.mana` file without executing it. |
| Catalogue integrity | **Passed** | Confirmed 91 species templates, 991 structure records, 23 systems, 407 unique material profiles, required material fields, and finite positive densities. |
| Extension JavaScript syntax | **Passed** | `node --check` on both extension entry points and the Visualiser viewer. |
| MANA CLI syntax check | **Passed** | `python mana.py --check examples/fireball.mana`. |
| Version metadata | **Passed** | `python tools/version_sync.py --check`. |
| Generated API/glossary indexes | **Passed** | `python tools/generate_reference_index.py --check`. |
| Generated error catalogue | **Passed** | `python tools/generate_error_catalogue.py --check`. |
| Documentation expected-output sync | **Passed** | `python tools/sync_documentation_outputs.py --check`. |
| Current documentation links | **Passed** | Also covered by `tests/test_project_layout.py`. |
| Visualiser webview integration | **Passed as part of full suite** | Node-backed integration is exercised by `tests/test_visualiser_recording.py`. Run through pytest; the JS harness requires a recording and viewer path. |
| Stress benchmark | **Passed** | `python tools/benchmark_many_creates.py` commits exactly 9,999 objects in the measured single-program budget; the script now exits nonzero if it fails to reach that count. |
| Source ZIP generation and integrity | **Passed** | The updated source archive was rebuilt and checked for ZIP integrity; both verified extension installers and the plain-English change log are included. |
| Ruff lint | **Not verified** | Ruff is not installed, and package installation was unavailable in this environment. |
| Pyflakes | **Not verified** | Pyflakes is not installed, and package installation was unavailable in this environment. |
| `pytest -q` shell entry point | **Environment-specific collection failure** | The shell entry point did not put the repository root on `sys.path`; `python -m pytest -q` collected and passed the complete suite. This is an invocation/environment issue, not a failing test. |

## Consolidated catalogue facts

- Anatomy catalogue: **91 stock organism/fantasy templates**, **991 named structure records**, and **23 system categories**.
- Human template: **691 addressable structures** and **206 individually named conventional adult bone records**. These are catalogue records; they do not mean every structure has a unique dynamic simulation.
- Body limits: up to **1024 addressable/tracked structures per body**, separately from **512 user-defined structure definitions per runtime**.
- Materials catalogue: **407 unique canonical stock profiles**, including all **118 periodic-table elements**. Alias spellings resolve to canonical entries rather than duplicating material identity.
- Materials and anatomy are reference/game-simulation data. Estimated material coefficients and fictional creature traits are not certified engineering or biological measurements.

## Compatibility pass completed (2026-10-23)

A cross-library review found a real naming-compatibility defect: a custom material registered with a hyphen could be found through `materials.profile()` but missed by world conjuration/transmutation, and the same separator mismatch affected custom equipment blueprint lookup. `materials.by_category("all")` also omitted runtime-defined materials. These defects are fixed and covered by regression tests. Spaces, underscores, and hyphens now normalise consistently for custom material/equipment lookup; invalid values and library prerequisites remain strict.

Added `docs/current/libraries/LIBRARY_COMPATIBILITY.md` to document which libraries share runtime data, which are calculation-only/reference-only, where load order still matters, and the intended limits of naming flexibility.

## Documentation consolidation completed

- Corrected two anatomy references that still claimed a 512-structure per-entity cap after the body cap had been raised to 1024.
- Kept `docs/current/INDEX.md` as the single current-documentation entry point; `docs/archive/` remains historical and must not be used as the current API contract.
- Kept implementation status and known limitations explicit: the world engine is 2D, the catalogue is broader than the dynamic simulation, and spell-interaction mechanics were not redesigned in this pass.
- Preserved generated references rather than hand-editing generated indexes; use their generator scripts when source APIs change.
- Added a current library-compatibility guide and linked it from the documentation index.

## Visualiser and repository layout refresh (2026-10-23)

- Updated the optional Visualiser to use pointer events for pan, focus entities on double-click, recenter selection in Character view, and change the view toggle label to **Exit character view** while active.
- Added separate procedural eastern-dragon and minotaur silhouettes, with additional species cues for triceratops, stegosaurus, and raptor-like dinosaurs. These remain illustrative 2D silhouettes; no 3D world renderer or 3D collision solver was added.
- Rebuilt and verified both `installers/vscode/mana-language-1.0.0.vsix` and `installers/vscode/mana-magic-visualiser-1.0.0.vsix` from their current extension sources.
- Moved the release-failure input to `tests/fixtures/`, added `docs/current/tooling/PROJECT_LAYOUT.md`, corrected the README's example count to 61, and removed generated caches before packaging.
- Latest full regression run: **463 passed**. Version sync, generated documentation indexes, expected-output sync, both VSIX build/verification scripts, and JavaScript syntax checks passed.

## Final pre-v2 stress audit (2026-10-23)

- The first stress pass exposed a tooling bug: `tools/benchmark_many_creates.py` requested 20,000 objects in one program despite the 10,000-object safety budget, and `release()` reported the rejection without making the benchmark script itself fail. The timing output therefore looked successful even though the workload had not committed.
- Fixed the benchmark to exercise 9,999 objects, assert that exactly 9,999 objects were committed, and exit with an error if the result is not reached. Added a regression test that runs the benchmark and rejects a misleading success report.
- Re-ran the complete test suite: **463 passed**. The final benchmark completed in approximately 0.18 seconds in this environment; timings are hardware/runtime dependent.
- Rebuilt both VSIX packages and repeated Python compilation, CLI syntax, generated-documentation, version-sync, JavaScript syntax and ZIP integrity checks.
- The supplied working archive is named `MANA_v2.zip`. Internal project and extension manifests remain at `1.0.0`; the filename does not itself constitute a semantic 2.0.0 release or a published GitHub release.

## Adversarial visualiser follow-up (2026-10-23)

A second review tested malformed but size-limited recording entries rather than only recordings produced by MANA. It found two failure classes in the viewer: some event lists were assumed to always be lists, and a weather record with an empty weather description could stop playback. The viewer now checks these shapes before use and keeps replaying when optional details are malformed. A regression test covers these hostile examples.

The camera's previous minimum zoom scale prevented wide scenes from fitting on screen: large distances were forced to remain too close. The scene scale now has a much lower floor, and grid spacing follows the actual zoom. The Visualiser also opens in an expanded editor area by default, has a working maximise/restore toggle, and restores the normal layout when its window closes. The option can be disabled in extension settings. The file picker now offers only the supported JSON Lines recording format rather than suggesting that ordinary JSON files are accepted.

A check of the editor's 2D and 3D helper lists found that the two 3D reference constants were absent from suggestions; they are now offered as constants rather than callable functions. The 3D library remains calculation-only; this does not add a 3D world or collision engine.

## Known limitations and follow-up

1. Install the pinned development tools from `requirements-dev.txt` in an environment with package access, then run Ruff and Pyflakes before a release.
2. Run the CI matrix on the supported Python versions and operating systems; this local audit used Python 3.13.5.
3. Keep new anatomy entries tagged as observed, approximate, user-defined, or fictional as appropriate. A catalogue record is not proof of a complete physiology solver.
4. Continue testing composite-species compatibility, especially circulation, respiration, movement, and life-support dependencies. The current pass improves material/equipment interoperability but does not claim every possible library combination is fully simulated.
5. Spell interactions—counterspells, absorption, reflection, adaptation, and related semantics—remain outside this pass and require the user's direct design decisions.

## Reproducible local checks

From the repository root:

```sh
python -m pytest -q
python -m compileall -q magiclang mana.py tools
python mana.py --check examples/fireball.mana
python tools/version_sync.py --check
python tools/generate_reference_index.py --check
python tools/generate_error_catalogue.py --check
python tools/sync_documentation_outputs.py --check
ruff check magiclang tests tools mana.py
python -m pyflakes magiclang
```

The last two commands require the optional development tools listed in `requirements-dev.txt`.


## Latest adversarial follow-up validation (2026-10-23)

- Full suite: **468 passed** after the final code fixes.
- Focused security, Visualiser recording, and editor-tooling suite: **69 passed**.
- Verified the Visualiser's editor-group toggle against the current Visual Studio Code command name.
- Rebuilt both VSIX packages after correcting the command name and adding the setting that controls whether the scene opens maximised.
- Checked extension JavaScript syntax, Python compilation, version metadata, generated indexes, error catalogue, and runnable-example output blocks.
- A generated set of 500 malformed scene records completed in the webview test harness without an unexpected viewer crash.
- Ruff and Pyflakes remain unverified because the tools are not installed in this environment. No public release was created.


## Visualiser motion and spell-art upgrade (2026-10-23)

This update focused entirely on the existing 2D Visualiser. It did not add a full 3D world or change the runtime's spell and collision outcomes.

- Rebuilt motion tracks from the recorded intermediate positions and contacts. The displayed travel path follows bends instead of connecting only the first and last positions. When event timestamps differ, interpolation uses recorded world time.
- Kept path storage bounded while preserving the latest samples and older sharp turns. Added a long-recording test for this case.
- Animated character gait and facing based on recorded movement. Added a short visual stagger at recorded contacts only.
- Gave elements distinct 2D forms and added event-specific art for beams, bursts, impacts, summoning/reanimation, constructs, transformations, body-state effects, metal/magnetic effects, smoke and flares.
- Added `examples/visualiser_steering_firebolt.mana` and updated both Visualiser guides.
- Full project suite: **475 passed**. Focused Visualiser suite: **36 passed**. JavaScript syntax checks passed.
- Browser screenshot verification was blocked by the environment's browser policy for local and loopback preview pages; no claim of pixel-level visual review is made.

Remaining limits: this is procedural Canvas-based 2D art, not hand-authored sprite animation or a skeletal rig. The viewer only displays turns that the runtime actually recorded, and it does not implement missing spell mechanics, a live world editor, or full 3D simulation.
