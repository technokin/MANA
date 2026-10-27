# MANA 2.0.0 Final Verification Report

**Page kind:** Release report  
**Version:** 2.0.0  
**Prepared:** 27 October 2026

## Scope

This report records the local verification baseline for MANA 2.0.0. The release workflow validates a matching `v2.0.0` tag against `VERSION` and runs the configured Linux/Windows × Python 3.12–3.15 quality matrix before publishing assets. Local checks and checks delegated to hosted CI are distinguished below.

## New example programs and targeted tests

Five new, executable `.mana` programs were added beyond the original 62 examples:

- `preview_commit_boundary.mana` — asserts that `post` leaves the persistent object count unchanged and `release` commits the object.
- `plane_path_lifecycle.mana` — opens a one-way plane path, checks forward/reverse direction, closes it, and checks that both directions are closed.
- `kinetic_thermal_ledger.mana` — combines mass, heating, velocity, cooling, and direct temperature assignment; the test verifies the energy-ledger identity.
- `selective_two_target_cast.mana` — selects one of two target profiles outside the reusable spell definition and verifies the other target is untouched.
- `impact_handler_counter.mana` — verifies that one actual impact invokes the handler once and updates target state deterministically.

Each new example is included in the all-example execution smoke test and has focused assertions on resulting runtime state.

## Other included corrections

- Preserved the spell's recorded identity and visible body independently from trails/impact effects; retained the spell-anatomy inspector and Visual Lab options.
- Replaced quality tiers with one adaptive graphics policy, including a bounded canvas backing store, event-parse cache, off-screen culling, and hidden-view idle pausing.
- Cached motion-path bounds per recording; fixed reduced-motion lifecycle transitions, malformed/non-finite/out-of-policy recording coordinates, camera fitting for accepted large worlds, and older contact events without their own position.
- Hardened current-version synchronization while keeping genuine historical audit details intact.
- Made release notes derive from the current changelog entry and kept exact matching between the release tag and `VERSION` as a publishing gate.
- Corrected current report references, README version claims and installer names; regenerated the reference, glossary usage and error indexes as needed.

## Verification record

- Full regression suite: **500 passed**.
- All **67** `.mana` examples pass the full example smoke test. The five representative examples used by CI also pass `python mana.py --check`.
- Both VS Code extension packages were built with version 2.0.0 and passed their package validation checks.
- Version synchronization, generated indexes, documentation expected-output checks, Python byte-compilation, JavaScript syntax checks, both VSIX build/validation steps, and the five CI example syntax checks passed locally.
- The source archive passed ZIP integrity/content checks and contains only the two current 2.0.0 VSIX installers.

## Checks not verified locally

Ruff, Pyflakes and pip-audit could not be run in the local environment: the tools were absent and package installation could not reach the configured package index. The hosted Windows/Linux × Python 3.12–3.15 matrix is not run from this local workspace; the release workflow executes it on GitHub Actions. A hardware-specific GPU/RAM benchmark and full pixel-level interactive browser review were also not completed. These are unverified, not passed.

## Release workflow

The configured `.github/workflows/release.yml` workflow creates or updates the GitHub `v2.0.0` release only after the matching tag passes the hosted verification matrix. Building this source archive does not itself create a commit, tag, GitHub release, or marketplace publication.
