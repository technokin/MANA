# MANA v0.7.1 — Source, Documentation and Example Audit

## Scope

Reviewed the interpreter, public `.mana` examples, current language documentation, VS Code extension source/package, Windows launch/setup scripts and automated tests. This is a code-only review; the Windows registry scripts were not run on Windows in this environment.

## Confirmed issues corrected

1. **`examples/fireball.mana`:** `release()` returns a `SpellResult`, not only the value passed to `incant`. A bare `show(result)` prints every record field and the full trace, which obscured its meaning. The example now displays labelled fields and reads the returned object through `result.incant_value`.
2. **`examples/physics_demo.mana`:** direct invocation of `projectile(...)` ran live and bypassed the spell execution record. The example now uses `release()` and inspects selected fields.
3. **Example outputs:** element, target-profile, spell-mode and standalone-release examples now label displayed values. The entire public example folder is smoke-tested.
4. **Failed `release()`:** previously, a failed call returned a failed record without a console error. It now prints `[RELEASE spell_name] ERROR: ...`, restores pre-release state, and returns a failed `SpellResult`.
5. **`sqrt()` errors:** negative inputs raise `PhysicsErrorML`; dimensional quantities raise `UnitErrorML`; unsupported types raise `TypeErrorML`. Host math errors are not deliberately leaked.
6. **Documentation drift:** current instructions now explicitly say `show` prints, `release` returns a `SpellResult`, and `result.incant_value` is the value supplied by `incant`. Current documents live under `docs/current/`; older v0.6 files are in `docs/archive/v0.6/`.
7. **Project structure:** Windows tools are in `tools/windows/` with internal launch/registry support files under `tools/windows/support/`; VS Code extension source and builder are in `tools/`; the installable VSIX is in `installers/vscode/`; future ideas live in `docs/ideas/`. Duplicate install/uninstall wrapper pairs were consolidated into one setup menu plus one PowerShell implementation.
8. **Workspace files:** `.vscode/settings.json` was removed because the VSIX already associates `.mana` files and configures indentation. `.vscode/tasks.json` remains at the project root because VS Code discovers workspace tasks there. It is not part of the VSIX and supplies run/test tasks.
9. **Entry point:** `mana.py` is the only root-level command-line runner. The source-loading helper lives inside `magiclang/runner.py`, with the rest of the interpreter modules. The stale internal package version was aligned with the release version.

## How to understand `show(result)`

`show(value)` prints what it receives. It does not execute a spell. If `value` is a `SpellResult`, the display is intentionally multi-line and includes success state, objects, changes, costs, errors and trace. Use `show(result.ok)`, `show(result.incant_value)`, `show(result.created)` or `show(result.mana_used)` for selected fields.

## Not changed

- Direct invocation of a `def` still executes it live; this remains an open design choice.
- `release(object)` remains a compatibility overload alongside `release(spell)`.
- Combine/source lifecycle, interaction rules, integrity/breakage design and energy multipliers were not redesigned in this audit.
- The VS Code extension remains editor support, not a language server or Grimoire IDE.
- Windows registry behaviour requires confirmation on a Windows machine.
