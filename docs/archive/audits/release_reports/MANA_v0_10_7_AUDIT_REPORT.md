# MANA v0.10.7 — Summoning spell distinction audit

## Changes

- `necromancy.reanimate(corpse[, name])` remains the special reanimation operation and requires an existing body introduced as bones, skeleton, corpse, or remains.
- Removed `necromancy.animate_construct()`. Creating an undead construct is expressed as an ordinary user-defined MANA spell using object creation, property setup, Necro-channel invocation, and regular movement/control operations.
- Added `examples/summon_skeleton_spell.mana` as a runnable demonstration of a user-authored spell; it is not a built-in spell or dedicated `summon_skeleton()` function.
- Renamed cross-plane transfer from `summoning.summon()` to `summoning.bring()` so the library operation does not imply that a specific undead spell is built in. `bring()` is only for bringing an already-defined being across an open route.
- Updated current docs, examples, function reference, extension metadata, and version labels to `0.10.7`.

## Verification

- Full pytest suite: 260 passed.
- Public `.mana` examples: smoke-tested, including the new ordinary `summon_skeleton` spell.
- VS Code extension VSIX rebuilt and validated at `installers/vscode/mana-language-0.10.7.vsix`.
- Historical v0.10.6 audit/changelog entries are retained as historical records.

## Boundary still to design

`planes.invoke("Necro")` grants permission to the Necro channel. The included example invokes that channel and creates/controls the body using ordinary MANA primitives. A general automatic rule for accounting the Underworld-channel usage of arbitrary user-written spell bodies is not yet implemented; this must be designed generically rather than adding a dedicated summon function or requiring the author to enter a joule amount.
