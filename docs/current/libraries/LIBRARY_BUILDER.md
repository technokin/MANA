# Building a MANA Library

**Page kind:** Reference  

MANA libraries provide reusable **MANA source code**. They are validated MANA library packages. The builder checks the library's manifest and source, then packages a `.manalib` archive that the MANA interpreter can load.

## Built-in libraries

- `geometry2d`: advanced 2D geometry and manually specified trajectory helpers.
- `vector3d`: standalone 3D calculations; it does not enable 3D world motion.
- `planes`: identifies and categorizes planes, manages one-way/bidirectional pathways, finds routes, and records internal energy transport. It does not create planes or transfer beings.
- `drafter`: creates custom plane definitions with custom values, regions, and beings; it cannot edit registered planes.
- `summoning`: manifests a defined being through an open pathway; it depends on `planes`.
- `necromancy`: reanimates declared local body/bone objects or animates existing solid constructs; the `Necro` mana usage is recorded through `planes` and does not add physical energy. It does not depend on `summoning`.
- `elemental_planes`, `hell`, `heaven`, `atlantis`, `fae_paradise`, `lineage_halls`, and `wild_realm`: built-in plane data libraries. Import `planes` before importing one explicitly; `planes` can load a plane's data internally when needed.

They are built into MANA and need no `.manalib` package. User libraries are placed under the project's `libraries/` directory.

## 1. Create a library project

From the MANA project root:

```powershell
python tools\library_builder.py init my_geometry --description "Extra geometry helpers"
```

The tool creates `libraries/my_geometry/` with:

- `mana-library.json`: package name, version, description, entry source and exports.
- `main.mana`: the MANA code that defines the exported helpers.
- `README.md`: starter library documentation.

## 2. Write library helpers

Library helpers may take ordinary parameters because they compute values. This rule applies inside library source files, not to ordinary spell definitions in `.mana` programs.

**Library source fragment (not a standalone `.mana` program):** this code is validated in the library-package context by the builder.

```mana
# libraries/my_geometry/main.mana
def twice(value):
    incant value * 2

def midpoint_value(a, b):
    incant (a + b) / 2
```

Update `exports` in the manifest to list only the names that users are meant to call:

```json
{
  "format": "manalib",
  "format_version": 1,
  "name": "my_geometry",
  "version": "1.0.0",
  "description": "Extra geometry helpers",
  "entry": "main.mana",
  "exports": ["twice", "midpoint_value"]
}
```

Only top-level function definitions, `load` statements, and `skip` are accepted in the entry file. This prevents a library from running arbitrary top-level spell code merely because it was imported. Export names must exist as top-level definitions.

Exports are accessed through the library namespace, so a library may deliberately export a name such as `force` or `distance` without replacing MANA's global `force` or another library's `distance`. Calls remain distinct: `force(stone)` uses the global world operation, while `my_library.force(value)` calls the namespaced helper. Language keywords such as `load`, `skip`, and `spldef` cannot be used as library names or exported function names. A word absent from the MANA keyword table is not identified as a keyword.

## 3. Validate and build

```powershell
python tools\library_builder.py validate libraries\my_geometry
python tools\library_builder.py build libraries\my_geometry
```

`validate` checks the JSON manifest, library name, entry path, MANA syntax, allowed top-level statements, and export names. `build` repeats validation, packages the manifest/source/optional README, and checks the resulting archive for integrity. It writes:

```text
libraries/my_geometry.manalib
```

## 4. Import and use it

**Package-dependent example (not standalone):** first complete the build step above so `libraries/my_geometry.manalib` exists.

```mana
load my_geometry
a = my_geometry.twice(21)
show a
```

The namespace keeps library functions separate from global built-ins and other libraries. Use a namespace prefix when calling a helper. User libraries are loaded from the project's `libraries/<name>.manalib` location.

## Safety and current scope

- The builder accepts MANA source and does not execute arbitrary host-language payloads.
- The library's MANA entry file is parsed by the same MANA lexer/parser and runs through the MANA runtime.
- The package loader rejects malformed manifests, unsafe entry paths, corrupt archives, missing exports and unsupported top-level statements. It caps an archive at 128 members and 2,000,000 bytes of total uncompressed content to reduce resource-exhaustion risk.
- Manifest and source files may include a UTF-8 BOM; it is stripped while reading.
- This first format packages one entry source file and an optional README. Multi-file dependency graphs and library version resolution are not yet supported.
- The library-loading system prevents a library from silently overwriting the global namespace; calls are made through the library namespace, and an export may reuse a global operation name without shadowing it outside that namespace.


## Declaring library dependencies

A `mana-library.json` manifest may contain a `dependencies` array. List each MANA library that users must load before loading this one. If omitted, it defaults to an empty list. Dependencies must be unique library identifiers. For example:

```json
{
  "format": "manalib",
  "format_version": 1,
  "name": "spirit_tools",
  "version": "1.0.0",
  "description": "Helpers using planar references.",
  "entry": "main.mana",
  "dependencies": ["planes"],
  "exports": ["identity"]
}
```

A program must write `load planes` before `load spirit_tools`. The runtime reports a clear dependency error otherwise; it does not silently load dependencies for the caller.
