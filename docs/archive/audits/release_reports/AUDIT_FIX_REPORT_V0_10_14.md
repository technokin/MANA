# MANA v0.10.14 Audit Fix Report

This report records fixes applied to the supplied `MANA_v0_10_14` source tree. The project version remains 0.10.14; this is an audit-fix build, not a version-number bump.

## Fixed

- **E1:** unreachable statements after `incant` now emit a MANA-format warning containing the source file, line, and column.
- **E4:** profiled 20,000-object `release` execution, removed a duplicate initial integrity recomputation, and confirmed that commit membership already uses a set. The main cost remains per-object construction and its energy/integrity state, not the final commit loop.
- **E5:** removed the reported unused assignments, lambda assignment, semicolon-separated statements, and one-line compound statements. Ruff and pyflakes themselves were unavailable in the isolated environment, so their executables could not be run; source-level checks found zero semicolon statements, one-line compound suites, or lambda assignments.
- **E6:** `incant (a + b) / 2` and `incant ((a + b) / 2)` are accepted. A parenthesized comma-separated call form receives a clear MANA syntax error. The documented `my_geometry` library now builds and loads in a regression test.
- **E7:** zero-step and oversized `span` values raise MANA errors instead of leaking host exceptions. A 1,463-case type/value sweep produced zero raw host exceptions.
- **E8:** packaged library load cycles, including self-loads, raise a MANA error naming the cycle.
- **E9:** removed the special handling for `break` and `continue`, removed `print` from the `simul` pure-call allowlist, and standardized unknown-name diagnostics to “is not identified.” Parser errors no longer expose internal token enum names.
- **T4:** `geometry2d` and `vector3d` were already present in the supplied TextMate grammar. Added a regression test to protect that existing support.
- **T5:** the library builder catches MANA errors and prints one concise located diagnostic without a Python traceback.
- **T6:** `grimoire.py --version` reports the version without importing the GUI. Verified with a subprocess that deliberately blocks all `tkinter` imports.
- **T7:** rewrote the specified documentation passages to describe MANA's own vocabulary and added the rule for words outside the keyword table.
- **Previous audit:** planar element type names are reserved against variable assignment; reopening an existing bidirectional pathway in reverse is idempotent and does not emit a duplicate event.

## Verification

- `python -m pytest -q`: **297 passed**.
- `python -m compileall -q magiclang mana.py tools/library_builder.py grimoire.py grimoire`: passed.
- `python grimoire.py --version`: passed.
- Tk-free version-reporting simulation: passed.
- Span type/value sweep: 1,463 cases, zero raw host exceptions.
- Static source scan: zero semicolon statements, zero one-line compound suites, zero lambda assignments.
- Ruff and pyflakes were not installed, and network access was unavailable to install them; therefore their actual command results remain unverified.

## Performance measurement

On the audit environment, the representative spell

```mana
spldef many():
    for i in span(20000):
        stone = create Earth
release(many)
```

ran in approximately **5.13 seconds** after the duplicate integrity calculation was removed (about 6.08 seconds before that change in the same environment). A `cProfile` run attributed most time to `MagicObject.__post_init__`, including the initialization of physical quantities, energy state, and integrity. The final commit step already uses set-based membership checks and was not the dominant cost. Detailed per-object trace and energy-ledger entries are also retained by design. Reaching below one second would require a broader batch-creation or reduced-state/trace policy; that behaviour change was not introduced in this patch.

## Follow-up: error-system and improvement-plan work

The follow-up improvement pass retains the v0.10.14 language semantics and adds the following:

- **Unified diagnostics:** each error exposes a stable code family, severity, optional hint, source location, and `to_diagnostic()` machine-readable record. CLI diagnostics include the code and error class. Unexpected host exceptions are concise by default; `MANA_DEBUG=1` enables traceback details for developers.
- **Name suggestions:** unknown names can suggest a close MANA keyword, built-in, or in-scope name without changing the failed program's behaviour.
- **Static checking:** `python mana.py --check file.mana` performs lexing and parsing without executing code or changing world state. It intentionally cannot detect all runtime-only errors.
- **D1 — example outputs:** runnable standalone MANA examples in `docs/current/` now have adjacent expected-output blocks. `tests/test_documentation_examples.py` compares captured output against them, normalizing generated object IDs. `python tools/sync_documentation_outputs.py --check` detects examples missing an output block.
- **D2 — version labels:** `VERSION` remains the source of truth; `tools/version_sync.py` updates generated labels or checks them with `--check`. Historical release notes are deliberately not rewritten.
- **D3 — terminology:** added a generated glossary usage index so reviewers can locate terms across current pages. This is a review aid; semantic consistency still requires review.
- **D4 — Python comparison:** kept the requested migration comparison and consolidated it in the Language Specification and beginner guide, without removing the surrounding explanations.
- **D5–D10:** added the cheat sheet, error catalogue, generated source-message index, not-supported-yet page, ten-minute tutorial, recipes, generated API index, page-kind tags, and navigation links. Existing documentation was retained and supplemented rather than broadly rewritten.
- **B1 — fuzzing:** added deterministic tests for 2,000 randomized `span` calls and 1,000 randomized operator expressions. Both fail if a raw host exception escapes.
- **B2 — energy invariants:** added randomized physical-state ledger checks and 50 randomized plane transfers that verify source and destination deltas balance to zero. This improves coverage but is not a proof of conservation for every possible random spell.
- **B3 — release checklist:** added a repeatable checklist and explicit reporting of skipped/unverified checks.
- **B4 — Windows build:** added a Windows GitHub Actions workflow to run tests, check MANA syntax, build the portable Grimoire package, and upload the artifact. The workflow itself has not been run by this local audit.
- **B5 — package security:** retained existing archive size/path/cycle checks and added fuzz/regression coverage around the loader's existing protections.
- **B6 — diagnostics:** added consistent error families and unknown-name suggestions; unsupported words are reported as not identified, and CLI errors avoid internal parser token names.
- **B7 — `--check`:** tested that syntax checking does not execute a valid program and reports a located diagnostic for invalid syntax.

### Follow-up verification

- `python -m pytest -q`: **310 passed**.
- `python -m compileall -q magiclang grimoire mana.py tools`: passed.
- `python tools/version_sync.py --check`: passed.
- `python tools/sync_documentation_outputs.py --check`: passed.
- `python tools/generate_reference_index.py --check`: passed.
- `python tools/generate_error_catalogue.py --check`: passed.
- Custom relative-link scan of `docs/current/`: zero broken relative links.
- Static syntax scan: zero semicolon-separated statements, one-line compound suites, or lambda assignments in `magiclang/`.
- Ruff and pyflakes remain **unverified** because neither executable was installed and package installation was unavailable in this isolated environment.
