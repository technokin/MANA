"""Regression tests for attacker-controlled MANA source and resource usage."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from magiclang.errors import PhysicsErrorML, RuntimeErrorML, SyntaxErrorML, TypeErrorML
from magiclang.lexer import Lexer, MAX_SOURCE_BYTES, MAX_SOURCE_LINES, MAX_TOKEN_COUNT, MAX_STRING_LITERAL_CHARS
from magiclang.parser import Parser
from magiclang.runner import read_mana_source, run_file
from magiclang.runtime import (
    Runtime,
    MAX_CUMULATIVE_ALLOCATION_UNITS,
    MAX_CUMULATIVE_OUTPUT_CHARS,
    MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS,
    MAX_LIBRARY_ARCHIVE_BYTES,
)


def run_source(source: str) -> Runtime:
    runtime = Runtime()
    program = Parser(Lexer(source, "security-test.mana").tokenize(), "security-test.mana").parse()
    runtime.execute(program)
    return runtime


def test_deterministic_malformed_source_fuzzing_only_returns_controlled_errors():
    """Malformed source should never leak an implementation exception."""
    import random
    import string

    from magiclang.errors import MagicLangError

    generator = random.Random(20261023)
    alphabet = string.ascii_letters + string.digits + "_()[]{}:,.'\"+-*/%<>=!#\n \t"
    for index in range(1_200):
        source = "".join(generator.choice(alphabet) for _ in range(generator.randrange(0, 240)))
        filename = f"fuzz-{index}.mana"
        try:
            Parser(Lexer(source, filename).tokenize(), filename).parse()
        except MagicLangError:
            # A normal language diagnostic is an acceptable rejection.
            continue


def test_lexer_rejects_source_over_character_limit_before_tokenization():
    with pytest.raises(SyntaxErrorML, match="character safety limit"):
        Lexer(" " * (MAX_SOURCE_BYTES + 1), "huge.mana")


def test_lexer_rejects_source_that_exceeds_utf8_byte_limit():
    # Character count is under the cap, but UTF-8 representation is over it.
    source = "é" * (MAX_SOURCE_BYTES // 2 + 10)
    with pytest.raises(SyntaxErrorML, match="byte safety limit"):
        Lexer(source, "unicode-huge.mana")


def test_lexer_accepts_crlf_files_under_the_real_line_limit():
    source = "x = 1\r\n" * 30_000
    tokens = Lexer(source, "crlf.mana").tokenize()
    assert tokens[-1].type.name == "EOF"


def test_lexer_rejects_too_many_physical_lines():
    with pytest.raises(SyntaxErrorML, match="line safety limit"):
        Lexer("\n" * (MAX_SOURCE_LINES + 1), "lines.mana")


def test_lexer_rejects_excessive_token_count():
    source = "x=1\n" * (MAX_TOKEN_COUNT // 4 + 100)
    with pytest.raises(SyntaxErrorML, match="token safety limit"):
        Lexer(source, "tokens.mana").tokenize()


def test_lexer_rejects_oversized_string_literal():
    source = "value = '" + ("x" * (MAX_STRING_LITERAL_CHARS + 1)) + "'\n"
    with pytest.raises(SyntaxErrorML, match="string literal exceeds"):
        Lexer(source, "string.mana").tokenize()


def test_file_reader_bounds_bytes_and_rejects_invalid_utf8(tmp_path):
    too_large = tmp_path / "too_large.mana"
    too_large.write_bytes(b"x" * (MAX_SOURCE_BYTES + 1))
    with pytest.raises(SyntaxErrorML, match="byte safety limit"):
        read_mana_source(too_large)

    invalid = tmp_path / "invalid.mana"
    invalid.write_bytes(b"value = '\xff'\n")
    with pytest.raises(SyntaxErrorML, match="not valid UTF-8"):
        read_mana_source(invalid)


def test_file_reader_rejects_non_regular_files(tmp_path):
    folder = tmp_path / "not-a-file.mana"
    folder.mkdir()
    with pytest.raises(SyntaxErrorML, match="regular file"):
        read_mana_source(folder)


def test_direct_host_methods_are_not_exposed_to_mana():
    with pytest.raises(TypeErrorML, match="no MANA property 'extend'"):
        run_source("items = [1]\nitems.extend([2])\n")
    with pytest.raises(TypeErrorML, match="no MANA property 'format'"):
        run_source("result = '{0.__class__}'.format(1)\n")


def test_documented_read_only_library_record_fields_still_work():
    runtime = run_source('load planes\nfire = planes.identify("Fire")\nshown = fire.name\n')
    assert runtime.global_env.get("shown") == "Fire"


def test_cumulative_container_allocations_are_bounded():
    source = (
        "first = [0] * 200000\n"
        "second = [0] * 200000\n"
        "third = [0] * 200000\n"
    )
    with pytest.raises(RuntimeErrorML, match="cumulative allocation safety limit"):
        run_source(source)
    assert MAX_CUMULATIVE_ALLOCATION_UNITS == 500_000


def test_cyclic_values_can_be_rendered_without_recursion_error():
    value = []
    value.append(value)
    rendered = Runtime.display_value(value)
    assert rendered.startswith("[") and "…" in rendered and rendered.endswith("]")


def test_show_output_has_a_cumulative_per_program_budget():
    source = "value = 'a' * 100000\n" + "show(value)\n" * 21
    with redirect_stdout(StringIO()):
        with pytest.raises(RuntimeErrorML, match="cumulative output safety limit"):
            run_source(source)
    assert MAX_CUMULATIVE_OUTPUT_CHARS == 2_000_000


def test_runtime_object_creation_has_a_program_wide_limit():
    source = (
        "i = 0\n"
        "while i < 10001:\n"
        "    object = create Earth\n"
        "    i = i + 1\n"
    )
    with pytest.raises(RuntimeErrorML, match="world-object safety limit"):
        run_source(source)


def test_reused_runtime_has_a_lifetime_allocation_budget():
    runtime = Runtime()
    program = Parser(Lexer("items = [0] * 200000\n", "repeat.mana").tokenize(), "repeat.mana").parse()
    for _ in range(MAX_RUNTIME_CUMULATIVE_ALLOCATION_UNITS // 200_001):
        runtime.execute(program)
    with pytest.raises(RuntimeErrorML, match="runtime exceeded its cumulative allocation safety limit"):
        runtime.execute(program)


def test_old_editor_snippet_source_locations_are_pruned():
    runtime = Runtime()
    for index in range(100):
        source = f"result_{index} = {index}\n"
        filename = f"snippet_{index}.mana"
        program = Parser(Lexer(source, filename).tokenize(), filename).parse()
        runtime.execute(program)
    assert len(runtime._source_locations) < 20


def test_library_archive_size_is_checked_before_zip_parsing(tmp_path):
    libraries = tmp_path / "libraries"
    libraries.mkdir()
    oversized = libraries / "hostile.manalib"
    oversized.write_bytes(b"x" * (MAX_LIBRARY_ARCHIVE_BYTES + 1))
    runtime = Runtime(project_root=tmp_path)
    with pytest.raises(RuntimeErrorML, match="compressed archive limit"):
        runtime._load_library("hostile")


def test_library_symlink_cannot_escape_project_library_directory(tmp_path):
    libraries = tmp_path / "libraries"
    libraries.mkdir()
    outside = tmp_path / "outside.manalib"
    outside.write_bytes(b"not actually a package")
    link = libraries / "external.manalib"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    runtime = Runtime(project_root=tmp_path)
    with pytest.raises(RuntimeErrorML, match="inside the project libraries directory"):
        runtime._load_library("external")


def test_very_large_integer_literal_is_a_controlled_mana_error():
    source = "value = " + ("9" * 10_000) + "\n"
    with pytest.raises(SyntaxErrorML, match="numeric literal exceeds"):
        Lexer(source, "large-integer.mana").tokenize()


def test_extensions_keep_trust_process_and_webview_boundaries():
    root = Path(__file__).resolve().parents[1]
    language = (root / "tools/vscode-extension/extension.js").read_text(encoding="utf-8")
    visualiser = (root / "tools/mana-visualiser-extension/extension.js").read_text(encoding="utf-8")
    for source in (language, visualiser):
        assert "vscode.workspace.isTrusted" in source
        assert "shell: false" in source
        assert "restrictedPythonEnv()" in source
        assert "RUN_TIMEOUT_MS" in source
        assert "MAX_SOURCE_BYTES" in source
    assert "connect-src 'none'" in visualiser
    assert "assertJsonDepth(line)" in visualiser
    assert "validateRecordShape(event, lineNumber)" in visualiser
    assert "crypto.randomUUID()" in visualiser
    assert "workbench.action.toggleMaximizeEditorGroup" in visualiser
    assert "MANA Visualiser recording (JSON Lines)" in visualiser
    assert "innerHTML" not in visualiser


def test_ci_pins_actions_and_audits_dependencies():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in workflow
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in workflow
    assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0" in workflow
    assert "python -m pip_audit --strict -r requirements-dev.txt" in workflow


def test_reexecuting_a_recent_program_preserves_source_diagnostics():
    runtime = Runtime()
    program = Parser(Lexer("value = 1 / 0\n", "repeat-error.mana").tokenize(), "repeat-error.mana").parse()
    for _ in range(2):
        with pytest.raises(PhysicsErrorML) as captured:
            runtime.execute(program)
        assert getattr(captured.value, "filename", None) == "repeat-error.mana"
        assert getattr(captured.value, "line", None) == 1


def test_source_zip_builder_skips_symlink_inputs_and_rejects_symlink_output(tmp_path, monkeypatch):
    import tools.package_project_zip as builder

    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setattr(builder, "ROOT", root)
    outside = tmp_path / "secret.txt"
    outside.write_text("outside project data", encoding="utf-8")
    link = root / "external.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    assert builder.should_include(link) is False
    output_link = tmp_path / "output.zip"
    output_link.symlink_to(outside)
    with pytest.raises(ValueError, match="must not be a symbolic link"):
        builder.build(output_link)
