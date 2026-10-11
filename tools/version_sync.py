"""Synchronize version labels from the repository's VERSION file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"


def targets() -> list[Path]:
    result = [ROOT / "magiclang/__init__.py", ROOT / "tools/vscode-extension/package.json"]
    for folder in (ROOT / "docs/current", ROOT / "tools/vscode-extension"):
        result.extend(path for path in folder.rglob("*.md") if path.is_file())
    result.extend([ROOT / "MANA_INTRO.md", ROOT / "README.md"])
    return sorted({path for path in result if path.is_file()})


def sync(check: bool = False) -> int:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    errors = []
    for path in targets():
        old = path.read_text(encoding="utf-8")
        if path.name == "package.json":
            data = json.loads(old)
            if data.get("version") != version:
                if check:
                    errors.append(f"{path.relative_to(ROOT)}: version is {data.get('version')!r}, expected {version}")
                else:
                    data["version"] = version
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            continue
        lines = old.splitlines(keepends=True)
        updated_lines = []
        for line in lines:
            is_version_label = (
                "**Version:**" in line
                or "**MANA version:**" in line
                or "**Current source version:**" in line
                or "Version rule:" in line
                or "img.shields.io/badge/version-" in line
                or (line.lstrip().startswith("#") and "MANA" in line and re.search(r"v?0\.\d+\.\d+", line))
                or ("mana-language-" in line and ".vsix" in line)
                or (path.parent == ROOT / "tools/vscode-extension" and "0.10." in line)
            )
            if is_version_label:
                line = re.sub(
                    r"(?<![0-9])(v?)(\d+\.\d+\.\d+)(?![0-9])",
                    lambda match: ("v" if match.group(1) else "") + version,
                    line,
                )
            updated_lines.append(line)
        updated = "".join(updated_lines)
        # The implementation packages use a plain quoted semantic version.
        updated = re.sub(r'(__version__\s*=\s*)"[^"]+"', rf'\g<1>"{version}"', updated)
        if updated != old:
            if check:
                errors.append(f"{path.relative_to(ROOT)}: stale version label")
            else:
                path.write_text(updated, encoding="utf-8")
    if errors:
        print("Version check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"Version labels {'match' if check else 'synchronized'}: {version}")
    return 0


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--check", action="store_true", help="fail instead of updating stale labels")
    raise SystemExit(sync(cli.parse_args().check))
