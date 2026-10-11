from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_project_has_clear_separate_readme_and_introduction():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    intro = (ROOT / "MANA_INTRO.md").read_text(encoding="utf-8")
    assert "Python 3.12 or newer" in readme
    assert "requirements-dev.txt" in readme
    assert "GNU General Public License v3.0 only" in readme
    assert "MANA_INTRO.md" in readme
    assert "requirements.txt" in readme
    assert "Ruff" in readme
    assert ".editorconfig" in readme
    assert f"mana-language-{VERSION}.vsix" in readme
    assert "The foundational concepts" in intro
    assert "MANA programs are stored as `.mana`" in intro


def test_current_project_does_not_include_a_custom_ide_or_native_launcher():
    assert not (ROOT / "grimoire.py").exists()
    assert not (ROOT / "grimoire").exists()
    assert not (ROOT / "tools" / "windows").exists()
    assert not (ROOT / ".github" / "workflows" / "windows-grimoire-build.yml").exists()
    assert (ROOT / "tools" / "vscode-extension" / "package.json").is_file()
    assert (ROOT / "mana.py").is_file()
    current_docs = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "docs/current").rglob("*.md"))
    assert "Grimoire" not in current_docs
    assert "grimoire.py" not in current_docs


def test_gitignore_covers_python_environment_and_generated_noise():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ("__pycache__/", ".pytest_cache/", ".venv/", ".env", "dist/", "*.vsix.tmp", ".DS_Store"):
        assert pattern in ignore
    assert ".env.example" in ignore
    assert (ROOT / ".gitattributes").is_file()
    assert (ROOT / "assets/branding/mana-icon.png").is_file()
    # The current VSIX is an intentional distributable and remains in the source ZIP.
    assert (ROOT / "installers" / "vscode" / f"mana-language-{VERSION}.vsix").is_file()


def test_release_version_metadata_and_current_docs_are_consistent():
    package_init = (ROOT / "magiclang/__init__.py").read_text(encoding="utf-8")
    extension = json.loads((ROOT / "tools/vscode-extension/package.json").read_text(encoding="utf-8"))
    assert f'__version__ = "{VERSION}"' in package_init
    assert extension["version"] == VERSION
    current_docs = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "docs/current").rglob("*.md"))
    assert not re.search(r"v0\.10\.(?:11|12)\b", current_docs)
    assert VERSION in current_docs


def test_version_sync_check_is_clean_and_does_not_rewrite_history():
    result = subprocess.run(
        [sys.executable, "tools/version_sync.py", "--check"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    historical = (ROOT / "docs/current/physics/ENERGY_MODEL.md").read_text(encoding="utf-8")
    assert "introduced in v0.6.2" in historical


def test_current_documentation_pages_have_page_kind_metadata():
    current = ROOT / "docs/current"
    missing = [str(path.relative_to(ROOT)) for path in current.rglob("*.md")
               if "**Page kind:**" not in path.read_text(encoding="utf-8")[:350]]
    assert not missing, "Missing page-kind metadata: " + ", ".join(missing)


def test_current_docs_relative_links_resolve():
    broken = []
    for page in (ROOT / "docs/current").rglob("*.md"):
        source = page.read_text(encoding="utf-8")
        for destination in re.findall(r"\]\(([^)]+)\)", source):
            if destination.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = destination.split("#", 1)[0]
            if not clean:
                continue
            target = (page.parent / clean).resolve()
            if not target.exists():
                broken.append(f"{page.relative_to(ROOT)} -> {destination}")
    assert not broken, "Broken current documentation links:\n" + "\n".join(broken)


def test_runnable_cli_syntax_check_does_not_execute_source(tmp_path):
    source = tmp_path / "check_only.mana"
    source.write_text('show("should not run")\n', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "mana.py", "--check", str(source)], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "MANA check passed" in result.stdout
    assert "should not run" not in result.stdout


def test_generated_reference_indexes_are_current():
    for script in ("tools/generate_reference_index.py", "tools/generate_error_catalogue.py", "tools/sync_documentation_outputs.py"):
        result = subprocess.run(
            [sys.executable, script, "--check"], cwd=ROOT,
            text=True, capture_output=True, check=False,
        )
        assert result.returncode == 0, result.stderr


def test_test_suite_uses_unversioned_current_module_names():
    tests = ROOT / "tests"
    for relative_path in ("test_spell_modes.py", "test_energy_model.py", "test_language.py", "test_stress_boundaries.py"):
        assert (tests / relative_path).is_file()
    assert not (tests / "test_grimoire_ide.py").exists()
    assert (ROOT / "ruff.toml").is_file()
    assert not (ROOT / "pyproject.toml").exists()
