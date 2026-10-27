"""Read-only periodic table reference for elemental matter in MANA worlds."""
from __future__ import annotations

from typing import Any

from ..errors import MagicErrorML, PhysicsErrorML, TypeErrorML
from ..materials import ELEMENTS, resolve_element
from ..units import DENSITY, K, Quantity


def _record(value: Any):
    if not isinstance(value, str) or not value.strip():
        raise TypeErrorML("periodic lookup expects an element name or symbol as text")
    item = resolve_element(value)
    if item is None:
        raise MagicErrorML(f"unknown chemical element '{value}'")
    return item


def build_library() -> dict[str, Any]:
    """Expose chemical data without coupling chemistry to the renderer."""
    def lookup(value: str) -> dict[str, Any]:
        return _record(value).as_dict()

    def by_number(value: int) -> dict[str, Any]:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeErrorML("periodic.by_number() expects an integer atomic number")
        if not 1 <= value <= len(ELEMENTS):
            raise PhysicsErrorML(f"atomic number must be between 1 and {len(ELEMENTS)}")
        return ELEMENTS[value - 1].as_dict()

    def all_elements() -> list[dict[str, Any]]:
        return [element.as_dict() for element in ELEMENTS]

    def search(query: str) -> list[dict[str, Any]]:
        if not isinstance(query, str):
            raise TypeErrorML("periodic.search() expects text")
        key = query.strip().casefold()
        if not key:
            raise TypeErrorML("periodic.search() requires a non-empty query")
        return [e.as_dict() for e in ELEMENTS if key in e.name.casefold() or key in e.symbol.casefold() or key in e.category.casefold()]

    def density(value: str) -> Quantity:
        entry = _record(value)
        if entry.density_kg_m3 is None:
            raise MagicErrorML(f"density for {entry.name} is not registered; provide density=... explicitly")
        return Quantity(entry.density_kg_m3, DENSITY)

    def melting_point(value: str):
        point = _record(value).melting_point_k
        return None if point is None else Quantity(point, K)

    def boiling_point(value: str):
        point = _record(value).boiling_point_k
        return None if point is None else Quantity(point, K)

    def symbol(value: str) -> str:
        return _record(value).symbol

    def name(value: str) -> str:
        return _record(value).name

    return {
        "lookup": lookup,
        "by_number": by_number,
        "all": all_elements,
        "search": search,
        "density": density,
        "melting_point": melting_point,
        "boiling_point": boiling_point,
        "symbol": symbol,
        "name": name,
        "count": len(ELEMENTS),
    }
