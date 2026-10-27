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
# Spatial broad-phase limits. The narrow phase remains the swept-circle solver;
# these caps prevent a single giant/fast object from expanding into millions of
# grid cells before the collision-work budget can be enforced.
MAX_BROADPHASE_CELLS_PER_OBJECT = 2048
MAX_BROADPHASE_CELL_MEMBERSHIPS = 2_000_000


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


def _restitution(obj, runtime=None) -> float:
    world_default = (getattr(runtime, "world_settings", {}).get("default_restitution", DEFAULT_RESTITUTION)
                     if runtime is not None else DEFAULT_RESTITUTION)
    value = obj.properties.get("restitution")
    if value is None:
        value = world_default
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


def _friction(obj, runtime=None) -> float:
    """Return validated per-object Coulomb friction or the world default."""
    world_default = (getattr(runtime, "world_settings", {}).get("friction_coefficient", 0.35)
                     if runtime is not None else 0.35)
    value = obj.properties.get("friction")
    if value is None:
        value = world_default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeErrorML("friction must be a finite number between 0 and 2")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 2.0:
        raise PhysicsErrorML("friction must be between 0 and 2")
    return value


def _collision_time_fraction(start_delta: Vector3, relative_displacement: Vector3, radius: float) -> float | None:
    """Earliest swept-circle contact fraction in the x-y plane, if any.

    Normalize all lengths before evaluating the quadratic. Squaring otherwise
    overflows for large-but-finite coordinates and can silently turn a valid
    collision into a NaN comparison that reports no contact.
    """
    if isinstance(radius, bool) or not isinstance(radius, (int, float)):
        raise PhysicsErrorML("collision radius must be finite and non-negative")
    radius = float(radius)
    if not math.isfinite(radius) or radius < 0:
        raise PhysicsErrorML("collision radius must be finite and non-negative")
    scale = max(
        abs(start_delta.x), abs(start_delta.y),
        abs(relative_displacement.x), abs(relative_displacement.y), radius,
    )
    if scale <= 0:
        return 0.0
    sx, sy = start_delta.x / scale, start_delta.y / scale
    dx, dy = relative_displacement.x / scale, relative_displacement.y / scale
    normalized_radius = radius / scale
    c = sx * sx + sy * sy - normalized_radius * normalized_radius
    if c <= 0:
        return 0.0
    a = dx * dx + dy * dy
    if a <= 1e-30:
        return None
    b = 2.0 * (sx * dx + sy * dy)
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


def _effective_armour(target) -> tuple[float, list]:
    """Return abstract damage mitigation and the participating gear.

    The engine is 2D and has no directional hitbox anatomy, so torso is the
    default impact region. A shield contributes partial cover; location-specific
    gear contributes when a MANA spell/script marks the hit region.
    """
    props = target.properties
    region = str(props.get("last_hit_region", "torso")).casefold()
    slot_weights = {
        "torso": {"body_armour": 1.0, "shield": 0.45},
        "head": {"head": 1.0, "body_armour": 0.25, "shield": 0.25},
        "hands": {"hands": 1.0, "body_armour": 0.1},
        "legs": {"legs": 1.0, "body_armour": 0.2},
    }
    weights = slot_weights.get(region, slot_weights["torso"])
    gear_used = []
    mitigation = 0.0
    for gear in props.get("equipment", []):
        gp = getattr(gear, "properties", None)
        if not isinstance(gp, dict) or not gp.get("active", True):
            continue
        slot = gp.get("equipment_slot")
        weight = weights.get(slot, 0.0)
        rating = gp.get("armour_rating", 0.0)
        durability = gp.get("durability", 1.0)
        maximum = gp.get("max_durability", durability)
        if weight <= 0 or not isinstance(rating, (int, float)) or not isinstance(durability, (int, float)) or durability <= 0:
            continue
        ratio = 1.0 if not isinstance(maximum, (int, float)) or maximum <= 0 else min(1.0, durability / maximum)
        effective = max(0.0, float(rating)) * weight * ratio
        if effective > 0:
            mitigation += effective
            gear_used.append((gear, effective))
    return mitigation, gear_used


def _apply_damage(runtime, target, striker, impact_energy_j: float) -> float:
    """Apply impact damage using material, weapon, body, and armour properties."""
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
    physical_resistance = target.properties.get("resist_physical", 0.0)
    if isinstance(physical_resistance, bool) or not isinstance(physical_resistance, (int, float)):
        physical_resistance = 0.0
    physical_resistance = min(1.0, max(0.0, float(physical_resistance)))
    defence = target.properties.get("defence", 0.0)
    if isinstance(defence, bool) or not isinstance(defence, (int, float)):
        defence = 0.0
    striker_props = getattr(striker, "properties", {})
    weapon_multiplier = striker_props.get("damage_multiplier", 1.0)
    if isinstance(weapon_multiplier, bool) or not isinstance(weapon_multiplier, (int, float)):
        weapon_multiplier = 1.0
    weapon_multiplier = min(10.0, max(0.1, float(weapon_multiplier)))
    strength = striker_props.get("strength_multiplier", 1.0)
    if isinstance(strength, bool) or not isinstance(strength, (int, float)):
        strength = 1.0
    strength = min(10.0, max(0.1, float(strength)))
    body_reduction = target.properties.get("body_damage_reduction", 0.0)
    if isinstance(body_reduction, bool) or not isinstance(body_reduction, (int, float)):
        body_reduction = 0.0
    body_reduction = min(0.9, max(0.0, float(body_reduction)))
    armour_rating, armour_used = _effective_armour(target)
    payload = str(striker_props.get("payload", "none")).casefold() if striker_props.get("item_kind") == "projectile" else "none"
    payload_multiplier = 1.4 if payload == "burst" else 1.0
    raw_damage = (impact_energy_j / JOULES_PER_HIT_POINT) * weapon_multiplier * strength * payload_multiplier
    raw_damage *= (1.0 - resistance) * (1.0 - physical_resistance) * (1.0 - body_reduction)
    damage = max(0.0, raw_damage - max(0.0, float(defence)) - armour_rating)
    if damage <= 0:
        return 0.0
    if hp - damage <= 0 and not target.properties.get("body_model_initialized") and (
        target.properties.get("living") or target.properties.get("is_being") or target.properties.get("is_summoned")
        or target.properties.get("targetable")
    ):
        from .libraries.physiology import _initialize as initialize_body
        initialize_body(target)
    target.properties["hp"] = max(0.0, hp - damage)
    target.properties["last_damage"] = min(hp, damage)
    target.properties["last_impact_energy"] = Quantity(impact_energy_j, ENERGY)
    if target.properties["hp"] <= 0 and target.properties.get("body_model_initialized"):
        from .libraries.physiology import _die as mark_body_dead
        mark_body_dead(runtime, target, "physical_impact")
    target.properties["last_damage_source"] = striker_props.get("display_name", getattr(striker, "element", "unknown"))
    # Worn protection absorbs wear when it actually mitigates an impact. The
    # model is intentionally coarse and deterministic; it is not metallurgy.
    wear = min(0.15, impact_energy_j / 5_000_000.0)
    if armour_used and wear > 0:
        gear, _rating = max(armour_used, key=lambda pair: pair[1])
        gp = gear.properties
        gp["durability"] = max(0.0, float(gp.get("durability", 0.0)) - max(0.05, wear * float(gp.get("max_durability", 1.0))))
        if gp["durability"] <= 0:
            runtime._observe("equipment.changed", operation="broken", item=runtime._visual_entity(gear), wearer=runtime._visual_entity(target))
    return min(hp, damage)


def _apply_projectile_payload(runtime, target, striker, impact_energy_j: float) -> None:
    """Resolve small, explicit single-target payload behaviours on real contact."""
    props = getattr(striker, "properties", {})
    if props.get("item_kind") != "projectile":
        return
    payload = str(props.get("payload", "none")).casefold()
    now = float(getattr(runtime, "elapsed_virtual_time", 0.0))
    tp = target.properties
    label = tp.get("display_name", target.element)
    if payload in {"binding", "net", "anchor"}:
        duration = 5.0 if payload == "anchor" else (4.0 if payload == "net" else 2.5)
        if not isinstance(tp.get("temporary_anchor_restore"), dict):
            tp["temporary_anchor_restore"] = {"anchored": bool(tp.get("anchored", False)), "until": now + duration, "source": payload}
        else:
            tp["temporary_anchor_restore"]["until"] = max(float(tp["temporary_anchor_restore"].get("until", now)), now + duration)
            tp["temporary_anchor_restore"]["source"] = payload
        tp["anchored"] = True
        tp["bound_until"] = now + duration
        tp["bound"] = True
    elif payload == "shock":
        velocity = tp.get("vel")
        if isinstance(velocity, Vector3) and velocity.dimension == VELOCITY:
            slowed = Vector3(velocity.x * 0.5, velocity.y * 0.5, 0.0, VELOCITY)
            _set_velocity(runtime, target, slowed)
        tp["shocked_until"] = now + 2.0
        tp["shocked"] = True
    elif payload == "smoke":
        tp["obscured_until"] = now + 4.0
        tp["obscured"] = True
        pos = tp.get("pos")
        if isinstance(pos, Vector3):
            runtime._observe("world.effect", effect="smoke", center_m=[pos.x, pos.y], radius_m=4.0, duration_s=4.0, target=runtime._visual_entity(target))
    elif payload == "flare":
        tp["illuminated_until"] = now + 5.0
        tp["illuminated"] = True
        pos = tp.get("pos")
        if isinstance(pos, Vector3):
            runtime._observe("world.effect", effect="flare", center_m=[pos.x, pos.y], radius_m=8.0, duration_s=5.0, target=runtime._visual_entity(target))
    elif payload == "acid":
        gear = [g for g in tp.get("equipment", []) if isinstance(getattr(g, "properties", None), dict) and g.properties.get("armour_rating", 0) > 0]
        for item in gear:
            ip = item.properties
            if isinstance(ip.get("durability"), (int, float)):
                ip["durability"] = max(0.0, float(ip["durability"]) - max(1.0, float(ip.get("max_durability", 1.0)) * 0.2))
        tp["corroded_until"] = now + 5.0
        tp["corroded"] = True
    if payload != "none":
        runtime._observe("magic.effect", effect="projectile_payload", payload=payload, entity=runtime._visual_entity(target), source=runtime._visual_entity(striker), impact_energy_j=float(impact_energy_j))
        runtime._record_step(f"projectile payload {payload}: {label}")


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


def _resolve_mana_projectile_contact(runtime, mana_obj, target, collision_time_s: float,
                                     contact_point: Vector3) -> None:
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
    _notify_collision(runtime, mana_obj, target, transfer_j, 0.0, collision_time_s, contact_point)


def _resolve_collision(runtime, a, b, normal: Vector3, remaining_seconds: float,
                       contact_a: Vector3, contact_b: Vector3, collision_time_s: float) -> None:
    contact_point = Vector3(
        (contact_a.x + contact_b.x) / 2,
        (contact_a.y + contact_b.y) / 2,
        0,
        M,
    )
    if a.element == "Mana" and a.properties.get("mana_collision_mode") == "projectile" and b.element != "Mana":
        _resolve_mana_projectile_contact(runtime, a, b, collision_time_s, contact_point)
        return
    if b.element == "Mana" and b.properties.get("mana_collision_mode") == "projectile" and a.element != "Mana":
        _resolve_mana_projectile_contact(runtime, b, a, collision_time_s, contact_point)
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
    restitution = min(_restitution(a, runtime), _restitution(b, runtime))
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

    # Apply Coulomb-style tangential friction after the normal restitution impulse.
    # This removes sliding velocity up to mu * normal impulse without inventing a
    # rotation/spin solver; any lost kinetic energy is subsequently accounted as heat.
    relative_after = _subtract(next_b, next_a, VELOCITY)
    tangent_speed_signed = _dot(relative_after, normal)
    tangent = Vector3(
        relative_after.x - tangent_speed_signed * normal.x,
        relative_after.y - tangent_speed_signed * normal.y,
        relative_after.z - tangent_speed_signed * normal.z, VELOCITY,
    )
    tangent_speed = tangent.magnitude()
    if tangent_speed > 1e-10:
        friction_mu = math.sqrt(_friction(a, runtime) * _friction(b, runtime))
        desired_tangent_impulse = tangent_speed / inv_sum
        tangent_impulse_size = min(desired_tangent_impulse, friction_mu * impulse_size)
        tangent_impulse = tangent.scaled(-tangent_impulse_size / tangent_speed, MOMENTUM)
        next_a = Vector3(
            next_a.x - tangent_impulse.x * inv_a, next_a.y - tangent_impulse.y * inv_a,
            next_a.z - tangent_impulse.z * inv_a, VELOCITY,
        )
        next_b = Vector3(
            next_b.x + tangent_impulse.x * inv_b, next_b.y + tangent_impulse.y * inv_b,
            next_b.z + tangent_impulse.z * inv_b, VELOCITY,
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
    _notify_collision(runtime, a, b, impact_energy, lost_energy, collision_time_s, contact_point)


def _notify_collision(runtime, a, b, impact_energy_j: float, lost_energy_j: float,
                      collision_time_s: float, contact_point: Vector3) -> None:
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
    runtime._observe(
        "contact.begin",
        entities=[runtime._visual_entity(a), runtime._visual_entity(b)],
        names=[label_a, label_b],
        position=[float(contact_point.x), float(contact_point.y)],
        distance_m=0.0,
        impact_kind="mana" if a.element == "Mana" or b.element == "Mana" else "physical",
    )
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
        _apply_projectile_payload(runtime, target, striker, impact_energy_j)
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


def _bounds_overlap(a: tuple[float, float, float, float],
                   b: tuple[float, float, float, float]) -> bool:
    """Whether two x-y AABBs overlap (bounds are min_x, max_x, min_y, max_y)."""
    return a[0] <= b[1] and b[0] <= a[1] and a[2] <= b[3] and b[2] <= a[3]


def _swept_bounds(obj, radius: float, old_position: Vector3) -> tuple[float, float, float, float]:
    """Conservative AABB for the object's swept circular collider this step."""
    end = _position(obj)
    bounds = (
        min(old_position.x, end.x) - radius,
        max(old_position.x, end.x) + radius,
        min(old_position.y, end.y) - radius,
        max(old_position.y, end.y) + radius,
    )
    if not all(math.isfinite(value) for value in bounds):
        raise PhysicsErrorML("world collider swept bounds exceed the supported numeric range")
    return bounds


def _candidate_collision_pairs(collision_objects, collision_radii, old_positions,
                               max_pair_checks: int | None) -> list[tuple[int, int]]:
    """Find overlapping swept AABBs using a spatial hash, preserving stable order.

    The old implementation ran a narrow-phase collision calculation for every
    possible pair, even when thousands of entities occupied unrelated regions.
    This broad phase indexes swept bounds into grid cells. Fast projectiles are
    indexed along their whole path, so broad-phase optimisation does not re-enable
    tunnelling. Very large swept bounds use a bounded fallback against the scene.
    """
    count = len(collision_objects)
    if count < 2:
        return []

    radii = sorted(collision_radii[id(obj)] for obj in collision_objects)
    typical_diameter = max(0.05, radii[len(radii) // 2] * 2.0)
    cell_size = max(0.05, min(8.0, typical_diameter * 2.0))
    bounds = [
        _swept_bounds(obj, collision_radii[id(obj)], old_positions[id(obj)])
        for obj in collision_objects
    ]
    cells: dict[tuple[int, int], list[int]] = {}
    large_indices: list[int] = []
    membership_count = 0

    for index, box in enumerate(bounds):
        x0, x1 = math.floor(box[0] / cell_size), math.floor(box[1] / cell_size)
        y0, y1 = math.floor(box[2] / cell_size), math.floor(box[3] / cell_size)
        memberships = (x1 - x0 + 1) * (y1 - y0 + 1)
        if memberships > MAX_BROADPHASE_CELLS_PER_OBJECT:
            large_indices.append(index)
            continue
        membership_count += memberships
        if membership_count > MAX_BROADPHASE_CELL_MEMBERSHIPS:
            raise RuntimeErrorML(
                "physics broad-phase index exceeded its cell-membership safety limit; "
                "reduce the number of very large or fast-moving colliders"
            )
        for cx in range(x0, x1 + 1):
            for cy in range(y0, y1 + 1):
                cells.setdefault((cx, cy), []).append(index)

    candidates: set[tuple[int, int]] = set()
    visited: set[tuple[int, int]] = set()
    # Broad-phase false positives are filtered by swept-AABB overlap. Bound the
    # number of unique co-cell pairs too, so a pathological dense bucket cannot
    # allocate an unbounded visited set while doing no useful collision work.
    visit_limit = None if max_pair_checks is None else max(10_000, max_pair_checks * 8 + 1)

    def consider(i: int, j: int) -> None:
        if i == j:
            return
        if i > j:
            i, j = j, i
        pair = (i, j)
        if pair in visited:
            return
        visited.add(pair)
        if visit_limit is not None and len(visited) > visit_limit:
            raise RuntimeErrorML(
                "physics broad-phase exceeded its candidate-work safety limit; "
                "reduce the number of densely packed colliders"
            )
        if _bounds_overlap(bounds[i], bounds[j]):
            candidates.add(pair)
            if max_pair_checks is not None and len(candidates) > max_pair_checks:
                raise RuntimeErrorML(
                    f"physics would check more than {max_pair_checks:,} collision pairs in one substep; "
                    "the current budget is exhausted. Reduce colliders or split the scene."
                )

    for bucket in cells.values():
        if len(bucket) < 2:
            continue
        # Local sweep-and-prune prevents a crowded cell from comparing objects
        # whose swept x intervals do not overlap.
        bucket.sort(key=lambda i: (bounds[i][0], bounds[i][1], i))
        active: list[int] = []
        for index in bucket:
            min_x = bounds[index][0]
            active = [other for other in active if bounds[other][1] >= min_x]
            for other in active:
                if bounds[other][2] <= bounds[index][3] and bounds[index][2] <= bounds[other][3]:
                    consider(other, index)
            active.append(index)

    # A very large collider/path is deliberately not expanded into an enormous
    # number of grid cells. Compare its swept bounds against the other objects.
    if large_indices:
        large_set = set(large_indices)
        for index in large_indices:
            for other in range(count):
                if other == index or (other in large_set and other < index):
                    continue
                consider(index, other)

    return sorted(candidates)


def step_world(runtime, dt: float, gravity: Vector3, *, max_pair_checks: int | None = None,
               objects: list | None = None) -> None:
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

    objects = [obj for obj in (runtime._collect_physics_objects() if objects is None else objects)
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

    # Broad-phase swept bounds cut sparse-world work from all-pairs O(n²) to
    # near-linear indexing plus actual local candidate pairs. The narrow phase
    # below still uses swept circles, preserving high-speed contact detection.
    candidate_pairs = _candidate_collision_pairs(
        collision_objects, collision_radii, old_positions, max_pair_checks
    )
    for i, j in candidate_pairs:
        a = collision_objects[i]
        b = collision_objects[j]
        if not a.properties.get("active", True) or not b.properties.get("active", True):
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
