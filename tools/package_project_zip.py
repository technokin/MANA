"""Build a clean source ZIP with both official local VS Code extensions included."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DEFAULT_OUTPUT = ROOT / "dist" / f"MANA-{VERSION}-source.zip"
EXCLUDED_DIRS = {
    ".git", ".pytest_cache", "__pycache__", ".ruff_cache", ".mypy_cache",
    ".venv", "venv", ".build-venv", "build", "dist",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp", ".log"}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", ".coverage", "coverage.xml"}
REQUIRED_PACKAGES = (
    Path("installers/vscode") / f"mana-language-{VERSION}.vsix",
    Path("installers/vscode") / f"mana-magic-visualiser-{VERSION}.vsix",
)


def should_include(path: Path) -> bool:
    """Exclude generated/cache noise and all symlinks from the source archive."""
    if path.is_symlink():
        return False
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if relative.parts[:2] == ("installers", "vscode") and path.suffix.lower() == ".vsix":
        return path.name in {item.name for item in REQUIRED_PACKAGES}
    if path.name.endswith(".vsix.tmp"):
        return False
    return path.is_file()


def build(output: Path = DEFAULT_OUTPUT) -> Path:
    requested_output = output.expanduser()
    if requested_output.is_symlink():
        raise ValueError("source ZIP output must not be a symbolic link")
    missing = [str(path) for path in REQUIRED_PACKAGES if not (ROOT / path).is_file() or (ROOT / path).is_symlink()]
    if missing:
        raise FileNotFoundError(
            "Build both VS Code extensions first; missing packages: " + ", ".join(missing)
        )

    output = output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        # Output inside the source tree must be placed under dist/, which is
        # excluded from the input scan so the archive cannot include itself.
        relative_parts = output.relative_to(ROOT).parts if output != ROOT else ()
        if not relative_parts or relative_parts[0] != "dist":
            raise ValueError("source ZIP output inside the project must be placed under dist/")
    output.parent.mkdir(parents=True, exist_ok=True)

    candidates = sorted(path for path in ROOT.rglob("*") if should_include(path))
    if not candidates:
        raise RuntimeError("No project files were found to package")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in candidates:
            archive.write(path, path.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Source ZIP integrity check failed")
        names = set(archive.namelist())
        required = {
            "README.md", "MANA_INTRO.md", "VERSION", "mana.py", "MANA_v2.0.0_RELEASE_LOG.md",
            "docs/current/RELEASE_V2_0_0_REPORT.md",
            "assets/branding/mana-icon.png",
            "tools/vscode-extension/README.md", "tools/mana-visualiser-extension/README.md",
            *(path.as_posix() for path in REQUIRED_PACKAGES),
        }
        missing = sorted(required - names)
        if missing:
            raise RuntimeError("Source ZIP is missing required project files: " + ", ".join(missing))
        noise = [name for name in names if any(part in EXCLUDED_DIRS for part in Path(name).parts)]
        if noise:
            raise RuntimeError("Source ZIP contains generated directories: " + ", ".join(sorted(noise)[:10]))
    print(f"Built {output} ({output.stat().st_size:,} bytes; {len(candidates):,} files)")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="output ZIP path (default: dist/MANA-<version>-source.zip)",
    )
    args = parser.parse_args()
    try:
        build(args.output)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"MANA ZIP packaging failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
