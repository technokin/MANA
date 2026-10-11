"""Data for the thirteen elemental planes and their spirits."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import make_being

ELEMENTAL_PLANES = (
    {
        "id": "fire",
        "name": "Fire",
        "element": "Fire",
        "spirit": "Fire Spirit",
        "hp": 180,
        "defence": 12,
        "attack": 20,
    },
    {
        "id": "water",
        "name": "Water",
        "element": "Water",
        "spirit": "Water Spirit",
        "hp": 180,
        "defence": 14,
        "attack": 18,
    },
    {
        "id": "earth",
        "name": "Earth",
        "element": "Earth",
        "spirit": "Earth Spirit",
        "hp": 240,
        "defence": 22,
        "attack": 19,
    },
    {
        "id": "air",
        "name": "Air",
        "element": "Air",
        "spirit": "Air Spirit",
        "hp": 160,
        "defence": 10,
        "attack": 20,
    },
    {
        "id": "ice",
        "name": "Ice",
        "element": "Ice",
        "spirit": "Ice Spirit",
        "hp": 190,
        "defence": 16,
        "attack": 20,
    },
    {
        "id": "metal",
        "name": "Metal",
        "element": "Metal",
        "spirit": "Metal Spirit",
        "hp": 260,
        "defence": 24,
        "attack": 22,
    },
    {
        "id": "thunder",
        "name": "Thunder",
        "element": "Thunder",
        "spirit": "Thunder Spirit",
        "hp": 175,
        "defence": 11,
        "attack": 27,
    },
    {
        "id": "life",
        "name": "Life",
        "element": "Life",
        "spirit": "Life Spirit",
        "hp": 220,
        "defence": 16,
        "attack": 18,
    },
    {
        "id": "death",
        "name": "Death",
        "element": "Death",
        "spirit": "Death Spirit",
        "hp": 220,
        "defence": 17,
        "attack": 24,
    },
    {
        "id": "underworld",
        "name": "Underworld",
        "element": "Underworld",
        "spirit": "Underworld Spirit",
        "hp": 260,
        "defence": 20,
        "attack": 25,
    },
    {
        "id": "holy",
        "name": "Holy",
        "element": "Holy",
        "spirit": "Holy Spirit",
        "hp": 220,
        "defence": 18,
        "attack": 24,
    },
    {
        "id": "shadow",
        "name": "Shadow",
        "element": "Shadow",
        "spirit": "Shadow Spirit",
        "hp": 200,
        "defence": 15,
        "attack": 24,
    },
    {
        "id": "void",
        "name": "Void",
        "element": "Void",
        "spirit": "Void Spirit",
        "hp": 280,
        "defence": 20,
        "attack": 30,
    },
)

BEINGS = [
    make_being(
        item["spirit"],
        "elemental",
        item["name"],
        element=item["element"],
        hp=item["hp"],
        max_hp=item["hp"],
        defence=item["defence"],
        attack=item["attack"],
    )
    for item in ELEMENTAL_PLANES
]


def build_library(runtime: Any) -> dict[str, Any]:
    beings = deepcopy(BEINGS)
    return {
        "planes": [dict(item) for item in ELEMENTAL_PLANES],
        "beings": beings,
        "spirits": beings,
        "find_being": lambda name: _find(beings, name),
    }


def _find(beings, name):
    if not isinstance(name, str):
        from ...errors import TypeErrorML

        raise TypeErrorML("elemental_planes.find_being() expects a name")
    match = next((being for being in beings if being.name.casefold() == name.casefold()), None)
    if match is None:
        from ...errors import RuntimeErrorML

        raise RuntimeErrorML(f"unknown elemental being '{name}'")
    return match
