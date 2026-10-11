"""Data library for beings whose home plane is Atlantis."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import make_being

BEINGS = [
    make_being(
        "Mermaid",
        "being",
        "Atlantis",
        hp=90,
        max_hp=90,
        defence=5,
        attack=8,
    ),
]


def build_library(runtime: Any) -> dict[str, Any]:
    return {"beings": deepcopy(BEINGS)}
