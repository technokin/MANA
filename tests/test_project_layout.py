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


def test_documentation_navigation_and_current_snapshot_labels_are_consistent():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index = (ROOT / "docs/current/INDEX.md").read_text(encoding="utf-8")
    assert "[Visualiser graphics and resource use](#visualiser-graphics-and-resource-use)" in readme
    assert "[What can I build with MANA?](#what-can-i-build-with-mana)" in readme
    assert "[Materials, equipment, and body magic](#materials-equipment-and-body-magic)" in readme
    assert "The Visualiser remains a record-and-replay viewer" in readme
    assert "The v2.0.0 Visualiser remains" not in readme
    assert index.count("**Page kind:**") == 1
    assert "**Current source snapshot:**" in index
    assert "**Current release:**" not in index
    for relative in (
        "docs/archive/audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md",
        "docs/archive/audits/release_reports/MANA_V2_PRE_RELEASE_AUDIT.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "current MANA 2.0.0 verification report" in text
        assert "MANA 2.0.0 release report" not in text


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
    visualiser = json.loads((ROOT / "tools/mana-visualiser-extension/package.json").read_text(encoding="utf-8"))
    assert f'__version__ = "{VERSION}"' in package_init
    assert extension["version"] == VERSION
    assert visualiser["version"] == VERSION
    assert (ROOT / "installers/vscode" / f"mana-language-{VERSION}.vsix").is_file()
    assert (ROOT / "installers/vscode" / f"mana-magic-visualiser-{VERSION}.vsix").is_file()
    current_docs = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "docs/current").rglob("*.md"))
    assert not re.search(r"v0\.10\.(?:11|12)\b", current_docs)
    assert VERSION in current_docs
    assert "MANA 2.0.0 Final Verification Report" in (ROOT / "README.md").read_text(encoding="utf-8")
    assert "MANA 2.0 deliberately keeps its world simulation 2D" in (ROOT / "docs/current/foundations/FUTURE_USES_AND_ROADMAP.md").read_text(encoding="utf-8")



def test_historical_audits_are_archived_not_in_current_docs():
    archive = ROOT / "docs/archive/audits/release_reports"
    expected = (
        archive / "MANA_V2_PRE_RELEASE_AUDIT.md",
        archive / "PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md",
    )
    assert all(path.is_file() for path in expected)
    assert not (ROOT / "docs/current/MANA_V2_CHANGE_LOG.md").exists()
    assert not (ROOT / "docs/current/PROJECT_AUDIT_AND_CONSOLIDATION.md").exists()
    current_index = (ROOT / "docs/current/INDEX.md").read_text(encoding="utf-8")
    assert "../archive/audits/release_reports/MANA_V2_PRE_RELEASE_AUDIT.md" in current_index
    assert "../archive/audits/release_reports/PROJECT_AUDIT_AND_CONSOLIDATION_PRE_RELEASE.md" in current_index

def test_version_sync_does_not_mistake_historical_reference_for_current_version():
    from tools.version_sync import is_current_version_line

    mixed_line = (
        "Read the current documentation index for user-facing guides and the "
        "historical v0.10.1 audit for fixes and remaining limitations."
    )
    assert not is_current_version_line(ROOT / "docs/current/internals/COMPONENT_REFERENCE.md", mixed_line)
    explicit_current_label = "Current release: MANA 2.0.0; earlier history is preserved."
    assert is_current_version_line(ROOT / "docs/current/INDEX.md", explicit_current_label)


def test_version_sync_check_is_clean_and_does_not_rewrite_history():
    result = subprocess.run(
        [sys.executable, "tools/version_sync.py", "--check"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    historical = (ROOT / "docs/current/physics/ENERGY_MODEL.md").read_text(encoding="utf-8")
    assert "introduced in v0.6.2" in historical
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "The existing [v1.0.0 release](https://github.com/technokin/MANA/releases/tag/v1.0.0) remains available" in readme
    assert "not a claim that the public v2.0.0 release has been published" not in readme


def test_test_only_mana_fixtures_are_separated_from_test_modules():
    assert (ROOT / "tests/fixtures/release_failure_test.mana").is_file()
    assert not (ROOT / "tests/release_failure_test.mana").exists()
    layout = (ROOT / "docs/current/tooling/PROJECT_LAYOUT.md").read_text(encoding="utf-8")
    assert "tests/fixtures/" in layout
    assert "tools/mana-visualiser-extension/" in layout


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


def _github_heading_id(heading: str) -> str:
    """Match the heading-fragment rules used by GitHub for ordinary headings."""
    heading = re.sub(r"`([^`]*)`", r"\1", heading).casefold()
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = re.sub(r"[^a-z0-9_\s-]", "", heading)
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", heading.strip()))


def test_all_local_markdown_heading_anchors_resolve():
    import urllib.parse

    headings_by_path = {}
    for page in ROOT.rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        heading_ids = set()
        duplicates = {}
        for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, flags=re.MULTILINE):
            base = _github_heading_id(heading)
            if not base:
                continue
            duplicate_number = duplicates.get(base, 0)
            duplicates[base] = duplicate_number + 1
            heading_ids.add(base if duplicate_number == 0 else f"{base}-{duplicate_number}")
        heading_ids.update(re.findall(r"<a\s+id=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE))
        headings_by_path[page.resolve()] = heading_ids

    broken = []
    for page in ROOT.rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        for destination in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            destination = destination.strip().split()[0].strip("<>")
            parts = urllib.parse.urlsplit(destination)
            if parts.scheme or not parts.fragment:
                continue
            target = page.resolve() if not parts.path else (page.parent / urllib.parse.unquote(parts.path)).resolve()
            if target not in headings_by_path:
                continue
            fragment = urllib.parse.unquote(parts.fragment)
            if fragment not in headings_by_path[target]:
                broken.append(f"{page.relative_to(ROOT)} -> {destination}")
    assert not broken, "Broken local Markdown heading anchors:\n" + "\n".join(broken)


def test_all_markdown_local_file_links_resolve():
    import urllib.parse

    broken = []
    for page in ROOT.rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        for destination in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            destination = destination.strip().split()[0].strip("<>")
            parts = urllib.parse.urlsplit(destination)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (page.parent / urllib.parse.unquote(parts.path)).resolve()
            if not target.exists():
                broken.append(f"{page.relative_to(ROOT)} -> {destination}")
    assert not broken, "Broken local Markdown file links:\n" + "\n".join(broken)


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


def test_extension_source_icons_match_canonical_branding():
    canonical = (ROOT / "assets" / "branding" / "mana-icon.png").read_bytes()
    for extension_path in (
        ROOT / "tools" / "vscode-extension" / "images" / "mana-icon.png",
        ROOT / "tools" / "mana-visualiser-extension" / "images" / "mana-icon.png",
    ):
        assert extension_path.is_file(), f"Missing extension logo: {extension_path.relative_to(ROOT)}"
        assert extension_path.read_bytes() == canonical


def test_language_extension_commands_have_explicit_activation_events():
    package = json.loads((ROOT / "tools" / "vscode-extension" / "package.json").read_text(encoding="utf-8"))
    events = set(package.get("activationEvents", []))
    commands = {item["command"] for item in package["contributes"]["commands"]}
    for command in commands:
        assert f"onCommand:{command}" in events, f"Missing activation event for {command}"


def test_source_zip_builder_bundles_both_extensions_and_excludes_cache_noise(tmp_path):
    import zipfile

    output = tmp_path / "MANA-source.zip"
    result = subprocess.run(
        [sys.executable, "tools/package_project_zip.py", "--output", str(output)],
        cwd=ROOT, text=True, capture_output=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        assert f"installers/vscode/mana-language-{VERSION}.vsix" in names
        assert f"installers/vscode/mana-magic-visualiser-{VERSION}.vsix" in names
        assert "MANA_v2.0.0_RELEASE_LOG.md" in names
        assert "docs/current/RELEASE_V2_0_0_REPORT.md" in names
        assert "docs/archive/audits/release_reports/MANA_2_0_2_LOCAL_PACKAGE_REPORT.md" in names
        bundled_vsix = {name for name in names if name.startswith("installers/vscode/") and name.endswith(".vsix")}
        assert bundled_vsix == {
            f"installers/vscode/mana-language-{VERSION}.vsix",
            f"installers/vscode/mana-magic-visualiser-{VERSION}.vsix",
        }
        assert "assets/branding/mana-icon.png" in names
        assert not any("__pycache__" in name or ".pytest_cache" in name or name.endswith(".pyc") for name in names)
        assert len([name for name in names if name.startswith("examples/") and name.endswith(".mana")]) == 67


def test_release_workflow_gates_publication_on_the_full_platform_matrix():
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    tag_checker = (ROOT / "tools/check_release_tag.py").read_text(encoding="utf-8")
    assert "- 'v*'" in workflow
    assert "v2.0.0" not in workflow
    assert "python tools/check_release_tag.py" in workflow
    assert "does not match VERSION" in tag_checker
    assert "os: [ubuntu-latest, windows-latest]" in workflow
    assert "python-version: ['3.12', '3.13', '3.14', '3.15']" in workflow
    assert "needs: verify" in workflow
    assert "python -m pytest -q" in workflow
    assert "tools/benchmark_many_creates.py" in workflow
    assert "tools/package_project_zip.py" in workflow
    assert "tools/render_release_notes.py" in workflow
    assert "dist/release-notes.md" in workflow
    assert "dist/MANA-${VERSION}-source.zip" in workflow
    assert "MANA_v2.0.0_RELEASE_LOG.md" not in workflow
    assert "gh release create" in workflow
    assert "gh release view" in workflow
    assert "gh release upload" in workflow
    assert "--clobber" in workflow
    assert "mana-language-${VERSION}.vsix" in workflow
    assert "mana-magic-visualiser-${VERSION}.vsix" in workflow


def test_release_tag_checker_rejects_wrong_tags():
    from tools.check_release_tag import check_release_tag

    assert check_release_tag(f"v{VERSION}", VERSION) is None
    assert check_release_tag("v2.0.0", "2.0.0") is None
    assert "does not match VERSION" in check_release_tag("v1.0.0", "2.0.0")
    assert "does not match VERSION" in check_release_tag(None, "2.0.0")


def test_release_notes_renderer_uses_only_the_current_changelog_entry():
    from tools.render_release_notes import render_release_notes

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    notes = render_release_notes(VERSION, changelog)
    assert notes.startswith(f"# MANA {VERSION} — Release Notes")
    assert "Motion-path bounds are cached" in notes
    assert "[2.0.2]" not in notes
    assert "MANA_v2.0.0_RELEASE_LOG.md" not in notes
    assert "local source snapshot" not in notes.lower()
    assert "no such public release tags were created" not in notes.lower()
    assert "nothing is published by creating this archive" not in notes.lower()
    assert "current verification for the updated 2.0.0 source snapshot" not in notes.lower()
    try:
        render_release_notes("9.9.9", changelog)
    except ValueError as error:
        assert "no section" in str(error).lower()
    else:
        raise AssertionError("The release-note renderer must reject missing changelog sections")


def test_version_sync_preserves_historical_versions_on_lines_with_current_labels():
    from tools.version_sync import replace_current_version

    line = "The historical v1.0.0 report is retained; current docs describe v1.9.9."
    updated = replace_current_version(line, "2.0.0")
    assert "historical v1.0.0" in updated
    assert "current docs describe v2.0.0" in updated

    ambiguous = "Historical v1.0.0 and previous package v1.5.0 are both mentioned."
    assert replace_current_version(ambiguous, "2.0.0") == ambiguous

    mixed_reference = (
        "`MANA_v2.0.0_RELEASE_LOG.md` is the historical summary; "
        "Current source version: v1.5.0."
    )
    updated_reference = replace_current_version(mixed_reference, "2.0.0")
    assert "MANA_v2.0.0_RELEASE_LOG.md" in updated_reference
    assert "Current source version: v2.0.0" in updated_reference
