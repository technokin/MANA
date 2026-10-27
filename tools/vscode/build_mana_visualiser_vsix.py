"""Build and validate the optional MANA Magic Visualiser VSIX."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "tools" / "mana-visualiser-extension"
OUTPUT_DIR = ROOT / "installers" / "vscode"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUTPUT = OUTPUT_DIR / f"mana-magic-visualiser-{VERSION}.vsix"
ICON_SOURCE = ROOT / "assets" / "branding" / "mana-icon.png"
ICON_PACKAGE_PATH = "images/mana-icon.png"

CONTENT_TYPES = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="txt" ContentType="text/plain" />
  <Default Extension="js" ContentType="application/javascript" />
  <Default Extension="css" ContentType="text/css" />
  <Default Extension="html" ContentType="text/html" />
  <Default Extension="png" ContentType="image/png" />
  <Default Extension="xml" ContentType="text/xml" />
</Types>
'''

MANIFEST = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="mana-magic-visualiser" Version="__VERSION__" Publisher="mana-language" />
    <DisplayName>MANA Magic Visualiser</DisplayName>
    <Description xml:space="preserve">Explore recorded MANA magic in a spell-first 2D scene with 32 colour themes, custom colour channels, reusable looks, configurable spell bodies, trails and glyphs, and scalable replay controls. Optional; the language runtime works without this extension.</Description>
    <Tags>mana;magic;visualiser;world engine;physics;periodic table;material simulation;spell replay</Tags>
    <Categories>Visualization;Other</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.80.0" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="workspace" />
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code" /></Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE.txt" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/images/mana-icon.png" />
    <Asset Type="Microsoft.VisualStudio.Services.VSIXPackage" Path="extension.vsixmanifest" Addressable="true" />
  </Assets>
</PackageManifest>
'''


def validate_icon(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Extension icon must be a valid PNG: {path}")
    import struct
    width, height = struct.unpack(">II", raw[16:24])
    if width != height or width < 128:
        raise ValueError(f"Extension icon must be square and at least 128x128; found {width}x{height}")


def build(check_only: bool = False) -> Path:
    required = [EXTENSION / "package.json", EXTENSION / "extension.js", EXTENSION / "README.md",
                EXTENSION / "LICENSE.txt", EXTENSION / "media" / "viewer.js", EXTENSION / "media" / "viewer.css"]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Visualiser extension files: " + ", ".join(missing))
    package = json.loads((EXTENSION / "package.json").read_text(encoding="utf-8"))
    if package.get("version") != VERSION:
        raise ValueError(f"Visualiser version must match VERSION ({VERSION}), got {package.get('version')}")
    if package.get("name") != "mana-magic-visualiser" or package.get("main") != "./extension.js":
        raise ValueError("Unexpected Visualiser package identity or entry point")

    has_icon = ICON_SOURCE.is_file()
    if has_icon:
        validate_icon(ICON_SOURCE)
        package["icon"] = ICON_PACKAGE_PATH
    else:
        package.pop("icon", None)

    if check_only:
        if not OUTPUT.is_file():
            raise FileNotFoundError(f"Visualiser VSIX is missing: {OUTPUT.relative_to(ROOT)}")
        with zipfile.ZipFile(OUTPUT) as archive:
            if archive.testzip() is not None:
                raise RuntimeError("Visualiser VSIX integrity check failed")
            names = set(archive.namelist())
            for name in ("[Content_Types].xml", "extension.vsixmanifest", "extension/package.json",
                         "extension/extension.js", "extension/media/viewer.js", "extension/media/viewer.css"):
                if name not in names:
                    raise RuntimeError(f"Visualiser VSIX is missing {name}")
            built_package = json.loads(archive.read("extension/package.json"))
            if built_package.get("version") != VERSION or built_package.get("name") != package.get("name"):
                raise RuntimeError("Visualiser VSIX metadata mismatch")
            if bool(built_package.get("icon")) != has_icon:
                raise RuntimeError("Visualiser icon metadata does not match the available branding asset")
            if has_icon and f"extension/{ICON_PACKAGE_PATH}" not in names:
                raise RuntimeError("Visualiser VSIX is missing the configured icon image")
            readme = archive.read("extension/README.md").decode("utf-8")
            if len(readme.strip()) < 500:
                raise RuntimeError("Visualiser README is too short to provide useful extension details")
            manifest_text = archive.read("extension.vsixmanifest").decode("utf-8")
            if 'Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"' not in manifest_text:
                raise RuntimeError("VSIX Details asset must point to extension/README.md")
            if "## Scene controls" not in readme or "## World rules, not renderer guesses" not in readme:
                raise RuntimeError("Visualiser README is missing its feature/details sections")
        print(f"Verified {OUTPUT.relative_to(ROOT)}")
        return OUTPUT

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("extension.vsixmanifest", MANIFEST.replace("__VERSION__", VERSION))
        for path in sorted(EXTENSION.rglob("*")):
            if path.is_file() and path.relative_to(EXTENSION).as_posix() != ICON_PACKAGE_PATH:
                archive.write(path, Path("extension") / path.relative_to(EXTENSION))
        if has_icon:
            archive.write(ICON_SOURCE, Path("extension") / ICON_PACKAGE_PATH)
    return build(check_only=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the existing VSIX without rebuilding")
    args = parser.parse_args()
    try:
        path = build(check_only=args.check)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"Visualiser packaging failed: {exc}", file=sys.stderr)
        return 1
    print(f"Visualiser package: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
