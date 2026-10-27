"""Plane identification, categories, pathways, energy transfer, and invocation.

This library does not create planes or transfer beings. Identity and pathway
state live in the runtime registry; elemental details and beings are held by
independently loaded data libraries.
"""
from __future__ import annotations

import math
from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from ..units import ENERGY, POWER, Quantity
from .plane_data import BeingRecord
from .planar_registry import (
    PathwayRecord, PlaneReference, _normalise, get_registry, pathway_key, resolve_plane,
)

BASE_ELEMENTS = frozenset({"Fire", "Water", "Earth", "Air"})
ELEMENTAL_ENERGY_KINDS = frozenset({
    "Fire", "Water", "Earth", "Air", "Ice", "Metal", "Thunder", "Life",
    "Death", "Underworld", "Holy", "Shadow", "Void",
})
_INTERNAL_ENERGY_KIND_LABELS = frozenset({
    "necro:reanimate", "necro:reanimate_many", "necro:lichify",
})


def _label(reference: PlaneReference | None) -> str:
    if reference is None:
        return "<missing plane>"
    return reference.qualified_name if reference.is_region else reference.name


def _element_record(runtime: Any, reference: PlaneReference) -> dict[str, Any]:
    """Load and resolve elemental metadata without bloating the identity list."""
    if reference.is_region or reference.category != "elemental":
        raise RuntimeErrorML(f"'{_label(reference)}' is not an elemental plane")
    if not reference.data_library:
        raise RuntimeErrorML(f"elemental plane '{reference.name}' has no data library assigned")
    namespace = runtime._load_library(reference.data_library)
    plane_records = namespace.values.get("planes", [])
    record = next((item for item in plane_records if item.get("id") == reference.id), None)
    if record is None:
        raise RuntimeErrorML(f"no elemental data record is registered for '{reference.name}'")
    return record


def _needs_invocation(runtime: Any, reference: PlaneReference) -> bool:
    if reference.category != "elemental" or reference.is_region:
        return False
    return _element_record(runtime, reference)["element"] not in BASE_ELEMENTS


def _require_permission(runtime: Any, registry: Any, reference: PlaneReference) -> None:
    if _needs_invocation(runtime, reference) and reference.id not in registry.permissions:
        channel_name = "Necro" if reference.id == "underworld" else reference.name
        raise MagicErrorML(
            f"the {channel_name} mana channel must be invoked before its energy can be recorded; "
            f"use planes.invoke(\"{channel_name}\") first"
        )


def _outgoing_neighbors(registry: Any, source_id: str) -> list[str]:
    """Get the deterministic outgoing adjacency implied by pathway records."""
    neighbors: set[str] = set()
    for path in registry.pathways.values():
        if path.state != "open":
            continue
        if path.source_id == source_id:
            neighbors.add(path.destination_id)
        elif not path.one_way and path.destination_id == source_id:
            neighbors.add(path.source_id)
    return sorted(neighbors, key=lambda key: _label(registry.reference(key)).casefold())


def _route_ids(registry: Any, source_id: str, destination_id: str) -> list[str]:
    """Return one deterministic shortest route through open directed pathways."""
    if source_id == destination_id:
        return [source_id]
    pending = [source_id]
    previous: dict[str, str | None] = {source_id: None}
    cursor = 0
    while cursor < len(pending):
        current = pending[cursor]
        cursor += 1
        for neighbour in _outgoing_neighbors(registry, current):
            if neighbour in previous:
                continue
            previous[neighbour] = current
            if neighbour == destination_id:
                route = [destination_id]
                while route[-1] != source_id:
                    route.append(previous[route[-1]])
                route.reverse()
                return route
            pending.append(neighbour)
    return []


def _path_is_open(registry: Any, source_id: str, destination_id: str) -> bool:
    path = registry.pathways.get(pathway_key(source_id, destination_id))
    if path is None or path.state != "open":
        return False
    if path.one_way:
        return path.source_id == source_id and path.destination_id == destination_id
    return {path.source_id, path.destination_id} == {source_id, destination_id}


def build_library(runtime: Any) -> dict[str, Any]:
    """Build the public API for ``import planes`` using runtime-owned state."""
    registry = get_registry(runtime)

    def load_plane_data(reference: PlaneReference) -> None:
        if reference.data_library:
            # Internal lazy loads do not need a second explicit import statement.
            runtime._load_library(reference.data_library)

    def resolve(value: Any) -> PlaneReference:
        try:
            return resolve_plane(registry, value)
        except RuntimeErrorML:
            if isinstance(value, str):
                data_library = registry.lazy_region_libraries.get(_normalise(value))
                if data_library is None and "." in value:
                    parent_name = value.split(".", 1)[0]
                    parent_id = registry.aliases.get(_normalise(parent_name))
                    parent = registry.planes.get(parent_id) if parent_id else None
                    data_library = parent.data_library if parent else None
                if data_library:
                    runtime._load_library(data_library)
                    return resolve_plane(registry, value)
            raise

    def identify(name: Any) -> PlaneReference:
        """Resolve a known plane or region name, alias, ID, or qualified name."""
        return resolve(name)

    def exists(name: Any) -> bool:
        """Return whether a plane or region can be identified."""
        if not isinstance(name, str):
            if isinstance(name, PlaneReference):
                try:
                    resolve(name)
                    return True
                except RuntimeErrorML:
                    return False
            raise TypeErrorML("planes.exists() expects a plane or region name")
        plane_id = registry.aliases.get(_normalise(name))
        if plane_id is None:
            data_library = registry.lazy_region_libraries.get(_normalise(name))
            if data_library:
                runtime._load_library(data_library)
                plane_id = registry.aliases.get(_normalise(name))
        return plane_id is not None and registry.reference(plane_id) is not None

    def plane_of(thing: Any) -> PlaneReference:
        """Return a being record/entity's home plane, or Mortal Plane otherwise.

        A summoned/reanimated world object stores a home_plane field only when
        it represents a being. Ordinary objects do not receive a current-plane
        property; the world simulation remains the Mortal Plane.
        """
        if isinstance(thing, BeingRecord):
            return resolve(thing.home_plane)
        if isinstance(thing, (str, PlaneReference)):
            raise TypeErrorML(
                "planes.plane_of() expects a being record or world object, not a plane name or plane reference"
            )
        properties = getattr(thing, "properties", None)
        if isinstance(properties, dict) and properties.get("is_being") is True:
            home = properties.get("home_plane")
            if isinstance(home, str) and home.strip():
                return resolve(home)
        return resolve("Mortal Plane")

    def all_planes() -> list[str]:
        """Return every top-level plane; regions are listed by regions_of()."""
        return [_label(reference) for reference in registry.planes.values()]

    def regions_of(plane: Any) -> list[str]:
        reference = resolve(plane)
        if reference.is_region:
            raise RuntimeErrorML(f"regions_of() expects a plane, not region '{_label(reference)}'")
        load_plane_data(reference)
        return sorted(
            (_label(region) for region in registry.regions.values() if region.parent_plane == reference.name),
            key=str.casefold,
        )

    def parent_of(region: Any) -> PlaneReference:
        reference = resolve(region)
        if not reference.is_region or not reference.parent_plane:
            raise RuntimeErrorML(f"parent_of() expects a region, not plane '{reference.name}'")
        return resolve(reference.parent_plane)

    def category_of(plane: Any) -> str:
        return resolve(plane).category

    def planes_in(category: Any) -> list[str]:
        if not isinstance(category, str) or not category.strip():
            raise TypeErrorML("planes.planes_in() category must be non-empty text")
        requested = " ".join(category.strip().casefold().replace("_", " ").replace("-", " ").split())
        return [_label(reference) for reference in registry.planes.values() if reference.category == requested]

    def same_category(first: Any, second: Any) -> bool:
        return resolve(first).category == resolve(second).category

    def _validate_one_way(one_way: Any) -> bool:
        if not isinstance(one_way, bool):
            raise TypeErrorML("planes.open_path() one_way must be true or false")
        return one_way

    def _prune_channels_with_no_route() -> None:
        channels = getattr(runtime, "_planar_channels", {})
        for key in list(channels):
            source_id, target_id = key
            if not _route_ids(registry, source_id, target_id):
                channels.pop(key, None)

    def open_path(source: Any, destination: Any, one_way: bool = False) -> bool:
        """Open one direct pathway, bidirectional unless one_way=true."""
        one_way = _validate_one_way(one_way)
        start, end = resolve(source), resolve(destination)
        if start.id == end.id:
            raise PhysicsErrorML("a pathway cannot connect a plane or region to itself")
        key = pathway_key(start.id, end.id)
        existing = registry.pathways.get(key)
        same_direction = (
            existing is not None
            and existing.source_id == start.id
            and existing.destination_id == end.id
        )
        same_open_path = (
            existing is not None and existing.state == "open"
            and existing.one_way == one_way
            and (same_direction or (not one_way and
                 existing.source_id == end.id and existing.destination_id == start.id))
        )
        if same_open_path:
            return False
        registry.pathways[key] = PathwayRecord(
            source_id=start.id, destination_id=end.id, one_way=one_way, state="open",
        )
        runtime.emit_event("path_opened", _label(start), _label(end), one_way)
        return True

    def close_path(source: Any, destination: Any) -> bool:
        """Close the pathway record between two endpoints, whichever direction it used."""
        start, end = resolve(source), resolve(destination)
        key = pathway_key(start.id, end.id)
        existing = registry.pathways.get(key)
        if existing is None or existing.state != "open":
            return False
        registry.pathways[key] = PathwayRecord(
            source_id=existing.source_id,
            destination_id=existing.destination_id,
            one_way=existing.one_way,
            state="closed",
        )
        _prune_channels_with_no_route()
        runtime.emit_event("path_closed", _label(start), _label(end), existing.one_way)
        return True

    def is_open(source: Any, destination: Any) -> bool:
        start, end = resolve(source), resolve(destination)
        return _path_is_open(registry, start.id, end.id)

    def paths_of(plane: Any) -> list[dict[str, Any]]:
        reference = resolve(plane)
        result = []
        for path in registry.pathways.values():
            if path.state != "open":
                continue
            if path.one_way:
                if path.source_id != reference.id:
                    continue
                destination_id = path.destination_id
                source_id = reference.id
            elif path.source_id == reference.id:
                destination_id = path.destination_id
                source_id = reference.id
            elif path.destination_id == reference.id:
                destination_id = path.source_id
                source_id = reference.id
            else:
                continue
            result.append({
                "source": _label(registry.reference(source_id)),
                "destination": _label(registry.reference(destination_id)),
                "state": path.state,
                "one_way": path.one_way,
            })
        return sorted(result, key=lambda path: path["destination"].casefold())

    def neighbors(plane: Any) -> list[str]:
        return [path["destination"] for path in paths_of(plane)]

    def find_route(source: Any, destination: Any) -> list[str]:
        start, end = resolve(source), resolve(destination)
        route_ids = _route_ids(registry, start.id, end.id)
        if not route_ids:
            raise RuntimeErrorML(f"no open route connects {_label(start)} to {_label(end)}")
        return [_label(registry.reference(plane_id)) for plane_id in route_ids]

    def reachable(source: Any) -> list[str]:
        start = resolve(source)
        pending = [start.id]
        visited = {start.id}
        result = []
        cursor = 0
        while cursor < len(pending):
            current_id = pending[cursor]
            cursor += 1
            for next_id in _outgoing_neighbors(registry, current_id):
                if next_id in visited:
                    continue
                visited.add(next_id)
                pending.append(next_id)
                result.append(_label(registry.reference(next_id)))
        return result

    def send_energy(amount: Any, source: Any, destination: Any, kind: Any = None) -> dict[str, Any]:
        """Move an energy quantity in joules along an open route and record it."""
        start, end = resolve(source), resolve(destination)
        if start.id == end.id:
            raise PhysicsErrorML("send_energy() requires different source and destination planes or regions")
        if not isinstance(amount, Quantity):
            raise UnitErrorML("planes.send_energy() amount must be an energy quantity in joules")
        if amount.dimension != ENERGY:
            raise UnitErrorML(f"planes.send_energy() requires joules, not {amount.dimension}")
        if not math.isfinite(amount.value) or amount.value < 0:
            raise PhysicsErrorML("planes.send_energy() amount must be finite and non-negative")
        if kind is not None:
            if not isinstance(kind, str) or not kind.strip():
                raise TypeErrorML("planes.send_energy() kind must be non-empty text when supplied")
            normalized_kind = kind.strip()
            kind_key = normalized_kind.casefold()
            element_names = {name.casefold(): name for name in ELEMENTAL_ENERGY_KINDS}
            if kind_key in element_names:
                kind = element_names[kind_key]
            elif kind_key in _INTERNAL_ENERGY_KIND_LABELS:
                kind = "Necro:" + kind_key.split(":", 1)[1]
            elif kind_key.startswith("being:") and normalized_kind.partition(":")[2].strip():
                kind = "being:" + normalized_kind.partition(":")[2].strip()
            else:
                allowed = ", ".join(sorted(ELEMENTAL_ENERGY_KINDS))
                raise TypeErrorML(
                    "planes.send_energy() kind must be a known elemental energy label "
                    f"({allowed}) or a registered internal transfer label"
                )
        _require_permission(runtime, registry, start)
        route_ids = _route_ids(registry, start.id, end.id)
        if not route_ids:
            raise RuntimeErrorML(f"no open route connects {_label(start)} to {_label(end)}")
        route_names = [_label(registry.reference(plane_id)) for plane_id in route_ids]
        entry = runtime.record_planar_energy_transfer(
            _label(start), _label(end), amount.value, route_names, kind=kind,
        )
        runtime.emit_event("energy_arrived", _label(start), _label(end), amount.value, kind)
        return {
            "source": _label(start), "destination": _label(end),
            "amount_j": amount.value, "kind": kind, "path": route_names,
            "ledger_entry": entry,
        }

    def energy_sent(source: Any, destination: Any) -> Quantity:
        start, end = resolve(source), resolve(destination)
        total = sum(
            float(entry.get("amount_j", 0.0))
            for entry in runtime.energy_ledger
            if entry.get("operation") == "planar_transfer"
            and entry.get("source") == _label(start)
            and entry.get("target") == _label(end)
        )
        return Quantity(total, ENERGY)

    def open_channel(source: Any, destination: Any, rate: Any) -> bool:
        """Open a continuous one-direction energy flow at a rate in watts."""
        start, end = resolve(source), resolve(destination)
        if start.id == end.id:
            raise PhysicsErrorML("open_channel() requires different source and destination planes")
        if not isinstance(rate, Quantity) or rate.dimension != POWER:
            actual = rate.dimension if isinstance(rate, Quantity) else type(rate).__name__
            raise UnitErrorML(f"planes.open_channel() rate must be measured in watts, not {actual}")
        if not math.isfinite(rate.value) or rate.value <= 0:
            raise PhysicsErrorML("planes.open_channel() rate must be finite and positive")
        _require_permission(runtime, registry, start)
        if not _route_ids(registry, start.id, end.id):
            raise RuntimeErrorML(f"no open route connects {_label(start)} to {_label(end)}")
        channels = getattr(runtime, "_planar_channels", None)
        if channels is None:
            channels = {}
            runtime._planar_channels = channels
        key = (start.id, end.id)
        previous = channels.get(key)
        changed = previous is None or previous.get("rate_w") != rate.value
        channels[key] = {
            "rate_w": rate.value,
            "source": _label(start),
            "destination": _label(end),
            "kind": None,
        }
        return changed

    def close_channel(source: Any, destination: Any) -> bool:
        start, end = resolve(source), resolve(destination)
        channels = getattr(runtime, "_planar_channels", {})
        return channels.pop((start.id, end.id), None) is not None

    def _invocation_reference(plane_or_mana: Any) -> PlaneReference:
        # Necro is a mana-channel name, not a new plane. Its energy source is
        # still the Underworld, so the permission is stored against that plane.
        if isinstance(plane_or_mana, str) and _normalise(plane_or_mana) in {"necro", "necromantic", "necromancy"}:
            return resolve("Underworld")
        return resolve(plane_or_mana)

    def invoke(plane_or_mana: Any) -> bool:
        reference = _invocation_reference(plane_or_mana)
        record = _element_record(runtime, reference)
        if record["element"] in BASE_ELEMENTS:
            return True
        if reference.id in registry.permissions:
            return False
        registry.permissions.add(reference.id)
        return True

    def revoke(plane_or_mana: Any) -> bool:
        reference = _invocation_reference(plane_or_mana)
        record = _element_record(runtime, reference)
        if record["element"] in BASE_ELEMENTS:
            return False
        changed = reference.id in registry.permissions
        registry.permissions.discard(reference.id)
        channels = getattr(runtime, "_planar_channels", {})
        for key in list(channels):
            if key[0] == reference.id:
                channels.pop(key, None)
        return changed

    def has_permission(plane_or_mana: Any) -> bool:
        reference = _invocation_reference(plane_or_mana)
        record = _element_record(runtime, reference)
        return record["element"] in BASE_ELEMENTS or reference.id in registry.permissions

    def element_of(plane: Any) -> str:
        return _element_record(runtime, resolve(plane))["element"]

    def spirit_of(plane: Any) -> BeingRecord:
        reference = resolve(plane)
        record = _element_record(runtime, reference)
        data = runtime._load_library(reference.data_library)
        spirit = next((being for being in data.values["spirits"] if being.name == record["spirit"]), None)
        if spirit is None:
            raise RuntimeErrorML(f"no elemental spirit record is defined for '{reference.name}'")
        return spirit

    return {
        "identify": identify,
        "exists": exists,
        "plane_of": plane_of,
        "all_planes": all_planes,
        "regions_of": regions_of,
        "parent_of": parent_of,
        "category_of": category_of,
        "planes_in": planes_in,
        "same_category": same_category,
        "open_path": open_path,
        "close_path": close_path,
        "is_open": is_open,
        "paths_of": paths_of,
        "neighbors": neighbors,
        "find_route": find_route,
        "reachable": reachable,
        "send_energy": send_energy,
        "open_channel": open_channel,
        "close_channel": close_channel,
        "energy_sent": energy_sent,
        "invoke": invoke,
        "revoke": revoke,
        "has_permission": has_permission,
        "element_of": element_of,
        "spirit_of": spirit_of,
    }


__all__ = ["PlaneReference", "PathwayRecord", "build_library"]
