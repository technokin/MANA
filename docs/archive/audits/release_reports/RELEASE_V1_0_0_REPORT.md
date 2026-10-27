# MANA v1.0.0 Source Verification Report

> Historical report for the pre-audit source snapshot. Despite the filename used in earlier versions of this document, this file does not establish that a GitHub tag or release was published. The owner’s audit states that no tag or release exists; publication remains a separate, uncompleted step. The audit remediation report records current verification.

**Release version:** `1.0.0`  
**Release tag convention:** `v1.0.0`  
**Scope:** repository organization, public-facing documentation, Python requirements, VS Code language-support packaging, logo integration, regression suite, generated documentation, and source-package hygiene.

## Release contents

- The current Python-based MANA interpreter and `.mana` source language remain the supported runtime.
- The root README, separate `MANA_INTRO.md`, documentation index, changelog, and contribution instructions are present.
- The existing GPL-3.0-only license is preserved.
- The custom Grimoire IDE and its IDE-specific build components remain removed. The VS Code extension is retained as **MANA Language Support**.
- The provided transparent MANA logo is retained as `assets/branding/mana-logo.png`; a 512 × 512 icon export is used by the README and packaged VS Code extension.
- `requirements.txt` lists runtime dependencies and currently contains no third-party package entries. `requirements-dev.txt` installs pytest and Ruff for development.
- `.editorconfig`, `.gitattributes`, `.gitignore`, and `ruff.toml` define common editor, repository, and code-check conventions.

## Verification results

The following checks passed in the available Linux environment:

- Full test suite: **316 passed in 8.69 seconds**.
- Python compilation: `python -m compileall -q magiclang tools mana.py`.
- Version synchronization: `python tools/version_sync.py --check`.
- Runnable documentation output check: `python tools/sync_documentation_outputs.py --check`.
- Generated reference index: `python tools/generate_reference_index.py --check`.
- Generated error catalogue: `python tools/generate_error_catalogue.py --check`.
- Syntax check without execution: `python mana.py --check examples/fireball.mana`.
- VS Code extension package build and verification: `python tools/vscode/build_mana_vsix.py` and `python tools/vscode/build_mana_vsix.py --check`.
- Local Markdown links: **98 Markdown files scanned, no broken local links found**.
- VSIX structure, metadata, logo inclusion, and ZIP integrity were checked by the package builder and regression tests.

## Checks not performed

- Ruff itself could not be installed or run in this offline environment; its presence and successful execution must not be inferred from the passing test suite. Contributors can run it after installing `requirements-dev.txt`, and it can be verified by the repository's CI after publication.
- The first GitHub Actions workflow did run remotely, but failed in the generated-reference-index test on affected platform/version combinations. The specific failures and corrections are recorded in the follow-up section below. The corrected archive has not yet had a new hosted run.
- The VS Code extension was package-verified locally; publishing it to the Visual Studio Marketplace is a separate action requiring a configured publisher account.

## Known implementation boundary

This release does not claim that every planned world-simulation or magic subsystem is complete. The current implementation status and `NOT_SUPPORTED_YET.md` page remain the authoritative guide to documented boundaries. The 1.0 version identifies the source snapshot, not a claim that a Git tag or GitHub release has been published, and not a claim that every future design idea is already implemented.

## Follow-up correction after first GitHub Actions run

The first hosted CI run on the initial repository push exposed two portability defects in `tools/generate_reference_index.py`: an f-string expression that Python 3.10 could not parse, and glossary-index ordering that differed on Windows. These were release-pipeline defects; Linux jobs using Python 3.12 and 3.14 passed the original matrix, while the affected jobs failed at the generated-index test.

This corrected project archive addresses both defects by precomputing the escaped description before formatting, retaining each function's own heading when generating anchors, and applying a deterministic case-insensitive path sort with a stable tie-breaker. Python 3.10 has also reached end-of-life, so the documented minimum is now Python 3.12 and the hosted CI matrix tests Python 3.12, 3.13, 3.14, and 3.15 on Windows and Linux.

The tests and generated-index checks must be run again after this corrected archive is uploaded to the replacement repository. A successful result from the earlier commit is not claimed for this follow-up archive.
