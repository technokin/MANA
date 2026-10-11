# MANA Operations Reference — v0.6.2

These are current operation names in the prototype, not a permanently closed list. The primitive operator catalogue remains editable.

## Object creation and inspection

- `create Element` — creates a runtime object from a registered element/material kind.
- `show value` — displays a value only, like print; `show(value)` is also accepted and neither form executes a spell.
- `detect(object)` or `detect(object, property_name)` — inspects an object/property.
- `active_objects()` — lists objects committed to the runtime.

## Shape and movement

- `shape(object, geometry)`
- `move(object, distance)`
- `velocity(object, speed_or_vector)`
- `accelerate(object, acceleration_or_vector)`
- `decelerate(object, amount)`
- `aim(object, direction)`
- `launch(object, speed)`
- `push(object, force, direction)`
- `pull(object, force, direction)`
- `rotate(object, angle)`
- `scale(object, factor)`
- `reflect(object, normal)`
- `split(object, count)`
- `anchor(object)` / `unanchor(object)`

## State and interactions

- `heat(object, temperature_change)` — adds a non-negative temperature delta in K.
- `cool(object, temperature_change)` — subtracts a non-negative temperature delta in K; temperature cannot fall below `0 K`.
- `compress(object, pressure_or_amount)`
- `expand(object, volume_or_factor)`
- `transform(object, state)`
- `combine(a, b, ...)` — creates a composite from active inputs; input property values remain intact, but source objects are marked inactive to avoid counting their matter/energy twice.
- `separate(object)` — restores the composite's source objects and returns any energy newly released by that composite as a `ThermalRelease` carrier; energy inherited from a source is not released a second time.
- `bind(object)`
- `release(object)` — for an object, marks/releases that object; when the first argument is a spell definition, executes and commits that spell.
- `dispel(object)`

## Physical calculations

- `distance(a, b)`
- `force(object)`
- `momentum(object)`
- `kinetic_energy(object)`
- `pressure(force_vector, area)`
- `magnitude(vector)`
- `has_domain(element, domain)`
- `matter_to_mana(mass)` / `mana_to_matter(mana)`
- `mana_to_energy(mana)` / `energy_to_mana(energy)`

The current multipliers are independent: `1 mana` manifests `10 kg` (`0.1 mana/kg`), and `1 mana` corresponds to `1 J`. Creation reports a matter-manifestation cost only; starting thermal energy is not charged to that cost. Energy-changing operations show a mana-equivalent cost readout but do not consume a budget. `combine(a, b)` defaults to each object's `mana_intensity`; optional `mana_a` and `mana_b` override elemental interaction magnitudes and are not a spell budget.

The prototype's editable starting temperatures are Fire `1000 K`, Water `273.15 K`, Earth `293.15 K`, and Air `288.15 K`.

## Spell execution and output

- `post(spell)` — trial-runs a spell with its default parameters, prints input values then a step-by-step report and summary, and rolls back runtime changes. Explicit overrides are also supported.
- `release(spell)` — executes and commits runtime changes, using parameter defaults unless values are explicitly overridden.
- `show value` — ordinary print-like output; `show(value)` also remains accepted.
- `incant value` — immediately ends the current definition and passes `value` to its caller, matching the behavior of a renamed `return` statement.

`return` is not valid in Mana source, and `incant(value)` is invalid. See `LANGUAGE_SPEC_V0_6.md` for the complete current semantics.
