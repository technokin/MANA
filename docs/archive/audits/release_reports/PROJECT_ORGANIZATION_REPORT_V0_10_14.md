# MANA Project Organization and Tooling Cleanup Report

**Project version:** 0.10.14  
**Status:** pre-1.0 working tree; this report does not declare a v1.0 release.

## Scope

This pass reorganizes the existing project for a public GitHub repository while preserving the language implementation and established MANA syntax. It is a source-tree cleanup, not a runtime rewrite.

## Changes

- Removed Grimoire's Python UI, its entry point, the Go launcher and Windows packaging scripts, its Windows build workflow, and current IDE-specific documentation/tests.
- Preserved `mana.py`, the `magiclang/` runtime, built-in libraries, user library folder, `.mana` examples, regression/stress tests, current docs, and historical audit/changelog records.
- Kept the VS Code extension and its versioned VSIX. The extension remains editing support, not the MANA runtime.
- Replaced the root README with a GitHub landing page covering Python requirements, actual runtime dependencies, quick start, examples, docs, tests, and the license. Kept `MANA_INTRO.md` as a separate conceptual overview.
- Added `CONTRIBUTING.md`, `tests/README.md`, a current Python/VS Code guide, and the runtime/tooling foundations page.
- Removed `pyproject.toml`, which only held Ruff configuration, and moved the settings to `ruff.toml`.
- Added a cross-platform GitHub Actions test workflow and VS Code tasks for running, syntax-checking, and testing MANA programs.
- Prepared the VSIX builder to package `assets/branding/mana-icon.png` as the extension icon when supplied. No actual logo image was present in the source ZIP, so the current VSIX has no custom icon yet.
- Preserved the existing GPL-3.0-only license; it was not changed to MIT based on the unrelated README example.

## Validation results

- Full pytest suite: **316 passed**.
- `compileall` for runtime, entry point, tools, and tests: passed.
- `mana.py --check examples/fireball.mana`: passed.
- Version synchronization: passed.
- Expected-output synchronization check: passed.
- Generated API, glossary-usage and error indexes: current.
- Current-document and repository landing-page links: zero broken local links in the scanned active Markdown files.
- VSIX rebuilt and ZIP integrity/package metadata verified.
- `ruff.toml` parsed as valid TOML.

## Not verified in this environment

Ruff and pyflakes could not be installed because the environment had no network access. Their configured CI dependencies remain in `requirements-dev.txt`, but their checks were not run here. The new GitHub Actions workflow has been authored but must run on GitHub to verify all listed Windows/Linux and Python-version combinations.

## Versioning

`VERSION` remains `0.10.14`. The repository remains pre-1.0 until language work and the owner's acceptance criteria are complete.
