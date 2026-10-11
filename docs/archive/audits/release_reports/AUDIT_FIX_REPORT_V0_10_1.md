# MANA v0.10.1 — Audit Fix and Verification Report

**Release:** `0.10.1`  
**Release type:** patch release for audit fixes, runtime correctness, language consistency, numerical stability, and current documentation.

## Verification results

- Full test suite: **189 passed**.
- Python bytecode compilation for `magiclang`, `mana.py`, and `tools/library_builder.py`: passed.
- VS Code extension package rebuilt and ZIP-validated as `installers/vscode/mana-language-0.10.1.vsix`.
- `examples/targeted_fireball.mana` executed successfully; the example reported the target hit and final target HP of `57.5`.
- All code examples in the function reference are checked independently by the test suite.
- Package/version consistency checks require `VERSION`, `magiclang.__version__`, VS Code `package.json`, and the VSIX filename to use `0.10.1`.
- Current documentation links and imported-library API coverage are checked by tests/review. The Windows launcher is updated but was not tested on a physical Windows host in this environment.

## Language and runtime changes

- **Deterministic `simul:`:** retains conflict validation and executes statements in source order. A failed statement rolls back changes made earlier in the same `simul` block. This is deterministic sequential execution, not parallel physics integration.
- **Lists:** added integer indexing, negative indexing, indexed assignment, nested assignment such as `matrix[0][1]`, and `len()` for lists, strings, and ranges. These work inside expressions and namespaced library calls.
- **Scope:** a variable first assigned inside `if`, `while`, `for`, and equivalent control-flow blocks is visible within its enclosing definition or module. Definitions keep their own scope; locals do not leak to a caller.
- **Direct definition calls:** helper calls can calculate and return values but cannot create objects, mutate object properties, or schedule world-changing work. Use standalone `post(name)` or `release(name)` for spell execution. Helpers may register `when` handlers.
- **Celsius:** signed `C` literals convert to absolute kelvin readings. Absolute temperatures cannot be multiplied, divided, or exponentiated, and cannot be passed to `heat()`/`cool()` as increments. Those operations take temperature changes in K.
- **Diagnostics and parsing:** runtime errors include available source positions and go to stderr; UTF-8 BOM source files work; bracketed expressions may span lines; inconsistent tabs/spaces are rejected; unreachable statements after `incant` warn; unknown event names warn; unknown units and incompatible dimensions get clearer messages.
- **Host-error safety:** common arithmetic overflow, non-finite results, invalid operators/arguments, excessive recursion, and malformed library manifests are converted to MANA errors where appropriate. Unexpected interpreter faults are not silently relabelled as ordinary spell failures.
- **Matter/energy accounting:** `combine(object, object)` now rejects using the same object twice. Library archives are limited to 128 members and 2,000,000 bytes of uncompressed content. Committed-object membership uses identity sets; trace verbosity can be reduced with `MANA_TRACE_DETAIL=summary`.
- **Reserved names:** remain reserved by design. The current full catalogue and unsupported `break`/`continue` status are documented. `break` and `continue` have not been added.

## Integrity and collapse

Every non-carrier object has a material/element-specific break-energy baseline, multiplied by its mass and adjusted by its assigned stabilizers. Current calibration values are documented in `docs/current/physics/ENERGY_MODEL.md` and implemented in `magiclang/runtime.py`.

The integrity rule is:

`integrity = max(0, min(1, 1 - (E_effective / E_break)^(1/3)))`

Integrity is 1 at zero effective stress energy and reaches 0 at the break threshold. Earth/Order/Time increase the threshold with diminishing bonuses and a cap; Water/Air/Light reduce thermal stress; Space reduces effective stress; Time dampens positive stress increases; Entropy/Death lower the threshold. Repeated stabilizers count once. At zero integrity, the object becomes inactive and its tracked physical energy moves to a `ThermalRelease` carrier. These baseline and stabilizer values are configurable starting values, not measured constants. Automatic spread of carrier energy into surrounding objects and environmental damage are not implemented.

## 2D and 3D library review

### `geometry2d`

- Kept the API namespaced and removed `geometry2d.launch`; targeting remains external through `tgset(target):`, and projectile motion uses `velocity()`.
- Corrected collinear segment touching/overlap behaviour and improved polygon boundary tolerance.
- Made 2D direction normalization and angle calculations robust against avoidable magnitude overflow.
- Scaled projection/reflection intermediates, avoiding overflow in dot products where the resulting components remain representable.
- Made midpoint and in-range interpolation safer for opposite-sign endpoints; hardened closest-point projection for large coordinates, tiny segments, and distant points.
- **Remaining numerical limitation:** intersection routines use floating-point tolerances rather than arbitrary-precision geometry. Very nearly parallel lines and extreme coordinate scales may still be sensitive.

### `vector3d`

- Rechecked 25 exported values/functions and documented it as calculation-only; importing it does not enable 3D world motion or collision handling.
- Kept magnitude/normalization/angle calculations scale-safe and fixed dot-product unit composition.
- Scaled projection/reflection intermediates so representable output components are not lost just because a scalar intermediate exceeds the float range.
- `pressure()` validates force quantity/vector units and a positive `m²` area.
- Fixed the documented `displacement(position, direction, distance)` signature to match the implementation.
- **Remaining numerical limitation:** outputs which truly exceed the finite floating-point range cannot be represented; the library is not arbitrary-precision mathematics.

## Documentation and tooling

- Updated current documentation to v0.10.1 and cross-checked language rules, APIs, implementation inventories, units, integrity defaults, CLI diagnostics, and package behaviour.
- Corrected outdated 2D library descriptions and the extension README/package path.
- Kept the historical v0.10.0 audit as a record of that version; the root report and current audit now describe v0.10.1.
- Updated the Windows launcher to try `python` and then `py -3`, with a Python 3.10+ check. Physical-host Windows validation remains outstanding.
- The user-library builder remains the simple `init`, `validate`, and `build` workflow for `.manalib` source libraries.

## Known limits not represented as fixed

- `break` and `continue` remain unsupported.
- Targeted flight still targets eligible objects created during the spell, uses the innermost target context, places distance-only targets on +X, and rejects estimated flight above 60 seconds.
- Collision impulses remain Newtonian even though energy and momentum readouts can use relativistic formulas; near-light-speed collision outcomes are not validated.
- The primary world engine remains 2D; `vector3d` is not a 3D world simulator.
- Integrity thresholds and stabilizer strengths need calibration; automatic environmental consequences of `ThermalRelease` are outside this release.
- The `.manalib` package format currently supports one entry source file and an optional README, without dependency graphs or dependency-version resolution.
- The IDE/World Engine interface and the `planes`/`summoning` libraries are not part of v0.10.1. The plane and summoning libraries are the next planned phase.

## Reproduction commands

```powershell
python -m pytest -q
python -m compileall -q magiclang mana.py tools\library_builder.py
python tools\vscode\build_mana_vsix.py
python mana.py examples\targeted_fireball.mana
```
