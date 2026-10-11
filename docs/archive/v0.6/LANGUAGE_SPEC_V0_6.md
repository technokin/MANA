# MANA — Syntax and Runtime Specification v0.6.2

This is the current specification for the prototype. The design remains editable.

## 1. Source and execution

- Source extension: `.mana`, UTF-8.
- Indentation-based blocks; four spaces recommended.
- `#` begins a comment.
- `python mana.py file.mana` starts the current interpreter. Python is the host implementation; the source language itself is Mana.
- A graphics/world viewer is optional and is not needed to execute code.

## 2. Definitions and values

`def` is the only user-defined function/spell definition:

```mana
def warm_stone(target, heat_change):
    heat(target, heat_change)
    incant target
```

`incant value` is the language's return statement: it immediately ends the current definition and passes `value` to its caller. Its behavior is the same as `return value` in languages that use that keyword; only the spelling differs. `incant(value)` is invalid, and `return` is invalid in Mana source.

Function parameters may declare defaults, such as `def spell(power=100):`. Defaults are evaluated when the function is called. Parameters without defaults must come before parameters with defaults.

Variables are only introduced when useful:

```mana
stone = create Earth
heat(stone, 1200 K)
show stone.temp
```

Core data include numbers, booleans, text, unit-aware quantities, magical objects, and lists. The first version does not provide tuples, sets or dictionaries as Mana-level types.

## 3. Output and spell execution

- `show value` prints ordinary output, like `print`; `show(value)` remains accepted. It does not execute spells.
- `post(spell)` runs a trial using the spell's default parameter values, prints all resolved inputs first, then displays execution steps and a final summary. It restores changes to pre-existing runtime state. Explicit argument overrides are also accepted for alternate trials.
- `release(spell)` executes the spell using its defaults and commits runtime changes. Explicit argument overrides are also accepted.
- `post` and `release` are standalone commands; assign their execution records only when you need to examine them programmatically.
- `incant value` returns that value from the current definition to its caller; it is the renamed return statement, not a spell firing mode.

Examples:

```mana
def ember(heat_change=1200 K):
    flame = create Fire
    heat(flame, heat_change)
    incant flame

post(ember)                 # trial, inputs, step trace, summary, rollback
release(ember)              # commit to runtime
```

## 4. Target profiles

`tgset` defines a target data object, not a spell:

```mana
guard = tgset:
    hp = 250
    max_hp = 250
    defence = 40
    resist_fire = 0.6
    resist_water = 0.1
    distance = 12 m
```

Resistance is a fraction: `0` means no resistance and `1` means full resistance. Additional custom target properties are supported. Objects do not store mana pools.

## 5. Elements and operations

The four fundamental elements are `Fire`, `Water`, `Earth`, and `Air`. Selected other elements/concepts are provided by the runtime, but users cannot redefine the fundamental catalogue.

Operations are separate from element names. Examples include:

```mana
shape(stone, circle)
heat(stone, 1200 K)
move(stone, 5 m)
velocity(stone, 300 m/s)
combine(water, earth)
```

The runtime validates operation/property compatibility and applies its interaction rules.

## 6. Element interactions currently encoded

- Fire + Water cancels. Cancellation output is a `ThermalRelease` material with released energy; cancellation does not create Null/Void.
- Near-equal cancellation uses a tolerance of 1% of the larger input.
- `ratio` consistently means remaining mana divided by the larger input.
- Fire + Air interaction is independent of argument order.
- Water + Earth creates Mud.
- Mud + Life creates Wood.
- Earth + Life without the Mud step returns a structured compound, not Wood.
- Water + Air may produce Ice when the water source has heat available for removal.
- Unspecified interactions produce a structured compound result rather than an ad-hoc string.
- Element domains have one main owner and can list other involved elements.
- Energy is not an element. Gravity is modelled as a possible effect of concentrated Earth, not a fundamental element.

## 7. Units and physics

Quantities use dimensions built from kg, m, s, K and mana. Named SI aliases include `N`, `J`, `Pa`, `W`, `m2`, `m3`, `m/s`, `m/s2`, and `kg*m/s`.

Bare numbers may acquire a unit from an operation's documented parameter. Explicit units are recommended in examples and complex code.

The physics module currently supports unit-aware vectors, force, momentum, kinetic energy, pressure and speed validation against `c`. A massive object cannot reach or exceed `c`; the runtime rejects invalid speed rather than silently scaling it down.

Current editable energy/mana defaults (v0.6.2):

- `1 mana` manifests `10 kg` of matter (`0.1 mana/kg`).
- `1 mana` corresponds to `1 J` in mana/energy conversions.
- These rates are independent multipliers, not values derived from `E = mc²`.
- Creating matter reports a matter-manifestation mana cost. Initial temperature is part of the object's initial state and is not charged as an extra energy cost.
- Energy-changing operations report an equivalent mana cost; it is a readout, not a spendable pool or a spell budget.
- `heat(object, change)` adds the temperature change; `cool(object, change)` subtracts it. Both take a temperature delta, not a target temperature.
- Editable prototype start temperatures: Fire `1000 K`, Water `273.15 K`, Earth `293.15 K`, Air `288.15 K`.

## 8. Timing, events and concurrency

- Ordinary statements execute sequentially.
- `simul:` runs supported direct operations concurrently and rejects detected conflicting writes to the same property.
- `wait`, `after`, and `every` use the runtime's virtual-time system.
- `when event_name:` registers an event handler.
- Loop, timer and persistent-effect caps prevent unbounded execution.

## 9. Errors

- `SyntaxErrorML`: invalid syntax/indentation or prohibited source keyword.
- `TypeErrorML`: wrong kind of value or missing property.
- `UnitErrorML`: incompatible dimensions.
- `RuntimeErrorML`: undefined name, invalid call, or execution limit.
- `MagicErrorML`: invalid elemental interaction, operation restriction, or attempts to modify runtime-managed properties.
- `PhysicsErrorML`: invalid physical quantity, division by zero, or velocity violation.

## 10. Scope and limitations

Mana programs run and update an internal runtime state without a graphical world engine. The current runtime does not yet provide a complete collision/combat simulation, realistic explosion propagation, full fluid/combustion simulation, or damage from automatically simulated hits. Those remain optional extensions to the non-graphical runtime, not prerequisites for the language itself.
