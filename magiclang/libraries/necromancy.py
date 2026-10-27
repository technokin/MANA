"""Reanimation of existing remains using the Necro mana channel.

Creating a summoned undead is an ordinary MANA spell written by the user;
this library does not provide a special summon/construct-animation shortcut.
The Underworld transfer for reanimation is bookkeeping only.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML
from ..units import ENERGY, Quantity

# These values are accounting markers only. They are not a fuel requirement,
# stored energy, or an object's physical energy. One ordinary reanimation is
# recorded as 100 J; construct animation is recorded as 250 J per construct.
NECRO_REANIMATE_RECORD_J = 100.0
NECRO_LICHIFY_RECORD_J = 500.0
MAX_REANIMATION_BATCH = 256


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
        return (normal("material") in valid or normal("kind") in valid or normal("state") in states
                or normal("body_condition") in states)

    def _is_corpse_or_bones(value: Any) -> bool:
        # body_present is established when a tgset object is introduced with
        # a corpse/bones material/state; changing labels afterwards is not
        # enough to transform a rock into actual remains.
        props = value.properties
        if props.get("body_present", False) is not True:
            return False
        if props.get("life_state") == "dead" and props.get("death_time") is not None:
            return True
        return _has_body_markers(value)

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
        props["living"] = False
        props["life_state"] = "undead"
        props["is_dead"] = False
        props["consciousness"] = "animated"
        props["body_present"] = False
        props["body_condition"] = "reanimated"
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
        if len(corpses) > MAX_REANIMATION_BATCH:
            raise RuntimeErrorML(
                f"necromancy.reanimate_many() is limited to {MAX_REANIMATION_BATCH} bodies per call"
            )
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


    def lichify(target: Any, phylactery: Any, name: Any = None) -> Any:
        """Bind an existing living/dead/undead entity to a conjured phylactery.

        The phylactery is a physical conjured object. Lichification is reversible
        only while that exact anchor remains active and bound to the lich.
        """
        _check_execution("lichify")
        from ..runtime import MagicObject
        from .physiology import _initialize as initialize_body
        if not isinstance(target, MagicObject) or not target.properties.get("active", True):
            raise TypeErrorML("necromancy.lichify() target must be an active MANA entity")
        if target is phylactery:
            raise MagicErrorML("necromancy.lichify() target and phylactery must be different objects")
        tp = target.properties
        if tp.get("undead_type") == "lich" or tp.get("phylactery_object_id") is not None:
            raise MagicErrorML("this entity is already bound to a lich phylactery")
        is_body = bool(tp.get("living") or tp.get("is_being") or tp.get("is_summoned")
                       or tp.get("targetable") or (tp.get("life_state") == "dead" and tp.get("body_present") is True))
        if not is_body:
            raise MagicErrorML("necromancy.lichify() requires a living being or an existing body/remains")
        if not isinstance(phylactery, MagicObject) or not phylactery.properties.get("active", True):
            raise TypeErrorML("necromancy.lichify() phylactery must be an active MANA object")
        pp = phylactery.properties
        if not pp.get("created_by_conjure"):
            raise MagicErrorML("necromancy.lichify() requires a physical object created by conjure() as the phylactery")
        mass = pp.get("mass")
        mass_value = getattr(mass, "value", None)
        if not isinstance(mass_value, (int, float)) or not math.isfinite(float(mass_value)) or float(mass_value) <= 0:
            raise PhysicsErrorML("necromancy.lichify() phylactery must have positive finite mass")
        if pp.get("equipped_to") is not None:
            raise MagicErrorML("necromancy.lichify() phylactery cannot be equipped; unequip it first")
        if pp.get("phylactery_owner_id") is not None:
            raise MagicErrorML("this phylactery is already bound to another entity")
        if name is not None and (not isinstance(name, str) or not name.strip() or len(name) > 80):
            raise TypeErrorML("necromancy.lichify() name must be non-empty text no longer than 80 characters")

        planes = _planes()
        roots = [runtime.global_env, runtime.active_objects, target, phylactery]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            _check_necro_access(planes, NECRO_LICHIFY_RECORD_J, "Necro:lichify")
            initialize_body(target)
            label = name.strip() if isinstance(name, str) else str(tp.get("display_name", tp.get("species", "Lich")))
            tp["display_name"] = label
            tp["species"] = label
            tp["object_kind"] = "being"
            tp["kind"] = "undead"
            tp["is_being"] = True
            tp["is_undead"] = True
            tp["living"] = False
            tp["life_state"] = "undead"
            tp["is_dead"] = False
            tp["consciousness"] = "awake"
            tp["body_present"] = False
            tp["body_condition"] = "lich"
            tp["undead_type"] = "lich"
            tp["soul_state"] = "bound_to_phylactery"
            tp["phylactery_object_id"] = phylactery.object_id
            tp["home_plane"] = tp.get("home_plane", "Mortal Plane")
            maximum = float(tp.get("max_hp", 100.0) or 100.0)
            tp["hp"] = max(1.0, min(maximum, float(tp.get("hp", maximum) or 0.0)))
            pp["phylactery_owner_id"] = target.object_id
            pp["soul_bound"] = True
            pp["phylactery_for"] = label
            pp["phylactery_created_at"] = runtime.elapsed_virtual_time
            runtime._observe("magic.effect", effect="lichification", entity=runtime._visual_entity(target), phylactery=runtime._visual_entity(phylactery))
            runtime.emit_event("being_lichified", target, phylactery)
            return target
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise

    def is_lich(thing: Any) -> bool:
        properties = getattr(thing, "properties", None)
        if not isinstance(properties, dict):
            raise TypeErrorML("necromancy.is_lich() expects a MANA object")
        return properties.get("undead_type") == "lich" and properties.get("phylactery_object_id") is not None

    def reconstitute(lich: Any) -> Any:
        """Restore an incapacitated lich from its active, bound phylactery."""
        _check_execution("reconstitute")
        from ..runtime import MagicObject
        if not isinstance(lich, MagicObject):
            raise TypeErrorML("necromancy.reconstitute() expects a MANA lich object")
        lp = lich.properties
        if lp.get("undead_type") != "lich" or lp.get("phylactery_object_id") is None:
            raise MagicErrorML("necromancy.reconstitute() requires a lich bound to a phylactery")
        anchor_id = lp.get("phylactery_object_id")
        anchor = next((obj for obj in runtime.active_objects if getattr(obj, "object_id", None) == anchor_id), None)
        if anchor is None:
            anchor = next((value for value in runtime.global_env.values.values()
                           if isinstance(value, MagicObject) and value.object_id == anchor_id), None)
        if anchor is None or not anchor.properties.get("active", True):
            raise MagicErrorML("the lich's phylactery is missing or inactive; reconstitution is impossible")
        ap = anchor.properties
        if ap.get("phylactery_owner_id") != lich.object_id or ap.get("soul_bound") is not True:
            raise MagicErrorML("the phylactery's soul binding is broken or belongs to another lich")
        roots = [runtime.global_env, runtime.active_objects, lich, anchor]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            maximum = float(lp.get("max_hp", 100.0) or 100.0)
            lp["active"] = True
            if all(existing is not lich for existing in runtime.active_objects):
                runtime.active_objects.append(lich)
            if all(existing is not anchor for existing in runtime.active_objects):
                runtime.active_objects.append(anchor)
            lp["hp"] = max(1.0, maximum * 0.65)
            lp["life_state"] = "undead"
            lp["is_dead"] = False
            lp["living"] = False
            lp["is_undead"] = True
            lp["consciousness"] = "awake"
            lp["body_present"] = False
            lp["body_condition"] = "lich"
            position = ap.get("pos")
            if position is not None:
                lp["pos"] = position
            lp["reconstitution_count"] = int(lp.get("reconstitution_count", 0)) + 1
            runtime._observe("magic.effect", effect="lich_reconstitution", entity=runtime._visual_entity(lich), phylactery=runtime._visual_entity(anchor))
            runtime.emit_event("being_reconstituted", lich, anchor)
            return lich
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
        "lichify": _marked_world_operation(lichify),
        "is_lich": is_lich,
        "reconstitute": _marked_world_operation(reconstitute),
        "is_undead": is_undead,
    }


__all__ = ["build_library"]
