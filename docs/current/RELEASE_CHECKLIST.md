# MANA Release Checklist

**Page kind:** How-to

Use this checklist for every release. Record the completed checklist in the release report; do not mark an item complete without running its command or documenting why it could not run.

## Source and tests

- [ ] Confirm `VERSION` and run `python tools/version_sync.py --check`.
- [ ] Run `python -m pytest -q` and record the test count and duration.
- [ ] Run `ruff check magiclang`.
- [ ] Run the deterministic fuzz suite and energy-ledger conservation tests.
- [ ] Validate `.manalib` loader security tests, including path traversal, size limits, compression expansion, and dependency cycles.

## Documentation and examples

- [ ] Run `python tools/sync_documentation_outputs.py --check` and `python -m pytest tests/test_documentation_examples.py -q` to compare examples with their expected output.
- [ ] Run `python tools/generate_error_catalogue.py --check` and `python tools/generate_reference_index.py --check`.
- [ ] Run `python tools/generate_reference_index.py` and verify generated indexes are current.
- [ ] Check links in `docs/current/`.
- [ ] Verify each current page has a page-kind tag and that terminology matches the glossary.
- [ ] Review the error catalogue and the not-supported-yet page.
- [ ] Update `CHANGELOG.md` and the release audit report without rewriting historical audit records.

## Packaging

- [ ] Build and test the VS Code extension/VSIX when its grammar or metadata changes.
- [ ] Test the source project on a clean Windows environment with Python 3.12+ installed.
- [ ] Build the VS Code VSIX and verify its metadata, language grammar, snippets, and optional icon.
- [ ] Inspect the final ZIP and ensure it excludes caches, temporary build folders, and private test data.

## Release record

Record the version, commit, platform, test count, lint results, documentation results, artifact names, known limitations, and any skipped checks with reasons. A check that was not run is **unverified**, not passed.
