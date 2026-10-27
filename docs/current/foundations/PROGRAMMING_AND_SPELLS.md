# MANA Programming Model and Spell Execution

**Page kind:** Explanation  

**Current source version:** v2.0.0

MANA supports ordinary computation and world-changing magic in the same language. It distinguishes those roles in the language rather than making every function a spell.

## 1. Ordinary definitions: `def`

Use `def` for a normal reusable calculation or helper. A direct call can calculate a value, work with lists and strings, and call other pure helpers. It must not secretly create or change world objects. This restriction makes a function predictable when used inside an expression.

```mana
def square(value):
    incant value * value

def total_with_tax(price, rate):
    incant price * (1 + rate)

show square(9)
show total_with_tax(100, 0.05)
```

Expected output:

```text
81
105.0
```

`incant` provides the result to the caller. A word absent from the MANA keyword table is not identified as a keyword. A definition that reaches its end without an `incant` result yields the runtime's no-result value.

## 2. Spell definitions: `spell` (legacy alias: `spldef`)

Use `spell` when the body represents world-changing behaviour. The older `spldef` spelling remains supported for existing projects. It can create objects, change object state, configure motion, interact with energy, and use specialist libraries where allowed. A spell is not executed just because its name appears in an expression. Use `appraise spell_name` to trial it without committing changes, or `cast spell_name` to commit supported effects. The older `post(spell_name)` and `release(spell_name)` forms remain supported.

The block below keeps the legacy `post`/`release` spell-execution forms visible for compatibility. New v2 programs should prefer `appraise warm_stone` and `cast warm_stone`.

```mana
spell warm_stone():
    stone = create Earth
    heat(stone, 100 K)
    incant stone

post(warm_stone)
release(warm_stone)
```

Expected output:

```text
[POST warm_stone] inputs: no parameters
[POST warm_stone] energy input: 293150 J (create Earth; matter creation (initial state))
[POST warm_stone] created Earth (Earth, 1 kg; create Earth)
[POST warm_stone] energy input: 100000 J (heat; spell energy input; mana-equivalent is readout only)
[POST warm_stone] stone.energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity: 0.9953940111610206 -> 0.9949206008522664 (heat)
[POST warm_stone] stone.integrity_effective_energy_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.integrity_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] stone.integrity_last_score_j: 293150.0 -> 393150.0 (heat)
[POST warm_stone] stone.mana_cost: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.mana_used: 0.1 -> 100000.1 (heat)
[POST warm_stone] stone.temp: 293.15 K -> 393.15 K (heat)
[POST warm_stone] stone.thermal_energy: 293150 J -> 393150 J (heat)
[POST warm_stone] spell completed
[POST warm_stone] mana appraisal: 100000 mana
[POST warm_stone] created: stone (Earth, 1 kg)
```

`appraise` runs the spell transactionally and restores world state after producing its report. `cast` runs and commits it. This boundary prevents ordinary direct calls from silently mutating the world without a trace. Calling a spell as a normal value-producing function is an error; use `appraise` or `cast`. The legacy `post` and `release` statements are retained for compatibility.

### Element-parameterised spell templates

A `spell` declared with a single parameter named `element` can be used as a reusable template:

```mana
spell bolt(element):
    projectile = create element
    shape(projectile, circle)
    velocity(projectile, 200 m/s)
    incant projectile

fire_bolt = bolt(Fire)
water_bolt = bolt(Water)
appraise fire_bolt
cast water_bolt
```

Expected output:

```text
[APPRAISAL fire_bolt] inputs: element=Fire
[APPRAISAL fire_bolt] energy input: 1e+06 J (create Fire; matter creation (initial state))
[APPRAISAL fire_bolt] created Fire (Fire, 1 kg; create Fire)
[APPRAISAL fire_bolt] projectile.shape: 'point' -> 'circle' (shape)
[APPRAISAL fire_bolt] energy input: 20000 J (velocity; spell work)
[APPRAISAL fire_bolt] projectile.energy: 1e+06 J -> 1.02e+06 J (velocity)
[APPRAISAL fire_bolt] projectile.integrity: 0.992062994740159 -> 0.9920104302595459 (velocity)
[APPRAISAL fire_bolt] projectile.integrity_effective_energy_j: 1000000.0 -> 1020000.0000000066 (velocity)
[APPRAISAL fire_bolt] projectile.integrity_energy: 1e+06 J -> 1.02e+06 J (velocity)
[APPRAISAL fire_bolt] projectile.integrity_last_score_j: 1000000.0 -> 1020000.0000000066 (velocity)
[APPRAISAL fire_bolt] projectile.kinetic_energy: 0 J -> 20000 J (velocity)
[APPRAISAL fire_bolt] projectile.mana_cost: 0.1 -> 20000.100000006674 (velocity)
[APPRAISAL fire_bolt] projectile.mana_used: 0.1 -> 20000.100000006674 (velocity)
[APPRAISAL fire_bolt] projectile.momentum: Vector3(0, 0, 0) [kg*m/s] -> Vector3(200, 0, 0) [kg*m/s] (velocity)
[APPRAISAL fire_bolt] projectile.vel: Vector3(0, 0, 0) [m/s] -> Vector3(200, 0, 0) [m/s] (velocity)
[APPRAISAL fire_bolt] spell completed
[APPRAISAL fire_bolt] mana appraisal: 20000.1 mana
[APPRAISAL fire_bolt] created: projectile (Fire, 1 kg)
[CAST water_bolt] spell committed
[CAST water_bolt] mana appraisal: 20000.1 mana
```

Only the four fundamental element type selectors are valid template arguments. Calling the template configures an instance; it does not execute the spell body immediately.

## 3. Target context: `tgset`

`tgset` is for target profiles and the active target context. Target selection stays outside the spell definition. A spell can therefore be reused against different targets rather than hard-coding the intended target into the spell.

```mana
npc = tgset:
    hp = 100
    max_hp = 100
    distance = 10 m

spell fireball():
    projectile = create Fire
    shape(projectile, circle)
    velocity(projectile, 300 m/s)
    incant projectile

tgset(npc):
    release(fireball)
```

Expected output:

```text
(no output)
```

A target profile can contain supported combat values and a relative distance. A target context can also provide a destination to functions such as `mana.toward` or automatic direction for `mana.emit`. The runtime uses the current target context; the spell itself does not choose its target.

`tgset` is not a new definition category and not a replacement for `spell`. The normal architecture is: target context outside, spell behaviour inside, engine calculations in the runtime.

## 4. The standard execution words

| Syntax | Role |
|---|---|
| `create Element` | Create a runtime object from an available element/type. |
| `show value` | Display values in the program output. |
| `incant value` | Provide the result from a definition. This ends that execution path. |
| `appraise spell` | Trial spell execution and report changes while rolling back world state. |
| `cast spell` | Execute a spell and commit the world-state changes. |
| `load library` | Load a library namespace into the current program. |
| `skip` | Explicit no-operation statement for a block that otherwise needs a statement. |
| `span(...)` | Generate an integer iteration span for loop control. |
| `length(value)` | Count the supported items in a sequence. |
| `tune(...)` | Change an already-defined supported operation in a spell instance. |

The common control-flow words `if`, `elif`, `else`, `while`, `for`, and `in` are intentionally retained. The boolean operators `and`, `or`, and `not` are also retained. `round` is a shape label with a MANA meaning, not a replacement for the mathematical rounding function. Loops terminate through their conditions or the iteration safety limit.

## 5. Operators and values

Arithmetic and comparison operators are shared conventional symbols: `+`, `-`, `*`, `/`, `%`, `**`, `==`, `!=`, `<`, `<=`, `>`, and `>=`. These operators provide familiar mathematical notation while MANA's statements and built-ins follow the language's own keyword and function tables.

Current values include numbers, strings, booleans (`true`, `false`), lists, quantities with SI dimensions, vectors, element type selectors, world objects, definitions, spell templates/instances, and loaded library namespaces. Lists support indexing, negative indices, mutation by indexed assignment, and `length(...)`. Indexes must be integers and be within the sequence's valid bounds.

## 6. Units

MANA quantities carry dimensions. The parser supports SI base/derived unit names and the documented prefixes. The most common units include `m`, `m2`, `m3`, `kg`, `s`, `K`, `C`, `m/s`, `m/s2`, `N`, `Pa`, `J`, and `W`. `C` is an absolute Celsius temperature literal; `heat` and `cool` take temperature changes in kelvin.

A dimension mismatch is a language/quantity error. A metre cannot be silently added to a second, a dimensionless number cannot automatically stand for every unit, and a physics operation must reject non-finite values.

## 7. Pure mana and universal manipulation

Uppercase `Mana` is a type selector used by the creation mechanism. Lowercase `mana` is a built-in namespace installed by the runtime, giving access to pure-mana constructs/effects and universal control. It is available without `load mana`, though `load mana` may be used when an explicit library list is helpful.

The namespace provides `form`, `burst`, `emit`, `control`, `toward`, `away`, `lift`, `hold`, `levitate`, `stop`, `release_control`, and `collect`. These are independent of the four base elements. Defaults make many calls short, but the unit/shape semantics remain those documented in [Pure Mana and Universal Control](../libraries/MANA_LIBRARY.md).

The objective is not to hardcode a separate spell for every visible effect. For example, a mana projectile can be a pure-mana construct given velocity; a shockwave can use a radial burst; a skeleton that should walk toward a target should use general object control. A specialised library may supply the entity or domain-specific rule, but shared movement remains shared.

## 8. Events, timers, and deterministic execution

`wait`, `after`, `every`, `when`, `emit`, `advance_time`, and `simul` allow timed behaviour and event responses. Recognised events include physical contacts such as `impact`, `collision`, and `damaged`, plus library/runtime events for pathways, energy arrival, pure-mana effects and ignition. Unknown events produce MANA-format warnings and remain inert.

`simul` currently validates conflicts and executes statements in deterministic source order against the transaction's state; it is not a multi-thread executor. If a statement fails, the transaction rolls back. `for` and `while` have a one-million-iteration safety limit.

## 9. Variable scope and pure helpers

Control-flow blocks share the enclosing module/definition scope for newly introduced variables, so a variable first assigned in an `if` or loop remains visible after the block. Each ordinary definition establishes a local scope. A normal direct `def` call is intended for calculation, so a pure helper cannot create objects, assign world-object properties, or perform world-changing library operations. Move that behaviour into `spell` and execute the spell with `post` or `release`.

## 10. Language migration rule

MANA source uses its own vocabulary. `load`, `incant`, `skip`, `span`, `length`, `def` and `spell` are the preferred language spellings; `spldef` remains a legacy alias. Any word absent from the MANA keyword table is not identified as a keyword.

Use [Language Specification](../language/LANGUAGE_SPEC.md), [Keyword Migration](../language/KEYWORD_MIGRATION.md), and [Function Reference](../reference/FUNCTION_REFERENCE.md) for exact syntax and errors.
