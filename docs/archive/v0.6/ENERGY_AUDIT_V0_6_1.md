> **Historical audit — current rules superseded in v0.6.2.** This records the previous build and is preserved for context. See `ENERGY_MODEL_V0_6_2.md` for current rates and behavior.

# Energy issue — v0.6.1 correction build

## Applied

- Thermal energy is recalculated as `mass * specific_heat * temperature` after direct mass/temperature assignments.
- Kinetic energy and momentum are recalculated after direct velocity assignment.
- Total energy is recomputed as `thermal_energy + kinetic_energy`.
- The `kinetic_energy(target)` operation no longer overwrites the total-energy property with kinetic energy alone.
- Heat operations and direct temperature assignments enforce the Planck-temperature ceiling.
- Regression tests run entirely in Python; no renderer or visualiser is required.

## Deliberately not decided here

The hand-off marks these as owner-open decisions, so this build does not invent answers:

- The accepted integrity curve and per-material/per-kg breaking energies.
- Stabilizer strengths and stacking cap.
- Whether a broken object becomes `ThermalRelease`, and where uncontrolled energy is released.
- How direct assignment to `energy`, `thermal_energy`, and `kinetic_energy` should be handled.
- Whether increasing `mass` directly should be rejected or treated as matter creation for mana accounting.

Consequently, this is an energy-ledger consistency fix, **not yet the complete integrity/breakage system**.
