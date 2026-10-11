# Generated MANA Error Message Index

**Page kind:** Reference

Generated from direct error-constructor calls in `magiclang/`. Run `python tools/generate_error_catalogue.py` after changing error messages. Dynamic templates show expressions in braces. Errors raised indirectly through a variable are listed as expression-supplied messages where statically visible; runtime-composed details depend on the values involved.

**Indexed call sites:** 603

| Error class | Source | Line | Message template |
|---|---|---:|---|
| `MagicErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 86 | `f"drafter.{operation}() defines plane data and cannot run inside post()/release()"` |
| `MagicErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 88 | `f"drafter.{operation}() cannot mutate a draft from a directly called helper"` |
| `MagicErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 222 | `f"{operation}() changes the world and cannot run inside a directly called helper; execute the containing spell with post() or release()"` |
| `MagicErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 448 | `'mana.control() action must be toward, away, lift, hold, stop, or release'` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 32 | `f"necromancy.{operation}() changes the world; execute it within post()/release()"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 39 | `f"necromancy.{operation}() cannot affect an inactive object"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 41 | `f"{runtime._object_label(value)} is already animated"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 60 | `f"necromancy.{operation}() requires an existing object identified as a corpse, bones, skeleton, or remains"` |
| `MagicErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 117 | `'reanimate_many() cannot contain the same body more than once'` |
| `MagicErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 58 | `f"the {channel_name} mana channel must be invoked before its energy can be recorded; use planes.invoke(\"{channel_name}\") first"` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 137 | `f"summoning '{record.name}' is missing required conditions: {', '.join(missing)}"` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 179 | `'summoning.bring() changes the world; call it from a spell using post()/release()'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 251 | `'this being has already been sent back'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 275 | `'only a named/tamed summoned being can be recalled'` |
| `MagicErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 277 | `'this being must be sent back before it can be recalled'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 259 | `'mana cannot be stored on a magical object'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 261 | `f"{name} is a runtime-managed property and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 754 | `'a directly called definition must be pure; move world-changing or scheduling statements into a spell and execute it with post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 765 | `'a directly called definition must be pure; use post() or release() to execute a spell'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 826 | `'a directly called definition must be pure; use show from a spell or top-level code'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 842 | `f"target '{self._object_label(selected)}' is not targetable"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1015 | `'a directly called definition cannot assign object properties; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1021 | `'a directly called definition cannot mutate a list; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1039 | `f"'{element_name}' is not a directly available elemental plane type; combine fundamental elements or use a registered elemental plane"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1046 | `f"creating {element_name} requires 'load planes' and 'planes.invoke(\"{element_name}\")' first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1052 | `f"creating {element_name} requires 'planes.invoke(\"{element_name}\")' first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1102 | `'a directly called definition cannot create objects; use post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1108 | `f"unknown built-in element or element variable '{element_name}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1112 | `f"create expects a registered element type; '{element_name}' is not an element selector"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1193 | `f"'{callee.name}' expects one of the four base element types: Fire, Water, Earth, or Air"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1269 | `'a directly called definition must be pure; move world-changing operations into a spell and execute it with post() or release()'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1447 | `'mana is not stored on objects'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1450 | `'acceleration_persistent is an internal physics flag; use accelerate() or assign .acc'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1452 | `'bound_energy is managed by planar energy transfers and cannot be assigned directly'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1454 | `f"{name} is a runtime-managed cost readout and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1459 | `f"{name} is managed by the energy-release ledger and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1463 | `f"{name} is managed by runtime object lifecycle operations"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1465 | `f"{name} is calculated by the integrity system and cannot be assigned directly"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1466 | `f"{name} is derived from mass, temp, and velocity; change those inputs instead"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1496 | `f"cannot change {name} on an inactive object; separate or reactivate it first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1523 | `'mass cannot be reduced by direct assignment; use a matter-removal operation or Null'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1564 | `'targets cannot store mana; spell mana is reported as a calculated cost'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1610 | `'target state must be solid, liquid, gas, plasma, powder, or burning'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1623 | `'target density is derived from mass and volume; set mass and volume instead'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1665 | `'cannot move an anchored object; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2286 | `'combine() requires two distinct objects; an object cannot be combined with itself'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2495 | `f"unsupported matter state '{state}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2497 | `f"{self._object_label(target)} is not defined as powderable"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2599 | `'cannot aim an anchored object; call unanchor() first'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2616 | `f"cannot {operation} an anchored object; call unanchor() first"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2924 | `'mana cost is calculated internally; do not pass mana= to an operation'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2941 | `'mana cost readout must be a finite non-negative number'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2945 | `'mana cost readout is outside the supported numeric range'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2947 | `'mana cost readout must be a finite non-negative number'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3014 | `f"{label} must be a non-negative mana amount"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3018 | `f"{label} is outside the supported numeric range"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3020 | `f"{label} must be finite"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3173 | `f"{operation}() cannot modify an inactive object"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3179 | `f"{operation}() is forbidden for this target"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3265 | `'simul blocks currently require direct operation calls; nested control flow is ambiguous'` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3270 | `f"simul cannot verify write conflicts for '{op_name}'"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3272 | `f"{op_name}() needs a target inside simul"` |
| `MagicErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3278 | `f"simul conflict: {writes[key]} and {op_name}() both write the same {prop} property"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 28 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 44 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 59 | `f"{label} must lie in the 2D x-y plane (z must be 0)"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 67 | `f"{label} must lie in the 2D x-y plane (z must be 0)"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 74 | `f"{label} cannot be negative"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 82 | `f"{label} is undefined for the zero vector"` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 92 | `'geometry2d.direction() requires z = 0; import vector3d for 3D vectors'` |
| `PhysicsErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 112 | `'angle() is undefined for the zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 38 | `f"{label} must be finite and {requirement}"` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 65 | `f"{label} cannot be the zero vector"` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 256 | `'mana.stop() needs an object with positive mass'` |
| `PhysicsErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 396 | `'mana.emit() energy (power × duration) must be finite'` |
| `PhysicsErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 123 | `'necromantic accounting total must be finite'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 226 | `'a pathway cannot connect a plane or region to itself'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 327 | `'send_energy() requires different source and destination planes or regions'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 333 | `'planes.send_energy() amount must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 382 | `'open_channel() requires different source and destination planes'` |
| `PhysicsErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 387 | `'planes.open_channel() rate must be finite and positive'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 30 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 77 | `'cannot normalize a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 116 | `'angle_between() is undefined for a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 132 | `'cannot project onto a zero vector'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 178 | `'vector3d.is_zero() tolerance cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 200 | `'vector3d.is_planar() tolerance cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 242 | `'vector3d.pressure() area must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 32 | `'vector component is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 48 | `'vector magnitude exceeds the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 75 | `'vector scale is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 77 | `'vector scale must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 89 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 96 | `'vector divisor is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 98 | `'vector divisor must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 100 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 118 | `'cannot normalize a zero-length vector'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 141 | `f"{label} must lie in the 2D x-y world plane (z must be 0); 3D vector calculations remain available outside world simulation"` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 164 | `'numeric physical quantity is outside the supported range'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 166 | `'numeric physical quantity must be finite'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 183 | `'speed cannot exceed c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 187 | `'a massive object cannot reach c; relativistic energy diverges'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 203 | `'speed cannot exceed c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 205 | `'a massive object cannot reach c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 221 | `'area must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 231 | `'cannot move in a zero-length direction'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 244 | `f"speed {speed} m/s exceeds c ({C} m/s)"` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 249 | `'a massive object cannot reach c'` |
| `PhysicsErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 259 | `f"speed {speed} m/s exceeds c ({C} m/s)"` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 71 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 81 | `'collision_radius cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 88 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 102 | `'restitution is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 106 | `'restitution must be between 0 (no bounce) and 1 (elastic bounce)'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 376 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 380 | `'physics timestep is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 382 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 962 | `'wait duration cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 971 | `'after delay cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 980 | `'every interval must be greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1146 | `'unary arithmetic result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1148 | `f"invalid unary arithmetic operation: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1279 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1281 | `'operation exceeded the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1283 | `f"operation rejected the supplied numeric value: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1365 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1369 | `f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1373 | `f"exponent exceeds the MANA safety limit ({MAX_POWER_EXPONENT}); value is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1386 | `f"integer power result exceeds the MANA size limit ({MAX_INTEGER_RESULT_BITS} bits)"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1395 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1397 | `'arithmetic result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1399 | `f"invalid arithmetic operation: {exc}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1403 | `'arithmetic result is complex; MANA supports real-valued numbers only'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1405 | `'arithmetic result must be finite; operation produced infinity or NaN'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1503 | `'restitution is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1507 | `'restitution must be between 0 and 1'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1575 | `f"target field '{name}' is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1577 | `f"target field '{name}' must be finite"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1591 | `f"target {name} must be {rule}"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1595 | `'target temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1621 | `'ignition temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1631 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1635 | `'target collision_radius cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1673 | `'move() cannot use a zero direction'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1692 | `'heat() amount cannot be negative; use cool() to decrease temperature'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1719 | `'cool() amount cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1724 | `'cooling cannot reduce temperature below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1784 | `'velocity() speed cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1794 | `f"cannot aim '{self._object_label(target)}' at '{self._object_label(selected)}': they occupy the same position; give the target a distance or position"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1993 | `'automatic target flight exceeds 60 s; use a closer target or configure motion explicitly'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2411 | `'not enough thermal energy is available to form Ice'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2509 | `'absolute pressure cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2519 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2585 | `'direction() component is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2587 | `'direction() components must be finite'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2591 | `'direction() cannot be the zero vector'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2604 | `'aim() direction cannot be zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2619 | `f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS} seconds"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2623 | `f"{operation}() duration is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2625 | `f"{operation}() duration must be between 0 and {MAX_PERSISTENCE_SECONDS} seconds"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2627 | `f"{operation}() force magnitude cannot be negative"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2632 | `f"{operation}() direction cannot be zero"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2638 | `f"{operation}() target must have positive mass"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2689 | `'rotate() angle is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2705 | `'scale() factor must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2709 | `'scale() factor is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2711 | `'scale() factor must be finite and greater than zero'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2718 | `'scale() result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2720 | `'scale() would reduce volume to zero; choose a larger factor'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2729 | `'scale() result is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2890 | `'sqrt() cannot calculate the real square root of a negative value'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2963 | `'planar energy transfer must be finite and non-negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3202 | `f"{label} is outside the supported numeric range"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3204 | `f"{label} must be finite"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3229 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3231 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3233 | `'area cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3235 | `'collision_radius cannot be negative; use 0 m for area-derived 2D bounds'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3238 | `'temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3240 | `'temperature exceeds the Planck temperature; this requires the causality library'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3244 | `'absolute pressure cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3379 | `'time advancement requires a finite non-negative duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3384 | `'physics timestep must be a finite positive duration'` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3386 | `f"physics timestep cannot exceed {MAX_TIMESTEP_SECONDS} s; smaller steps reduce missed collisions"` |
| `PhysicsErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3448 | `'planar channel produced an invalid energy amount'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 160 | `'quantity is outside the supported numeric range'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 162 | `'quantity must be finite'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 165 | `'mass cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 167 | `'volume cannot be negative'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 169 | `'absolute temperature cannot be below 0 K'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 227 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 231 | `'division by zero'` |
| `PhysicsErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 242 | `'division by zero'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 75 | `'this draft has already been created; registered plane data is immutable through drafter'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 204 | `f"'{key}' is reserved for plane-definition metadata"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 207 | `'a plane draft may define at most 256 custom properties'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 219 | `'a plane draft may define at most 100 regions'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 221 | `f"region '{name}' is already present in this draft"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 246 | `'a plane draft may define at most 1000 beings'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 276 | `'being hp cannot exceed max_hp'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 278 | `'being hp cannot exceed max_hp'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 299 | `f"unknown resistance element '{element_name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 310 | `'being field must be kind, element, hp, max_hp, defence, attack, summoning_requirements, or resistance.<Element>'` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 319 | `f"being '{being_name}' must identify exactly one being in this draft or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 387 | `f"plane or region '{reference.qualified_name}' has no custom property '{key}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 142 | `f"plane or region reference '{value.qualified_name}' is not registered in this MANA runtime"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 149 | `f"unknown plane or region '{value}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 152 | `f"plane or region '{value}' is not currently loaded"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 164 | `"a region's parent must be a plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 172 | `f"region alias '{alias}' conflicts with an existing plane or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 197 | `"a region's parent must be a top-level plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 203 | `f"region ID '{region_id}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 209 | `f"region alias '{alias}' conflicts with an existing plane or region"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 253 | `f"plane ID '{plane_id}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 265 | `f"plane alias '{alias}' is already registered"` |
| `RuntimeErrorML` | [`magiclang/libraries/plane_data/elemental_planes.py`](../../../magiclang/libraries/plane_data/elemental_planes.py) | 163 | `f"unknown elemental being '{name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 38 | `f"'{_label(reference)}' is not an elemental plane"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 40 | `f"elemental plane '{reference.name}' has no data library assigned"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 45 | `f"no elemental data record is registered for '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 184 | `f"regions_of() expects a plane, not region '{_label(reference)}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 194 | `f"parent_of() expects a region, not plane '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 303 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 355 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 390 | `f"no open route connects {_label(start)} to {_label(end)}"` |
| `RuntimeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 455 | `f"no elemental spirit record is defined for '{reference.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 57 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 59 | `f"being '{record.name}' belongs to '{record.home_plane}', not '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 71 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 81 | `f"being '{being}' is not defined in plane '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 83 | `f"being name '{being}' is duplicated in plane '{source_ref.name}'"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 112 | `f"unknown being '{being}'; for a custom being, provide its home plane, e.g. summoning.bring(\"Crystal Drake\", \"Crystal Reach\")"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 117 | `f"being name '{being}' is ambiguous; supply its home plane ({homes})"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 121 | `"a being's home plane must be a top-level plane, not a region"` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 184 | `'summoning source and destination must be different planes'` |
| `RuntimeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 254 | `'this being has no distinct home plane to return to'` |
| `RuntimeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 400 | `f"physics would check {pair_checks} collision pairs in one substep; the current budget is {max_pair_checks}. Use a larger timestep to reduce step count or reduce the number of collidable objects."` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 252 | `"mana is not stored on objects; inspect the spell's mana cost readout"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 372 | `f"'{name}' is not identified"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 546 | `<message supplied by expression: 'library load cycle detected: ' + ' -> '.join(cycle)>` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 548 | `f"invalid library name '{name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 568 | `f"library {name} needs {dependency} loaded first"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 614 | `f"library name '{name}' is reserved by the MANA language or built-in API"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 617 | `f"library '{name}' is not available; built-in libraries are geometry2d, vector3d, planes, elemental_planes, hell, heaven, atlantis, fae_paradise, lineage_halls, and wild_realm. User libraries must be packaged as libraries/{name}.manalib"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 629 | `f"library '{name}' exceeds the {MAX_LIBRARY_ARCHIVE_MEMBERS}-member archive limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 634 | `f"library '{name}' exceeds the {MAX_LIBRARY_UNCOMPRESSED_BYTES}-byte uncompressed size limit"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 639 | `f"library package '{name}' is corrupt at {bad_member}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 643 | `f"library '{name}' has no valid mana-library.json manifest"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 645 | `f"library '{name}' manifest must be a JSON object"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 647 | `f"library '{name}' has an unsupported package format"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 649 | `f"library manifest name does not match loaded name '{name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 655 | `f"library '{name}' manifest dependencies must be a unique list of library names"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 659 | `f"library '{name}' manifest entry must be a relative path string"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 664 | `f"library '{name}' has an unsafe entry path"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 668 | `f"library '{name}' is missing its UTF-8 MANA entry file '{entry}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 680 | `f"library '{name}' entry files may contain only ordinary def functions, load statements, and skip at top level"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 688 | `f"library '{name}' manifest must list one or more valid exported names"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 695 | `f"library '{name}' exports undefined names: {', '.join(missing_exports)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 703 | `f"library '{name}' is not a valid .manalib archive"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 721 | `'execution stopped by user'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 800 | `f"invalid library function name '{stmt.name}'"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 835 | `'incant can only be used inside a def'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 926 | `'while loop exceeded the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 942 | `'for loop exceeded the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 964 | `f"wait duration exceeds the {MAX_PERSISTENCE_SECONDS}s safety cap"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 973 | `f"after delay exceeds the {MAX_PERSISTENCE_SECONDS}s safety cap"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 982 | `'every interval exceeds the persistent-spell safety cap'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 995 | `f"unsupported statement {type(stmt).__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1029 | `f"list index {index} is out of range for a list of length {len(container)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1059 | `f"expression evaluation exceeds the safety limit ({MAX_EXPRESSION_DEPTH} nested operations)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1098 | `f"index {index} is out of range for a value of length {len(container)}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1151 | `f"unknown unary operator {expr.op}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1164 | `f"{name} is a MANA command/special form, not a value-producing function; write it using its documented standalone syntax"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1184 | `f"unsupported expression {type(expr).__name__}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1223 | `f"MANA definition call depth exceeded the safety limit ({MAX_FUNCTION_DEPTH})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1340 | `f"string result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} characters)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1345 | `f"list result exceeds the MANA size limit ({MAX_COLLECTION_SIZE} items)"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1359 | `f"repeated {kind} exceed the MANA size limit ({MAX_COLLECTION_SIZE})"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1391 | `f"unknown binary operator {op}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2048 | `'integer is too large to display; reduce its size before using show()'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2539 | `'integer is too large to display; reduce its size before using show()'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3222 | `'timing value is outside the supported numeric range'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3224 | `'timing value must be finite'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3346 | `'timer execution exceeded the per-advance safety limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3350 | `'incant cannot escape from a persistent timer'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3397 | `f"advance_time() requires {step_count} physics steps; the safety cap is {MAX_PHYSICS_STEPS_PER_ADVANCE}"` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3488 | `'span() step cannot be zero'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3501 | `'span() exceeds the safety iteration limit'` |
| `RuntimeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3517 | `f"'{name}' is reserved and cannot be used as an identifier"` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 43 | `'mixed tabs and spaces in indentation'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 48 | `'mixed tabs and spaces in indentation; use one style consistently'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 62 | `'inconsistent indentation'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 100 | `'unterminated string'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 112 | `'numeric literal exceeds the supported input range'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 117 | `'numeric literal is outside the supported finite range'` |
| `SyntaxErrorML` | [`magiclang/lexer.py`](../../../magiclang/lexer.py) | 172 | `f"unexpected character {ch}"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 63 | `<message supplied by expression: message or self._unexpected_token_message(token_type)>` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 123 | `"expression or block nesting exceeds MANA's parser safety limit"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 147 | `f"'{self.current.value}' is reserved and cannot be used as an identifier"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 196 | `"show needs a value, for example 'show stone.temp'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 202 | `'show/post/release/tune cannot be nested inside another expression'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 204 | `"create must be assigned to a name first, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 210 | `f"'{expr.name}' is not identified"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 220 | `"write tuning as 'tune(spell.operation) = target, value'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 226 | `'tune must identify a named spell instance'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 237 | `"the old '.tune' syntax is removed; use 'tune(spell.operation) = target, value'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 243 | `'show/post/release cannot be assigned to variables; tune is only valid as a special assignment form'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 248 | `"create results must be assigned directly to a variable name, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 250 | `"create results must be assigned directly, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 256 | `"create results must be assigned directly, for example 'fire = create Fire'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 259 | `'show/post/release must be standalone commands; tune must be used as an assignment'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 261 | `'show/post/release/tune cannot be nested inside another command'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 269 | `f"{mode} accepts one spell name, for example '{mode}(fireball)'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 271 | `f"{mode} accepts exactly one argument: the spell name; use 'tune(spell.operation) = target, value' to change an existing operation"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 278 | `f"{context} cannot contain show/post/release; these are standalone commands"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 283 | `f"{context} cannot contain an unassigned create; use 'name = create Element'"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 347 | `f"parameter '{param}' is defined more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 355 | `'required parameters must come before parameters with defaults'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 363 | `'spell definitions currently accept no parameters or one element selector: spldef name(element):'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 368 | `'the spell element selector cannot have a default value'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 370 | `'library modules may export ordinary def functions, not spldef spells'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 387 | `'incant accepts one value expression; function-call syntax is not supported'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 398 | `'incant accepts one value expression; function-call syntax is not supported'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 403 | `'create results must be assigned directly before use with incant'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 405 | `'show/post/release are commands and tune is not an incant value'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 433 | `f"target field '{field_name}' is defined more than once"` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 620 | `'property name must be an identifier'` |
| `SyntaxErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 756 | `<message supplied by expression: message>` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 77 | `'expected a draft returned by drafter.begin() or drafter.add_region()'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 94 | `'custom plane data nesting exceeds 16 levels'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 99 | `'custom plane numeric values must be finite'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 107 | `'custom plane data can contain values, not executable functions or world objects'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 110 | `'custom plane data cannot contain circular references'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 129 | `'custom plane data object keys must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 134 | `f"unsupported custom plane data value: {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 165 | `f"invalid being definition '{being.name}': {exc}"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 175 | `'drafter.begin() name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 177 | `'drafter.begin() category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 180 | `'plane category must start with a letter and contain only letters, digits, or spaces'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 184 | `'plane_id must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 191 | `'drafter.alias() expects non-empty alias text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 202 | `'custom property name must be a valid identifier'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 215 | `'drafter.add_region() expects a plane draft'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 217 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 223 | `'region_id must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 234 | `'being name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 236 | `'being kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 238 | `'being element must be non-empty text or null'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 242 | `'being requirements must be a list of text values'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 244 | `'being requirements must contain non-empty text values'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 268 | `f"being {key} must be a finite non-negative number or null"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 272 | `f"being {key} is outside the supported numeric range"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 274 | `f"being {key} must be a finite non-negative number or null"` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 283 | `'being kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 288 | `'being element must be non-empty text or null'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 293 | `'summoning_requirements must be a list of non-empty strings'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 301 | `'element resistance must be a finite number from 0 to 1'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 305 | `'element resistance is outside the supported numeric range'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 307 | `'element resistance must be a finite number from 0 to 1'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 316 | `'drafter.set_being() expects a being name and field name'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 326 | `'drafter.create() expects a plane draft'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 328 | `'plane name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/drafter.py`](../../../magiclang/libraries/drafter.py) | 383 | `'drafter.get_value() key must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 24 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 30 | `f"{label} must be a finite number"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 40 | `f"{label} must be a finite distance in metres"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 46 | `f"{label} must be a finite distance in metres"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 55 | `f"{label} must be a 2D point or an object with a position"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 65 | `f"{label} must be a vector"` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 252 | `'polygon_area() expects a list of at least three 2D points'` |
| `TypeErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 389 | `'point_in_polygon() expects a list of at least three points'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 59 | `f"{label} must be a direction vector"` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 245 | `'destination is required outside tgset(target):'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 291 | `'mana.form() shape must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 297 | `'mana.form() collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 299 | `'mana.form() anchored must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 445 | `'mana.control() action must be text'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 37 | `f"necromancy.{operation}() expects an existing MANA object"` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 91 | `'necromancy.reanimate() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 110 | `'necromancy.reanimate_many() expects a non-empty list of corpse objects'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 115 | `'reanimate_many() list entries must be MANA objects'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 120 | `'necromancy.reanimate_many() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/necromancy.py`](../../../magiclang/libraries/necromancy.py) | 144 | `'necromancy.is_undead() expects a MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 146 | `'plane identifier must be a name, ID, or plane/region reference'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 166 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 195 | `'region parent must be a registered plane'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 199 | `'region ID must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 201 | `'region name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 240 | `'plane ID must start with a lowercase letter and contain lowercase letters, digits, or underscores'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 242 | `'plane name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 244 | `'plane category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 247 | `'plane category must start with a letter and contain only letters, digits, or spaces'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 251 | `'plane data_library must be a library name or null'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 255 | `'plane aliases must be a list of names'` |
| `TypeErrorML` | [`magiclang/libraries/planar_registry.py`](../../../magiclang/libraries/planar_registry.py) | 260 | `'plane aliases must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/plane_data/elemental_planes.py`](../../../magiclang/libraries/plane_data/elemental_planes.py) | 158 | `'elemental_planes.find_being() expects a name'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 148 | `'planes.exists() expects a plane or region name'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 167 | `'planes.plane_of() expects a being record or world object, not a plane name or plane reference'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 202 | `'planes.planes_in() category must be non-empty text'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 211 | `'planes.open_path() one_way must be true or false'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 336 | `'planes.send_energy() kind must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 348 | `f"planes.send_energy() kind must be a known elemental energy label ({allowed}) or a registered internal transfer label"` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 65 | `'summoning.bring() expects a being name or a BeingRecord'` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 134 | `'summoning requirements must be a list of non-empty text values'` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 158 | `f"summoning.{operation}() expects a being created by summoning.bring()"` |
| `TypeErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 235 | `'summoning.tame() name must be non-empty text when supplied'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 26 | `f"{label} must be a finite number or a {dimension} quantity"` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 32 | `f"{label} must be a finite number or a {dimension} quantity"` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 62 | `'vector3d.magnitude() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 74 | `'vector3d.normalize() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 85 | `'vector3d.dot() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 93 | `'vector3d.cross() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 102 | `'vector3d.distance() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 110 | `'vector3d.angle_between() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 129 | `'vector3d.project() expects two vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 148 | `'vector3d.reflect() expects vectors'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 162 | `'vector3d.scale() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 169 | `'vector3d.components() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 175 | `'vector3d.is_zero() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 190 | `'vector3d.planar() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 197 | `'vector3d.is_planar() expects a vector'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 214 | `'vector3d.object_vector() expects a vector or MANA object'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 217 | `'vector3d.object_vector() field must be pos, vel, acc, force, momentum, direction, or anchor_pos'` |
| `TypeErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 235 | `'vector3d.pressure() force must be a force quantity or force vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 28 | `'vector components must be finite numeric values'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 34 | `'vector components must be finite numeric values'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 53 | `'vector operation requires another vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 67 | `'boolean values cannot scale a vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 86 | `'boolean values cannot scale a vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 106 | `'vector dot product requires another vector'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 139 | `f"{label} requires a vector"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 152 | `'boolean values are not numeric physical quantities'` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 168 | `f"expected numeric value, got {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 173 | `f"{label} requires a vector"` |
| `TypeErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 229 | `'displacement direction must be a vector'` |
| `TypeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 98 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 104 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 254 | `f"{self.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 263 | `f"{self.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 768 | `f"{stmt.mode}({stmt.spell.name}) expects a named spell or configured spell instance, not {type(spell).__name__}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 775 | `"tune requires a configured spell instance; create one first, for example 'fire_ball = e_ball(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 781 | `f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': that operation and target do not exist in the spell"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 786 | `f"cannot tune '{spell.name}.{stmt.operation}' for '{stmt.target_name}': multiple matching operations exist; make the target/operation unambiguous"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 806 | `"spell definitions accept no parameters or one base-element selector: use 'spldef name(element):'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 933 | `'for loop expects a list or span'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1025 | `'indexed assignment requires a list; only list items are assignable'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1027 | `'list index must be an integer'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1032 | `'assignment target must be a variable or object property'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1094 | `'indexing is supported for lists, strings, and spans'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1096 | `'index must be an integer'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1150 | `f"unary '{expr.op}' is not supported for {type(value).__name__}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1190 | `f"spell template '{callee.name}' expects exactly one element: {callee.name}(Fire)"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1198 | `f"spell '{callee.name}' takes no arguments"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1202 | `f"function '{callee.name}' takes at most {len(callee.params)} arguments"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1208 | `f"function '{callee.name}' has no parameter '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1210 | `f"function '{callee.name}' got multiple values for '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1218 | `f"function '{callee.name}' is missing required argument '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1244 | `f"spell '{callee.name}' cannot be called as a value; use post({callee.name}) or release({callee.name})"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1257 | `f"configured spell '{callee.name}' is not called directly; use post({callee.name}) or release({callee.name})"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1285 | `<message supplied by expression: str(exc)>` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1286 | `f"value {callee} is not callable"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1401 | `<message supplied by expression: str(exc)>` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1411 | `f"library '{obj.name}' does not export '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1419 | `f"object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1424 | `'properties can only be assigned on magical objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1445 | `'properties can only be assigned on magical objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1470 | `'display_name must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1472 | `'object_kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1474 | `'material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1477 | `'stabilizers must be a list of registered element names'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1484 | `'stabilizers may contain only Earth, Water, Air, Order, Light, Space, Time, Entropy, or Death'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1491 | `f"{obj.element} object has no property '{name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1499 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1505 | `'restitution must be a finite number between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1509 | `'collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1571 | `f"target field '{name}' must be a non-negative number"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1584 | `f"{name} must be between 0 and 1 (0 = none, 1 = full resistance)"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1598 | `'target material must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1602 | `'target kind must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1606 | `'target shape must be non-empty text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1614 | `'target combustible must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1617 | `'target powderable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1642 | `'target restitution must be between 0 and 1'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1646 | `'target collidable must be true or false'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1655 | `'shape() expects a built-in geometry name'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1670 | `'move() direction must be a vector'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1822 | `'detect() currently expects a magical object'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1825 | `'detect() property name must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1827 | `f"detect() target has no property '{property_name}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1848 | `f"'{candidate.name}' is an ordinary function, not a spell; call it normally to calculate a value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1850 | `f"'{candidate.name}' is a spell template; configure it first, e.g. '{candidate.name}(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1861 | `f"'{candidate}' is an ordinary function, not a spell; call it normally to calculate a value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1863 | `f"'{candidate}' is a spell template; configure it first, e.g. '{candidate}(Fire)'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1865 | `f"{mode}() expected a named spell or configured spell instance, got {candidate}"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1867 | `f"{mode}() accepts a spell name only, not a magical object; use object operations for objects"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1868 | `f"{mode}() expects one spell name"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2491 | `'transform() state must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2527 | `'show() separator must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2580 | `'direction() components must be numbers'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2601 | `'aim() direction must be a vector created by direction()'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2629 | `f"{operation}() direction must be a vector"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2673 | `'pull() needs position vectors on both objects'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2685 | `'rotate() angle must be a finite number of radians'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2691 | `'rotate() angle must be a finite number of radians'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2744 | `'reflect() needs a non-zero direction vector as surface normal'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2766 | `'split() parts must be an integer between 2 and 10000'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2882 | `'sqrt() expects a non-negative number'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2888 | `'sqrt() expects a non-negative number'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2899 | `'magnitude() expects a vector or numeric quantity'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2905 | `'has_domain() domain must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3167 | `f"{operation}() expects a magical object"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3184 | `f"{operation}() requires target property '{prop}'"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3195 | `f"{label} requires a numeric value"` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3218 | `'timing requires a numeric duration'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3468 | `'emit() event name must be text'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3484 | `'span() expects 1 to 3 integer arguments'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3486 | `'span() arguments must be integers'` |
| `TypeErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3508 | `'length() expects a list, string, or span'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 156 | `'quantity value must be numeric, not boolean or text'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 176 | `f"cannot combine a quantity in {self.dimension} with {other_kind}; expected another quantity in {self.dimension}"` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 208 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 222 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 237 | `'boolean values cannot be used as quantities'` |
| `TypeErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 250 | `'quantity exponent must be an integer'` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 21 | `f"{label} must be a plain number, not {value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 37 | `f"{label} must be measured in metres"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 57 | `f"{label} must use metre coordinates"` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 120 | `'angle_between() requires vectors with matching dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/geometry2d.py`](../../../magiclang/libraries/geometry2d.py) | 185 | `'lerp() requires vectors with matching dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 53 | `'mana effect position must be a position vector in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 61 | `f"{label} must be dimensionless or a displacement vector"` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 142 | `'mana energy transfer needs a target temperature in K'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 164 | `'mana burst recipients need position and velocity vectors'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 241 | `'the selected tgset target needs a position for automatic control'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 258 | `'mana.stop() needs a valid velocity vector'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 260 | `'mana.stop() needs an object temperature in K'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 464 | `'mana.control() target needs a position in metres'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 525 | `'mana.collect() items need positions in metres'` |
| `UnitErrorML` | [`magiclang/libraries/mana.py`](../../../magiclang/libraries/mana.py) | 554 | `f"{label} must be a position vector in metres or a positioned object"` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 329 | `'planes.send_energy() amount must be an energy quantity in joules'` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 331 | `f"planes.send_energy() requires joules, not {amount.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/planes.py`](../../../magiclang/libraries/planes.py) | 385 | `f"planes.open_channel() rate must be measured in watts, not {actual}"` |
| `UnitErrorML` | [`magiclang/libraries/summoning.py`](../../../magiclang/libraries/summoning.py) | 152 | `'summoning position must be a position vector measured in metres or a positioned object'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 23 | `f"{label} must use {dimension}, not {value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 104 | `'vector3d.distance() requires matching coordinate units'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 112 | `'angle_between() requires matching vector dimensions'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 220 | `f"object has no vector-valued '{field}' property"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 228 | `f"vector3d.pressure() force vector must use N, not {force_value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 232 | `f"vector3d.pressure() force must use N, not {force_value.dimension}"` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 237 | `'vector3d.pressure() force must include N units'` |
| `UnitErrorML` | [`magiclang/libraries/three_d.py`](../../../magiclang/libraries/three_d.py) | 240 | `f"vector3d.pressure() area must use m2, not {actual}"` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 679 | `f"unknown unit '{candidate}'"` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 692 | `'numeric literal is outside the supported range for unit conversion'` |
| `UnitErrorML` | [`magiclang/parser.py`](../../../magiclang/parser.py) | 697 | `'numeric literal is outside the supported finite range for unit conversion'` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 55 | `f"vector dimensions differ: {self.dimension} and {other.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 158 | `f"expected {expected}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 175 | `f"{label} expects {dimension}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/physics.py`](../../../magiclang/physics.py) | 256 | `'clamp_speed() expects a velocity vector'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 43 | `'2D world physics requires every active object to have a position vector in metres'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 50 | `'2D world physics requires every active object to have a velocity vector in m/s'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 57 | `'2D world physics requires every active object to have an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 69 | `'physics simulation requires mass measured in kg'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 79 | `'collision_radius must be measured in metres'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 86 | `'2D collision bounds require area measured in m2'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 228 | `'mana projectile impact target needs a temperature in K'` |
| `UnitErrorML` | [`magiclang/physics_engine.py`](../../../magiclang/physics_engine.py) | 384 | `'2D world gravity must be an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1335 | `f"cannot compare these values: {exc}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1518 | `f"{obj.element}.{name} requires a vector in {old.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1568 | `f"target field '{name}' must be a plain number"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1581 | `f"target field '{name}' must be dimensionless"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1626 | `'target pos must be a position vector'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1639 | `'target restitution must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1689 | `'heat() expects a temperature change in K, not an absolute Celsius temperature'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1716 | `'cool() expects a temperature change in K, not an absolute Celsius temperature'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1739 | `'accelerate() vector must be in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1757 | `'decelerate() vector must be in m/s2'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1778 | `'velocity() vector must be in m/s'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1790 | `'targeted velocity requires source and target positions in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 1969 | `'selected target needs a world position in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2577 | `'direction() components must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2682 | `'rotate() angle is dimensionless and interpreted in radians'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2702 | `'scale() factor must be dimensionless'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2812 | `'anchor() position must be a position vector in metres'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 2885 | `'sqrt() currently accepts only dimensionless quantities'` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3011 | `f"{label} must be measured in mana"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3192 | `f"{label} requires {expected}, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3215 | `f"timing requires seconds, got {value.dimension}"` |
| `UnitErrorML` | [`magiclang/runtime.py`](../../../magiclang/runtime.py) | 3394 | `'advance_time() gravity must be an acceleration vector in m/s2'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 84 | `f"unknown or unsupported dimension/unit '{value}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 116 | `f"unknown unit '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 133 | `f"C is only supported as a standalone absolute-temperature literal, not '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 142 | `f"unknown unit '{text}'"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 181 | `f"incompatible dimensions: {self.dimension} and {other.dimension}"` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 187 | `'two absolute temperatures cannot be added'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 197 | `'an absolute temperature cannot be subtracted from a temperature change'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 210 | `'absolute temperatures cannot be multiplied; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 224 | `'absolute temperatures cannot be divided; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 239 | `'absolute temperatures cannot be divided; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 248 | `'absolute temperatures cannot be exponentiated; use a temperature difference in K'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 256 | `'an absolute temperature cannot be negated; use a signed Celsius literal such as -10 C'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 291 | `'matter_to_mana() expects mass in kg'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 297 | `'mana_to_matter() expects a mana quantity'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 303 | `'mana_to_energy() expects a mana quantity'` |
| `UnitErrorML` | [`magiclang/units.py`](../../../magiclang/units.py) | 309 | `'energy_to_mana() expects energy in joules'` |
