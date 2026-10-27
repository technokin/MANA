#!/usr/bin/env python3
"""Create, validate, and package MANA-native .manalib libraries.

A .manalib package contains a JSON manifest and MANA source only. It does not
load Python modules or execute arbitrary host code.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from magiclang.ast_nodes import FunctionDef, LoadLibrary, SkipStatement  # noqa: E402  (the script bootstraps the repository root for direct invocation)
from magiclang.lexer import Lexer  # noqa: E402  (the script bootstraps the repository root for direct invocation)
from magiclang.parser import Parser  # noqa: E402  (the script bootstraps the repository root for direct invocation)
from magiclang.elements import ELEMENTS  # noqa: E402  (the script bootstraps the repository root for direct invocation)
from magiclang.errors import MagicLangError  # noqa: E402  (the script bootstraps the repository root for direct invocation)
from magiclang.runtime import (  # noqa: E402  (the script bootstraps the repository root for direct invocation)
    Runtime, MAX_LIBRARY_ARCHIVE_BYTES, MAX_LIBRARY_ARCHIVE_MEMBERS,
    MAX_LIBRARY_MANIFEST_BYTES, MAX_LIBRARY_UNCOMPRESSED_BYTES,
)
from magiclang.runner import MAX_SOURCE_FILE_BYTES  # noqa: E402

MANIFEST_NAME = "mana-library.json"
ENTRY_DEFAULT = "main.mana"
FORMAT_VERSION = 1
# Keep the builder's reserved-name checks in sync with the interpreter. A package
# that passes validation should not later fail simply because it exports a global
# built-in, a built-in property, or any catalogue element name.
RESERVED_LIBRARY_NAMES = (
    Runtime.LANGUAGE_KEYWORDS
    | Runtime.BUILTIN_NAMES
    | Runtime.RESERVED_PROPERTIES
    | set(ELEMENTS)
    | {
        "magiclang", "system", "python", "os", "sys", "subprocess",
        "ELEMENTS", "FUNDAMENTAL_ELEMENTS", "geometry2d", "vector3d", "planes",
    }
)


def valid_identifier(name: str) -> bool:
    return isinstance(name, str) and bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))


def valid_name(name: str) -> bool:
    return valid_identifier(name) and name not in RESERVED_LIBRARY_NAMES


def _read_bounded_member(folder: Path, relative: str | Path, *, limit: int, label: str) -> bytes:
    """Read one regular package input boundedly and reject symlink/path escapes."""
    root = folder.resolve()
    lexical = root / relative
    # Reject symlink components as well as final symlinks; this makes the bundle
    # independent of files outside the project and avoids following swapped links.
    current = root
    try:
        for component in Path(relative).parts:
            if component in ("", ".", ".."):
                raise ValueError(f"unsafe {label} path")
            current = current / component
            if current.is_symlink():
                raise ValueError(f"{label} cannot be a symbolic link: {relative}")
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
        info = resolved.stat()
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cannot safely access {label}: {exc}") from exc
    except ValueError as exc:
        if "symbolic link" in str(exc) or "unsafe" in str(exc):
            raise
        raise ValueError(f"{label} must remain inside the library folder") from exc
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{label} must be a regular file")
    if info.st_size > limit:
        raise ValueError(f"{label} exceeds the {limit:,}-byte safety limit")
    fd = None
    try:
        # Open the resolved target without following a last-moment symlink swap.
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(resolved, flags)
        opened_info = os.fstat(fd)
        if not stat.S_ISREG(opened_info.st_mode):
            raise ValueError(f"{label} must be a regular file")
        if opened_info.st_size > limit:
            raise ValueError(f"{label} exceeds the {limit:,}-byte safety limit")
        with os.fdopen(fd, "rb") as handle:
            fd = None
            data = handle.read(limit + 1)
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    finally:
        if fd is not None:
            os.close(fd)
    if len(data) > limit:
        raise ValueError(f"{label} exceeds the {limit:,}-byte safety limit")
    return data


def read_package_source(folder: Path):
    folder = folder.expanduser().resolve()
    try:
        manifest_bytes = _read_bounded_member(
            folder, MANIFEST_NAME, limit=MAX_LIBRARY_MANIFEST_BYTES, label=MANIFEST_NAME,
        )
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, OSError) as exc:
        raise ValueError(f"invalid JSON in {MANIFEST_NAME}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"{MANIFEST_NAME} must contain a JSON object")
    if manifest.get("format") != "manalib" or type(manifest.get("format_version")) is not int or manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError("unsupported MANA library package format")
    name = manifest.get("name")
    if not isinstance(name, str) or not valid_name(name):
        raise ValueError("manifest 'name' must be a valid MANA library identifier")
    entry = manifest.get("entry", ENTRY_DEFAULT)
    entry_parts = entry.replace("\\", "/").split("/") if isinstance(entry, str) else []
    if (not isinstance(entry, str) or not entry or len(entry) > 240 or "\x00" in entry
            or Path(entry).is_absolute() or entry.startswith(("/", "\\"))
            or re.match(r"^[A-Za-z]:", entry) or ".." in entry_parts):
        raise ValueError("manifest 'entry' must be a safe relative path inside the library folder")
    source_bytes = _read_bounded_member(
        folder, entry, limit=MAX_SOURCE_FILE_BYTES, label=f"entry source {entry}",
    )
    try:
        source = source_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"entry source {entry} is not valid UTF-8") from exc
    source_path = folder / entry
    program = Parser(Lexer(source, str(source_path)).tokenize(), str(source_path), allow_library_parameters=True).parse()
    illegal = [type(statement).__name__ for statement in program.statements
               if not isinstance(statement, (FunctionDef, LoadLibrary, SkipStatement))]
    if illegal:
        raise ValueError("library top level may contain only def declarations, loads, and skip; found " + ", ".join(illegal))
    declared = {statement.name for statement in program.statements if isinstance(statement, FunctionDef)}
    dependencies = manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise ValueError("manifest 'dependencies' must be a list of library names")
    if any(not valid_identifier(item) or item in Runtime.LANGUAGE_KEYWORDS for item in dependencies):
        raise ValueError("manifest 'dependencies' must contain valid library names")
    if len(dependencies) != len(set(dependencies)):
        raise ValueError("manifest 'dependencies' contains duplicates")
    exports = manifest.get("exports")
    if not isinstance(exports, list) or not exports:
        raise ValueError("manifest 'exports' must be a non-empty list of public function names")
    if any(not valid_identifier(item) or item in Runtime.LANGUAGE_KEYWORDS for item in exports):
        raise ValueError("every exported name must be a valid non-keyword MANA identifier")
    if len(exports) != len(set(exports)):
        raise ValueError("manifest 'exports' contains duplicates")
    missing = sorted(set(exports) - declared)
    if missing:
        raise ValueError("exports have no matching top-level def: " + ", ".join(missing))
    return manifest, entry, source, program


def init_library(name: str, output: Path, *, description: str | None = None) -> Path:
    if not valid_identifier(name):
        raise ValueError("library name must start with a letter or underscore and contain only letters, numbers, and underscores")
    if name in RESERVED_LIBRARY_NAMES:
        raise ValueError(f"library name '{name}' is reserved by MANA")
    folder = output / name
    folder.mkdir(parents=True, exist_ok=False)
    manifest = {
        "format": "manalib",
        "format_version": FORMAT_VERSION,
        "name": name,
        "version": "1.0.0",
        "description": description or f"A MANA-native library named {name}.",
        "entry": ENTRY_DEFAULT,
        "dependencies": [],
        "exports": ["identity"],
    }
    (folder / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / ENTRY_DEFAULT).write_text(
        "# Library helper functions use parameters because they calculate values.\n"
        "# Spell definitions in an ordinary .mana program still use only the element parameter.\n"
        "def identity(value):\n"
        "    incant value\n",
        encoding="utf-8",
    )
    (folder / "README.md").write_text(
        f"# {name}\n\n{manifest['description']}\n\n"
        f"Edit `{ENTRY_DEFAULT}` and `exports` in `{MANIFEST_NAME}`, then build it with:\n\n"
        f"```powershell\npython tools\\library_builder.py validate libraries\\{name}\n"
        f"python tools\\library_builder.py build libraries\\{name}\n```\n",
        encoding="utf-8",
    )
    return folder


def validate_library(folder: Path) -> tuple[dict, str, str, object]:
    folder = folder.resolve()
    manifest, entry, source, program = read_package_source(folder)
    return manifest, entry, source, program


def build_library(folder: Path, output: Path) -> Path:
    folder = folder.expanduser().resolve()
    manifest, entry, source, _program = validate_library(folder)
    output = output.expanduser()
    output.mkdir(parents=True, exist_ok=True)
    output = output.resolve()
    package_path = output / f"{manifest['name']}.manalib"
    if package_path.is_symlink():
        raise ValueError("output package must not be a symbolic link")
    if package_path.exists() and not stat.S_ISREG(package_path.stat().st_mode):
        raise ValueError("output package path must be a regular file")

    # Read all members under strict per-file and total uncompressed limits before
    # creating the archive. writestr() avoids a second unbounded file read.
    members: list[tuple[str, bytes]] = []
    manifest_data = _read_bounded_member(
        folder, MANIFEST_NAME, limit=MAX_LIBRARY_MANIFEST_BYTES, label=MANIFEST_NAME,
    )
    source_data = _read_bounded_member(
        folder, entry, limit=MAX_SOURCE_FILE_BYTES, label=f"entry source {entry}",
    )
    members.extend(((MANIFEST_NAME, manifest_data), (entry, source_data)))
    readme = folder / "README.md"
    if readme.exists() or readme.is_symlink():
        members.append(("README.md", _read_bounded_member(
            folder, "README.md", limit=MAX_LIBRARY_UNCOMPRESSED_BYTES, label="README.md",
        )))
    names = [arcname for arcname, _ in members]
    if len(members) > MAX_LIBRARY_ARCHIVE_MEMBERS or len(names) != len(set(names)):
        raise ValueError("library package has too many or duplicate members")
    if sum(len(data) for _, data in members) > MAX_LIBRARY_UNCOMPRESSED_BYTES:
        raise ValueError(f"library package exceeds the {MAX_LIBRARY_UNCOMPRESSED_BYTES:,}-byte uncompressed safety limit")

    fd, temp_name = tempfile.mkstemp(prefix=f".{manifest['name']}.", suffix=".manalib.tmp", dir=output)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for arcname, data in members:
                archive.writestr(arcname, data)
        if temp_path.stat().st_size > MAX_LIBRARY_ARCHIVE_BYTES:
            raise ValueError(f"compressed library package exceeds the {MAX_LIBRARY_ARCHIVE_BYTES:,}-byte safety limit")
        with zipfile.ZipFile(temp_path, "r") as archive:
            if archive.testzip() is not None:
                raise ValueError("built library archive failed its integrity check")
            bundled_manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8-sig"))
            if bundled_manifest != manifest or entry not in archive.namelist():
                raise ValueError("built library package does not match its source manifest")
        # Replace the output atomically only after the new package is verified; a
        # failed build must not destroy a previously valid .manalib file.
        os.replace(temp_path, package_path)
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError, RecursionError, RuntimeError) as exc:
        temp_path.unlink(missing_ok=True)
        raise ValueError(f"failed to verify built library package: {exc}") from exc
    except ValueError:
        temp_path.unlink(missing_ok=True)
        raise
    return package_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate MANA-native .manalib packages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="create a starter library folder")
    init_cmd.add_argument("name")
    init_cmd.add_argument("--output", type=Path, default=ROOT / "libraries")
    init_cmd.add_argument("--description")

    validate_cmd = subparsers.add_parser("validate", help="validate a source library before building")
    validate_cmd.add_argument("source", type=Path)

    build_cmd = subparsers.add_parser("build", help="validate and package a source library")
    build_cmd.add_argument("source", type=Path)
    build_cmd.add_argument("--output", type=Path, default=ROOT / "libraries")

    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            folder = init_library(args.name, args.output.resolve(), description=args.description)
            print(f"Created starter library: {folder}")
            print(f"Next: python tools/library_builder.py validate {folder}")
        elif args.command == "validate":
            manifest, entry, _source, program = validate_library(args.source)
            function_count = sum(isinstance(statement, FunctionDef) for statement in program.statements)
            print(f"Library '{manifest['name']}' is valid: {function_count} function(s), {len(manifest['exports'])} export(s), entry {entry}")
        elif args.command == "build":
            package = build_library(args.source, args.output.resolve())
            print(f"Built and verified: {package}")
        return 0
    except MagicLangError as exc:
        location = f"{exc.filename}:{exc.line}:{exc.column}" if exc.line is not None else exc.filename
        print(f"LibraryBuildError: {location}: {exc.message}", file=sys.stderr)
        return 1
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"LibraryBuildError: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
