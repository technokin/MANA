"""Plain data records for MANA planes and beings.

Plane-specific data modules are loaded independently by the runtime. They do
not define physics rules or alter how unrelated MANA code executes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from ...elements import ELEMENTS

# Include every core element, plus plane elements not yet part of the core
# object's elemental catalogue. Resistance defaults are present for all of them.
ELEMENT_NAMES = tuple(dict.fromkeys((*ELEMENTS.keys(), "Ice", "Thunder", "Underworld", "Holy", "Shadow")))


@dataclass(frozen=True, slots=True)
class BeingRecord:
    name: str
    kind: str
    home_plane: str
    element: str | None = None
    summoning_requirements: list[str] = field(default_factory=list)
    hp: float | None = None
    max_hp: float | None = None
    defence: float | None = None
    attack: float | None = None
    resistance: dict[str, float] = field(default_factory=dict)

    @property
    def is_being_record(self) -> bool:
        return True


def make_being(
    name: str,
    kind: str,
    home_plane: str,
    *,
    element: str | None = None,
    summoning_requirements: tuple[str, ...] | list[str] = (),
    hp: float | None = None,
    max_hp: float | None = None,
    defence: float | None = None,
    attack: float | None = None,
    resistance: dict[str, float] | None = None,
) -> BeingRecord:
    """Create a validated data record with zero resistance by default."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("being name must be non-empty text")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("being kind must be non-empty text")
    if not isinstance(home_plane, str) or not home_plane.strip() or "." in home_plane:
        raise ValueError("being home_plane must name a plane, not a region")
    if element is not None and (not isinstance(element, str) or not element.strip()):
        raise ValueError("being element tie must be non-empty text or null")
    if isinstance(summoning_requirements, str) or not isinstance(summoning_requirements, (tuple, list)):
        raise ValueError("summoning requirements must be a list of text requirements")
    if any(not isinstance(requirement, str) or not requirement.strip() for requirement in summoning_requirements):
        raise ValueError("summoning requirements must be non-empty text values")
    numeric_fields = {"hp": hp, "max_hp": max_hp, "defence": defence, "attack": attack}
    for field_name, field_value in numeric_fields.items():
        if field_value is None:
            continue  # The owner has not assigned this stat yet.
        if isinstance(field_value, bool) or not isinstance(field_value, (int, float)) or not math.isfinite(float(field_value)) or field_value < 0:
            raise ValueError(f"being {field_name} must be finite and non-negative when assigned")
    if hp is not None and max_hp is not None and hp > max_hp:
        raise ValueError("being hp cannot exceed max_hp")
    resist = {name: 0.0 for name in ELEMENT_NAMES}
    if resistance:
        for element_name, amount in resistance.items():
            if element_name not in resist:
                raise ValueError(f"unknown resistance element '{element_name}'")
            if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not 0 <= amount <= 1:
                raise ValueError("element resistance must be a number from 0 to 1")
            resist[element_name] = float(amount)
    return BeingRecord(
        name=name.strip(),
        kind=kind.strip(),
        home_plane=home_plane.strip(),
        element=element,
        summoning_requirements=list(summoning_requirements),
        hp=None if hp is None else float(hp),
        max_hp=None if max_hp is None else float(max_hp),
        defence=None if defence is None else float(defence),
        attack=None if attack is None else float(attack),
        resistance=resist,
    )


__all__ = ["BeingRecord", "ELEMENT_NAMES", "make_being"]
