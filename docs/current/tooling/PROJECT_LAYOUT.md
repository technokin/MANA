# Project File Layout

**Page kind:** Guide

This page maps the MANA 2.0.0 source package. Automated GitHub Actions workflow files and the bundled test suite are not included.

## Main directories

| Path | Purpose |
|---|---|
| `magiclang/` | Interpreter, runtime, physics, units, errors, and built-in libraries |
| `libraries/` | Project-level library packages and library notes |
| `examples/` | Runnable `.mana` programs illustrating language and library features |
| `docs/current/` | Maintained language/runtime documentation |
| `docs/ideas/` | Proposals and future concepts |
| `docs/archive/` | Historical reports and superseded documents |
| `tools/vscode-extension/` | MANA syntax support, completion, hover, and editor commands |
| `tools/mana-visualiser-extension/` | Optional Visualiser host, replay UI, and package metadata |
| `tools/vscode/` | VSIX package builders |
| `tools/` | Documentation generation, library builder, package generation, and release-note helpers |
| `installers/vscode/` | Versioned `.vsix` distribution packages |
| `assets/branding/` | Canonical MANA logo/icon sources |

## Root-level files

`README.md`, `MANA_INTRO.md`, `MANA_MAGIC_INSPIRATION_CATALOGUE.md`, `MANA_v2.0.0_RELEASE_LOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SECURITY_AUDIT.md`, `CHANGELOG.md`, `LICENSE`, and `VERSION` are the project entry points, policies, release history, and metadata. The `.github/` directory may contain release notes; this source package contains no Actions workflow files.

## Visualiser change boundaries

- `tools/mana-visualiser-extension/extension.js` handles VS Code commands, execution, recording, and webview messages.
- `tools/mana-visualiser-extension/media/viewer.js` owns scene state, rendering, selection, camera, and playback presentation.
- `tools/mana-visualiser-extension/media/viewer.css` owns layout and visual styling.
- `tools/vscode/build_mana_visualiser_vsix.py` builds the installable extension package.

The Visualiser displays recorded runtime outcomes; it must not invent them. The world solver remains 2D, and `vector3d` is a calculation library rather than a 3D world renderer. Keep the Visualiser optional so `.mana` programs remain usable without it.

## Working-tree hygiene

Do not include `__pycache__/`, virtual environments, temporary recordings, or build scratch files in a source archive. Keep generated VSIX packages under `installers/vscode/` and rebuild them from extension source rather than editing binary packages manually.
