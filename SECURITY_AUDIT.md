# MANA security audit — 2026-10-15

## Summary

The audit hardened the interpreter, optional Visualiser recorder, library packaging
boundary and repository tooling, and reviewed the existing extension process/webview
security controls. The current regression
suite passes **405 tests**. Static review and automated checks cover the source files,
all checked-in MANA files, editor extensions, build tools and documentation.

This is an in-repository security review and regression exercise, not an independent
penetration test or proof that no vulnerabilities remain. MANA is **not an OS sandbox**:
a program runs with the permissions of the Python process. Run untrusted projects in a
disposable VM/container or under a low-privilege OS account.

## Findings fixed in this pass

1. **Generic host-object methods were reachable from MANA values.** Attribute access is
   now restricted instead of exposing arbitrary Python methods such as mutating list
   methods and string-formatting methods. Regression tests cover representative escape
   paths and ensure supported read-only library record properties continue to work.
2. **Valid-looking programs could amplify resource consumption.** Source bytes/lines,
   token count, string length, parser/evaluation depth, nested statements, cumulative
   allocations, output, retained source locations and world-object creation have explicit
   limits. Reusing a `Runtime` cannot bypass the lifetime allocation/output budgets.
3. **Cyclic or highly shared objects could explode during observation sanitisation.** The
   recorder now uses a 20,000-node per-event budget, detects cycles, bounds strings,
   arrays, dictionaries and giant integers, and omits arbitrary host objects without
   invoking their custom string methods.
4. **Concurrent recording writes could race past quotas, and payload fields could spoof
   event metadata.** The record-count and byte-count checks, file writes and counters are
   synchronised. Structural `schema`, `type` and `time` fields override payload fields.
5. **Library packages had unsafe file-boundary and resource cases.** `.manalib` loading
   and building cap compressed/uncompressed sizes, member count, source size and manifest
   size; reject duplicate ZIP member names, symlinked inputs and path escapes; and verify
   generated archives. Builder output replaces the previous package atomically after
   successful verification.
6. **Source packaging could follow symlinks.** The source ZIP tool excludes symlinked
   input files and directories and refuses a symlink as its output destination.
7. **CI supply-chain controls were weakly specified.** GitHub Actions are pinned to
   immutable commit SHAs, workflow permissions are read-only, superseded runs can be
   cancelled, direct development tools are pinned, and CI runs a strict `pip-audit` step.

## Automated verification performed

- `pytest`: **405 passed** in 21.48 seconds.
- Python syntax compilation: **67 `.py` files**, zero compile errors.
- MANA syntax scan: **60 `.mana` files**, zero parse errors.
- JSON parse scan: **5 files**, zero errors.
- Markdown scan: **110 files**, zero unmatched fenced-code blocks and zero broken local
  inline links.
- JavaScript syntax: all three extension JavaScript files passed `node --check`.
- Documentation generation: reference index, error catalogue and standalone-example
  expected-output checks all current.
- Version synchronisation and five representative CLI `--check` runs passed.
- Both VSIX packages rebuilt and their ZIP integrity, expected files, package identity,
  and Details-page README assets were verified by their build scripts.
- The source ZIP was rebuilt and verified with required files and generated/cache noise
  checks. It contains 264 source/archive files.
- Source scans found no `eval(`, built-in `exec(`, `shell=True`, `os.system(` or
  `pickle.load(s)`/`pickle.loads(` usages. The only `innerHTML` token was the security
  test asserting that it is absent from the Visualiser extension source.

## Dependency and platform coverage

The runtime currently has no third-party Python runtime dependencies. As of this audit,
maintainer dependencies are pinned to pytest 9.1.1, Ruff 0.17.0, Pyflakes 4.0.3 and
pip-audit 2.10.1. CI is configured for Python 3.12–3.15 on Linux and Windows, but that
entire matrix was not executed from this local environment.

**Not run locally:** Ruff, Pyflakes and pip-audit are not installed in this offline
workspace. The workflow installs the pinned tools and runs them in CI, but this report
cannot claim that the current dependency tree has a clean advisory scan until that CI
job completes. A static scan is not a substitute for dependency advisories, OS isolation,
fuzzing on additional interpreters, or an independent security review.

## Recommended follow-up

1. Review the strict dependency-audit result after the first network-enabled CI run and
   update pins deliberately when security fixes are released.
2. Keep MANA out of security-sensitive environments when executing untrusted programs;
   add OS-level isolation if hostile-code execution becomes a supported use case.
3. Add Windows and Python 3.12–3.15 CI results to each release record, and preserve
   these stress/security regressions when changing the interpreter, recorder or library
   package format.
