# MANA v0.10.1 — Audit and Verification

**Release type:** patch release for runtime correctness, language consistency, library fixes, and documentation.  
**Version source:** `VERSION` is `0.10.1`; package metadata and VS Code extension metadata must match it.

## Release summary

MANA v0.10.1 applies the v0.10.0 audit fixes, settles the selected language behaviour, introduces the first configurable integrity/collapse model, and rechecks the optional 2D and 3D calculation libraries. The project remains a headless language/runtime prototype: the default world simulation operates in the x-y plane, and the `vector3d` library remains calculation-only.

## Main fixes

| Area | v0.10.1 result |
|---|---|
| `simul:` | Conflict validation is retained. Statements execute in source order, and runtime state is rolled back if a statement fails. It is deterministic sequential execution, not a parallel-thread scheduler. |
| Runtime exceptions | Overflow and invalid numeric operations are translated to MANA errors where expected. Unexpected interpreter defects are not disguised as ordinary spell failures. |
| Runtime source locations | Runtime diagnostics include file/line/column where source-node data is available and use standard error for CLI errors. |
| Object composition | `combine(object, object)` rejects using the same object as both sources. |
| Source encoding | UTF-8 BOM-prefixed MANA files are accepted. |
| Scope | Assignments introduced in control-flow blocks belong to their enclosing function/module scope. A definition has its own local scope. |
| Lists | List/string/range reads support integer indexing and negative indexes. Lists support indexed assignment, including nested lists; `len()` supports lists, strings, and ranges. These features work inside larger expressions and namespaced library calls. |
| Bracketed expressions | Newlines inside parentheses and square brackets are ignored by the lexer. |
| Indentation | Mixed tabs and spaces in one indentation block are rejected; a tab expands to four spaces. |
| Unreachable statements | The parser/runtime diagnostic path warns about statements after `incant` in the same block. |
| Direct calls | A direct call is a calculation/helper call. It cannot create objects, mutate object properties, or schedule world-changing work. Use standalone `post(name)` or `release(name)` for spell execution. A helper may register a `when` handler. |
| Events | Unknown event names issue a warning; only `impact`, `collision`, and `damaged` are emitted by the current engine. |
| Units | SI prefixes `k`, `M`, `G`, `m`, `u`, and `n` are supported on registered units; `g` converts to kilograms. Celsius is accepted as an absolute reading only. `heat()` and `cool()` require a K temperature change, and absolute Celsius values cannot be multiplied, divided, or exponentiated. |
| Numeric validity | Non-finite arithmetic results are rejected at the operation. Dimension errors identify the incompatible dimensions/values. |
| Library packages | Invalid manifest structures, unsafe entry paths, corrupt archives, missing exports, and oversized archives are rejected with language/runtime errors. |
| Performance | Committed-object membership checks use identity sets rather than repeated linear scans; trace verbosity can be selected with `MANA_TRACE_DETAIL=summary` or `full`. |
| Tooling/docs | VS Code grammar and Windows launcher updated; current examples and reference sections refreshed. Windows launcher changes have not been exercised on a physical Windows host in this environment. |

## Integrity, stabilizers, and collapse

Each object receives an integrity readout derived from its effective stress energy and its material-specific break-energy baseline:

`integrity = max(0, min(1, 1 - (E_effective / E_break)^(1/3)))`

`E_break` uses a per-kilogram baseline multiplied by object mass. Current baselines, fallback behaviour, and the starting stabilizer strengths are listed in [Energy Model](../../current/physics/ENERGY_MODEL.md). These are configurable calibration values, not measured material constants.

At zero integrity, the source object becomes inactive and a `ThermalRelease` carrier retains the tracked physical energy. The source's `collapsed_into` property references that carrier. The energy is not intentionally destroyed or charged to a mana pool. Automatic spread of the carrier's energy into surrounding objects and resulting environmental damage are **not implemented** in v0.10.1.

## 2D library review

- Reviewed API is exported only through `import geometry2d`; it has 28 exports and does not export a `launch` helper.
- Motion still uses `velocity(...)`; target selection remains outside spell definitions in `tgset(target):`.
- Collinear segment overlap/touching now returns a deterministic shared endpoint; separated collinear segments return `false`.
- Polygon boundary checks use a small geometric tolerance rather than exact floating-point equality.
- Direction/normalization and `angle_between` scale components before computing a norm or dot product; projection and reflection keep intermediate dot products scaled.
- Midpoint, interpolation, and closest-point projection avoid several avoidable overflow paths, including opposite-sign endpoints and tiny segments with distant points.
- Intersection routines still use floating-point tolerances and are not arbitrary-precision geometry.
- The world simulation remains 2D and uses equivalent-circle collision bounds. Exact polygonal contact geometry is not claimed.

## 3D library review

- Reviewed API is namespaced under `vector3d` and has 25 exports. It provides calculations, not 3D world simulation.
- Vector magnitude and normalization avoid unnecessary overflow for large finite components. `angle_between`, projection, and reflection use scaled intermediates.
- Dot products compose dimensions; position·force therefore returns energy dimensions instead of requiring matching input dimensions.
- `pressure()` accepts a force quantity or a force vector and requires a positive area in square metres.
- `displacement(position, direction, distance)` documentation matches the exported implementation signature.
- World velocity, acceleration, positions, targeting and collision interactions still require `z = 0`.

## Verification

Run from the project root:

```powershell
python -m pytest -q
python -m compileall -q magiclang mana.py tools\library_builder.py
python tools\vscode\build_mana_vsix.py
```

The regression suite includes repeated deterministic `simul` runs, rollback after a failed `simul` statement, indexing/`len()` integration, block scope, direct-call restrictions (including packaged functions), Celsius arithmetic, material-based integrity, collapse energy retention, 2D collinear intersections/boundaries, and 3D dimensions/pressure/displacement/large-vector calculations. A separate test executes every MANA code block in the function reference independently.

## Remaining limitations

- `break` and `continue` remain unsupported and are not introduced by this patch.
- The source-order `simul:` block is sequential, not simultaneous physical integration. Conflict validation remains deliberately restrictive and requires direct supported operations.
- The numeric integrity baselines and stabilizer strengths are starting configuration values that need calibration. `ThermalRelease` retains energy, but automatic environmental consequences are not implemented.
- Targeted flight still considers only suitable objects created during the spell, uses the innermost active target context, places distance-only targets on +X, and rejects estimated flight times above 60 seconds.
- Collision impulses remain Newtonian while energy/momentum calculations support relativistic readouts; near-light-speed collision outcomes are not validated.
- The primary world engine remains 2D; `vector3d` cannot enable 3D world motion or collisions.
- User `.manalib` packages currently support a single entry source file plus optional README, not multi-file dependency graphs or dependency-version resolution.
- The Windows launcher change has not been validated on a physical Windows host here.
- The `planes` and `summoning` libraries are not part of v0.10.1; they are planned for the next development stage.
