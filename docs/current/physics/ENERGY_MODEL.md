# MANA Energy and Mana Model — current in v2.0.0

**Page kind:** Explanation  

This is the current energy/mana specification for MANA v2.0.0. The multiplier rules were introduced in v0.6.2 and remain current. It supersedes the older rate and budget descriptions in `../../archive/v0.6/DECISIONS_V0_4.md` and `../../archive/v0.6/ENERGY_AUDIT_V0_6_1.md`. Those files are retained as historical records.

## Independent conversion multipliers

The prototype uses independent conversion rules rather than deriving one from another:

- **Matter manifestation:** `1 mana` manifests `10 kg` of matter, so `0.1 mana/kg`.
- **Mana to energy:** `1 mana` corresponds to `1 J` when an energy conversion is explicitly involved.
- Chaining the two rules means `10 kg` maps to `1 mana`, then to `1 J`. This intentionally does **not** follow `E = mc²`; rest-mass energy is not available through that equation in MANA.

These are configurable magic rules, not claims that SI physics says matter and mana have these ratios.

## Mana cost readout — no user-supplied budget

There is no stored mana pool, per-spell spending limit, or `mana` budget parameter required to fire a spell. `release(spell)` and `post(spell)` work from the spell's real inputs, not an amount of mana entered as a budget.

- Creating matter reports a manifestation cost using the matter/mana multiplier.
- The initial thermal and kinetic state of a created object is **not** charged as an extra creation energy cost.
- Energy-changing operations calculate an equivalent mana-cost readout from the energy change using `1 mana = 1 J`. They do not subtract mana from a pool and cannot fail for exceeding a mana budget.
- `combine(a, b)` defaults to each object's `mana_intensity` (default `1`). Optional `mana_a` and `mana_b` arguments override the amounts of elemental mana being interacted with; they are not spell budgets.
- Persistent effects are limited by runtime duration/safety caps, not mana upkeep.

## Starting temperatures and temperature changes

The current editable defaults are:

| Element | Starting temperature |
|---|---:|
| Fire | 1000 K |
| Water | 273.15 K |
| Earth | 293.15 K |
| Air | 288.15 K |

These are prototype defaults, not a final cosmological law. The default specific heat is `1000 J/(kg·K)` for all current objects; material-specific heat is not yet implemented.

- `heat(object, ΔT)` adds a non-negative temperature delta.
- `cool(object, ΔT)` subtracts a non-negative temperature delta and cannot lower the object below `0 K`.
- Celsius literals are absolute readings converted to kelvin; they are not valid heat/cool increments and cannot be multiplied, divided, or raised to a power.
- `heat(stone, 100 K)` raises a 293.15 K Earth object to 393.15 K. It does not set it to 100 K.
- Thermal energy is recalculated as `mass × specific_heat × absolute_temperature`.

## Canonical energy state

`energy` is runtime-derived:

`energy = thermal_energy + kinetic_energy + released_energy + mana_energy + bound_energy`

The final two terms represent the current model's energy associated with pure-mana constructs and bound planar energy. They are not a spendable mana pool. Thermal energy uses `mass × specific_heat × temperature`; kinetic energy and momentum are recalculated from mass and velocity using the physics module. These derived values, plus release-origin metadata, cannot be assigned directly through the MANA runtime.

## Energy ledger and composition

The runtime records energy inputs and outputs for object creation, temperature/velocity changes, direct state changes and explicit energy release. A created object's starting energy is entered as an initial-state source for ledger accounting, but that entry does not add an energy-conversion charge to its creation cost.

Combining objects creates one active composite whose mass and inherited energy reflect its inputs. The source objects' stored mass/property values are not rewritten, but the source records become inactive so their energy is not counted twice. `separate(composite)` restores the original source objects. Any newly released energy is carried separately. Splitting divides mass, thermal/kinetic state, released energy and provenance records across the resulting pieces.

`ThermalRelease` records aggregate `released_energy`, `energy_origin`, and `energy_sources`, plus the release created by the current interaction separately from energy inherited from its sources. This distinction prevents `separate()` from emitting inherited energy twice. Fire/Water cancellation currently identifies newly released energy as `mana_to_energy`. The provenance model supports origins such as `matter_to_energy`, `mana_to_energy`, and mixed origins, but **no matter-destruction-to-energy operation is implemented yet**.

## Verification

The regression suite checks:

- the independent conversion rates and creation-only matter cost;
- all four element starting temperatures and delta-based `heat`/`cool`;
- no budget parameter or spendable pool is required;
- derived energy and provenance fields are protected;
- combination/splitting preserve object energy and release provenance;
- world energy state matches the ledger's initial sources and recorded transfers, including 1,000 randomized objects with direct mass, temperature and velocity changes.

## Integrity, stabilizers, and collapse

Each object has an integrity readout based on its current effective stress energy and a material/element-specific breaking-energy threshold. The prototype uses:

`integrity = max(0, min(1, 1 - (E_effective / E_break)^(1/3)))`

`E_break` is a configurable starting threshold in J/kg multiplied by the object's mass and adjusted by stabilizers. The initial values in `magiclang/runtime.py` are calibration defaults, not externally measured material properties. The current per-kilogram break-energy baselines are:

| Element/material label | Baseline `E_break` |
|---|---:|
| Air | `1.5e12 J/kg` |
| Darkness | `1.5e12 J/kg` |
| Death | `1.0e12 J/kg` |
| Earth | `3.0e12 J/kg` |
| Entropy | `5.0e11 J/kg` |
| Fire | `2.0e12 J/kg` |
| Ice | `2.5e12 J/kg` |
| Life | `2.0e12 J/kg` |
| Light | `2.0e12 J/kg` |
| Lightning | `8.0e11 J/kg` |
| Metal | `3.0e12 J/kg` |
| Mud | `1.5e12 J/kg` |
| Nature | `2.0e12 J/kg` |
| Order | `3.0e12 J/kg` |
| Soul | `1.2e12 J/kg` |
| Sound | `8.0e11 J/kg` |
| Space | `1.5e12 J/kg` |
| Spirit | `1.2e12 J/kg` |
| Time | `1.5e12 J/kg` |
| Void | `5.0e11 J/kg` |
| Water | `2.5e12 J/kg` |
| Wood | `2.0e12 J/kg` |
| Compound | `1.5e12 J/kg` |
| ThermalRelease | `0 J/kg` (energy carrier; not a stabilizable material) |

For a label without an explicit entry, the fallback is `1.5e12 J/kg`. `E_break` is the chosen specific threshold multiplied by current mass and then modified by the stabilizer rules. These values are initial calibration constants and should be changed only alongside corresponding integrity regression tests.

The runtime updates integrity after object-state changes and physics steps. At 0 integrity, the object becomes inactive and its tracked physical energy is transferred to a `ThermalRelease` carrier. The original object's `collapsed_into` property points to that carrier. Integrity is an additional stability model; it does not destroy physical energy or silently convert it to mana.

The `stabilizers` list is assigned per object and accepts `Earth`, `Water`, `Air`, `Order`, `Light`, `Space`, `Time`, `Entropy`, and `Death`. Earth/Order/Time increase the breaking threshold with diminishing additional benefit; Water/Air/Light reduce thermal stress; Space reduces effective stress; Time dampens positive stress increases over time; Entropy and Death lower the breaking threshold. Repeated names are counted once. The starting strengths and thresholds are deliberately configurable and should be calibrated with tests before being treated as final.

The engine preserves the collapsed object's energy in `ThermalRelease`. A separate automatic environmental propagation/damage model for that energy is not implemented in this release; the carrier is available for subsequent operations or inspection.

## Physics interactions and collision heat

Acceleration and explicit world gravity can change kinetic energy during `advance_time`; the ledger records this as external work/input. When a collision response reduces tracked kinetic energy, that lost amount is distributed as thermal energy between the colliding objects by mass share. Impact damage is a separate prototype consequence, not an energy sink. Because contact impulses are currently Newtonian while core kinetic-energy reporting is relativistic, near-`c` collisions are not a validated energy-conservation regime. See `PHYSICS_ENGINE.md`.
