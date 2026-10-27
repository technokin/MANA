# MANA Release Checklist

**Page kind:** How-to

Use this checklist for every release. Record the completed checklist in the release report; do not mark an item complete without running its command or documenting why it could not run.

## Source and tests

- [ ] Confirm `VERSION` and run `python tools/version_sync.py --check`.
- [ ] Run `python -m pytest -q` and record the test count and duration.
- [ ] Run `python -m pytest tests/test_v200_examples.py -q` to verify the integrated examples assert runtime state, not just parse successfully.
- [ ] Run `python -m ruff check magiclang tests tools mana.py`.
- [ ] Run `python -m pyflakes magiclang` and `python -m pip_audit --strict -r requirements-dev.txt`; record unavailable tools as **unverified**, not passed.
- [ ] Run the deterministic fuzz suite and energy-ledger conservation tests through the full test suite.
- [ ] Validate `.manalib` loader security tests, including path traversal, size limits, compression expansion, duplicate entries, and dependency cycles.

## Documentation and examples

- [ ] Run `python -m pytest tests/test_documentation_examples.py -q` to compare examples with their expected output.
- [ ] Regenerate expected outputs and indexes with `python tools/sync_documentation_outputs.py`, `python tools/generate_reference_index.py`, and `python tools/generate_error_catalogue.py`.
- [ ] Re-run the three commands above with `--check` where supported to confirm generated files are current.
- [ ] Check local links and heading anchors across all Markdown files, including archived documents that link forward to the current report.
- [ ] Confirm the current `.mana` example inventory count matches `tests/test_examples_smoke.py`, the source ZIP test, and `examples/README.md`.
- [ ] Verify each current page has a page-kind tag and that terminology matches the glossary.
- [ ] Review the error catalogue and the not-supported-yet page.
- [ ] Update `CHANGELOG.md` and the release audit report without rewriting historical audit records.

## Packaging

- [ ] Build both VS Code extensions and run each builder with `--check` when grammar, runtime recording, metadata or presentation changes. Confirm both package versions equal `VERSION`.
- [ ] Check `python mana.py --check examples/fireball_contact.mana` and `python mana.py --check examples/visual_preview.mana`.
- [ ] Run `examples/fireball_contact.mana` with observation enabled and confirm the Visualiser recording contains the genuine contact event.
- [ ] Confirm the editor-title Run action does not record/open the Visualiser, and the eye-shaped Visual action does.
- [ ] Confirm Visualiser recordings distinguish hypothetical `post(..., visual)` previews from committed `release()` events and that preview objects do not persist in the runtime world.
- [ ] Test the source project on a clean Windows environment with Python 3.12+ installed.
- [ ] Build the VS Code VSIX and verify its metadata, language grammar, snippets, and optional icon.
- [ ] Inspect the final ZIP and ensure it excludes caches, temporary build folders, private test data, and stale versioned VSIX files. Confirm the report and changelog refer to the intended version.

## Release record

Record the version, commit, platform, test count, lint results, documentation results, artifact names, known limitations, and any skipped checks with reasons. A check that was not run is **unverified**, not passed.
