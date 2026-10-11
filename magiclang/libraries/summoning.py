"""Summoning, taming, and returning beings through `planes` pathways.

Summoned beings manifest in the Mortal Plane because it is the only active
world simulation. The source plane can be inferred for built-in beings, so the
common call is simply `summoning.bring("Griffin")`. Assigning the result to a
variable tames that particular entity; it can later be returned and recalled.
"""
from __future__ import annotations

from typing import Any

from ..errors import MagicErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from ..physics import Vector3, require_2d_world_vector
from ..units import ENERGY, M, Quantity
from .plane_data import BeingRecord
from .planar_registry import PlaneReference


def _marked_world_operation(function):
    function.__mana_runtime_operation__ = True
    return function


def _label(reference: PlaneReference) -> str:
    return reference.qualified_name if reference.is_region else reference.name


def _same_plane(first: str, second: str) -> bool:
    return first.casefold().replace("_", " ").strip() == second.casefold().replace("_", " ").strip()


# This is only a lookup index. Full being data remains inside each plane's
# separate, lazily loaded data library.
_BUILTIN_BEING_LIBRARY_INDEX = {
    **{name.casefold(): "wild_realm" for name in ("Griffin", "Werewolf", "Vampire", "Chimera", "Giant", "Orc")},
    "mermaid": "atlantis",
    "elf": "fae_paradise",
    **{f"{element} spirit".casefold(): "elemental_planes" for element in (
        "Fire", "Water", "Earth", "Air", "Ice", "Metal", "Thunder", "Life", "Death",
        "Underworld", "Holy", "Shadow", "Void",
    )},
}


def build_library(runtime: Any) -> dict[str, Any]:
    def _planes_namespace():
        namespace = runtime._load_library("planes")
        return namespace.values

    def _find_being(being: Any, source_plane: Any = None) -> tuple[BeingRecord, PlaneReference]:
        if isinstance(being, BeingRecord):
            record = being
            source_value = source_plane if source_plane is not None else record.home_plane
            plane_lib = _planes_namespace()
            source_ref = plane_lib["identify"](source_value)
            if source_ref.is_region:
                raise RuntimeErrorML("a being's home plane must be a top-level plane, not a region")
            if not _same_plane(source_ref.name, record.home_plane):
                raise RuntimeErrorML(
                    f"being '{record.name}' belongs to '{record.home_plane}', not '{source_ref.name}'"
                )
            return record, source_ref

        if not isinstance(being, str) or not being.strip():
            raise TypeErrorML("summoning.bring() expects a being name or a BeingRecord")

        plane_lib = _planes_namespace()
        if source_plane is not None:
            source_ref = plane_lib["identify"](source_plane)
            if source_ref.is_region:
                raise RuntimeErrorML("a being's home plane must be a top-level plane, not a region")
            custom_data = getattr(runtime, "_custom_plane_data", {}).get(source_ref.id)
            if custom_data is not None:
                records = custom_data.get("beings", [])
            elif source_ref.data_library:
                records = runtime._load_library(source_ref.data_library).values.get("beings", [])
            else:
                records = []
            matches = [item for item in records if isinstance(item, BeingRecord) and item.name.casefold() == being.strip().casefold()]
            if not matches:
                raise RuntimeErrorML(f"being '{being}' is not defined in plane '{source_ref.name}'")
            if len(matches) > 1:
                raise RuntimeErrorML(f"being name '{being}' is duplicated in plane '{source_ref.name}'")
            return matches[0], source_ref

        # First search custom data and plane libraries already loaded by the
        # program. Do not scan/load all the data libraries for every summon.
        candidates: list[BeingRecord] = []
        for namespace in runtime._library_namespaces.values():
            values = namespace.values if isinstance(namespace.values, dict) else {}
            for record in values.get("beings", []):
                if isinstance(record, BeingRecord) and record.name.casefold() == being.strip().casefold():
                    candidates.append(record)
        for custom in getattr(runtime, "_custom_plane_data", {}).values():
            for record in custom.get("beings", []):
                if isinstance(record, BeingRecord) and record.name.casefold() == being.strip().casefold():
                    candidates.append(record)
        unique = {(item.name.casefold(), item.home_plane.casefold()): item for item in candidates}
        candidates = list(unique.values())

        if not candidates:
            library_name = _BUILTIN_BEING_LIBRARY_INDEX.get(being.strip().casefold())
            if library_name is not None:
                namespace = runtime._load_library(library_name)
                values = namespace.values if isinstance(namespace.values, dict) else {}
                candidates = [
                    item for item in values.get("beings", [])
                    if isinstance(item, BeingRecord) and item.name.casefold() == being.strip().casefold()
                ]

        if not candidates:
            raise RuntimeErrorML(
                f"unknown being '{being}'; for a custom being, provide its home plane, e.g. summoning.bring(\"Crystal Drake\", \"Crystal Reach\")"
            )
        if len(candidates) > 1:
            homes = ", ".join(sorted({item.home_plane for item in candidates}))
            raise RuntimeErrorML(f"being name '{being}' is ambiguous; supply its home plane ({homes})")
        record = candidates[0]
        source_ref = plane_lib["identify"](record.home_plane)
        if source_ref.is_region:
            raise RuntimeErrorML("a being's home plane must be a top-level plane, not a region")
        return record, source_ref

    def find_being(being: Any, source_plane: Any = None) -> BeingRecord:
        record, _source = _find_being(being, source_plane)
        return record

    def _validate_requirements(record: BeingRecord, requirements: Any) -> None:
        if requirements is None:
            supplied: list[str] = []
        elif isinstance(requirements, list) and all(isinstance(item, str) and item.strip() for item in requirements):
            supplied = [item.strip() for item in requirements]
        else:
            raise TypeErrorML("summoning requirements must be a list of non-empty text values")
        missing = [item for item in record.summoning_requirements if item not in supplied]
        if missing:
            raise MagicErrorML(
                f"summoning '{record.name}' is missing required conditions: {', '.join(missing)}"
            )

    def _position(value: Any = None) -> Vector3:
        if value is None:
            caster = getattr(runtime, "caster_position", Vector3(0, 0, 0, M))
            if not isinstance(caster, Vector3) or caster.dimension != M:
                caster = Vector3(0, 0, 0, M)
            # Without an explicit position, manifest ten metres ahead of the
            # runtime's origin/forward (+X) rather than on top of the caster.
            value = Vector3(caster.x + 10.0, caster.y, 0.0, M)
        elif hasattr(value, "properties"):
            value = value.properties.get("pos")
        if not isinstance(value, Vector3) or value.dimension != M:
            raise UnitErrorML("summoning position must be a position vector measured in metres or a positioned object")
        return require_2d_world_vector(value, "summoning position")

    def _validate_entity(being: Any, operation: str):
        from ..runtime import MagicObject
        if not isinstance(being, MagicObject) or not being.properties.get("is_summoned", False):
            raise TypeErrorML(f"summoning.{operation}() expects a being created by summoning.bring()")
        return being

    def _record_transfer(being: Any, source: str, destination: str):
        plane_lib = _planes_namespace()
        route = plane_lib["find_route"](source, destination)
        amount_j = runtime.object_energy_j(being)
        plane_lib["send_energy"](
            Quantity(amount_j, ENERGY), source, destination,
            f"being:{being.properties.get('species', being.properties.get('display_name', 'being'))}",
        )
        return route

    @_marked_world_operation
    def bring(being: Any, source_plane: Any = None, position: Any = None, requirements: Any = None):
        """Bring a defined being to the Mortal Plane through an open route.

        Destination is intentionally implicit: MANA's active world is the
        Mortal Plane. The source plane is inferred for registered built-in beings.
        """
        if getattr(runtime, "_pure_call_depth", 0):
            raise MagicErrorML("summoning.bring() changes the world; call it from a spell using post()/release()")
        record, source_ref = _find_being(being, source_plane)
        plane_lib = _planes_namespace()
        destination_ref = plane_lib["identify"]("Mortal Plane")
        if _same_plane(destination_ref.name, source_ref.name):
            raise RuntimeErrorML("summoning source and destination must be different planes")
        _validate_requirements(record, requirements)
        plane_lib["find_route"](source_ref, destination_ref)
        world_position = _position(position)

        from ..runtime import MagicObject
        obj = MagicObject("Being")
        obj.properties.update({
            "object_kind": "being",
            "kind": record.kind,
            "display_name": record.name,
            "species": record.name,
            "is_being": True,
            "is_summoned": True,
            "is_tamed": False,
            "is_returned_to_plane": False,
            "home_plane": record.home_plane,
            "element_tie": record.element,
            "summoning_requirements": list(record.summoning_requirements),
            "resistances": dict(record.resistance),
            "pos": world_position,
            "anchor_pos": world_position,
        })
        for key in ("hp", "max_hp", "defence", "attack"):
            value = getattr(record, key)
            if value is not None:
                obj.properties[key] = value
        for element_name, amount in record.resistance.items():
            obj.properties[f"resist_{element_name.casefold()}"] = amount

        roots = [runtime.global_env, runtime.active_objects, obj]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            plane_lib["send_energy"](
                Quantity(runtime.object_energy_j(obj), ENERGY), source_ref, destination_ref,
                kind=f"being:{record.name}",
            )
            runtime._record_created(obj, reason=f"summoned from {_label(source_ref)}")
            runtime.emit_event("being_summoned", record.name, _label(source_ref), _label(destination_ref))
            return obj
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise

    @_marked_world_operation
    def tame(being: Any, name: Any = None):
        """Give a summoned being a stable personal name so it can be recalled."""
        _validate_entity(being, "tame")
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise TypeErrorML("summoning.tame() name must be non-empty text when supplied")
        props = being.properties
        chosen = name.strip() if isinstance(name, str) else str(props.get("species", props.get("display_name", "being")))
        if props.get("is_tamed", False) and name is None:
            return being
        props["is_tamed"] = True
        props["tame_name"] = chosen
        runtime.emit_event("being_tamed", chosen, props.get("species"))
        return being

    @_marked_world_operation
    def send_back(being: Any):
        """Return a summoned entity to its home plane; an open reverse route is required."""
        _validate_entity(being, "send_back")
        props = being.properties
        if props.get("is_returned_to_plane", False) or not props.get("active", True):
            raise MagicErrorML("this being has already been sent back")
        home = props.get("home_plane")
        if not isinstance(home, str) or not home.strip() or _same_plane(home, "Mortal Plane"):
            raise RuntimeErrorML("this being has no distinct home plane to return to")
        roots = [runtime.global_env, runtime.active_objects, being]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            _record_transfer(being, "Mortal Plane", home)
            props["active"] = False
            props["is_returned_to_plane"] = True
            runtime.emit_event("being_returned", props.get("tame_name", props.get("species")), home)
            return being
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise

    @_marked_world_operation
    def call(being: Any):
        """Recall the same tamed entity after it has been returned home."""
        _validate_entity(being, "call")
        props = being.properties
        if not props.get("is_tamed", False):
            raise MagicErrorML("only a named/tamed summoned being can be recalled")
        if not props.get("is_returned_to_plane", False) or props.get("active", True):
            raise MagicErrorML("this being must be sent back before it can be recalled")
        home = props.get("home_plane")
        plane_lib = _planes_namespace()
        # Validate route first, then perform transfer and reactivate atomically.
        plane_lib["find_route"](home, "Mortal Plane")
        roots = [runtime.global_env, runtime.active_objects, being]
        roots.extend(handler.env for handler in runtime.event_handlers)
        roots.extend(timer.env for timer in runtime.timers)
        snapshot = runtime._snapshot_runtime_state(roots)
        try:
            _record_transfer(being, home, "Mortal Plane")
            position = _position(None)
            props["pos"] = position
            props["anchor_pos"] = position
            props["active"] = True
            props["is_returned_to_plane"] = False
            runtime.emit_event("being_summoned", props.get("tame_name", props.get("species")), home, "Mortal Plane")
            return being
        except Exception:
            runtime._restore_runtime_state(snapshot)
            raise

    return {
        "find_being": find_being,
        "bring": bring,
        "tame": tame,
        "send_back": send_back,
        "call": call,
    }


__all__ = ["build_library"]
