"""Data library for the Wild Realm's listed species."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import make_being

BEINGS = [
    make_being("Griffin", "beast", "Wild Realm", hp=180, max_hp=180, defence=14, attack=22),
    make_being("Werewolf", "being", "Wild Realm", hp=150, max_hp=150, defence=11, attack=18),
    make_being("Vampire", "being", "Wild Realm", hp=140, max_hp=140, defence=10, attack=17),
    make_being("Chimera", "beast", "Wild Realm", hp=220, max_hp=220, defence=13, attack=24),
    make_being("Giant", "being", "Wild Realm", hp=300, max_hp=300, defence=20, attack=28),
    make_being("Orc", "being", "Wild Realm", hp=110, max_hp=110, defence=8, attack=14),
]


def build_library(runtime: Any) -> dict[str, Any]:
    return {"beings": deepcopy(BEINGS)}
