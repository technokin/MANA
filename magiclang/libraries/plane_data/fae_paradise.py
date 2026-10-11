"""Data library for beings whose home plane is Fae Paradise."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import make_being

BEINGS = [
    make_being(
        "Elf",
        "fairy",
        "Fae Paradise",
        hp=80,
        max_hp=80,
        defence=5,
        attack=11,
    ),
]


def build_library(runtime: Any) -> dict[str, Any]:
    return {"beings": deepcopy(BEINGS)}
