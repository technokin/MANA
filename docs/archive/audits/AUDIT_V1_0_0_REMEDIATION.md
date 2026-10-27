# MANA v1.0.0 audit — remediation report

This report records the changes made against `AUDIT_V1_0_0.md`. The working copy was provided as a ZIP, so this report describes the local working tree and its checks; it does not claim that a GitHub commit, tag, or release was published.

## Audit items

| ID | Result | Evidence / notes |
|---|---|---|
| E1 | Fixed | The parser warns when a statement follows `incant` in the same block. Regression test checks warning text, filename and line. |
| E4 | Investigated; cost documented | `tools/benchmark_many_creates.py` reproduces the 20,000-object case. Recent runs in this container took about 1.8–1.9 s (the latest measured 1.930 s) using the benchmark script. A cProfile run measured about 5.2 s under profiler overhead; most cumulative time is object initialization and derived-unit/energy values, not the final `active_objects` membership pass. The commit step uses set-based membership. Timing depends on hardware and Python version. |
| E5 | Changes made; CI configured | Removed the listed unused test imports and unused local, defined `ROOT`, marked the six deliberate post-bootstrap imports in `tools/library_builder.py`, added Ruff and pyflakes to development requirements, and added both checks to CI. Ruff/pyflakes executables were not installed in the offline working environment, so those commands still need the configured CI run. |
| E10 | Fixed | Unknown-name hints now prefer actual MANA words and documented equivalents (`len` → `length`, `range` → `span`, `True`/`False` → `true`/`false`). Python-only words do not receive misleading shape-name suggestions; `heet` still suggests `heat`. |
| E11 | Fixed | Parser wording is `unexpected end of line`; library-builder regression test checks it. |
| T4 | Fixed | The TextMate grammar includes `geometry2d`, `vector3d` and `weave`. Both extension packages are rebuilt and checked by the packaging tests. |
| T8 | Package prepared; publication not performed | The language-support and Visualiser VSIX files are built locally. The source ZIP has no `.git` directory, and the owner has required explicit confirmation before pushing. Creating a remote tag/release and attaching the VSIX remain deliberately pending that confirmation. |

## Approved language changes

- `weave mana` is the public operation for shaping a construct from ambient mana. `create Mana` now raises a MANA error with migration guidance; ordinary `create Fire`, `create Water`, `create Earth` and `create Air` remain supported.
- The block form accepts `shape`, `radius`, `energy`, `position`, `collidable`, and `anchored`. These settings use one shared validator with `mana.form(...)` and `shape(...)`.
- Target selection stays outside spell bodies. A `tgset(target):` selection block inside a spell definition is rejected, preserving the rule that a spell defines its behaviour rather than choosing its target.
- The energy documentation now uses the runtime formula `thermal_energy + kinetic_energy + released_energy + mana_energy + bound_energy`. `mana_energy` and `bound_energy` are model terms, not a spendable mana pool.
- `post()` observations are marked as previews. Output is still written to the ordinary command output; a separate `preview.output` observation lets the viewer display it. Observation events from a failed `release()` are filtered so uncommitted object changes and contacts are not presented as successful effects.

## Visualiser and game integration

The optional **MANA Magic Visualiser** is a separate VS Code extension. The language extension adds a normal Run button (no debugger); a separate Visual button records and opens a replay only when clicked. `post(spell, visual)` records the hypothetical spell without committing its world changes; plain `post(spell)` and `post(spell, text)` keep text as the default view. Preview entities remain visibly marked as hypothetical after the world-restored snapshot. Its first version records to bounded JSON Lines and replays a magical 2D scene. It does not connect over a network, and MANA still runs normally if the extension is absent. The scene hides coordinate axes and energy-flow details, shows entity names and scalar distance, and draws contact feedback only for `contact.begin` events reported by the physics engine.

Portals, gateways, plane maps, plane workspaces and mana-from-plane animations are intentionally absent. Summoning may use a local manifestation effect after a successful event; it must not imply that a portal opened.

To address the game-integration concern, the repository now includes:

- `examples/fireball_contact.mana`, an end-to-end spell that reaches a real contact under the current 2D solver;
- `examples/adapters/minimal_game_adapter.py`, an engine-neutral dispatch example;
- `docs/current/foundations/FUTURE_USES_AND_ROADMAP.md`, which explains the event contract and the need for a game-specific adapter;
- `docs/current/tooling/MAGIC_VISUALISER.md`, with install/run/recording steps.

This is not a finished Unity/Godot/Unreal integration. The event stream is a stable boundary to build such adapters against; the game still owns its renderer, animation assets, entity lifecycle mapping and final presentation.

## Stress and verification results

- Test suite at the time of this report: **338 passed** with `python -m pytest -q` on 2026-10-12. Re-run the full suite before final packaging.
- The 20,000-object benchmark script reports the timing above and prints a cProfile summary with `--profile`.
- The observer buffer is capped at 50,000 records per transaction. Time advances sample at no more than roughly 200 scene snapshots per advance; snapshots include at most 300 entities and report truncation. Dropped observations are reported as `recording.notice` events. These limits protect the recorder, not the simulation.
- The Visualiser rejects unsupported JSONL schemas, excessive file sizes, very long lines and excessive event counts; it renders user-provided labels as text in a sandboxed WebView with no network connection.
- Verified in this working copy: 338 pytest tests, Python compileall, JavaScript syntax checks, both VSIX builds and integrity checks, `mana.py --check` for `examples/fireball_contact.mana`, a recorded example run consumed by the sample adapter, version sync, and generated-document checks. Ruff/pyflakes were added to development requirements and CI but could not be installed/run here because the environment has no network access. The configured CI run remains required before publication.

## Remaining release step

No remote change has been made. After the owner reviews the packaged files and explicitly approves the push, record the resulting commit, push to `main`, create the `v1.0.0` tag/release as appropriate, and attach both VSIX files with the changelog. Do not describe the remote release as published until those actions have completed.
