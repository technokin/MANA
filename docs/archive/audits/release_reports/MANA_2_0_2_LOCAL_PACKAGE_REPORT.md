> **Historical local-package report:** This file documents the 2.0.2 source snapshot and its test counts at the time. It is retained for history, not as current verification. For the current source and audit results, use [MANA 2.0.3 Bug-Hunt and Verification Report](../../../current/RELEASE_V2_0_0_REPORT.md).

# MANA 2.0.2 Release Report

**Page kind:** Release report  
**Version:** 2.0.2  
**Prepared:** 23 October 2026

## Release focus

MANA 2.0.0 focuses on polishing the existing project, with an additional focused upgrade to its optional 2D Visualiser. It does not add a full 3D world. The world engine remains 2D, and `vector3d` remains a calculation library. The Visualiser remains a magic-first viewer for recorded runs rather than a live world editor.

## Visualiser improvements included in the release candidate

- Recorded curved paths use the runtime's intermediate positions; the renderer no longer treats the first and last positions as the entire journey. Interpolation uses recorded simulation timestamps when available.
- Path storage stays bounded, retains recent detail and preserves sharp turns while reducing older history.
- Humanoids and knights animate gait, face their travel direction and stagger briefly at real recorded contacts. The existing creature silhouettes keep distinct movement cues.
- Projectile art is differentiated by elemental identity rather than relying on a common glowing particle. Dedicated 2D treatments cover fire, water, ice, lightning, earth/metal, air, life, shadow/death, mana, beams, bursts, impacts, manifestation, reanimation, constructs, transformations, body-state effects, metal/magnetic effects, smoke and flares.
- Effects animate against replay time; idle animation continues during inspection, respecting reduced-motion.
- Added a runnable steering example and regression coverage for real bends, nonuniform event timing, long paths, recorded collision reactions and magic effects.

## What was aligned

- The root version, Python package version, language extension, Visualiser extension, current documentation, and release installer names now use version **2.0.2**.
- The version checker checks both extensions and detects stale labels while leaving historical audit notes unchanged.
- The clean project archive includes the correct installers for the current version and rejects archive/cache noise.
- The release workflow checks the tag against `VERSION`, then runs the release gates across Linux and Windows for Python 3.12–3.15. The publish job depends on all eight verification jobs, so an unsuccessful or cancelled matrix cannot publish release assets.
- The documentation separates supported features from future concepts and records the project's deliberate 2D scope. Two pre-release audit snapshots were moved out of the current-docs area and placed under the historical audit archive; the current index now links every maintained page.

## Verification record

Checks completed in the supplied build environment:

- **Regression tests:** 480 passed with the full project test suite on Python 3.13.5.
- **Examples:** all 62 example programs passed both CLI syntax checks and the runnable-example smoke checks.
- **Large-object benchmark:** created 9,999 objects in 0.187 seconds on this build machine; performance varies by machine.
- **Version consistency:** passed; the runtime, both editor add-ons, current documentation, and installer names agree on version 2.0.2.
- **Generated documentation:** expected-output checks, reference indexes, and the error-message catalogue are current. A regression test also verifies local heading anchors in current documentation.
- **Source checks:** Python files compile successfully; all three editor JavaScript files pass syntax checks.
- **Safety-pattern scan:** checked 54 Python source files for direct `eval`, `exec`, `shell=True`, `os.system`, and pickle deserialization calls; none were found. The Visualiser renderer contains no `innerHTML` usage. This targeted scan is not a substitute for OS isolation or a dependency advisory audit.
- **Visualiser-focused tests:** 36 passed, including curved path tracking, simulated-time interpolation, long path memory caps, contact-only character reactions and spell-effect render paths.
- **Editor add-ons:** both version 2.0.0 packages rebuilt and passed the package checks.
- **Documentation links:** all 124 Markdown files were scanned; no broken local file links were found. Local Markdown heading anchors are covered by automated tests.
- **Source archive:** built successfully with 294 files; ZIP integrity passed and contents were checked for current installers and cache exclusion.
- **Release workflow:** checks that the pushed tag matches the version, runs the release quality gates on Linux and Windows for Python 3.12–3.15, and makes the publishing job depend on all eight verification jobs. Local workflow-file checks pass; the hosted matrix has not run in this session.
- **Not verified locally:** Ruff, Pyflakes, and the dependency audit could not run because those tools were unavailable and the package index could not be reached. They are part of the release workflow.
- **Not run locally:** the full Windows/Linux, multi-Python matrix. The hosted jobs must still run; the release workflow is designed not to publish unless every verification job succeeds.

## Known limitations

| Area | Current boundary |
|---|---|
| World simulation | 2D object motion and collisions; not a full 3D world. |
| 3D calculations | Standalone vector and physical-calculation helpers only. |
| Visualiser | Optional record-and-replay viewer; not a live world editor. |
| External integrations | No supported public game-engine API. The recording file is internal to the viewer. |
| Magic catalogues | A listed concept or example does not mean every related physical or magical effect is fully simulated. |
| Creature behaviour | Anatomy and body-plan data are not complete biological simulation or autonomous intelligence. |

## Publishing status

The local 2.0.0 package can be validated and installed from its included VSIX files. The existing v1.0.0 public release is a separate historical release and is not changed by this package. A public v2.0.0 GitHub release exists only after the `v2.0.0` tag triggers the included release workflow and the upload succeeds.
