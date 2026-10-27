# Project File Layout

**Page kind:** Guide  

This page defines where new files belong so source code, user-facing material, test fixtures, documentation, and release artifacts do not become mixed together.

## Main directories

| Path | Put here | Do not put here |
|---|---|---|
| `magiclang/` | Interpreter, runtime, physics, and built-in library implementation | Tests, packaged extensions, generated recordings |
| `magiclang/libraries/` | Built-in library implementations and their data | User-created `.mana` examples |
| `libraries/` | Project-level/user library packages and library notes | Python runtime implementation |
| `examples/` | Runnable, documented `.mana` examples | Inputs that exist only to exercise a test |
| `tests/` | Automated Python tests and the JavaScript webview harness | User tutorials and release installers |
| `tests/fixtures/` | Small `.mana`, JSONL, or other inputs used only by tests | Public showcase examples |
| `docs/current/` | Maintained documentation for the current language/runtime version | Historical audit snapshots or unimplemented promises presented as shipped features |
| `docs/ideas/` | Proposals and future concepts | Current API reference material |
| `docs/archive/` | Historical reports, old decisions, and superseded documents | The canonical current guide for a feature |
| `tools/vscode-extension/` | MANA syntax support, completion, hover, and editor commands | Visualiser rendering code |
| `tools/mana-visualiser-extension/` | Optional Visualiser host, HTML/CSS/JS scene UI, and its package metadata | Runtime physics or library semantics |
| `tools/vscode/` | Repeatable VSIX build and verification scripts | Extension source files |
| `tools/check_release_tag.py` | Cross-platform check that the tag agrees with `VERSION` before release publication | Manual release tags or version changes |
| `tools/render_release_notes.py` | Builds release notes from the current `CHANGELOG.md` section only | Historical release-note files |
| `installers/vscode/` | Versioned `.vsix` distribution packages only | Editable extension source |
| `assets/branding/` | Canonical MANA logo/icon sources | Copies intended to diverge from the canonical icon |

## Root-level files kept intentionally

`README.md`, `MANA_INTRO.md`, `MANA_MAGIC_INSPIRATION_CATALOGUE.md`, `MANA_v2.0.0_RELEASE_LOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SECURITY_AUDIT.md`, `CHANGELOG.md`, `LICENSE`, and `VERSION` remain at the repository root because they are entry points, policy files, release notes, a dated audit, or release metadata. `CHANGELOG.md` is the cumulative history; `MANA_v2.0.0_RELEASE_LOG.md` is a historical plain-English summary of the 2.0.0 snapshot; `docs/current/RELEASE_V2_0_0_REPORT.md` is the current verification record for the local v2.0.0 source snapshot. The prior 2.0.2 local-package report is retained under `docs/archive/audits/release_reports/`. Do not move these files without updating every link and its regression test.

## Visualiser change boundaries

- `tools/mana-visualiser-extension/extension.js` handles VS Code commands, execution, recording validation/streaming, and webview messages.
- `tools/mana-visualiser-extension/media/viewer.js` owns scene state, rendering, selection, camera, and playback presentation.
- `tools/mana-visualiser-extension/media/viewer.css` owns layout and visual styling.
- `tools/mana-visualiser-extension/README.md` and `docs/current/tooling/MAGIC_VISUALISER.md` describe user-visible controls and limitations.
- `tools/vscode/build_mana_visualiser_vsix.py` packages and verifies the extension. Rebuild the `.vsix` after changing any shipped extension file.

The Visualiser must display recorded runtime outcomes, not invent them. The world solver remains 2D; `vector3d` is a calculation library, not a 3D world renderer. Keep the Visualiser optional so MANA programs remain usable without installing it.

## Clean working-tree rules

Do not commit `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.venv/`, temporary recordings, or build scratch files. The source ZIP builder excludes these paths. Keep generated VSIX packages under `installers/vscode/` and rebuild them from extension source rather than editing the binary packages manually.
