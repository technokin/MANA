from __future__ import annotations

import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from magiclang.runtime import Runtime

ROOT = Path(__file__).resolve().parents[1]


def test_vscode_extension_declares_mana_language_and_grammar():
    extension = ROOT / "tools" / "vscode-extension"
    package = json.loads((extension / "package.json").read_text(encoding="utf-8"))
    language = package["contributes"]["languages"][0]
    grammar = package["contributes"]["grammars"][0]
    assert package["name"] == "mana-language"
    assert package["displayName"] == "MANA Language Support"
    assert package["publisher"] == "mana-language"
    assert package["license"] == "GPL-3.0-only"
    assert language["id"] == "mana"
    assert ".mana" in language["extensions"]
    assert grammar["scopeName"] == "source.mana"
    assert (extension / grammar["path"].removeprefix("./")).is_file()


def test_vsix_package_is_well_formed_and_contains_extension():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    package_path = ROOT / "installers" / "vscode" / f"mana-language-{version}.vsix"
    assert package_path.is_file()
    with zipfile.ZipFile(package_path) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        assert "[Content_Types].xml" in names
        assert "extension.vsixmanifest" in names
        assert "extension/package.json" in names
        assert "extension/syntaxes/mana.tmLanguage.json" in names
        ET.fromstring(archive.read("[Content_Types].xml"))
        ET.fromstring(archive.read("extension.vsixmanifest"))
        package = json.loads(archive.read("extension/package.json"))
        assert package["version"] == version
        if (ROOT / "assets/branding/mana-icon.png").is_file():
            assert package["icon"] == "images/mana-icon.png"
            assert "extension/images/mana-icon.png" in names
        else:
            assert "icon" not in package


def test_function_reference_covers_registered_callable_builtins():
    runtime = Runtime()
    reference = (ROOT / "docs" / "current" / "reference" / "FUNCTION_REFERENCE.md").read_text(encoding="utf-8")
    omitted = []
    for name, value in runtime.global_env.values.items():
        if callable(value) and f"`{name}" not in reference:
            omitted.append(name)
    assert omitted == [], f"built-ins missing from function reference: {omitted}"


def test_workspace_has_only_relevant_mana_tasks():
    tasks = json.loads((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    labels = {task["label"] for task in tasks["tasks"]}
    assert "MANA: Run current file" in labels
    assert "MANA: Check current file" in labels
    assert "MANA: Run tests" in labels
    assert all("Grimoire" not in label for label in labels)


def test_project_version_is_consistent():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    package_init = (ROOT / "magiclang" / "__init__.py").read_text(encoding="utf-8")
    package = json.loads((ROOT / "tools" / "vscode-extension" / "package.json").read_text(encoding="utf-8"))
    assert f'__version__ = "{version}"' in package_init
    assert package["version"] == version


def test_installer_directory_has_only_current_extension_package():
    package_names = sorted(path.name for path in (ROOT / "installers" / "vscode").glob("*.vsix"))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert package_names == [f"mana-language-{version}.vsix"]


def test_vscode_grammar_highlights_library_namespaces_and_public_calls():
    extension = ROOT / "tools" / "vscode-extension"
    grammar = json.loads((extension / "syntaxes" / "mana.tmLanguage.json").read_text(encoding="utf-8"))
    repository = grammar["repository"]
    namespace_pattern = repository["libraryNamespaces"]["patterns"][0]["match"]
    function_patterns = [pattern["match"] for pattern in repository["libraryFunctions"]["patterns"]]
    for name in ("planes", "drafter", "summoning", "necromancy", "geometry2d", "vector3d", "mana"):
        assert name in namespace_pattern
    for name in ("bring", "tame", "send_back", "reanimate", "invoke", "find_route"):
        assert any(name in pattern for pattern in function_patterns), name


def test_mana_example_can_be_run_through_the_documented_entry_point():
    source = ROOT / "examples" / "standalone_release.mana"
    from subprocess import run
    import sys

    result = run([sys.executable, str(ROOT / "mana.py"), str(source)], cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
