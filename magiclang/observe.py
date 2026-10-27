"""Optional JSON Lines recorder for MANA's magic-first Visualiser.

The interpreter is authoritative. This recorder only copies already-computed facts
and is not instantiated during ordinary execution.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from itertools import islice
from threading import Lock
from typing import Any

SCHEMA_VERSION = 1
MAX_RECORDS = 100_000
MAX_RECORDING_BYTES = 25 * 1024 * 1024
MAX_CLEAN_NODES = 20_000


def _clean(
    value: Any, *, depth: int = 0, _budget: list[int] | None = None,
    _active: set[int] | None = None,
) -> Any:
    """Convert event data to bounded JSON primitives without expanding cycles."""
    if _budget is None:
        _budget = [MAX_CLEAN_NODES]
    if _active is None:
        _active = set()
    if _budget[0] <= 0:
        return "[truncated: recording value budget]"
    _budget[0] -= 1
    if depth > 8:
        return "…"
    if value is None:
        return None
    if type(value) is str:
        return value[:2000]
    if type(value) is bool:
        return value
    if type(value) is int:
        if value.bit_length() > 4096:
            return "[integer omitted: exceeds recording limit]"
        return value
    if type(value) is float:
        return value if math.isfinite(value) else None
    if type(value) in (list, tuple, dict):
        marker = id(value)
        if marker in _active:
            return "[cycle]"
        _active.add(marker)
        try:
            if type(value) is list:
                return [_clean(item, depth=depth + 1, _budget=_budget, _active=_active) for item in value[:2000]]
            if type(value) is tuple:
                return [_clean(item, depth=depth + 1, _budget=_budget, _active=_active) for item in value[:2000]]
            result = {}
            for key, item in islice(value.items(), 2000):
                safe_key = key[:200] if type(key) is str else f"<{type(key).__name__}>"
                result[safe_key] = _clean(item, depth=depth + 1, _budget=_budget, _active=_active)
            return result
        finally:
            _active.remove(marker)
    # Do not invoke arbitrary host __str__ implementations in the observation path.
    return f"<{type(value).__name__} omitted>"


class ObservationRecorder:
    """Write a recording without sending data over a network or blocking on a viewer."""

    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._file = self.path.open("w", encoding="utf-8", newline="\n")
        self._disabled = False
        self._warned = False
        self._record_count = 0
        header = json.dumps({"schema": SCHEMA_VERSION, "type": "recording", "application": "MANA Visualiser"}, separators=(",", ":")) + "\n"
        self._file.write(header)
        self._bytes_written = len(header.encode("utf-8"))

    def write(self, event_type: str, time_s: float, payload: dict[str, Any]) -> None:
        # Normalise outside the lock; all externally supplied collections are clipped by _clean.
        try:
            safe_payload = _clean(payload)
            if not isinstance(safe_payload, dict):
                safe_payload = {"payload": safe_payload}
            numeric_time = float(time_s)
            record = {
                **safe_payload,
                # Structural fields always win over payload keys.
                "schema": SCHEMA_VERSION,
                "type": str(event_type)[:100],
                "time": numeric_time if math.isfinite(numeric_time) else 0.0,
            }
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"
            line_bytes = len(line.encode("utf-8"))
        except (OSError, TypeError, ValueError, OverflowError, RecursionError) as exc:
            self._stop_recording(f"could not encode recording event: {exc}")
            return

        # Check limits, write the line, and update both counters atomically.
        # Otherwise concurrent physics callbacks can race past the safety caps.
        reason = None
        try:
            with self._lock:
                if self._disabled or self._file.closed:
                    return
                if self._record_count >= MAX_RECORDS:
                    reason = f"recording reached the {MAX_RECORDS:,}-record safety limit"
                elif self._bytes_written + line_bytes > MAX_RECORDING_BYTES:
                    reason = f"recording reached the {MAX_RECORDING_BYTES // (1024 * 1024)} MB safety limit"
                else:
                    self._file.write(line)
                    self._record_count += 1
                    self._bytes_written += line_bytes
        except (OSError, ValueError) as exc:
            reason = f"recording write failed: {exc}"
        if reason:
            self._stop_recording(reason)

    def _stop_recording(self, reason: str) -> None:
        warn = False
        with self._lock:
            self._disabled = True
            if not self._warned:
                self._warned = True
                warn = True
        if warn:
            print(f"MANA Visualiser recording stopped: {reason}", file=sys.stderr)

    def close(self) -> None:
        error = None
        with self._lock:
            if self._file.closed:
                return
            self._disabled = True
            try:
                self._file.flush()
            except OSError as exc:
                error = exc
            try:
                self._file.close()
            except OSError as exc:
                error = error or exc
            if error is not None and not self._warned:
                self._warned = True
                warn = True
            else:
                warn = False
        if warn:
            print(f"MANA Visualiser recording could not be closed cleanly: {error}", file=sys.stderr)

