"""Configuration-time builder for player-defined planes and plane data.

The module creates new definitions. A draft is mutable until `create()` is
called; registered definitions are not edited by this library.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import math
import re
from typing import Any

from ..errors import MagicErrorML, RuntimeErrorML, TypeErrorML
from .plane_data import ELEMENT_NAMES, BeingRecord, make_being
from .planar_registry import (
    PlaneReference,
    get_registry,
    register_plane,
    register_region,
    resolve_plane,
    snapshot_registry,
    restore_registry,
)


@dataclass
class BeingDraft:
    name: str
    kind: str = "beast"
    element: str | None = None
    summoning_requirements: list[str] = field(default_factory=list)
    hp: float | None = None
    max_hp: float | None = None
    defence: float | None = None
    attack: float | None = None
    resistance: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in ELEMENT_NAMES})


@dataclass
class RegionDraft:
    name: str
    region_id: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    beings: list[BeingDraft] = field(default_factory=list)
    parent: "PlaneDraft | None" = None


@dataclass
class PlaneDraft:
    name: str
    category: str
    plane_id: str
    aliases: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    beings: list[BeingDraft] = field(default_factory=list)
    regions: list[RegionDraft] = field(default_factory=list)
    created: bool = False
    reference: PlaneReference | None = None


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    if not result:
        result = "custom_plane"
    if not result[0].isalpha():
        result = f"plane_{result}"
    return result


def _require_draft(value: Any) -> PlaneDraft | RegionDraft:
    if isinstance(value, (PlaneDraft, RegionDraft)):
        root = value if isinstance(value, PlaneDraft) else value.parent
        if root is None or root.created:
            raise RuntimeErrorML("this draft has already been created; registered plane data is immutable through drafter")
        return value
    raise TypeErrorML("expected a draft returned by drafter.begin() or drafter.add_region()")


def _root(draft: PlaneDraft | RegionDraft) -> PlaneDraft:
    return draft if isinstance(draft, PlaneDraft) else draft.parent  # validated by _require_draft


def _check_configuration_context(runtime: Any, operation: str) -> None:
    if getattr(runtime, "_spell_run_stack", None):
        raise MagicErrorML(f"drafter.{operation}() defines plane data and cannot run inside post()/release()")
    if getattr(runtime, "_pure_call_depth", 0):
        raise MagicErrorML(f"drafter.{operation}() cannot mutate a draft from a directly called helper")


def _safe_data_value(value: Any, *, depth: int = 0, seen: set[int] | None = None) -> Any:
    """Accept plain data and MANA quantities/vectors, never executable objects."""
    if depth > 16:
        raise TypeErrorML("custom plane data nesting exceeds 16 levels")
    if seen is None:
        seen = set()
    if value is None or isinstance(value, (str, bool, int, float)):
        if isinstance(value, float) and not __import__("math").isfinite(value):
            raise TypeErrorML("custom plane numeric values must be finite")
        return value
    # Imported late to keep the library independent from runtime initialization.
    from ..physics import Vector3
    from ..units import Quantity
    if isinstance(value, (Vector3, Quantity, PlaneReference)):
        return value
    if callable(value) or isinstance(value, BeingDraft) or hasattr(value, "properties"):
        raise TypeErrorML("custom plane data can contain values, not executable functions or world objects")
    identity = id(value)
    if identity in seen:
        raise TypeErrorML("custom plane data cannot contain circular references")
    if isinstance(value, list):
        seen.add(identity)
        try:
            return [_safe_data_value(item, depth=depth + 1, seen=seen) for item in value]
        finally:
            seen.remove(identity)
    if isinstance(value, tuple):
        seen.add(identity)
        try:
            return tuple(_safe_data_value(item, depth=depth + 1, seen=seen) for item in value)
        finally:
            seen.remove(identity)
    if isinstance(value, dict):
        seen.add(identity)
        try:
            output = {}
            for key, item in value.items():
                if not isinstance(key, str) or not key.strip():
                    raise TypeErrorML("custom plane data object keys must be non-empty text")
                output[key] = _safe_data_value(item, depth=depth + 1, seen=seen)
            return output
        finally:
            seen.remove(identity)
    raise TypeErrorML(f"unsupported custom plane data value: {type(value).__name__}")


def _property_target_data(runtime: Any, value: PlaneReference | str) -> dict[str, Any]:
    registry = get_registry(runtime)
    reference = resolve_plane(registry, value)
    all_data = getattr(runtime, "_custom_plane_data", {})
    if reference.is_region:
        parent_id = registry.aliases.get(re.sub(r"[^a-z0-9]", "", reference.parent_plane.casefold()))
        entry = all_data.get(parent_id, {})
        region_entry = entry.get("regions", {}).get(reference.id)
        if region_entry is None:
            return {"properties": {}, "beings": []}
        return region_entry
    entry = all_data.get(reference.id)
    if entry is None:
        return {"properties": {}, "beings": []}
    return entry


def _make_record(being: BeingDraft, home_plane: str) -> BeingRecord:
    try:
        return make_being(
            being.name, being.kind, home_plane,
            element=being.element,
            summoning_requirements=being.summoning_requirements,
            hp=being.hp, max_hp=being.max_hp,
            defence=being.defence, attack=being.attack,
            resistance=being.resistance,
        )
    except (TypeError, ValueError) as exc:
        raise TypeErrorML(f"invalid being definition '{being.name}': {exc}") from exc


def build_library(runtime: Any) -> dict[str, Any]:
    if not hasattr(runtime, "_custom_plane_data"):
        runtime._custom_plane_data = {}

    def begin(name: Any, category: Any = "ordinary", plane_id: Any = None) -> PlaneDraft:
        _check_configuration_context(runtime, "begin")
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("drafter.begin() name must be non-empty text")
        if not isinstance(category, str) or not category.strip():
            raise TypeErrorML("drafter.begin() category must be non-empty text")
        category_value = " ".join(category.strip().casefold().replace("_", " ").replace("-", " ").split())
        if len(category_value) > 48 or not re.fullmatch(r"[a-z][a-z0-9 ]*", category_value):
            raise TypeErrorML("plane category must start with a letter and contain only letters, digits, or spaces")
        if plane_id is None:
            plane_id = _slug(name)
        if not isinstance(plane_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", plane_id):
            raise TypeErrorML("plane_id must start with a lowercase letter and contain lowercase letters, digits, or underscores")
        return PlaneDraft(name.strip(), category_value, plane_id)

    def alias(draft: Any, name: Any) -> bool:
        _check_configuration_context(runtime, "alias")
        draft = _require_draft(draft)
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("drafter.alias() expects non-empty alias text")
        name = name.strip()
        if name.casefold() in {value.casefold() for value in draft.aliases}:
            return False
        draft.aliases.append(name)
        return True

    def set_value(draft: Any, key: Any, value: Any) -> Any:
        _check_configuration_context(runtime, "set_value")
        draft = _require_draft(draft)
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise TypeErrorML("custom property name must be a valid identifier")
        if key.casefold() in {"id", "name", "category", "beings", "regions", "parent", "created"}:
            raise RuntimeErrorML(f"'{key}' is reserved for plane-definition metadata")
        data = _safe_data_value(value)
        if key not in draft.properties and len(draft.properties) >= 256:
            raise RuntimeErrorML("a plane draft may define at most 256 custom properties")
        draft.properties[key] = data
        return data

    def add_region(draft: Any, name: Any, region_id: Any = None) -> RegionDraft:
        _check_configuration_context(runtime, "add_region")
        draft = _require_draft(draft)
        if not isinstance(draft, PlaneDraft):
            raise TypeErrorML("drafter.add_region() expects a plane draft")
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("region name must be non-empty text")
        if len(draft.regions) >= 100:
            raise RuntimeErrorML("a plane draft may define at most 100 regions")
        if any(region.name.casefold() == name.strip().casefold() for region in draft.regions):
            raise RuntimeErrorML(f"region '{name}' is already present in this draft")
        if region_id is not None and (not isinstance(region_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", region_id)):
            raise TypeErrorML("region_id must start with a lowercase letter and contain lowercase letters, digits, or underscores")
        result = RegionDraft(name.strip(), region_id=region_id, parent=draft)
        draft.regions.append(result)
        return result

    def _add_being(target: PlaneDraft | RegionDraft, name: Any, kind: Any = "beast", element: Any = None,
                   requirements: Any = None, hp: Any = None, max_hp: Any = None,
                   defence: Any = None, attack: Any = None) -> BeingDraft:
        _check_configuration_context(runtime, "add_being")
        target = _require_draft(target)
        if not isinstance(name, str) or not name.strip():
            raise TypeErrorML("being name must be non-empty text")
        if not isinstance(kind, str) or not kind.strip():
            raise TypeErrorML("being kind must be non-empty text")
        if element is not None and (not isinstance(element, str) or not element.strip()):
            raise TypeErrorML("being element must be non-empty text or null")
        if requirements is None:
            requirements = []
        if isinstance(requirements, str) or not isinstance(requirements, list):
            raise TypeErrorML("being requirements must be a list of text values")
        if any(not isinstance(item, str) or not item.strip() for item in requirements):
            raise TypeErrorML("being requirements must contain non-empty text values")
        if len(_root(target).beings) + sum(len(r.beings) for r in _root(target).regions) >= 1000:
            raise RuntimeErrorML("a plane draft may define at most 1000 beings")
        draft_being = BeingDraft(
            name=name.strip(), kind=kind.strip(), element=element.strip() if isinstance(element, str) else None,
            summoning_requirements=[item.strip() for item in requirements],
        )
        for field_name, value in (("hp", hp), ("max_hp", max_hp), ("defence", defence), ("attack", attack)):
            if value is not None:
                _set_being_field(draft_being, field_name, value)
        target.beings.append(draft_being)
        return draft_being

    def add_being(draft: Any, name: Any, kind: Any = "beast", element: Any = None,
                  requirements: Any = None, hp: Any = None, max_hp: Any = None,
                  defence: Any = None, attack: Any = None) -> BeingDraft:
        return _add_being(draft, name, kind, element, requirements, hp, max_hp, defence, attack)

    def _set_being_field(being: BeingDraft, key: str, value: Any) -> Any:
        if key in {"hp", "max_hp", "defence", "attack"}:
            if value is None:
                setattr(being, key, None)
                return None
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise TypeErrorML(f"being {key} must be a finite non-negative number or null")
            try:
                numeric_value = float(value)
            except (OverflowError, ValueError) as exc:
                raise TypeErrorML(f"being {key} is outside the supported numeric range") from exc
            if not math.isfinite(numeric_value):
                raise TypeErrorML(f"being {key} must be a finite non-negative number or null")
            if key == "hp" and being.max_hp is not None and numeric_value > being.max_hp:
                raise RuntimeErrorML("being hp cannot exceed max_hp")
            if key == "max_hp" and being.hp is not None and being.hp > numeric_value:
                raise RuntimeErrorML("being hp cannot exceed max_hp")
            setattr(being, key, numeric_value)
            return value
        if key == "kind":
            if not isinstance(value, str) or not value.strip():
                raise TypeErrorML("being kind must be non-empty text")
            being.kind = value.strip()
            return value
        if key == "element":
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise TypeErrorML("being element must be non-empty text or null")
            being.element = value.strip() if isinstance(value, str) else None
            return being.element
        if key == "summoning_requirements":
            if isinstance(value, str) or not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
                raise TypeErrorML("summoning_requirements must be a list of non-empty strings")
            being.summoning_requirements = [v.strip() for v in value]
            return list(being.summoning_requirements)
        if key.startswith("resistance."):
            element_name = key.split(".", 1)[1]
            if element_name not in ELEMENT_NAMES:
                raise RuntimeErrorML(f"unknown resistance element '{element_name}'")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise TypeErrorML("element resistance must be a finite number from 0 to 1")
            try:
                numeric_value = float(value)
            except (OverflowError, ValueError) as exc:
                raise TypeErrorML("element resistance is outside the supported numeric range") from exc
            if not math.isfinite(numeric_value):
                raise TypeErrorML("element resistance must be a finite number from 0 to 1")
            being.resistance[element_name] = numeric_value
            return numeric_value
        raise RuntimeErrorML("being field must be kind, element, hp, max_hp, defence, attack, summoning_requirements, or resistance.<Element>")

    def set_being(target: Any, being_name: Any, key: Any, value: Any) -> Any:
        _check_configuration_context(runtime, "set_being")
        target = _require_draft(target)
        if not isinstance(being_name, str) or not isinstance(key, str):
            raise TypeErrorML("drafter.set_being() expects a being name and field name")
        matches = [item for item in target.beings if item.name.casefold() == being_name.casefold()]
        if len(matches) != 1:
            raise RuntimeErrorML(f"being '{being_name}' must identify exactly one being in this draft or region")
        return _set_being_field(matches[0], key, value)

    def create(draft: Any) -> PlaneReference:
        _check_configuration_context(runtime, "create")
        draft = _require_draft(draft)
        if not isinstance(draft, PlaneDraft):
            raise TypeErrorML("drafter.create() expects a plane draft")
        if not draft.name.strip():
            raise TypeErrorML("plane name must be non-empty text")
        registry = get_registry(runtime)
        registry_snapshot = snapshot_registry(registry)
        custom_data = getattr(runtime, "_custom_plane_data", None)
        if custom_data is None:
            custom_data = {}
            runtime._custom_plane_data = custom_data
        custom_snapshot = deepcopy(custom_data)
        try:
            reference = register_plane(
                runtime, draft.plane_id, draft.name, draft.category,
                aliases=draft.aliases, data_library=None,
            )
            region_records = {}
            region_beings: list[BeingRecord] = []
            for region in draft.regions:
                region_id = region.region_id or f"{draft.plane_id}_{_slug(region.name)}"
                region_ref = register_region(runtime, reference, region_id, region.name)
                records = [_make_record(being, reference.name) for being in region.beings]
                region_beings.extend(records)
                region_records[region_ref.id] = {
                    "name": region_ref.name,
                    "properties": deepcopy(region.properties),
                    "beings": records,
                }
            top_beings = [_make_record(being, reference.name) for being in draft.beings]
            custom_data[reference.id] = {
                "id": reference.id,
                "name": reference.name,
                "category": reference.category,
                "properties": deepcopy(draft.properties),
                "beings": top_beings + region_beings,
                "regions": region_records,
            }
            # Fire the event before sealing the draft: if a handler fails,
            # rollback restores the registry and the draft remains retryable.
            runtime.emit_event("plane_created", reference.name, reference.id, reference.category)
            draft.created = True
            draft.reference = reference
            return reference
        except Exception:
            restore_registry(registry, registry_snapshot)
            custom_data.clear()
            custom_data.update(custom_snapshot)
            draft.created = False
            draft.reference = None
            raise

    def properties_of(plane: Any) -> dict[str, Any]:
        reference = resolve_plane(get_registry(runtime), plane)
        data = _property_target_data(runtime, reference)
        return deepcopy(data.get("properties", {}))

    def get_value(plane: Any, key: Any) -> Any:
        if not isinstance(key, str) or not key:
            raise TypeErrorML("drafter.get_value() key must be non-empty text")
        reference = resolve_plane(get_registry(runtime), plane)
        data = _property_target_data(runtime, reference)
        if key not in data.get("properties", {}):
            raise RuntimeErrorML(f"plane or region '{reference.qualified_name}' has no custom property '{key}'")
        return deepcopy(data["properties"][key])

    def beings_of(plane: Any) -> list[BeingRecord]:
        reference = resolve_plane(get_registry(runtime), plane)
        data = _property_target_data(runtime, reference)
        if reference.is_region:
            return list(data.get("beings", []))
        if reference.id in getattr(runtime, "_custom_plane_data", {}):
            return list(data.get("beings", []))
        if reference.data_library:
            namespace = runtime._load_library(reference.data_library)
            return list(namespace.values.get("beings", []))
        return []

    return {
        "begin": begin,
        "alias": alias,
        "set_value": set_value,
        "add_region": add_region,
        "add_being": add_being,
        "set_being": set_being,
        "create": create,
        "properties_of": properties_of,
        "get_value": get_value,
        "beings_of": beings_of,
    }


__all__ = ["PlaneDraft", "RegionDraft", "BeingDraft", "build_library"]
