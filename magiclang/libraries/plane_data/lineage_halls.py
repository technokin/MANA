"""Data library for Lineage Halls."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

BEINGS = []


def build_library(runtime: Any) -> dict[str, Any]:
    return {"beings": deepcopy(BEINGS)}
