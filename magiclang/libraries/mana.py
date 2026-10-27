"""Pure-mana constructs, area effects, and accessible universal object control.

The namespace is installed by the core runtime and may also be imported with
``import mana``. These functions never require an elemental type. The headless
world's caster origin is (0, 0, 0); an omitted effect position defaults to 10 m
along +X from that origin.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3, enforce_speed, kinetic_energy, momentum, require_2d_world_vector
from ..shapes import DEFAULT_ANCHORED_MANA_SHAPES, DEFAULT_COLLIDABLE_MANA_SHAPES, SUPPORTED_SHAPES
from ..units import (
    ACCELERATION, DENSITY, DIMENSIONLESS, ENERGY, FORCE, K, KG, M, M2, M3, POWER, S,
    VELOCITY, Quantity, JOULES_PER_MANA,
)

SPECIFIC_HEAT_J_PER_KG_K = 1000.0
DEFAULT_EFFECT_OFFSET_M = 10.0
DEFAULT_BURST_ENERGY_J = 1000.0
DEFAULT_BURST_RADIUS_M = 1.0
DEFAULT_EMIT_POWER_W = 1000.0
DEFAULT_EMIT_DURATION_S = 1.0
DEFAULT_EMIT_RANGE_M = 10.0
DEFAULT_CONTROL_FORCE_N = 100.0
DEFAULT_CONTROL_DURATION_S = 1.0


def _quantity(runtime: Any, value: Any, dimension: Any, label: str) -> Quantity:
    return runtime.as_quantity(value, dimension, label)


def _nonnegative(value: Quantity, label: str, *, positive: bool = False) -> float:
    if not math.isfinite(value.value) or value.value < 0 or (positive and value.value <= 0):
        requirement = "greater than zero" if positive else "non-negative"
        raise PhysicsErrorML(f"{label} must be finite and {requirement}")
    return float(value.value)


def _origin(runtime: Any, position: Any = None) -> Vector3:
    if position is None:
        caster = getattr(runtime, "caster_position", Vector3(0, 0, 0, M))
        if not isinstance(caster, Vector3) or caster.dimension != M:
            caster = Vector3(0, 0, 0, M)
        result = Vector3(caster.x + DEFAULT_EFFECT_OFFSET_M, caster.y, 0, M)
    elif hasattr(position, "properties"):
        result = position.properties.get("pos")
    else:
        result = position
    if not isinstance(result, Vector3) or result.dimension != M:
        raise UnitErrorML("mana effect position must be a position vector in metres or a positioned object")
    return require_2d_world_vector(result, "mana effect position")


def _direction(value: Any, label: str) -> Vector3:
    if not isinstance(value, Vector3):
        raise TypeErrorML(f"{label} must be a direction vector")
    if value.dimension not in {DIMENSIONLESS, M}:
        raise UnitErrorML(f"{label} must be dimensionless or a displacement vector")
    value = require_2d_world_vector(value, label)
    magnitude = math.hypot(value.x, value.y)
    if magnitude <= 1e-12:
        raise PhysicsErrorML(f"{label} cannot be the zero vector")
    return Vector3(value.x / magnitude, value.y / magnitude, 0, DIMENSIONLESS)


def _object_position(obj: Any) -> Vector3 | None:
    if not hasattr(obj, "properties"):
        return None
    value = obj.properties.get("pos")
    if isinstance(value, Vector3) and value.dimension == M:
        return value
    return None


def _world_objects(runtime: Any) -> list[Any]:
    seen: set[int] = set()
    output = []
    for obj in runtime._collect_physics_objects():
        if id(obj) in seen or not obj.properties.get("active", True):
            continue
        seen.add(id(obj))
        if obj.element == "Mana" or obj.element == "ThermalRelease":
            continue
        if _object_position(obj) is None:
            continue
        mass = obj.properties.get("mass")
        if not isinstance(mass, Quantity) or mass.dimension != KG or mass.value <= 0:
            continue
        if not obj.properties.get("collidable", True):
            continue
        output.append(obj)
    return output


def _record_effect_input(runtime: Any, operation: str, energy_j: float, details: dict[str, Any]) -> None:
    if energy_j <= 0:
        return
    entry = {
        "operation": operation,
        "direction": "input",
        "source": "ambient mana",
        "target": "world",
        "amount_j": energy_j,
        "delta_j": energy_j,
        "accounting": "ambient mana supplied this energy; no stored mana pool",
        **details,
    }
    runtime.energy_input_j += energy_j
    runtime.energy_ledger.append(entry)
    # This is a readout of ambient-mana use, not a stored or spendable pool.
    runtime.record_mana_cost(energy_j / JOULES_PER_MANA, reason=operation)
    if runtime._spell_run_stack:
        runtime._record_step(f"{operation}: {energy_j:g} J from ambient mana")


def _record_transfer(runtime: Any, operation: str, obj: Any, energy_j: float) -> None:
    if energy_j <= 0:
        return
    runtime.energy_ledger.append({
        "operation": operation,
        "direction": "transfer",
        "source": "ambient mana effect",
        "target": runtime._object_label(obj),
        "amount_j": energy_j,
        "delta_j": 0.0,
        "accounting": "included in the ambient-mana input above",
    })
    if runtime._spell_run_stack:
        runtime._record_step(f"{operation} affected {runtime._object_label(obj)} ({energy_j:g} J)")


def _apply_heat_share(runtime: Any, obj: Any, energy_j: float) -> float:
    mass = obj.properties["mass"].value
    if mass <= 0 or energy_j <= 0:
        return 0.0
    old = runtime.object_energy_j(obj)
    temp = obj.properties.get("temp")
    if not isinstance(temp, Quantity) or temp.dimension != K:
        raise UnitErrorML("mana energy transfer needs a target temperature in K")
    next_temp = temp.value + energy_j / (mass * SPECIFIC_HEAT_J_PER_KG_K)
    obj.properties["temp"] = Quantity(next_temp, K)
    runtime.update_energy(obj)
    if obj.properties.get("combustible", False) and not obj.properties.get("burning", False):
        ignition = obj.properties.get("ignition_temp", Quantity(573.15, K))
        if isinstance(ignition, Quantity) and ignition.dimension == K and next_temp >= ignition.value:
            obj.properties["state"] = "burning"
            obj.properties["burning"] = True
            runtime.emit_event("object_ignited", obj, obj.properties.get("material", obj.element))
    return max(0.0, runtime.object_energy_j(obj) - old)


def _apply_burst_share(runtime: Any, obj: Any, energy_j: float, center: Vector3) -> float:
    mass_q = obj.properties["mass"]
    if not isinstance(mass_q, Quantity) or mass_q.dimension != KG or mass_q.value <= 0 or energy_j <= 0:
        return 0.0
    if obj.properties.get("anchored", False):
        return _apply_heat_share(runtime, obj, energy_j)
    position = _object_position(obj)
    velocity = obj.properties.get("vel")
    if position is None or not isinstance(velocity, Vector3) or velocity.dimension != VELOCITY:
        raise UnitErrorML("mana burst recipients need position and velocity vectors")
    dx, dy = position.x - center.x, position.y - center.y
    mag = math.hypot(dx, dy)
    if mag <= 1e-12:
        ux, uy = 1.0, 0.0
    else:
        ux, uy = dx / mag, dy / mag
    speed_along = velocity.x * ux + velocity.y * uy
    old_kinetic = kinetic_energy(mass_q, velocity).value

    # Solve the relativistic kinetic-energy change rather than using a Newtonian
    # delta-v approximation, which can overshoot the energy allocated to this object.
    delta_speed = max(0.0, -speed_along + math.sqrt(
        speed_along * speed_along + 2.0 * energy_j / mass_q.value
    ))

    def candidate_for(delta: float) -> Vector3:
        return Vector3(velocity.x + delta * ux, velocity.y + delta * uy, 0, VELOCITY)

    def gain_for(delta: float) -> float:
        candidate = candidate_for(delta)
        if candidate.magnitude() >= 299_792_458.0:
            return math.inf
        try:
            return kinetic_energy(mass_q, candidate).value - old_kinetic
        except PhysicsErrorML:
            return math.inf

    low, high = 0.0, max(delta_speed, 1e-12)
    for _ in range(100):
        if gain_for(high) >= energy_j:
            break
        high *= 2.0
    else:
        high = max(high, 299_792_458.0)
    for _ in range(100):
        middle = (low + high) / 2.0
        if gain_for(middle) >= energy_j:
            high = middle
        else:
            low = middle
    candidate = candidate_for((low + high) / 2.0)
    new_velocity = enforce_speed(candidate, massive=True)
    old_energy = runtime.object_energy_j(obj)
    obj.properties["vel"] = new_velocity
    obj.properties["kinetic_energy"] = kinetic_energy(mass_q, new_velocity)
    obj.properties["momentum"] = momentum(mass_q, new_velocity)
    runtime.update_total_energy(obj)
    return max(0.0, runtime.object_energy_j(obj) - old_energy)


def _all_energy_recipients(runtime: Any) -> list[Any]:
    return _world_objects(runtime)


def _reject_pure_helper_side_effect(runtime: Any, operation: str) -> None:
    """Prevent a directly called calculation helper from mutating world state."""
    if getattr(runtime, "_pure_call_depth", 0):
        raise MagicErrorML(
            f"{operation}() changes the world and cannot run inside a directly called helper; "
            "execute the containing spell with post() or release()"
        )


def _caster_position(runtime: Any) -> Vector3:
    value = getattr(runtime, "caster_position", None)
    if not isinstance(value, Vector3) or value.dimension != M:
        return Vector3(0, 0, 0, M)
    return require_2d_world_vector(value, "caster position")


def _default_control_destination(runtime: Any, *, fallback_to_caster: bool = False) -> Vector3:
    """Use the active tgset target, or optionally the caster's position."""
    stack = getattr(runtime, "_target_context_stack", None)
    if stack:
        target_position = _object_position(stack[-1])
        if target_position is None:
            raise UnitErrorML("the selected tgset target needs a position for automatic control")
        return target_position
    if fallback_to_caster:
        return _caster_position(runtime)
    raise TypeErrorML("destination is required outside tgset(target):")


def _stop_object(runtime: Any, target: Any) -> Any:
    """Stop an object while conserving its kinetic energy as internal heat."""
    target = runtime.require_object(target, "mana.stop")
    runtime.require_active_object(target, "mana.stop")
    mass = target.properties.get("mass")
    velocity = target.properties.get("vel")
    temp = target.properties.get("temp")
    if not isinstance(mass, Quantity) or mass.dimension != KG or mass.value <= 0:
        raise PhysicsErrorML("mana.stop() needs an object with positive mass")
    if not isinstance(velocity, Vector3) or velocity.dimension != VELOCITY:
        raise UnitErrorML("mana.stop() needs a valid velocity vector")
    if not isinstance(temp, Quantity) or temp.dimension != K:
        raise UnitErrorML("mana.stop() needs an object temperature in K")
    kinetic = kinetic_energy(mass, velocity).value
    target.properties["vel"] = Vector3(0, 0, 0, VELOCITY)
    target.properties["acc"] = Vector3(0, 0, 0, ACCELERATION)
    target.properties["force"] = Vector3(0, 0, 0, FORCE)
    target.properties["kinetic_energy"] = Quantity(0, ENERGY)
    target.properties["momentum"] = momentum(mass, target.properties["vel"])
    if kinetic > 0:
        target.properties["temp"] = Quantity(temp.value + kinetic / (mass.value * SPECIFIC_HEAT_J_PER_KG_K), K)
    runtime.update_energy(target)
    runtime.energy_ledger.append({
        "operation": "mana.stop",
        "direction": "internal_transfer",
        "source": runtime._object_label(target),
        "target": runtime._object_label(target),
        "amount_j": kinetic,
        "delta_j": 0.0,
        "accounting": "kinetic energy converted to thermal energy; total object energy conserved",
    })
    return target


def build_library(runtime: Any) -> dict[str, Any]:
    """Return the namespace exports for the core ``mana`` toolkit."""

    def form(shape: str = "sphere", energy: Quantity = Quantity(DEFAULT_BURST_ENERGY_J, ENERGY),
             radius: Quantity = Quantity(DEFAULT_BURST_RADIUS_M, M), collidable: bool | None = None,
             anchored: bool | None = None, position: Any = None, name: str | None = None):
        """Form a pure-mana construct; optional position defaults 10 m ahead of the caster."""
        _reject_pure_helper_side_effect(runtime, "mana.form")
        if not isinstance(shape, str) or not shape.strip():
            raise TypeErrorML("mana.form() shape must be non-empty text")
        normal_shape = shape.casefold()
        if normal_shape not in SUPPORTED_SHAPES:
            raise MagicErrorML(f"unsupported mana construct shape '{shape}'; choose a shape from the MANA shape catalogue")
        energy_q = _quantity(runtime, energy, ENERGY, "mana.form() energy")
        energy_j = _nonnegative(energy_q, "mana.form() energy")
        radius_q = _quantity(runtime, radius, M, "mana.form() radius")
        radius_m = _nonnegative(radius_q, "mana.form() radius", positive=True)
        if collidable is not None and not isinstance(collidable, bool):
            raise TypeErrorML("mana.form() collidable must be true or false")
        if anchored is not None and not isinstance(anchored, bool):
            raise TypeErrorML("mana.form() anchored must be true or false")
        center = _origin(runtime, position)
        is_barrier = normal_shape in {"barrier", "wall", "shield", "disc"}
        is_collidable = collidable if collidable is not None else normal_shape in DEFAULT_COLLIDABLE_MANA_SHAPES
        is_anchored = (normal_shape in DEFAULT_ANCHORED_MANA_SHAPES if anchored is None else anchored)
        from ..runtime import MagicObject
        obj = runtime.require_object(MagicObject("Mana"), "mana.form")
        obj.properties.update({
            "display_name": name.strip() if isinstance(name, str) else f"mana_{shape.casefold()}",
            "object_kind": "mana_construct",
            "kind": normal_shape,
            "material": "PureMana",
            "shape": normal_shape,
            "mana_collision_mode": "barrier" if is_barrier else "projectile",
            "pos": center,
            "mass": Quantity(0, KG),
            "volume": Quantity(0, M3),
            "area": Quantity(math.pi * radius_m * radius_m, M2),
            "density": Quantity(0, DENSITY),
            "collision_radius": radius_q,
            "mana_energy": energy_q,
            "collidable": is_collidable,
            "anchored": is_anchored,
            "anchor_pos": center,
            "state": "field",
        })
        runtime.update_total_energy(obj)
        runtime._record_created(obj, reason="pure-mana construct")
        _record_effect_input(runtime, "mana.form", energy_j, {
            "construct": obj.properties["display_name"], "position_m": [center.x, center.y],
            "radius_m": radius_m,
        })
        runtime._observe("magic.effect", effect="construct_formed", entity=runtime._visual_entity(obj),
                         position=[center.x, center.y], shape=normal_shape)
        runtime.emit_event("mana_formed", obj, energy_q, center)
        return obj

    def burst(energy: Quantity = Quantity(DEFAULT_BURST_ENERGY_J, ENERGY),
              radius: Quantity = Quantity(DEFAULT_BURST_RADIUS_M, M), position: Any = None):
        """Release a radial pure-mana pulse; defaults to 1000 J, 1 m radius, 10 m ahead."""
        _reject_pure_helper_side_effect(runtime, "mana.burst")
        energy_q = _quantity(runtime, energy, ENERGY, "mana.burst() energy")
        energy_j = _nonnegative(energy_q, "mana.burst() energy")
        radius_q = _quantity(runtime, radius, M, "mana.burst() radius")
        radius_m = _nonnegative(radius_q, "mana.burst() radius", positive=True)
        center = _origin(runtime, position)
        recipients = []
        for obj in _all_energy_recipients(runtime):
            pos = _object_position(obj)
            distance = math.hypot(pos.x - center.x, pos.y - center.y)
            if distance <= radius_m:
                recipients.append(obj)
        share = energy_j / len(recipients) if recipients else 0.0
        delivered = 0.0
        for obj in recipients:
            actual = _apply_burst_share(runtime, obj, share, center)
            delivered += actual
            _record_transfer(runtime, "mana.burst_transfer", obj, actual)
        _record_effect_input(runtime, "mana.burst", energy_j, {
            "position_m": [center.x, center.y], "radius_m": radius_m,
            "recipient_count": len(recipients), "delivered_j": delivered,
            "unabsorbed_j": max(0.0, energy_j - delivered),
        })
        runtime._observe("magic.effect", effect="burst", position=[center.x, center.y], radius_m=radius_m,
                         recipients=len(recipients))
        runtime.emit_event("mana_burst", center, energy_q, radius_q)
        return {
            "effect": "burst", "energy_j": energy_j, "radius_m": radius_m,
            "position_m": [center.x, center.y], "affected": len(recipients),
            "delivered_j": delivered, "unabsorbed_j": max(0.0, energy_j - delivered),
        }

    def emit(power: Quantity = Quantity(DEFAULT_EMIT_POWER_W, POWER),
             duration: Quantity = Quantity(DEFAULT_EMIT_DURATION_S, S), direction: Any = None,
             range: Quantity = Quantity(DEFAULT_EMIT_RANGE_M, M),
             beam_radius: Quantity = Quantity(DEFAULT_BURST_RADIUS_M, M), position: Any = None):
        """Emit a pure-mana ray; defaults are 1000 W, 1 s, 10 m range and 1 m radius."""
        _reject_pure_helper_side_effect(runtime, "mana.emit")
        power_q = _quantity(runtime, power, POWER, "mana.emit() power")
        power_w = _nonnegative(power_q, "mana.emit() power")
        duration_q = _quantity(runtime, duration, S, "mana.emit() duration")
        duration_s = _nonnegative(duration_q, "mana.emit() duration")
        range_q = _quantity(runtime, range, M, "mana.emit() range")
        range_m = _nonnegative(range_q, "mana.emit() range", positive=True)
        beam_q = _quantity(runtime, beam_radius, M, "mana.emit() beam_radius")
        beam_m = _nonnegative(beam_q, "mana.emit() beam_radius", positive=True)
        start = _origin(runtime, position)
        if direction is None and getattr(runtime, "_target_context_stack", None):
            target_pos = _object_position(runtime._target_context_stack[-1])
            if target_pos is not None:
                delta = Vector3(target_pos.x - start.x, target_pos.y - start.y, 0, M)
                direction_unit = _direction(delta, "mana.emit() automatic direction") if math.hypot(delta.x, delta.y) > 1e-12 else Vector3(1, 0, 0, DIMENSIONLESS)
            else:
                direction_unit = Vector3(1, 0, 0, DIMENSIONLESS)
        elif direction is None:
            direction_unit = Vector3(1, 0, 0, DIMENSIONLESS)
        else:
            direction_unit = _direction(direction, "mana.emit() direction")
        total_energy = power_w * duration_s
        if not math.isfinite(total_energy):
            raise PhysicsErrorML("mana.emit() energy (power × duration) must be finite")
        recipients = []
        for obj in _all_energy_recipients(runtime):
            pos = _object_position(obj)
            dx, dy = pos.x - start.x, pos.y - start.y
            projection = dx * direction_unit.x + dy * direction_unit.y
            if projection < 0 or projection > range_m:
                continue
            perpendicular = abs(dx * direction_unit.y - dy * direction_unit.x)
            collision_q = obj.properties.get("collision_radius", Quantity(0, M))
            collision_radius = collision_q.value if isinstance(collision_q, Quantity) and collision_q.dimension == M else 0.0
            if collision_radius <= 0:
                area_q = obj.properties.get("area", Quantity(0, M2))
                if isinstance(area_q, Quantity) and area_q.dimension == M2 and area_q.value > 0:
                    collision_radius = math.sqrt(area_q.value / math.pi)
            if perpendicular <= beam_m + collision_radius:
                recipients.append(obj)
        share = total_energy / len(recipients) if recipients else 0.0
        delivered = 0.0
        for obj in recipients:
            actual = _apply_heat_share(runtime, obj, share)
            delivered += actual
            _record_transfer(runtime, "mana.emit_transfer", obj, actual)
        _record_effect_input(runtime, "mana.emit", total_energy, {
            "position_m": [start.x, start.y], "direction": [direction_unit.x, direction_unit.y],
            "power_w": power_w, "duration_s": duration_s, "range_m": range_m,
            "beam_radius_m": beam_m, "recipient_count": len(recipients),
            "delivered_j": delivered, "unabsorbed_j": max(0.0, total_energy - delivered),
        })
        runtime._observe("magic.effect", effect="beam", position=[start.x, start.y],
                         direction=[direction_unit.x, direction_unit.y], range_m=range_m,
                         radius_m=beam_m)
        runtime.emit_event("mana_emitted", start, direction_unit, power_q, duration_q)
        return {
            "effect": "emit", "power_w": power_w, "duration_s": duration_s,
            "energy_j": total_energy, "range_m": range_m,
            "position_m": [start.x, start.y], "affected": len(recipients),
            "delivered_j": delivered, "unabsorbed_j": max(0.0, total_energy - delivered),
        }

    def control(target: Any, action: str, strength: Quantity = Quantity(DEFAULT_CONTROL_FORCE_N, FORCE),
                duration: Quantity = Quantity(DEFAULT_CONTROL_DURATION_S, S), destination: Any = None):
        """Apply element-independent control to an existing object.

        Actions are toward, away, lift, hold, stop and release. In a tgset block,
        toward/away default to the selected target; outside one they require a
        destination. hold anchors at the current position unless a position is given.
        """
        _reject_pure_helper_side_effect(runtime, "mana.control")
        target = runtime.require_object(target, "mana.control")
        runtime.require_active_object(target, "mana.control")
        if not isinstance(action, str):
            raise TypeErrorML("mana.control() action must be text")
        action = action.strip().casefold()
        if action not in {"toward", "away", "lift", "hold", "stop", "release"}:
            raise MagicErrorML("mana.control() action must be toward, away, lift, hold, stop, or release")
        if action == "release":
            return runtime.op_unanchor(target)
        if action == "hold":
            position = _object_position(target) if destination is None else _position_arg(destination, "mana.control() destination")
            _stop_object(runtime, target)
            target.properties["pos"] = position
            return runtime.op_anchor(target, position)
        if action == "stop":
            return _stop_object(runtime, target)
        if action in {"toward", "away"}:
            if destination is None:
                destination = _default_control_destination(runtime)
            dest = _position_arg(destination, "mana.control() destination")
            current = _object_position(target)
            if current is None:
                raise UnitErrorML("mana.control() target needs a position in metres")
            dx, dy = dest.x - current.x, dest.y - current.y
            if action == "away":
                dx, dy = -dx, -dy
            direction_unit = _direction(Vector3(dx, dy, 0, M), f"mana.control({action}) direction")
        else:  # lift
            direction_unit = Vector3(0, 1, 0, DIMENSIONLESS)
        force_q = _quantity(runtime, strength, FORCE, "mana.control() strength")
        _nonnegative(force_q, "mana.control() strength")
        duration_q = _quantity(runtime, duration, S, "mana.control() duration")
        duration_s = _nonnegative(duration_q, "mana.control() duration")
        return runtime._apply_force(target, force_q, direction_unit, f"mana.control {action}", {}, duration_seconds=duration_s)

    def toward(target: Any, destination: Any = None, strength: Quantity = Quantity(DEFAULT_CONTROL_FORCE_N, FORCE),
               duration: Quantity = Quantity(DEFAULT_CONTROL_DURATION_S, S)):
        """Apply universal control toward a position; in tgset it defaults to that target."""
        return control(target, "toward", strength, duration, destination)

    def away(target: Any, source: Any = None, strength: Quantity = Quantity(DEFAULT_CONTROL_FORCE_N, FORCE),
             duration: Quantity = Quantity(DEFAULT_CONTROL_DURATION_S, S)):
        """Apply universal control away from a source; in tgset it defaults to that target."""
        return control(target, "away", strength, duration, source)

    def lift(target: Any, strength: Quantity = Quantity(DEFAULT_CONTROL_FORCE_N, FORCE),
             duration: Quantity = Quantity(DEFAULT_CONTROL_DURATION_S, S)):
        """Apply an upward universal-control impulse; defaults to 100 N for one second."""
        return control(target, "lift", strength, duration)

    def hold(target: Any, position: Any = None):
        """Stop and anchor an object at its current position or an optional position."""
        return control(target, "hold", destination=position)

    def levitate(target: Any, position: Any = None):
        """Hold an object at a fixed position independently of its elemental type."""
        return control(target, "hold", destination=position)

    def stop(target: Any):
        """Stop motion while converting kinetic energy to heat on the same object."""
        return control(target, "stop")

    def release_control(target: Any):
        """Release an object from a mana hold without deleting its energy."""
        return control(target, "release")

    def collect(targets: Any, destination: Any = None, strength: Quantity = Quantity(DEFAULT_CONTROL_FORCE_N, FORCE),
                duration: Quantity = Quantity(DEFAULT_CONTROL_DURATION_S, S)):
        """Move one object or a list of objects toward a destination.

        Destination defaults to the active tgset target, or the caster's position
        when no target block is active.
        """
        _reject_pure_helper_side_effect(runtime, "mana.collect")
        items = targets if isinstance(targets, list) else [targets]
        if not items:
            return []
        resolved_destination = _default_control_destination(runtime, fallback_to_caster=True) if destination is None else destination
        destination_pos = _position_arg(resolved_destination, "mana.collect() destination")
        results = []
        for item in items:
            position = _object_position(runtime.require_object(item, "mana.collect"))
            if position is None:
                raise UnitErrorML("mana.collect() items need positions in metres")
            if math.hypot(position.x - destination_pos.x, position.y - destination_pos.y) <= 1e-12:
                # Already collected: leave it untouched rather than failing on a
                # zero direction while processing the rest of the collection.
                results.append(item)
                continue
            results.append(toward(item, destination_pos, strength, duration))
        return results

    return {
        "form": form,
        "burst": burst,
        "emit": emit,
        "control": control,
        "toward": toward,
        "away": away,
        "lift": lift,
        "hold": hold,
        "levitate": levitate,
        "stop": stop,
        "release_control": release_control,
        "collect": collect,
    }


def _position_arg(value: Any, label: str) -> Vector3:
    if hasattr(value, "properties"):
        value = value.properties.get("pos")
    if not isinstance(value, Vector3) or value.dimension != M:
        raise UnitErrorML(f"{label} must be a position vector in metres or a positioned object")
    return require_2d_world_vector(value, label)
