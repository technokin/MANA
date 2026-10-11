> **Historical record — superseded for the current v0.6.2 prototype.** The older conversion rates, per-spell mana budgets, and upkeep rules below are not current. See `ENERGY_MODEL_V0_6_2.md`.

# v0.4 implementation decisions

This release applies the whole proposal list and chooses provisional values for its unresolved items:

- **Matter/mana rate:** 10 mana per kg, flat across materials.
- **Mana/energy rate:** 1 mana = 1 kJ of ordinary energy.
- **Cancellation:** consumed mana is released as thermal energy; exact/near cancellation makes a `ThermalRelease` material. It never returns `Null` or `Void`.
- **Cancellation tolerance:** 1% relative to the larger input.
- **Domain ownership:** exactly one primary owner per domain; overlap is an explicit `also_involved` list.

Other applied changes:

- Element mana is looked up by element name, so Fire + Air works with swapped arguments.
- Wood requires the staged route Water + Earth → Mud, then Mud + Life → Wood.
- Water + Air only makes Ice if the Water object is above 273.15 K.
- Element interactions return structured results (`element`, `material`, or `compound`) rather than a free-form concatenated element string.
- `Energy` and `Gravity` are removed from the element catalogue; gravity is an Earth-derived effect concept.
- Unit dimensions are exponent vectors for kg, m, s, K, and mana, with SI aliases including N, J, Pa, W, m2 and m3.
- Division by zero raises `PhysicsErrorML`; bools are not accepted as quantities; negative mass/volume and sub-zero absolute temperature are rejected at relevant boundaries.
- Speed violations above c raise `PhysicsErrorML`; tiny floating-point overshoots are normalized by the compatibility helper.
- Relativistic momentum and kinetic energy are used; low-speed kinetic energy uses a numerically stable formula.
- Positions, velocity, acceleration, force and momentum are unit-aware vectors. `force()` returns a vector; `magnitude()` gets its magnitude.
- Spell parameter `mana` is an execution budget, not stored mana. Each magical operation charges costs to the active budget; persistent timers also incur upkeep.
- `simul` detects conflicting writes to the same object's property and rejects ambiguous blocks.
- Operations check required properties (`TypeErrorML`) and operation prohibitions (`MagicErrorML`).
- Program values remain intentionally small: numbers, booleans, text, quantities, magical objects and lists.

The two mana conversion rates and numeric operation costs are prototype defaults and can be changed in `magiclang/units.py` and `magiclang/runtime.py`.
