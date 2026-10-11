"""Reanimation of existing remains using the Necro mana channel.

Creating a summoned undead is an ordinary MANA spell written by the user;
this library does not provide a special summon/construct-animation shortcut.
The Underworld transfer for reanimation is bookkeeping only.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML
from ..units import ENERGY, Quantity

# These values are accounting markers only. They are not a fuel requirement,
# stored energy, or an object's physical energy. One ordinary reanimation is
# recorded as 100 J; construct animation is recorded as 250 J per construct.
NECRO_REANIMATE_RECORD_J = 100.0


def _marked_world_operation(function):
    function.__mana_runtime_operation__ = True
    return function


def build_library(runtime: Any) -> dict[str, Any]:
    def _planes():
        return runtime._load_library("planes").values

    def _check_execution(operation: str) -> None:
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML(f"necromancy.{operation}() changes the world; execute it within post()/release()")

    def _validate_object(value: Any, operation: str) -> None:
        from ..runtime import MagicObject
        if not isinstance(value, MagicObject):
            raise TypeErrorML(f"necromancy.{operation}() expects an existing MANA object")
        if not value.properties.get("active", True):
            raise MagicErrorML(f"necromancy.{operation}() cannot affect an inactive object")
        if value.properties.get("is_undead", False):
            raise MagicErrorML(f"{runtime._object_label(value)} is already animated")

    def _has_body_markers(value: Any) -> bool:
        props = value.properties
        def normal(key):
            return str(props.get(key, "")).strip().casefold().replace("_", " ")
        valid = {"bone", "bones", "skeleton", "corpse", "dead body", "remains"}
        states = {"corpse", "dead", "dead body", "remains", "bones"}
        return normal("material") in valid or normal("kind") in valid or normal("state") in states

    def _is_corpse_or_bones(value: Any) -> bool:
        # body_present is established when a tgset object is introduced with
        # a corpse/bones material/state; changing labels afterwards is not
        # enough to transform a rock into actual remains.
        return value.properties.get("body_present", False) is True and _has_body_markers(value)

    def _check_corpse(corpse: Any, operation: str) -> None:
        _validate_object(corpse, operation)
        if not _is_corpse_or_bones(corpse):
            raise MagicErrorML(
                f"necromancy.{operation}() requires an existing object identified as a corpse, bones, skeleton, or remains"
            )

    def _check_necro_access(planes: dict[str, Any], record_j: float, kind: str) -> None:
        # `Necro` is the mana/channel name; the physical source remains Underworld.
        planes["send_energy"](Quantity(record_j, ENERGY), "Underworld", "Mortal Plane", kind)

    def _apply_animation(body: Any, name: str | None = None) -> Any:
        props = body.properties
        previous_name = str(props.get("display_name", body.element))
        material = str(props.get("material", "")).casefold()
        default_name = "Skeleton" if "bone" in material or material == "skeleton" or str(props.get("state", "")).casefold() == "bones" else f"Undead {previous_name}"
        species = name.strip() if isinstance(name, str) and name.strip() else default_name
        props["animation_state"] = "reanimated"
        props["is_being"] = True
        props["is_undead"] = True
        props["object_kind"] = "being"
        props["kind"] = "undead"
        props["home_plane"] = "Mortal Plane"
        props["species"] = species
        props["display_name"] = species
        props["necromantic_mana_type"] = "Necro"
        runtime.emit_event("being_reanimated", body, species, "Necro")
        return body

    def reanimate(corpse: Any, name: Any = None) -> Any:
        """Animate an existing corpse/bone/skeleton object already in the world."""
        _check_execution("reanimate")
        _check_corpse(corpse, "reanimate")
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise TypeErrorML("necromancy.reanimate() name must be non-empty text when supplied")
        planes = _planes()
        roots = [runtime.global_env, runtime.active_objects, corpse]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            _check_necro_access(planes, NECRO_REANIMATE_RECORD_J, "Necro:reanimate")
            result = _apply_animation(corpse, name)
            return result
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise

    def reanimate_many(corpses: Any, name: Any = None) -> list[Any]:
        """Reanimate several existing bodies; ledger usage is recorded per body."""
        _check_execution("reanimate_many")
        from ..runtime import MagicObject
        if not isinstance(corpses, list) or not corpses:
            raise TypeErrorML("necromancy.reanimate_many() expects a non-empty list of corpse objects")
        seen: set[int] = set()
        for corpse in corpses:
            _check_corpse(corpse, "reanimate_many")
            if not isinstance(corpse, MagicObject):
                raise TypeErrorML("reanimate_many() list entries must be MANA objects")
            if id(corpse) in seen:
                raise MagicErrorML("reanimate_many() cannot contain the same body more than once")
            seen.add(id(corpse))
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise TypeErrorML("necromancy.reanimate_many() name must be non-empty text when supplied")
        total = NECRO_REANIMATE_RECORD_J * len(corpses)
        if not math.isfinite(total):
            raise PhysicsErrorML("necromantic accounting total must be finite")
        planes = _planes()
        roots = [runtime.global_env, runtime.active_objects, *corpses]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            _check_necro_access(planes, total, "Necro:reanimate_many")
            results = []
            for index, corpse in enumerate(corpses, 1):
                assigned_name = f"{name.strip()} {index}" if isinstance(name, str) and name.strip() else None
                results.append(_apply_animation(corpse, assigned_name))
            return results
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise


    def is_undead(thing: Any) -> bool:
        properties = getattr(thing, "properties", None)
        if properties is None:
            raise TypeErrorML("necromancy.is_undead() expects a MANA object")
        return properties.get("is_undead", False) is True

    return {
        "reanimate": _marked_world_operation(reanimate),
        "reanimate_many": _marked_world_operation(reanimate_many),
        "is_undead": is_undead,
    }


__all__ = ["build_library"]
