# Security policy

MANA is an experimental language and world-simulation runtime. Report suspected vulnerabilities privately through GitHub's **Report a vulnerability** flow for `technokin/MANA` instead of posting a working exploit publicly. Include the affected version, platform, reproduction steps, and impact. Do not include secrets or other people's data.

## Execution boundary

MANA source is not an operating-system sandbox. Interpreter restrictions limit language-visible operations, but Python itself runs with the invoking user's permissions. Do not run hostile programs under an account with important credentials or data. Use a disposable VM/container or a separate low-privilege OS account when evaluating untrusted code.

## Resource and input controls

The runtime caps source size at 2 MiB, source lines at 50,000, token count at 150,000, string literals at 100,000 characters, expression evaluation depth, function depth, cumulative statements, per-run and per-Runtime container/string allocation units, output, source-location entries and object creation. Individual collections and integer powers also have limits. User `.manalib` files are limited by compressed size, member count, total uncompressed size and manifest size; duplicate archive member names and package symlinks escaping the project library directory are rejected. The Visualiser uses a 25 MiB recording cap, bounded JSONL chunks, JSON nesting/node limits, a five-minute child-process timeout, and bounded captured output. These limits reduce but cannot eliminate the impact of interpreter defects or host-level resource pressure.

## Extension and release safety

The Run actions require a trusted VS Code workspace, use process argument arrays rather than a shell, pass a reduced environment, cap captured output, and terminate long-running processes. The Visualiser uses a random private temporary directory, removes generated recordings when its panel closes, validates imports, restricts source navigation to workspace `.mana` files, and uses a restrictive Content Security Policy. Extension and language-level restrictions are defence-in-depth; they are not equivalent to OS isolation.

CI runs the full test suite, linting, syntax/package checks, generated-document validation, and a `pip-audit` scan of development dependencies. GitHub Actions are pinned to verified immutable commit SHAs, and CI jobs request read-only repository permissions. Release builds must be rebuilt from the source tree and tested before distribution.


## Additional audit notes

The optional JSONL recorder has a 20,000-node value-sanitisation budget per event,
detects cyclic container references, uses a hard record/byte cap, and serialises
reserved event fields after payload fields so a payload cannot spoof the event type,
schema version, or timestamp. Recorder writes and counters are synchronised under one
lock. `.manalib` packaging rejects symlinked members, oversized manifests and source
files, duplicate/oversized archives, and output archive paths that are symlinks. The
source ZIP builder excludes symlinks rather than following them into unrelated files.


## Maintainer tooling

As of 2026-10-15, the development tools are directly pinned to pytest 9.1.1, Ruff
0.17.0, Pyflakes 4.0.3 and pip-audit 2.10.1. CI runs a strict dependency audit and
checks Python 3.12 through 3.15 on Linux and Windows. These tools are not runtime
dependencies; the MANA interpreter itself currently uses only the Python standard
library. Pins should be reviewed as part of routine security maintenance rather than
left to silently drift.
