"""Benchmark the largest single-program object batch accepted by current safety limits."""
from __future__ import annotations

import argparse
import cProfile
import pstats
import tempfile
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from magiclang.runner import run_file  # noqa: E402 (direct script execution bootstraps the project root)


SOURCE = """spldef many():
    for i in span(9999):
        obj = create Earth
    incant 1
release(many)
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", action="store_true", help="print cumulative profile output")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="mana-benchmark-") as temp:
        path = Path(temp) / "many.mana"
        path.write_text(SOURCE, encoding="utf-8")
        profiler = cProfile.Profile() if args.profile else None
        start = perf_counter()
        if profiler:
            profiler.enable()
        runtime = run_file(str(path))
        if profiler:
            profiler.disable()
        elapsed = perf_counter() - start
        active_count = len(runtime.active_objects)
        if active_count != 9999:
            raise SystemExit(
                f"Benchmark failed: expected 9,999 committed objects, got {active_count}; "
                "inspect the runtime safety limits and release diagnostics."
            )
        print(f"9,999-object release: {elapsed:.3f} s; active objects: {active_count}")
        if profiler:
            pstats.Stats(profiler).strip_dirs().sort_stats("cumtime").print_stats(25)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
