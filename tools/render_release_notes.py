"""Render release notes from the current VERSION entry in CHANGELOG.md."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def render_release_notes(version: str, changelog: str) -> str:
    """Return the exact current changelog section as release notes.

    Historical changelog entries are intentionally excluded, preventing a new
    release from publishing old feature lists, installer names, or test counts.
    """
    version = version.strip()
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"Invalid semantic version: {version!r}")
    lines = changelog.splitlines()
    target = f"## [{version}]"
    start = next((i for i, line in enumerate(lines) if line.startswith(target) and (line == target or line.startswith(target + " ") or line.startswith(target + " —"))), None)
    if start is None:
        raise ValueError(f"CHANGELOG.md has no section for current VERSION {version}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## [")), len(lines))
    section = "\n".join(lines[start + 1:end]).strip()
    if not section:
        raise ValueError(f"CHANGELOG section for {version} is empty")
    notes = f"# MANA {version} — Release Notes\n\n{section}\n"
    return notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "release-notes.md")
    parser.add_argument("--check", action="store_true", help="validate current notes without writing an output file")
    args = parser.parse_args()
    try:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        rendered = render_release_notes(version, changelog)
        if args.check:
            print(f"Release notes are available for MANA {version}")
            return 0
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Rendered release notes: {output}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Release notes rendering failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
