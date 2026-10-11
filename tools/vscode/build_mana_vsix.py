"""Build and validate the local MANA VS Code extension VSIX."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "tools" / "vscode-extension"
OUTPUT_DIR = ROOT / "installers" / "vscode"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUTPUT = OUTPUT_DIR / f"mana-language-{VERSION}.vsix"
ICON_SOURCE = ROOT / "assets" / "branding" / "mana-icon.png"
ICON_PACKAGE_PATH = "images/mana-icon.png"

CONTENT_TYPES = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="vsixmanifest" ContentType="text/xml" />
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="md" ContentType="text/markdown" />
  <Default Extension="txt" ContentType="text/plain" />
  <Default Extension="xml" ContentType="text/xml" />
  <Default Extension="png" ContentType="image/png" />
</Types>
'''

MANIFEST_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="mana-language" Version="__VERSION__" Publisher="mana-language" />
    <DisplayName>MANA Language Support</DisplayName>
    <Description xml:space="preserve">Syntax highlighting, comments, indentation, and snippets for MANA .mana source files.</Description>
    <Tags>programming languages;mana;magic</Tags>
    <Categories>Programming Languages</Categories>
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
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE.txt" />
    <Asset Type="Microsoft.VisualStudio.Services.VSIXPackage" Path="extension.vsixmanifest" Addressable="true" />
  </Assets>
</PackageManifest>
'''


def validate_icon(path: Path) -> None:
    """Validate a square PNG of at least 128 px without an imaging dependency."""
    raw = path.read_bytes()
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Extension icon must be a valid PNG: {path}")
    width, height = struct.unpack(">II", raw[16:24])
    if width != height or width < 128:
        raise ValueError(f"Extension icon must be square and at least 128x128; found {width}x{height}")


def build(check_only: bool = False) -> Path:
    required = [
        EXTENSION / "package.json",
        EXTENSION / "language-configuration.json",
        EXTENSION / "syntaxes" / "mana.tmLanguage.json",
        EXTENSION / "snippets" / "mana.json",
        EXTENSION / "README.md",
        EXTENSION / "LICENSE.txt",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing VS Code extension files: " + ", ".join(missing))

    package = json.loads((EXTENSION / "package.json").read_text(encoding="utf-8"))
    if package.get("version") != VERSION:
        raise ValueError(f"Extension source version must be {VERSION}, found {package.get('version')}")
    if package.get("name") != "mana-language" or package.get("displayName") != "MANA Language Support":
        raise ValueError("VS Code extension id/name must remain aligned with MANA Language Support")

    has_icon = ICON_SOURCE.is_file()
    if has_icon:
        validate_icon(ICON_SOURCE)
        package["icon"] = ICON_PACKAGE_PATH
    else:
        package.pop("icon", None)

    if check_only:
        if not OUTPUT.is_file():
            raise FileNotFoundError(f"VSIX is missing: {OUTPUT.relative_to(ROOT)}")
        with zipfile.ZipFile(OUTPUT) as archive:
            if archive.testzip() is not None:
                raise RuntimeError("VSIX archive integrity check failed")
            built = json.loads(archive.read("extension/package.json"))
            if built.get("version") != VERSION:
                raise RuntimeError("VSIX package version mismatch")
            if bool(built.get("icon")) != has_icon:
                raise RuntimeError("VSIX icon metadata does not match the available branding asset")
            if has_icon and f"extension/{ICON_PACKAGE_PATH}" not in archive.namelist():
                raise RuntimeError("VSIX is missing the configured icon image")
        print(f"Verified {OUTPUT.relative_to(ROOT)}")
        return OUTPUT

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = MANIFEST_TEMPLATE.replace("__VERSION__", VERSION)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("extension.vsixmanifest", manifest)
        for path in sorted(EXTENSION.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(EXTENSION)
            if relative.as_posix() == "package.json":
                archive.writestr(
                    "extension/package.json",
                    json.dumps(package, indent=2, ensure_ascii=False) + "\n",
                )
            else:
                archive.write(path, Path("extension") / relative)
        if has_icon:
            archive.write(ICON_SOURCE, Path("extension") / ICON_PACKAGE_PATH)

    with zipfile.ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("VSIX archive integrity check failed")
        names = set(archive.namelist())
        for required_name in (
            "[Content_Types].xml",
            "extension.vsixmanifest",
            "extension/package.json",
            "extension/syntaxes/mana.tmLanguage.json",
            "extension/snippets/mana.json",
        ):
            if required_name not in names:
                raise RuntimeError(f"VSIX is missing {required_name}")
        built = json.loads(archive.read("extension/package.json"))
        if built.get("version") != VERSION:
            raise RuntimeError("VSIX package version mismatch")
        if bool(built.get("icon")) != has_icon:
            raise RuntimeError("VSIX icon metadata does not match the available branding asset")
        if has_icon and f"extension/{ICON_PACKAGE_PATH}" not in names:
            raise RuntimeError("VSIX is missing the configured icon image")
    print(f"Built and verified {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)")
    return OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the existing VSIX without rebuilding it")
    args = parser.parse_args()
    try:
        build(check_only=args.check)
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"VS Code extension packaging failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
