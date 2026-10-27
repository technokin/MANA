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
  <Default Extension="js" ContentType="application/javascript" />
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
    <Description xml:space="preserve">Write and run MANA .mana programs with syntax colours, contextual inline completions, periodic-table material suggestions and a focused Run action. Pair with MANA Magic Visualiser for the second editor toolbar action.</Description>
    <Tags>programming languages;mana;magic;inline completions;world engine;periodic table</Tags>
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
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE.txt" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/images/mana-icon.png" />
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
        EXTENSION / "extension.js",
        EXTENSION / "language-configuration.json",
        EXTENSION / "syntaxes" / "mana.tmLanguage.json",
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

    readme_text = (EXTENSION / "README.md").read_text(encoding="utf-8")
    if len(readme_text.strip()) < 500:
        raise ValueError("MANA Language Support README is too short to provide useful extension details")
    if "## Features" not in readme_text or "## World-engine language helpers" not in readme_text or "## Install from VSIX" not in readme_text:
        raise ValueError("MANA Language Support README is missing its feature, world-engine, or installation sections")
    if 'Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"' not in MANIFEST_TEMPLATE:
        raise ValueError("MANA Language Support manifest must publish extension/README.md as its Details asset")

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
            names = set(archive.namelist())
            if has_icon and f"extension/{ICON_PACKAGE_PATH}" not in names:
                raise RuntimeError("VSIX is missing the configured icon image")
            if "extension/README.md" not in names:
                raise RuntimeError("VSIX is missing extension/README.md for the Details page")
            readme = archive.read("extension/README.md").decode("utf-8")
            manifest_text = archive.read("extension.vsixmanifest").decode("utf-8")
            if 'Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"' not in manifest_text:
                raise RuntimeError("VSIX Details asset must point to extension/README.md")
            if "## Features" not in readme or "## World-engine language helpers" not in readme or "## Install from VSIX" not in readme:
                raise RuntimeError("VSIX README is missing its feature, world-engine, or installation sections")
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
            # The project-level branding file is the canonical icon. Skip a
            # source-tree copy here because the build writes it once below.
            if relative.as_posix() == ICON_PACKAGE_PATH:
                continue
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
            "extension/extension.js",
            "extension/syntaxes/mana.tmLanguage.json",
            "extension/README.md",
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
        readme = archive.read("extension/README.md").decode("utf-8")
        manifest_text = archive.read("extension.vsixmanifest").decode("utf-8")
        if 'Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"' not in manifest_text:
            raise RuntimeError("VSIX Details asset must point to extension/README.md")
        if "## Features" not in readme or "## World-engine language helpers" not in readme or "## Install from VSIX" not in readme:
            raise RuntimeError("VSIX README is missing its feature, world-engine, or installation sections")
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
