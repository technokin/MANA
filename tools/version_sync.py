"""Synchronize current release version labels from the repository's VERSION file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
EXTENSION_PACKAGES = (
    ROOT / "tools/vscode-extension/package.json",
    ROOT / "tools/mana-visualiser-extension/package.json",
)
# These files are intentionally historical snapshots. Keep their original facts
# instead of rewriting the version of the source they audited.
HISTORICAL_DOCS = {
    ROOT / "docs/archive/audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md",
    ROOT / "docs/archive/audits/release_reports/MANA_V2_PRE_RELEASE_AUDIT.md",
}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
VERSION_TOKEN = re.compile(r"(?<![0-9])v?(\d+\.\d+\.\d+)(?![0-9])")


def targets() -> list[Path]:
    result = [ROOT / "magiclang/__init__.py", *EXTENSION_PACKAGES]
    for folder in (
        ROOT / "docs/current",
        ROOT / "tools/vscode-extension",
        ROOT / "tools/mana-visualiser-extension",
    ):
        result.extend(path for path in folder.rglob("*.md") if path.is_file())
    result.extend([
        ROOT / "MANA_INTRO.md",
        ROOT / "examples/README.md",
        ROOT / "README.md",
        ROOT / "docs/README.md",
    ])
    return sorted({path for path in result if path.is_file() and path not in HISTORICAL_DOCS})


def is_current_version_line(path: Path, line: str) -> bool:
    """Return true only for lines that label the current release, not history."""
    if any(marker in line for marker in (
        "**Version:**", "**MANA version:**", "**Current source version:**",
        "**Source version:", "**Documentation edition:**", "**Edition:**",
        "**MANA v", "Version rule:", "img.shields.io/badge/version-",
        "Current documentation —",
    )):
        return True
    if ".vsix" in line:
        # Only an actual versioned installer filename is a current label; prose
        # that also mentions a historical release log must remain untouched.
        return bool(re.search(r"mana-(?:language|magic-visualiser)-\d+\.\d+\.\d+\.vsix", line))
    if current_version_match(line):
        return True
    if path == ROOT / "MANA_INTRO.md" and "MANA " in line and " includes " in line and VERSION_TOKEN.search(line):
        return True
    if "implemented in the v" in line and "interpreter" in line:
        return bool(re.search(r"implemented in the v\d+\.\d+\.\d+ interpreter", line, re.IGNORECASE))
    return False



def current_version_match(line: str) -> re.Match[str] | None:
    """Find the version token that labels the current source, not an earlier release.

    Documentation lines may contain both an old release filename and a later
    current-version link. Always select the token associated with the explicit
    current label instead of blindly replacing the first version on the line.
    """
    if "img.shields.io/badge/version-" in line:
        return VERSION_TOKEN.search(line)
    # Version numbers embedded in installer filenames are handled by the
    # installer-specific substitution in sync(); do not match a nearby history
    # filename just because the same line also mentions a VSIX.
    if ".vsix" in line:
        for match in re.finditer(r"mana-(?:language|magic-visualiser)-(\d+\.\d+\.\d+)\.vsix", line):
            return VERSION_TOKEN.search(line, match.start(1))
        return None
    markers = (
        "**Version:**", "**MANA version:**", "**Current source version:**",
        "**Source version:", "**Documentation edition:**", "**Edition:**",
        "**MANA v", "**MANA source/package version:", "Version rule:", "Current documentation —",
        "Declares the implementation package version",
    )
    marker_positions = [(line.find(marker), marker) for marker in markers if marker in line]
    if marker_positions:
        position, marker = min(marker_positions)
        match = VERSION_TOKEN.search(line, position + len(marker))
        if match:
            return match
    current_label = re.search(r"(?<![A-Za-z0-9_./\\-])current\b", line, re.IGNORECASE)
    if current_label:
        tail = line[current_label.end():]
        match = VERSION_TOKEN.search(tail)
        if match:
            between = tail[:match.start()]
            # Do not walk across a sentence/semicolon into a later historical
            # reference just because the word "current" occurred earlier.
            if not re.search(r";|\.\s|\b(?:historical|prior|previous|older)\b", between, re.IGNORECASE):
                return VERSION_TOKEN.search(line, current_label.end())
    if re.search(r"implemented in the v\d+\.\d+\.\d+ interpreter", line, re.IGNORECASE):
        match = re.search(r"\bv?\d+\.\d+\.\d+", line, re.IGNORECASE)
        if match:
            return match
    if line.lstrip().startswith("#") and "MANA" in line:
        return VERSION_TOKEN.search(line)
    return None


def replace_current_version(line: str, version: str) -> str:
    """Update the current version label while preserving historical references."""
    if "img.shields.io/badge/version-" in line:
        return VERSION_TOKEN.sub(
            lambda match: ("v" if match.group(0).startswith("v") else "") + version,
            line,
        )
    if ".vsix" in line:
        return re.sub(
            r"(mana-(?:language|magic-visualiser)-)\d+\.\d+\.\d+(\.vsix)",
            lambda match: f"{match.group(1)}{version}{match.group(2)}",
            line,
        )
    match = current_version_match(line)
    if match is None:
        # A fallback is safe only when the line contains a single version
        # token. On mixed historical/current lines, leave the text untouched
        # rather than silently changing whichever version happens to come first.
        candidates = list(VERSION_TOKEN.finditer(line))
        if len(candidates) != 1:
            return line
        match = candidates[0]
    if not match:
        return line
    prefix = "v" if match.group(0).startswith("v") else ""
    return line[:match.start()] + prefix + version + line[match.end():]


def sync(check: bool = False) -> int:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        print(f"VERSION must contain a plain semantic version, found {version!r}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in targets():
        old = path.read_text(encoding="utf-8")
        if path in EXTENSION_PACKAGES:
            data = json.loads(old)
            if data.get("version") != version:
                if check:
                    errors.append(
                        f"{path.relative_to(ROOT)}: version is {data.get('version')!r}, expected {version}"
                    )
                else:
                    data["version"] = version
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            continue

        lines = old.splitlines(keepends=True)
        updated_lines = []
        for line in lines:
            if is_current_version_line(path, line):
                line = replace_current_version(line, version)
            updated_lines.append(line)
        updated = "".join(updated_lines)
        # The Python implementation package exposes the same single source version.
        updated = re.sub(r'(__version__\s*=\s*)"[^"]+"', rf'\g<1>"{version}"', updated)
        if updated != old:
            if check:
                errors.append(f"{path.relative_to(ROOT)}: stale current version label")
            else:
                path.write_text(updated, encoding="utf-8")

    # These files are intentionally not rewritten; check that readers are told so.
    for path in HISTORICAL_DOCS:
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if "Historical pre-release snapshot" not in content:
            message = f"{path.relative_to(ROOT)}: historical snapshot must be labelled explicitly"
            if check:
                errors.append(message)

    if errors:
        print("Version check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"Version labels {'match' if check else 'synchronized'}: {version}")
    return 0


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--check", action="store_true", help="fail instead of updating stale labels")
    raise SystemExit(sync(cli.parse_args().check))
