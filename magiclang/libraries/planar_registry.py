"""Compact registry of plane identities, regions, and pathway records.

Plane identity records contain only identity/category/parent/data-library
references. Elemental details and beings live in separately loaded data
libraries. Plane contents never change MANA execution rules.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from ..errors import RuntimeErrorML, TypeErrorML


@dataclass(frozen=True, slots=True)
class PlaneReference:
    """Read-only identity for one plane or a region within a plane."""
    id: str
    name: str
    category: str
    data_library: str | None = None
    parent_plane: str | None = None

    @property
    def is_region(self) -> bool:
        return self.parent_plane is not None

    @property
    def qualified_name(self) -> str:
        if self.parent_plane:
            return f"{self.parent_plane}.{self.name}"
        return self.name

    def __repr__(self) -> str:
        kind = "RegionReference" if self.is_region else "PlaneReference"
        label = self.qualified_name if self.is_region else self.name
        return f"<{kind} {label!r} ({self.category})>"


@dataclass(frozen=True, slots=True)
class PathwayRecord:
    """A single pathway record: its endpoints, directionality, and state."""
    source_id: str
    destination_id: str
    one_way: bool
    state: str = "open"


@dataclass
class PlaneRegistry:
    planes: dict[str, PlaneReference]
    regions: dict[str, PlaneReference]
    aliases: dict[str, str]
    pathways: dict[tuple[str, str], PathwayRecord]
    lazy_region_libraries: dict[str, str] = field(default_factory=dict)
    permissions: set[str] = field(default_factory=set)

    def reference(self, plane_id: str) -> PlaneReference | None:
        return self.planes.get(plane_id) or self.regions.get(plane_id)


# Identity and categories are always available. Element and spirit information
# is deliberately kept in elemental_planes, not duplicated in this catalogue.
_BASE_PLANES = (
    # id, display name, category, data library, aliases
    ("fire", "Fire", "elemental", "elemental_planes", ("Fire Plane",)),
    ("water", "Water", "elemental", "elemental_planes", ("Water Plane",)),
    ("earth", "Earth", "elemental", "elemental_planes", ("Earth Plane",)),
    ("air", "Air", "elemental", "elemental_planes", ("Air Plane",)),
    ("ice", "Ice", "elemental", "elemental_planes", ("Ice Plane",)),
    ("metal", "Metal", "elemental", "elemental_planes", ("Metal Plane",)),
    ("thunder", "Thunder", "elemental", "elemental_planes", ("Thunder Plane",)),
    ("life", "Life", "elemental", "elemental_planes", ("Life Plane",)),
    ("death", "Death", "elemental", "elemental_planes", ("Death Plane",)),
    ("underworld", "Underworld", "elemental", "elemental_planes", ("Underworld Plane",)),
    ("holy", "Holy", "elemental", "elemental_planes", ("Holy Plane",)),
    ("shadow", "Shadow", "elemental", "elemental_planes", ("Shadow Plane",)),
    ("void", "Void", "elemental", "elemental_planes", ("Void Plane",)),
    ("mortal_plane", "Mortal Plane", "mortal", None, ("Mortal", "Mortal World", "World", "Our World")),
    ("hell", "Hell", "afterlife", "hell", ()),
    ("heaven", "Heaven", "afterlife", "heaven", ()),
    ("atlantis", "Atlantis", "living realm", "atlantis", ()),
    ("fae_paradise", "Fae Paradise", "living realm", "fae_paradise", ("Fae Realm", "Fae")),
    ("lineage_halls", "Lineage Halls", "afterlife", "lineage_halls", ("Lineage Hall", "Ancestor Hall", "Ancestor Halls")),
    ("wild_realm", "Wild Realm", "living realm", "wild_realm", ()),
)


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def pathway_key(first_id: str, second_id: str) -> tuple[str, str]:
    """Return a stable key for the unique pathway between two endpoints."""
    return tuple(sorted((first_id, second_id)))


def _build_default_registry() -> PlaneRegistry:
    planes: dict[str, PlaneReference] = {}
    aliases: dict[str, str] = {}
    for plane_id, name, category, data_library, extra_aliases in _BASE_PLANES:
        reference = PlaneReference(
            id=plane_id, name=name, category=category, data_library=data_library,
        )
        planes[plane_id] = reference
        for alias in (plane_id, plane_id.replace("_", " "), name, *extra_aliases):
            key = _normalise(alias)
            existing = aliases.get(key)
            if existing is not None and existing != plane_id:
                raise RuntimeError(f"duplicate built-in plane alias: {alias}")
            aliases[key] = plane_id

    lazy_region_libraries = {}
    for alias in (
        "Naraka", "Hell.Naraka", "hell.naraka",
        "The Ten Courts", "Hell.The Ten Courts", "hell.ten_courts",
        "Yomi Hollows", "Hell.Yomi Hollows", "hell.yomi_hollows",
    ):
        lazy_region_libraries[_normalise(alias)] = "hell"

    return PlaneRegistry(
        planes=planes, regions={}, aliases=aliases, pathways={},
        lazy_region_libraries=lazy_region_libraries, permissions=set(),
    )


def get_registry(runtime: Any) -> PlaneRegistry:
    """Get or lazily construct the registry owned by one Runtime instance."""
    registry = getattr(runtime, "_planar_registry", None)
    if registry is None:
        registry = _build_default_registry()
        runtime._planar_registry = registry
    return registry


def resolve_plane(registry: PlaneRegistry, value: Any) -> PlaneReference:
    if isinstance(value, PlaneReference):
        current = registry.reference(value.id)
        if current is not None and current.name == value.name:
            return current
        raise RuntimeErrorML(
            f"plane or region reference '{value.qualified_name}' is not registered in this MANA runtime"
        )
    if not isinstance(value, str):
        raise TypeErrorML("plane identifier must be a name, ID, or plane/region reference")
    plane_id = registry.aliases.get(_normalise(value))
    if plane_id is None:
        raise RuntimeErrorML(f"unknown plane or region '{value}'")
    current = registry.reference(plane_id)
    if current is None:
        raise RuntimeErrorML(f"plane or region '{value}' is not currently loaded")
    return current


def register_builtin_region(runtime: Any, *, id: str, name: str, parent_plane: str) -> PlaneReference:
    """Register a region from its built-in data library, not a public creator API."""
    registry = get_registry(runtime)
    existing = registry.regions.get(id)
    if existing is not None:
        return existing
    parent = resolve_plane(registry, parent_plane)
    if parent.is_region:
        raise RuntimeErrorML("a region's parent must be a plane")
    if not isinstance(name, str) or not name.strip():
        raise TypeErrorML("region name must be non-empty text")
    candidate_aliases = (id, f"{parent.name}.{name}", name)
    for alias in candidate_aliases:
        key = _normalise(alias)
        current_id = registry.aliases.get(key)
        if current_id is not None and current_id != id:
            raise RuntimeErrorML(f"region alias '{alias}' conflicts with an existing plane or region")
    region = PlaneReference(
        id=id, name=name.strip(), category=parent.category,
        data_library=parent.data_library, parent_plane=parent.name,
    )
    registry.regions[id] = region
    for alias in candidate_aliases:
        registry.aliases[_normalise(alias)] = id
    registry.lazy_region_libraries.pop(_normalise(name), None)
    registry.lazy_region_libraries.pop(_normalise(f"{parent.name}.{name}"), None)
    return region


def register_region(
    runtime: Any,
    parent_plane: str | PlaneReference,
    region_id: str,
    name: str,
) -> PlaneReference:
    """Register a player-defined region under an existing top-level plane."""
    registry = get_registry(runtime)
    parent = resolve_plane(registry, parent_plane) if isinstance(parent_plane, (str, PlaneReference)) else None
    if parent is None:
        raise TypeErrorML("region parent must be a registered plane")
    if parent.is_region:
        raise RuntimeErrorML("a region's parent must be a top-level plane")
    if not isinstance(region_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", region_id):
        raise TypeErrorML("region ID must start with a lowercase letter and contain lowercase letters, digits, or underscores")
    if not isinstance(name, str) or not name.strip():
        raise TypeErrorML("region name must be non-empty text")
    if region_id in registry.planes or region_id in registry.regions:
        raise RuntimeErrorML(f"region ID '{region_id}' is already registered")
    qualified = f"{parent.name}.{name.strip()}"
    required_aliases = (region_id, qualified)
    for alias in required_aliases:
        key = _normalise(alias)
        if key in registry.aliases:
            raise RuntimeErrorML(f"region alias '{alias}' conflicts with an existing plane or region")
    region = PlaneReference(
        id=region_id,
        name=name.strip(),
        category=parent.category,
        data_library=parent.data_library,
        parent_plane=parent.name,
    )
    registry.regions[region_id] = region
    registry.aliases[_normalise(region_id)] = region_id
    registry.aliases[_normalise(qualified)] = region_id
    # A short alias is useful when unique, but a same-named region elsewhere
    # must not replace an existing global alias.
    short_key = _normalise(name.strip())
    if short_key not in registry.aliases:
        registry.aliases[short_key] = region_id
    return region


def register_plane(
    runtime: Any,
    plane_id: str,
    name: str,
    category: str,
    *,
    aliases: tuple[str, ...] | list[str] = (),
    data_library: str | None = None,
) -> PlaneReference:
    """Internal identity-only hook for the future ``drafter`` library."""
    registry = get_registry(runtime)
    if not isinstance(plane_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", plane_id):
        raise TypeErrorML("plane ID must start with a lowercase letter and contain lowercase letters, digits, or underscores")
    if not isinstance(name, str) or not name.strip():
        raise TypeErrorML("plane name must be non-empty text")
    if not isinstance(category, str) or not category.strip():
        raise TypeErrorML("plane category must be non-empty text")
    category = " ".join(category.strip().casefold().replace("_", " ").replace("-", " ").split())
    if len(category) > 48 or not re.fullmatch(r"[a-z][a-z0-9 ]*", category):
        raise TypeErrorML("plane category must start with a letter and contain only letters, digits, or spaces")
    if data_library is not None and (
        not isinstance(data_library, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", data_library)
    ):
        raise TypeErrorML("plane data_library must be a library name or null")
    if plane_id in registry.planes or plane_id in registry.regions:
        raise RuntimeErrorML(f"plane ID '{plane_id}' is already registered")
    if isinstance(aliases, str) or not isinstance(aliases, (tuple, list)):
        raise TypeErrorML("plane aliases must be a list of names")
    candidate_aliases = (plane_id, plane_id.replace("_", " "), name.strip(), *aliases)
    normalised: set[str] = set()
    for alias in candidate_aliases:
        if not isinstance(alias, str) or not alias.strip():
            raise TypeErrorML("plane aliases must be non-empty text")
        key = _normalise(alias)
        if key in normalised:
            continue
        if key in registry.aliases:
            raise RuntimeErrorML(f"plane alias '{alias}' is already registered")
        normalised.add(key)
    reference = PlaneReference(
        id=plane_id, name=name.strip(), category=category, data_library=data_library,
    )
    registry.planes[plane_id] = reference
    for alias in candidate_aliases:
        registry.aliases[_normalise(alias)] = plane_id
    return reference


def snapshot_registry(registry: PlaneRegistry) -> dict[str, Any]:
    return {
        "planes": dict(registry.planes),
        "regions": dict(registry.regions),
        "aliases": dict(registry.aliases),
        "pathways": dict(registry.pathways),
        "lazy_region_libraries": dict(registry.lazy_region_libraries),
        "permissions": set(registry.permissions),
    }


def restore_registry(registry: PlaneRegistry, snapshot: dict[str, Any]) -> None:
    registry.planes.clear()
    registry.planes.update(snapshot["planes"])
    registry.regions.clear()
    registry.regions.update(snapshot["regions"])
    registry.aliases.clear()
    registry.aliases.update(snapshot["aliases"])
    registry.pathways.clear()
    registry.pathways.update(snapshot["pathways"])
    registry.lazy_region_libraries.clear()
    registry.lazy_region_libraries.update(snapshot["lazy_region_libraries"])
    registry.permissions.clear()
    registry.permissions.update(snapshot["permissions"])


__all__ = [
    "PlaneReference", "PathwayRecord", "PlaneRegistry", "get_registry", "resolve_plane",
    "register_builtin_region", "register_region", "register_plane", "snapshot_registry", "restore_registry",
    "pathway_key", "_normalise",
]
