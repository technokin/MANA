"""Deterministic 2D world motion, collision, and impact-damage stepper.

World objects move in the x-y plane. Circular collision bounds are inferred
from projected area unless collision_radius is explicitly set. General Vector3
and 3D physics calculations remain available to library code, but z motion is
not accepted by the primary world engine. Contact impulses use a Newtonian
restitution model; this is not a high-speed relativistic collision solver.
"""
from __future__ import annotations

import math
from .errors import PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from .physics import Vector3, enforce_speed, kinetic_energy, momentum, require_2d_world_vector
from .units import ACCELERATION, DIMENSIONLESS, ENERGY, KG, K, M, M2, MOMENTUM, VELOCITY, Quantity

DEFAULT_TIMESTEP_SECONDS = 1.0 / 60.0
MAX_TIMESTEP_SECONDS = 0.1
MAX_PHYSICS_STEPS_PER_ADVANCE = 100_000
MAX_COLLISION_PAIR_CHECKS_PER_ADVANCE = 20_000_000
DEFAULT_RESTITUTION = 0.2
# Tuning constant for the prototype's impact-to-target-health conversion.
# It is not a universal physical law and is documented as editable.
JOULES_PER_HIT_POINT = 100.0
DEFAULT_SPECIFIC_HEAT_J_PER_KG_K = 1000.0
POSITION_SLOP_M = 1e-7


def _dot(a: Vector3, b: Vector3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def _subtract(a: Vector3, b: Vector3, dimension=None) -> Vector3:
    return Vector3(a.x - b.x, a.y - b.y, a.z - b.z, dimension or a.dimension)


def _add(a: Vector3, b: Vector3, dimension=None) -> Vector3:
    return Vector3(a.x + b.x, a.y + b.y, a.z + b.z, dimension or a.dimension)


def _position(obj) -> Vector3:
    value = obj.properties.get("pos")
    if not isinstance(value, Vector3) or value.dimension != M:
        raise UnitErrorML("2D world physics requires every active object to have a position vector in metres")
    return require_2d_world_vector(value, "world object position")


def _velocity(obj) -> Vector3:
    value = obj.properties.get("vel")
    if not isinstance(value, Vector3) or value.dimension != VELOCITY:
        raise UnitErrorML("2D world physics requires every active object to have a velocity vector in m/s")
    return require_2d_world_vector(value, "world object velocity")


def _acceleration(obj) -> Vector3:
    value = obj.properties.get("acc")
    if not isinstance(value, Vector3) or value.dimension != ACCELERATION:
        raise UnitErrorML("2D world physics requires every active object to have an acceleration vector in m/s2")
    # push()/pull() are defined as one-second action impulses in the current
    # runtime. They retain an acceleration readout, but must not apply it again
    # on every future world tick unless the user explicitly sets acceleration.
    if not obj.properties.get("acceleration_persistent", True):
        return Vector3(0, 0, 0, ACCELERATION)
    return require_2d_world_vector(value, "world object acceleration")


def _mass(obj) -> float:
    value = obj.properties.get("mass")
    if not isinstance(value, Quantity) or value.dimension != KG:
        raise UnitErrorML("physics simulation requires mass measured in kg")
    if value.value < 0:
        raise PhysicsErrorML("mass cannot be negative")
    return value.value


def _collision_radius(obj) -> float:
    explicit = obj.properties.get("collision_radius", Quantity(0, M))
    if isinstance(explicit, Quantity):
        if explicit.dimension != M:
            raise UnitErrorML("collision_radius must be measured in metres")
        if explicit.value < 0:
            raise PhysicsErrorML("collision_radius cannot be negative")
        if explicit.value > 0:
            return explicit.value
    area = obj.properties.get("area", Quantity(0, M2))
    if not isinstance(area, Quantity) or area.dimension != M2:
        raise UnitErrorML("2D collision bounds require area measured in m2")
    if area.value < 0:
        raise PhysicsErrorML("area cannot be negative")
    if area.value <= 0 or _mass(obj) <= 0:
        return 0.0
    # Circle with the same projected area. Shape labels remain semantic labels.
    return math.sqrt(area.value / math.pi)


def _restitution(obj) -> float:
    value = obj.properties.get("restitution", DEFAULT_RESTITUTION)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML("restitution must be a finite number between 0 and 1")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise PhysicsErrorML("restitution is outside the supported numeric range") from exc
    if not math.isfinite(value):
        raise TypeErrorML("restitution must be a finite number between 0 and 1")
    if not 0.0 <= value <= 1.0:
        raise PhysicsErrorML("restitution must be between 0 (no bounce) and 1 (elastic bounce)")
    return value


def _collision_time_fraction(start_delta: Vector3, relative_displacement: Vector3, radius: float) -> float | None:
    """Earliest swept-circle contact fraction in the x-y plane, if any."""
    c = _dot(start_delta, start_delta) - radius * radius
    if c <= 0:
        return 0.0
    a = _dot(relative_displacement, relative_displacement)
    if a <= 1e-24:
        return None
    b = 2.0 * _dot(start_delta, relative_displacement)
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0:
        return None
    entry = (-b - math.sqrt(max(0.0, discriminant))) / (2.0 * a)
    if 0.0 <= entry <= 1.0:
        return entry
    return None


def _set_velocity(runtime, obj, velocity: Vector3) -> None:
    mass_value = obj.properties["mass"]
    velocity = enforce_speed(velocity, massive=mass_value.value > 0)
    obj.properties["vel"] = velocity
    obj.properties["kinetic_energy"] = kinetic_energy(mass_value, velocity)
    obj.properties["momentum"] = momentum(mass_value, velocity)
    runtime.update_total_energy(obj)


def _apply_damage(runtime, target, striker, impact_energy_j: float) -> float:
    """Apply the documented prototype hit-point model to tgset targets only."""
    if target.properties.get("hp") is None or target.properties.get("targetable") is False:
        return 0.0
    hp = float(target.properties.get("hp", 0.0))
    if hp <= 0 or impact_energy_j <= 0:
        return 0.0
    element = str(getattr(striker, "element", "")).lower()
    resistance = target.properties.get(f"resist_{element}", 0.0)
    if isinstance(resistance, bool) or not isinstance(resistance, (int, float)):
        resistance = 0.0
    resistance = min(1.0, max(0.0, float(resistance)))
    defence = target.properties.get("defence", 0.0)
    if isinstance(defence, bool) or not isinstance(defence, (int, float)):
        defence = 0.0
    raw_damage = (impact_energy_j / JOULES_PER_HIT_POINT) * (1.0 - resistance)
    damage = max(0.0, raw_damage - max(0.0, float(defence)))
    if damage <= 0:
        return 0.0
    target.properties["hp"] = max(0.0, hp - damage)
    target.properties["last_damage"] = damage
    target.properties["last_impact_energy"] = Quantity(impact_energy_j, ENERGY)
    return min(hp, damage)


def _correct_overlap(a, b, normal: Vector3, radius_sum: float) -> None:
    pa, pb = _position(a), _position(b)
    delta = _subtract(pb, pa, M)
    distance = delta.magnitude()
    penetration = radius_sum - distance
    if penetration <= POSITION_SLOP_M:
        return
    inv_a = 0.0 if a.properties.get("anchored", False) else (1.0 / _mass(a) if _mass(a) > 0 else 0.0)
    inv_b = 0.0 if b.properties.get("anchored", False) else (1.0 / _mass(b) if _mass(b) > 0 else 0.0)
    inv_sum = inv_a + inv_b
    if inv_sum <= 0:
        return
    # Resolve the complete overlap in this one-pass solver. A percentage-based
    # correction would require iterative constraint solving; here it can leave
    # perfectly inelastic objects interpenetrating forever when relative speed
    # becomes zero. The supplied contact normal also resolves coincident centers.
    correction_size = (penetration - POSITION_SLOP_M) / inv_sum
    correction = normal.scaled(correction_size, M)
    if inv_a:
        a.properties["pos"] = Vector3(
            pa.x - correction.x * inv_a, pa.y - correction.y * inv_a,
            pa.z - correction.z * inv_a, M,
        )
    if inv_b:
        b.properties["pos"] = Vector3(
            pb.x + correction.x * inv_b, pb.y + correction.y * inv_b,
            pb.z + correction.z * inv_b, M,
        )


def _heat_collision_loss(runtime, a, b, lost_energy_j: float) -> None:
    """Convert collision energy lost from motion into thermal energy on the bodies."""
    if lost_energy_j <= 1e-9:
        return
    mass_a, mass_b = _mass(a), _mass(b)
    total_mass = mass_a + mass_b
    if total_mass <= 0:
        return
    for obj, mass in ((a, mass_a), (b, mass_b)):
        if mass <= 0:
            continue
        share = lost_energy_j * mass / total_mass
        current_temp = obj.properties["temp"].value
        next_temp = current_temp + share / (mass * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K)
        runtime.validate_quantity_property("temp", Quantity(next_temp, K))
        obj.properties["temp"] = Quantity(next_temp, K)
        runtime.update_energy(obj)


def _resolve_mana_projectile_contact(runtime, mana_obj, target, collision_time_s: float) -> None:
    """Transfer a pure-mana projectile's stored energy into a struck body.

    The construct has no material mass. Its finite mana_energy is transferred to
    the target as heat, the same amount is removed from the construct, and the
    existing ledger records an internal transfer rather than creating energy.
    """
    energy_q = mana_obj.properties.get("mana_energy", Quantity(0, ENERGY))
    if not isinstance(energy_q, Quantity) or energy_q.dimension != ENERGY or energy_q.value <= 0:
        mana_obj.properties["active"] = False
        return
    target_mass = target.properties.get("mass")
    target_temp = target.properties.get("temp")
    if not isinstance(target_mass, Quantity) or target_mass.dimension != KG or target_mass.value <= 0:
        mana_obj.properties["active"] = False
        return
    if not isinstance(target_temp, Quantity) or target_temp.dimension != K:
        raise UnitErrorML("mana projectile impact target needs a temperature in K")
    transfer_j = energy_q.value
    target.properties["temp"] = Quantity(
        target_temp.value + transfer_j / (target_mass.value * DEFAULT_SPECIFIC_HEAT_J_PER_KG_K), K
    )
    mana_obj.properties["mana_energy"] = Quantity(0, ENERGY)
    mana_obj.properties["active"] = False
    runtime.update_energy(target)
    runtime.update_total_energy(mana_obj)
    runtime.energy_ledger.append({
        "operation": "mana_projectile_impact",
        "direction": "transfer",
        "source": runtime._object_label(mana_obj),
        "target": runtime._object_label(target),
        "amount_j": transfer_j,
        "source_delta_j": -transfer_j,
        "target_delta_j": transfer_j,
        "delta_j": 0.0,
        "accounting": "pure-mana construct energy transferred internally to impact target",
    })
    runtime._record_step(f"pure-mana projectile transferred {transfer_j:g} J to {runtime._object_label(target)}")
    _notify_collision(runtime, mana_obj, target, transfer_j, 0.0, collision_time_s)


def _resolve_collision(runtime, a, b, normal: Vector3, remaining_seconds: float,
                       contact_a: Vector3, contact_b: Vector3, collision_time_s: float) -> None:
    if a.element == "Mana" and a.properties.get("mana_collision_mode") == "projectile" and b.element != "Mana":
        _resolve_mana_projectile_contact(runtime, a, b, collision_time_s)
        return
    if b.element == "Mana" and b.properties.get("mana_collision_mode") == "projectile" and a.element != "Mana":
        _resolve_mana_projectile_contact(runtime, b, a, collision_time_s)
        return
    mass_a, mass_b = _mass(a), _mass(b)
    anchored_a = bool(a.properties.get("anchored", False))
    anchored_b = bool(b.properties.get("anchored", False))
    inv_a = 0.0 if anchored_a or mass_a <= 0 else 1.0 / mass_a
    inv_b = 0.0 if anchored_b or mass_b <= 0 else 1.0 / mass_b
    inv_sum = inv_a + inv_b
    if inv_sum <= 0:
        return

    vel_a, vel_b = _velocity(a), _velocity(b)
    relative = _subtract(vel_b, vel_a, VELOCITY)
    normal_speed = _dot(relative, normal)
    if normal_speed >= -1e-10:
        return

    old_ke = a.properties["kinetic_energy"].value + b.properties["kinetic_energy"].value
    # The effective collision mass must respect anchoring. An anchored body has
    # zero inverse mass (infinite effective mass for this contact); using the
    # ordinary m1*m2/(m1+m2) formula would incorrectly halve impact energy when
    # a finite-mass object strikes an anchored target with a finite stored mass.
    effective_mass = 1.0 / inv_sum
    impact_energy = 0.5 * effective_mass * normal_speed * normal_speed
    restitution = min(_restitution(a), _restitution(b))
    impulse_size = -(1.0 + restitution) * normal_speed / inv_sum
    impulse = normal.scaled(impulse_size, MOMENTUM)

    next_a = Vector3(
        vel_a.x - impulse.x * inv_a, vel_a.y - impulse.y * inv_a,
        vel_a.z - impulse.z * inv_a, VELOCITY,
    )
    next_b = Vector3(
        vel_b.x + impulse.x * inv_b, vel_b.y + impulse.y * inv_b,
        vel_b.z + impulse.z * inv_b, VELOCITY,
    )
    _set_velocity(runtime, a, next_a)
    _set_velocity(runtime, b, next_b)
    new_ke = a.properties["kinetic_energy"].value + b.properties["kinetic_energy"].value
    lost_energy = max(0.0, old_ke - new_ke)
    _heat_collision_loss(runtime, a, b, lost_energy)

    # Reposition at contact and travel the rest of the step with post-impact velocity.
    for obj, contact in ((a, contact_a), (b, contact_b)):
        if obj.properties.get("anchored", False):
            continue
        velocity = _velocity(obj)
        obj.properties["pos"] = Vector3(
            contact.x + velocity.x * remaining_seconds,
            contact.y + velocity.y * remaining_seconds,
            contact.z + velocity.z * remaining_seconds,
            M,
        )

    _correct_overlap(a, b, normal, _collision_radius(a) + _collision_radius(b))
    _notify_collision(runtime, a, b, impact_energy, lost_energy, collision_time_s)


def _notify_collision(runtime, a, b, impact_energy_j: float, lost_energy_j: float,
                      collision_time_s: float) -> None:
    label_a = runtime._object_label(a)
    label_b = runtime._object_label(b)
    record = {
        "object_a": label_a,
        "object_b": label_b,
        "impact_energy_j": float(impact_energy_j),
        "converted_to_heat_j": float(lost_energy_j),
        "time_s": float(collision_time_s),
    }
    runtime.last_collisions.append(record)
    if len(runtime.last_collisions) > 1000:
        del runtime.last_collisions[:-1000]

    result = runtime._spell_run_stack[-1] if runtime._spell_run_stack else None
    if result is not None:
        for obj in (a, b):
            if all(existing is not obj for existing in result.affected):
                result.affected.append(obj)

    runtime._record_step(
        f"collision: {label_a} ↔ {label_b}; impact energy {impact_energy_j:g} J; "
        f"{lost_energy_j:g} J converted to heat"
    )
    runtime.emit_event("impact", a, b, Quantity(impact_energy_j, ENERGY))
    runtime.emit_event("collision", a, b, Quantity(impact_energy_j, ENERGY))

    # Only target profiles receive HP damage. If both are targets, neither is the striker.
    a_target = a.properties.get("targetable") is not None and a.properties.get("hp") is not None
    b_target = b.properties.get("targetable") is not None and b.properties.get("hp") is not None
    if a_target and not b_target:
        target, striker = a, b
    elif b_target and not a_target:
        target, striker = b, a
    else:
        target = striker = None
    if target is not None:
        damage = _apply_damage(runtime, target, striker, impact_energy_j)
        if damage > 0:
            if result is not None:
                if all(existing is not target for existing in result.hits):
                    result.hits.append(target)
                if all(existing is not target for existing in result.affected):
                    result.affected.append(target)
            runtime._record_step(
                f"hit: {label_a if striker is a else label_b} hit {runtime._object_label(target)}; "
                f"{damage:g} HP damage; HP {target.properties['hp']:g}"
            )
            runtime.emit_event("damaged", target, striker, Quantity(impact_energy_j, ENERGY), damage)


def step_world(runtime, dt: float, gravity: Vector3, *, max_pair_checks: int | None = None) -> None:
    """Advance active objects by one deterministic physics step.

    ``max_pair_checks`` is the portion of this advance_time call's collision
    work budget available to the current substep. It prevents large object
    counts combined with tiny timesteps from locking the interpreter.
    """
    if isinstance(dt, bool) or not isinstance(dt, (int, float)):
        raise PhysicsErrorML("physics timestep must be a finite positive duration")
    try:
        dt = float(dt)
    except (OverflowError, ValueError) as exc:
        raise PhysicsErrorML("physics timestep is outside the supported numeric range") from exc
    if not math.isfinite(dt) or dt <= 0:
        raise PhysicsErrorML("physics timestep must be a finite positive duration")
    if not isinstance(gravity, Vector3) or gravity.dimension != ACCELERATION:
        raise UnitErrorML("2D world gravity must be an acceleration vector in m/s2")
    gravity = require_2d_world_vector(gravity, "world gravity")

    objects = [obj for obj in runtime._collect_physics_objects()
               if obj.properties.get("active", True)]
    collision_radii: dict[int, float] = {}
    collision_objects = []
    for obj in objects:
        if not obj.properties.get("collidable", True):
            continue
        radius = _collision_radius(obj)
        if radius > 0:
            collision_objects.append(obj)
            collision_radii[id(obj)] = radius
    pair_checks = len(collision_objects) * (len(collision_objects) - 1) // 2
    if max_pair_checks is not None and pair_checks > max_pair_checks:
        raise RuntimeErrorML(
            f"physics would check {pair_checks:,} collision pairs in one substep; "
            f"the current budget is {max_pair_checks:,}. Use a larger timestep to reduce step count or reduce the number of collidable objects."
        )
    old_positions: dict[int, Vector3] = {}

    # Integrate free motion with constant acceleration over this small interval.
    for obj in objects:
        mass = _mass(obj)
        position = _position(obj)
        velocity = _velocity(obj)
        acceleration = _acceleration(obj)
        old_positions[id(obj)] = position
        if obj.properties.get("anchored", False):
            continue
        total_acc = _add(acceleration, gravity, ACCELERATION)
        old_energy = runtime.object_energy_j(obj)
        new_velocity = Vector3(
            velocity.x + total_acc.x * dt,
            velocity.y + total_acc.y * dt,
            velocity.z + total_acc.z * dt,
            VELOCITY,
        )
        new_velocity = enforce_speed(new_velocity, massive=mass > 0)
        new_position = Vector3(
            position.x + velocity.x * dt + 0.5 * total_acc.x * dt * dt,
            position.y + velocity.y * dt + 0.5 * total_acc.y * dt * dt,
            position.z + velocity.z * dt + 0.5 * total_acc.z * dt * dt,
            M,
        )
        obj.properties["pos"] = new_position
        obj.properties["vel"] = new_velocity
        obj.properties["force"] = Vector3(
            mass * total_acc.x, mass * total_acc.y, mass * total_acc.z, obj.properties["force"].dimension,
        )
        runtime.update_energy(obj)
        delta = runtime.object_energy_j(obj) - old_energy
        if abs(delta) > 1e-9:
            source = "configured acceleration and world gravity"
            runtime.record_energy_delta("physics integration", obj, delta, source=source)

    # Swept bounding-circle collision detection prevents fast objects from simply
    # jumping over one another during a timestep.
    count = len(collision_objects)
    for i in range(count):
        a = collision_objects[i]
        if not a.properties.get("active", True):
            continue
        for j in range(i + 1, count):
            b = collision_objects[j]
            if not b.properties.get("active", True):
                continue
            ra, rb = collision_radii[id(a)], collision_radii[id(b)]
            radius_sum = ra + rb
            if radius_sum <= 0:
                continue
            start_a, start_b = old_positions[id(a)], old_positions[id(b)]
            end_a, end_b = _position(a), _position(b)
            start_delta = _subtract(start_b, start_a, M)
            displacement_a = _subtract(end_a, start_a, M)
            displacement_b = _subtract(end_b, start_b, M)
            relative_displacement = _subtract(displacement_b, displacement_a, M)
            fraction = _collision_time_fraction(start_delta, relative_displacement, radius_sum)
            if fraction is None:
                continue
            contact_delta = Vector3(
                start_delta.x + relative_displacement.x * fraction,
                start_delta.y + relative_displacement.y * fraction,
                start_delta.z + relative_displacement.z * fraction,
                M,
            )
            distance = contact_delta.magnitude()
            if distance > 1e-12:
                normal = Vector3(contact_delta.x / distance, contact_delta.y / distance,
                                 contact_delta.z / distance, DIMENSIONLESS)
            else:
                relative_velocity = _subtract(_velocity(b), _velocity(a), VELOCITY)
                relative_speed = relative_velocity.magnitude()
                if relative_speed <= 1e-12:
                    continue
                normal = Vector3(-relative_velocity.x / relative_speed, -relative_velocity.y / relative_speed,
                                 -relative_velocity.z / relative_speed, DIMENSIONLESS)

            # Do not repeatedly report stationary overlap. It is only an impact when
            # relative motion is closing along the contact normal.
            relative_velocity = _subtract(_velocity(b), _velocity(a), VELOCITY)
            if _dot(relative_velocity, normal) >= -1e-10:
                continue
            contact_a = Vector3(
                start_a.x + displacement_a.x * fraction,
                start_a.y + displacement_a.y * fraction,
                start_a.z + displacement_a.z * fraction,
                M,
            )
            contact_b = Vector3(
                start_b.x + displacement_b.x * fraction,
                start_b.y + displacement_b.y * fraction,
                start_b.z + displacement_b.z * fraction,
                M,
            )
            collision_time_s = runtime.elapsed_virtual_time + dt * fraction
            _resolve_collision(
                runtime, a, b, normal, dt * (1.0 - fraction), contact_a, contact_b, collision_time_s
            )
