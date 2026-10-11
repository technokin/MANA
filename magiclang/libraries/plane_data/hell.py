"""Data for Hell and its currently defined regions."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

REGIONS = (
    {"id": "hell.naraka", "name": "Naraka", "parent_plane": "hell"},
    {"id": "hell.ten_courts", "name": "The Ten Courts", "parent_plane": "hell"},
    {"id": "hell.yomi_hollows", "name": "Yomi Hollows", "parent_plane": "hell"},
)
BEINGS = []


def build_library(runtime: Any) -> dict[str, Any]:
    from ..planar_registry import register_builtin_region

    for region in REGIONS:
        register_builtin_region(runtime, **region)
    return {"regions": [dict(item) for item in REGIONS], "beings": deepcopy(BEINGS)}
