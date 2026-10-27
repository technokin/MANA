"""Metal manipulation and magnetic-field controls for physical MANA objects."""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3, require_2d_world_vector
from ..units import FORCE, M, S, Quantity


def _marked(function):
    function.__mana_runtime_operation__ = True
    return function


def build_library(runtime: Any) -> dict[str, Any]:
    def _position(value: Any, label: str) -> Vector3:
        if hasattr(value, "properties"):
            value = value.properties.get("pos")
        if not isinstance(value, Vector3) or value.dimension != M:
            raise UnitErrorML(f"metals.{label}() center must be a positioned object or Vector3 in metres")
        return require_2d_world_vector(value, f"metals.{label}() center")

    def _finite_quantity(value: Any, dimension: str, label: str, *, positive: bool = True, maximum: float | None = None) -> float:
        if not isinstance(value, Quantity) or value.dimension != dimension:
            raise UnitErrorML(f"metals.{label}() requires a quantity in {dimension}")
        number = float(value.value)
        if not math.isfinite(number) or (number <= 0 if positive else number < 0) or (maximum is not None and number > maximum):
            bound = f" and no more than {maximum:g}" if maximum is not None else ""
            raise PhysicsErrorML(f"metals.{label}() value must be {'greater than 0' if positive else 'non-negative'}{bound}")
        return number

    def _is_metal(obj: Any) -> bool:
        props = obj.properties
        profile = props.get("material_properties", {})
        category = str(profile.get("category", "")).casefold() if isinstance(profile, dict) else ""
        material = str(props.get("material", "")).casefold()
        return bool(props.get("is_metal", False) or props.get("magnetic_response", 0) > 0
                    or "metal" in category or "alloy" in category
                    or material in {"iron", "steel", "stainless steel", "gold", "silver", "copper", "aluminum", "aluminium", "bronze", "brass", "lead", "tin", "titanium", "platinum", "mithril", "adamant"})

    @_marked
    def control(target: Any, direction: Any, strength: Any, *, duration: Any = Quantity(0.4, S)):
        """Apply a bounded one-shot force to a metallic object in a chosen direction."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("metals.control() changes the world; use it inside a spell")
        from ..runtime import MagicObject
        if not isinstance(target, MagicObject):
            raise TypeErrorML("metals.control() target must be a MANA world object")
        if not target.properties.get("active", True):
            raise MagicErrorML("metals.control() cannot control an inactive object")
        if not _is_metal(target):
            raise MagicErrorML("metals.control() requires an object made from a registered metal or alloy")
        if not isinstance(direction, Vector3):
            raise TypeErrorML("metals.control() direction must be a planar direction vector")
        direction = require_2d_world_vector(direction, "metals.control() direction")
        duration_s = _finite_quantity(duration, S, "control", maximum=10.0)
        force_q = strength if isinstance(strength, Quantity) else Quantity(float(strength), FORCE)
        force_n = _finite_quantity(force_q, FORCE, "control", maximum=1_000_000.0)
        old = runtime.object_energy_j(target)
        result = runtime._apply_force(target, Quantity(force_n, FORCE), direction, "metal control", {}, duration_seconds=duration_s)
        runtime._observe("magic.effect", effect="metal_manipulation", mode="directed_force", entity=runtime._visual_entity(target), force_n=force_n, duration_s=duration_s)
        return result

    @_marked
    def field(center: Any, strength: Any, radius: Any, *, polarity: str = "attract", duration: Any = Quantity(3.0, S)):
        """Create a time-bounded magnetic field that acts on magnetically responsive materials."""
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("metals.field() changes world state; use it inside a spell")
        position = _position(center, "field")
        force_n = _finite_quantity(strength if isinstance(strength, Quantity) else Quantity(float(strength), FORCE), FORCE, "field", maximum=1_000_000.0)
        radius_m = _finite_quantity(radius, M, "field", maximum=5000.0)
        duration_s = _finite_quantity(duration, S, "field", maximum=60.0)
        if not isinstance(polarity, str) or polarity.strip().casefold() not in {"attract", "repel"}:
            raise TypeErrorML("metals.field() polarity must be 'attract' or 'repel'")
        if len(runtime.magnetic_fields) >= 64:
            raise PhysicsErrorML("the world can contain at most 64 active magnetic fields; wait for one to expire")
        now = runtime.elapsed_virtual_time
        field_record = {
            "id": runtime._next_magnetic_field_id,
            "center": position,
            "strength_n": force_n,
            "radius_m": radius_m,
            "polarity": polarity.strip().casefold(),
            "started_at": now,
            "until": now + duration_s,
        }
        runtime._next_magnetic_field_id += 1
        runtime.magnetic_fields.append(field_record)
        public = {key: value for key, value in field_record.items() if key != "center"}
        public["center_m"] = [position.x, position.y]
        runtime._observe("world.changed", operation="magnetic_field_created", field=public)
        runtime._observe("magic.effect", effect="magnetic_field", **public)
        return public

    def active_fields() -> list[dict[str, Any]]:
        now = runtime.elapsed_virtual_time
        return [{"id": item["id"], "center_m": [item["center"].x, item["center"].y],
                 "strength_n": item["strength_n"], "radius_m": item["radius_m"],
                 "polarity": item["polarity"], "until": item["until"]}
                for item in runtime.magnetic_fields if item.get("until", 0) > now]

    return {"control": control, "field": field, "active_fields": active_fields}
