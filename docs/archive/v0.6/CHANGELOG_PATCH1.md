# v0.6.1 — Patch release

- `incant value` is documented as the return statement with a MANA-specific keyword; it passes the supplied value to the caller and exits the current definition.
- `show value` is supported as print-style output. The older `show(value)` call form remains accepted.
- Function parameters can have defaults, allowing `post(spell)` and `release(spell)` to run without repeated argument lists.
- `post(spell)` prints resolved parameter values first, then the execution trace and a final mana/creation/hit/error summary. It remains a trial and rolls back state changes.
- Updated the spell-mode examples and execution documentation to stop using `show(spell)` as a prelude to `post`.
- Added regression tests for no-argument `post`, default values, rollback, default-value `release`, and bare `show` syntax.

## Energy consistency correction build (still v0.6.1)

- Direct assignment to `mass` or `temp` now refreshes thermal and total energy; mass assignment also refreshes density.
- Direct assignment to `vel` now refreshes kinetic energy, momentum and total energy.
- `kinetic_energy(target)` now updates the kinetic-energy component and recomputes total energy instead of overwriting thermal-plus-kinetic total energy.
- Added the universal Planck-temperature ceiling to both `heat()` and direct temperature assignment; exceeding it raises `PhysicsErrorML` and identifies the causality-library dependency.
- Added code-only regression tests for the energy ledger and temperature ceiling.
- The integrity curve, material break-energy values, stabilizer strengths, collapse behaviour, and rules for direct assignment to derived energy properties remain open and are not guessed in this build.
