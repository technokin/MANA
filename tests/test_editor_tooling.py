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
    assert package_names == sorted([
        f"mana-language-{version}.vsix",
        f"mana-magic-visualiser-{version}.vsix",
    ])


def test_geometry_and_vector_library_completions_include_public_constants():
    source = (ROOT / "tools" / "vscode-extension" / "extension.js").read_text(encoding="utf-8")
    assert "const NAMESPACE_CONSTANTS" in source
    assert "vector3d: ['C', 'PLANCK_TEMPERATURE_K']" in source
    assert "vscode.CompletionItemKind.Constant" in source


def test_spell_declaration_spellings_trigger_editor_auto_indent():
    extension = ROOT / "tools" / "vscode-extension"
    configuration = json.loads((extension / "language-configuration.json").read_text(encoding="utf-8"))
    increase = configuration["indentationRules"]["increaseIndentPattern"]
    on_enter = configuration["onEnterRules"][0]["beforeText"]
    assert "spell" in increase
    assert "spell" in on_enter
    assert "spldef" in increase
    assert "spldef" in on_enter


def test_vscode_grammar_highlights_library_namespaces_and_public_calls():
    extension = ROOT / "tools" / "vscode-extension"
    grammar = json.loads((extension / "syntaxes" / "mana.tmLanguage.json").read_text(encoding="utf-8"))
    repository = grammar["repository"]
    namespace_pattern = repository["libraryNamespaces"]["patterns"][0]["match"]
    function_patterns = [pattern["match"] for pattern in repository["libraryFunctions"]["patterns"]]
    for name in ("planes", "drafter", "summoning", "necromancy", "geometry2d", "vector3d", "mana", "weather"):
        assert name in namespace_pattern
    for name in ("bring", "tame", "send_back", "reanimate", "invoke", "find_route", "configure", "precipitation", "clouds", "lightning"):
        assert any(name in pattern for pattern in function_patterns), name


def test_mana_example_can_be_run_through_the_documented_entry_point():
    source = ROOT / "examples" / "standalone_release.mana"
    from subprocess import run
    import sys

    result = run([sys.executable, str(ROOT / "mana.py"), str(source)], cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr


def test_language_extension_has_only_a_run_toolbar_button_and_inline_completions():
    extension = ROOT / "tools" / "vscode-extension"
    package = json.loads((extension / "package.json").read_text(encoding="utf-8"))
    assert package["main"] == "./extension.js"
    commands = {item["command"]: item for item in package["contributes"]["commands"]}
    assert set(commands) == {"mana.runFile"}
    assert commands["mana.runFile"]["icon"] == "$(play)"
    title_commands = [item["command"] for item in package["contributes"]["menus"]["editor/title"]]
    assert title_commands == ["mana.runFile"]
    assert "snippets" not in package["contributes"]
    source = (extension / "extension.js").read_text(encoding="utf-8")
    assert "registerCompletionItemProvider" in source
    assert "provideCompletionItems" in source
    assert "spawn(python" in source
    assert "shell: false" in source
    assert "debug.startDebugging" not in source
    assert "mana.checkFile" not in source

def test_native_magic_completions_cover_spell_actions_and_summon_contexts():
    extension = ROOT / "tools" / "vscode-extension"
    source = (extension / "extension.js").read_text(encoding="utf-8")
    for fragment in (
        "const PLANES =", "const BEINGS =", "summonSourceContext",
        "summonBeingContext", "Native spell declaration", "Preview and appraise",
        "Cast and commit a spell",
    ):
        assert fragment in source
    grammar = json.loads((extension / "syntaxes" / "mana.tmLanguage.json").read_text(encoding="utf-8"))
    patterns = grammar["repository"]["builtins"]["patterns"]
    assert any(pattern.get("name") == "meta.summon.mana" for pattern in patterns)


def test_visualiser_is_an_opt_in_editor_action():
    extension = ROOT / "tools" / "mana-visualiser-extension"
    package = json.loads((extension / "package.json").read_text(encoding="utf-8"))
    assert "onCommand:manaVisualiser.runWithVisualiser" in package["activationEvents"]
    assert any(command["command"] == "manaVisualiser.runWithVisualiser" and command.get("icon") == "$(eye)"
               for command in package["contributes"]["commands"])
    assert any(item["command"] == "manaVisualiser.runWithVisualiser"
               for item in package["contributes"]["menus"]["editor/title"])
    assert any(item["command"] == "manaVisualiser.openRecording"
               for item in package["contributes"]["menus"]["commandPalette"])
    source = (extension / "extension.js").read_text(encoding="utf-8")
    assert "--record" in source
    assert "showRecording(recording" in source
    assert "Open the partial recording" in source
    assert "if (fs.existsSync(recording))" in source


def test_extension_details_pages_and_branding_are_packaged():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    for package_name in (f"mana-language-{version}.vsix", f"mana-magic-visualiser-{version}.vsix"):
        package_path = ROOT / "installers" / "vscode" / package_name
        with zipfile.ZipFile(package_path) as archive:
            names = set(archive.namelist())
            package = json.loads(archive.read("extension/package.json"))
            manifest = ET.fromstring(archive.read("extension.vsixmanifest"))
            manifest_text = archive.read("extension.vsixmanifest").decode("utf-8")
            readme = archive.read("extension/README.md").decode("utf-8")
            assert len(readme.strip()) >= 500
            assert package["icon"] == "images/mana-icon.png"
            assert "extension/images/mana-icon.png" in names
            assert "Microsoft.VisualStudio.Services.Content.Details" in manifest_text
            assert 'Path="extension/README.md" Addressable="true"' in manifest_text
            assert "Microsoft.VisualStudio.Services.Icons.Default" in manifest_text
            assert manifest.tag.endswith("PackageManifest")


def test_language_extension_has_practical_inline_completions_not_extra_ui_commands():
    extension = ROOT / "tools" / "vscode-extension"
    source = (extension / "extension.js").read_text(encoding="utf-8")
    package = json.loads((extension / "package.json").read_text(encoding="utf-8"))
    for word in ("weave", "post", "release", "conjure", "transmute", "transfigure", "weather.configure"):
        assert word in source
    assert "registerCompletionItemProvider" in source
    assert set(item["command"] for item in package["contributes"]["commands"]) == {"mana.runFile"}
    assert "registerHoverProvider" not in source
    assert "registerCodeActionsProvider" not in source
    assert not (extension / "snippets" / "mana.json").exists()

def test_extension_javascript_parses_with_node_when_available():
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        import pytest
        pytest.skip("Node.js is required for extension JavaScript syntax checks")
    scripts = [
        ROOT / "tools/vscode-extension/extension.js",
        ROOT / "tools/mana-visualiser-extension/extension.js",
        ROOT / "tools/mana-visualiser-extension/media/viewer.js",
    ]
    for script in scripts:
        result = subprocess.run([node, "--check", str(script)], cwd=ROOT, capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, f"{script.relative_to(ROOT)}: {result.stderr}"
