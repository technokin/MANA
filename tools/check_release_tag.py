"""Check that a GitHub release tag matches the project's VERSION file."""
from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_release_tag(tag: str | None, version: str) -> str | None:
    """Return an error message when ``tag`` is not the tag for ``version``."""
    expected = f"v{version.strip()}"
    actual = (tag or "").strip()
    if actual != expected:
        return f"Release tag {actual!r} does not match VERSION ({expected!r})"
    return None


def main() -> int:
    version_file = ROOT / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip()
    tag = os.environ.get("RELEASE_TAG")
    error = check_release_tag(tag, version)
    if error:
        print(error, file=sys.stderr)
        return 1
    print(f"Releasing MANA {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
