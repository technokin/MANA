from __future__ import annotations

import json
from pathlib import Path
import re
import zipfile

import pytest

from magiclang.errors import MagicErrorML, MagicLangError, PhysicsErrorML, RuntimeErrorML, SyntaxErrorML, TypeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runner import run_file
from magiclang.runtime import Runtime
from magiclang.units import KG, M, S, ENERGY, Quantity, parse_unit, parse_unit_info
from tools.library_builder import validate_library


def run_source(source: str, *, filename: str = "<audit-test>.mana", project_root: Path | None = None) -> Runtime:
    runtime = Runtime(project_root=project_root)
    program = Parser(Lexer(source, filename).tokenize(), filename).parse()
    runtime.execute(program)
    return runtime


def make_library_archive(project_root: Path, name: str, manifest: object, *, extra_members: int = 0) -> Path:
    libraries = project_root / "libraries"
    libraries.mkdir(parents=True, exist_ok=True)
    package_path = libraries / f"{name}.manalib"
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mana-library.json", json.dumps(manifest))
        archive.writestr("main.mana", "def identity(value):\n    incant value\n")
        for index in range(extra_members):
            archive.writestr(f"resources/file_{index}.txt", "")
    return package_path


def test_overflow_and_nonfinite_arithmetic_are_mana_errors_with_location():
    with pytest.raises(PhysicsErrorML, match="outside the supported numeric range") as overflow:
        run_source("x = 2.5 ** 1e308\n", filename="overflow.mana")
    assert overflow.value.filename == "overflow.mana"
    assert overflow.value.line == 1
    assert overflow.value.column == 1

    with pytest.raises(PhysicsErrorML, match="must be finite"):
        run_source("x = 1e308 * 10\n", filename="infinite.mana")


def test_bad_unary_operands_are_mana_errors_not_python_type_errors():
    for source in (
        "stone = create Earth\nx = -stone\n",
        'load geometry2d\nx = -geometry2d.direction(1, 0)\n',
        "x = -[1, 2]\n",
        "x = -'a'\n",
    ):
        with pytest.raises(TypeErrorML):
            run_source(source)


def test_oversized_integer_display_raises_a_mana_error():
    with pytest.raises(RuntimeErrorML, match="too large to display"):
        run_source("x = 2 ** 100000\nshow(x)\n", filename="bigint.mana")


def test_display_name_and_object_kind_reject_non_text_values():
    with pytest.raises(TypeErrorML, match="display_name must be non-empty text"):
        run_source("stone = create Earth\nstone.display_name = stone\n")
    with pytest.raises(TypeErrorML, match="object_kind must be non-empty text"):
        run_source("stone = create Earth\nstone.object_kind = stone\n")


def test_self_combine_is_rejected_instead_of_double_counting():
    with pytest.raises(MagicErrorML, match="two distinct objects"):
        run_source("stone = create Earth\nresult = combine(stone, stone)\n")


def test_utf8_bom_source_files_run(tmp_path):
    path = tmp_path / "bom_file.mana"
    path.write_text("\ufeffvalue = 42\nshow(value)\n", encoding="utf-8")
    run_file(str(path))


def test_multiline_expressions_inside_brackets_are_supported(capsys):
    run_source("value = (1 +\n         2)\nshow(value)\n")
    assert capsys.readouterr().out.strip() == "3"


def test_mixed_tabs_and_spaces_in_indentation_are_rejected():
    with pytest.raises(SyntaxErrorML, match="mixed tabs and spaces"):
        Lexer("if true:\n\tshow(1)\n    show(2)\n").tokenize()


def test_words_outside_the_mana_language_are_not_identified():
    for source, word in (
        ("import planes\n", "import"),
        ("return 5\n", "return"),
        ("print(1)\n", "print"),
        ("break\n", "break"),
        ("range(3)\n", "range"),
        ("x = None\n", "None"),
        ("x = [i for i in span(3)]\n", "for"),
    ):
        with pytest.raises(MagicLangError, match=f"'{word}' is not identified"):
            run_source(source, filename="unknown_word.mana")


def test_second_incant_warns_that_following_statement_is_unreachable(capsys):
    source = "def helper():\n    incant 1\n    incant 2\n"
    Parser(Lexer(source, "incant.mana").tokenize(), "incant.mana").parse()
    warning = capsys.readouterr().err
    assert "Warning: incant.mana:2:5: statement after incant is unreachable" in warning


def test_unknown_events_use_mana_warnings_with_source_locations(capsys):
    run_source("when impct:\n    pass\n", filename="event_handler.mana")
    handler_warning = capsys.readouterr().err
    assert "Warning: event_handler.mana:1:1: unknown MANA event 'impct'" in handler_warning
    assert "RuntimeWarning" not in handler_warning
    assert "magiclang/runtime.py" not in handler_warning

    run_source("emit('typo')\n", filename="event_call.mana")
    emit_warning = capsys.readouterr().err
    assert "Warning: event_call.mana:1:1: unknown MANA event 'typo'" in emit_warning
    assert "RuntimeWarning" not in emit_warning


def test_non_base_element_creation_requires_plane_invocation():
    with pytest.raises(MagicErrorML, match="requires 'load planes'"):
        run_source("life = create Life\n", filename="life_without_planes.mana")

    with pytest.raises(MagicErrorML, match=r'planes\.invoke\("Life"\)'):
        run_source('load planes\nlife = create Life\n', filename="life_without_invocation.mana")

    runtime = run_source(
        'load planes\nplanes.invoke("Life")\nlife = create Life\n',
        filename="life_invoked.mana",
    )
    life = runtime.global_env.get("life")
    assert life.element == "Life"
    assert life.properties["object_kind"] == "element"

    with pytest.raises(MagicErrorML, match=r'planes\.invoke\("Ice"\)'):
        run_source('load planes\nice = create Ice\n', filename="ice_without_invocation.mana")

    invoked_ice = run_source(
        'load planes\nplanes.invoke("Ice")\nice = create Ice\n',
        filename="ice_invoked.mana",
    ).global_env.get("ice")
    assert invoked_ice.element == "Ice"


def test_ice_can_be_composed_from_water_and_air_without_invocation():
    runtime = run_source(
        "water = create Water\nair = create Air\nheat(water, 100 K)\nice = combine(water, air)\n"
    )
    ice = runtime.global_env.get("ice")
    assert ice.properties["material"] == "Ice"


def test_collapsed_into_exists_before_collapse():
    runtime = run_source("stone = create Earth\nshow stone.collapsed_into\n")
    assert runtime.global_env.get("stone").properties["collapsed_into"] is None


def test_reserved_special_commands_report_a_consistent_message():
    with pytest.raises(SyntaxErrorML, match="'show' is reserved"):
        Parser(Lexer("show = 1\n").tokenize()).parse()
    with pytest.raises(MagicLangError, match="'post' is reserved"):
        run_source("post = 1\n")
    with pytest.raises(MagicLangError, match="'release' is reserved"):
        run_source("release = 1\n")


def test_si_prefixes_convert_values_to_base_si():
    assert parse_unit("km") == M
    assert parse_unit("ms") == S
    assert parse_unit("MJ") == ENERGY
    assert parse_unit("g") == KG
    assert parse_unit_info("km") == (M, 1000.0)

    runtime = Runtime()
    program = Parser(Lexer("a = 1 km\nb = 3 ms\nenergy_amount = 1 MJ\nd = 2 g\n").tokenize()).parse()
    runtime.execute(program)
    assert runtime.global_env.get("a") == Quantity(1000, M)
    assert runtime.global_env.get("b") == Quantity(0.003, S)
    assert runtime.global_env.get("energy_amount") == Quantity(1_000_000, ENERGY)
    assert runtime.global_env.get("d") == Quantity(0.002, KG)


def test_unknown_units_have_direct_error_messages_and_celsius_is_absolute_temperature():
    with pytest.raises(UnitErrorML, match="unknown unit 'furlong'"):
        Parser(Lexer("travel_distance = 1 furlong\n").tokenize()).parse()
    runtime = run_source("temperature = 20 C\nnegative_temperature = -10 C\n")
    temperature = runtime.global_env.get("temperature")
    negative = runtime.global_env.get("negative_temperature")
    assert temperature == Quantity(293.15, "K")
    assert temperature.is_absolute_temperature
    assert negative == Quantity(263.15, "K")
    assert negative.is_absolute_temperature


def test_heat_and_cool_require_temperature_changes_not_absolute_celsius():
    with pytest.raises(UnitErrorML, match="temperature change in K"):
        run_source("stone = create Earth\nheat(stone, 20 C)\n")
    with pytest.raises(UnitErrorML, match="temperature change in K"):
        run_source("stone = create Earth\ncool(stone, 20 C)\n")
    runtime = run_source("stone = create Earth\nstone.temp = 20 C\nheat(stone, 5 K)\n")
    assert runtime.global_env.get("stone").properties["temp"] == Quantity(298.15, "K")


def test_dimension_errors_name_the_dimension_and_plain_number():
    with pytest.raises(TypeErrorML, match="quantity in m with a plain number"):
        run_source("value = 5 m + 3\n")
    with pytest.raises(TypeErrorML, match="quantity in K with a plain number"):
        run_source("value = 5 K > 3\n")


def test_source_position_is_attached_to_runtime_errors():
    with pytest.raises(PhysicsErrorML) as err:
        run_source("value = 1\nresult = 1 / 0\n", filename="position.mana")
    assert err.value.filename == "position.mana"
    assert err.value.line == 2
    assert err.value.column == 1


def test_definition_recursion_hits_mana_limit_instead_of_python_recursion(capsys):
    # release() is a standalone command, so this specifically exercises re-entry.
    runtime = Runtime()
    source = 'spldef loop():\n    release(loop)\nrelease(loop)\n'
    runtime.execute(Parser(Lexer(source, "recursive.mana").tokenize(), "recursive.mana").parse())
    output = capsys.readouterr().out
    assert "MANA definition call depth exceeded the safety limit" in output
    assert "RecursionError" not in output


def test_malformed_manifest_schema_is_reported_cleanly_by_builder(tmp_path):
    folder = tmp_path / "bad_library"
    folder.mkdir()
    (folder / "mana-library.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a JSON object"):
        validate_library(folder)


def test_malformed_manifest_schema_is_a_mana_error_on_import(tmp_path):
    manifest = []
    make_library_archive(tmp_path, "badpack", manifest)
    with pytest.raises(RuntimeErrorML, match="manifest must be a JSON object"):
        run_source('load badpack\n', filename="import.mana", project_root=tmp_path)


def test_library_archive_member_limit_is_enforced(tmp_path):
    manifest = {
        "format": "manalib", "format_version": 1, "name": "bigpack",
        "version": "1.0.0", "description": "test", "entry": "main.mana",
        "exports": ["identity"],
    }
    make_library_archive(tmp_path, "bigpack", manifest, extra_members=130)
    with pytest.raises(RuntimeErrorML, match="member archive limit"):
        run_source('load bigpack\n', project_root=tmp_path)


def test_runtime_documented_operations_have_basic_regression_coverage():
    runtime = run_source('\nload geometry2d\nstone = create Earth\nsource = create Earth\nmove(source, 2 m, geometry2d.direction(1, 0))\nexpand(stone, 2 m3)\ncompress(stone, 200000 Pa)\ntransform(stone, "solid")\nshow detect(stone, "mass")\nshow has_domain(stone, "strength")\npull(stone, source, 1 N)\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["volume"] == Quantity(2, runtime.global_env.get("stone").properties["volume"].dimension)
    assert stone.properties["pressure"] == Quantity(200000, stone.properties["pressure"].dimension)


def test_reserved_measurement_names_cannot_be_variables():
    for name in ("distance", "magnitude", "aim"):
        with pytest.raises(RuntimeErrorML, match=f"'{name}' is reserved"):
            run_source(f"{name} = 3\n")


def test_function_reference_examples_are_runnable_individually():
    project_root = Path(__file__).resolve().parents[1]
    reference = project_root / "docs" / "current" / "reference" / "FUNCTION_REFERENCE.md"
    content = reference.read_text(encoding="utf-8")
    examples = re.findall(r"```mana\n(.*?)\n```", content, flags=re.DOTALL)
    assert len(examples) >= 50, "the function reference should have a runnable example for each entry"
    for index, source in enumerate(examples, start=1):
        run_source(
            source + "\n",
            filename=f"function_reference_example_{index}.mana",
            project_root=project_root,
        )


def test_trace_summary_mode_suppresses_per_change_detail(monkeypatch, capsys):
    monkeypatch.setenv("MANA_TRACE_DETAIL", "summary")
    run_source('spldef warm():\n    stone = create Earth\n    heat(stone, 10 K)\n    incant stone\npost(warm)\n')
    output = capsys.readouterr().out
    assert "[POST warm]" in output
    assert "stone.temp:" not in output


def test_vscode_grammar_is_present_and_unwanted_ide_files_are_absent():
    project_root = Path(__file__).resolve().parents[1]
    grammar_path = project_root / "tools" / "vscode-extension" / "syntaxes" / "mana.tmLanguage.json"
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    serialized = json.dumps(grammar)
    assert "last_collisions" in serialized
    assert (project_root / "mana.py").is_file()
    assert not (project_root / "grimoire.py").exists()
    assert not (project_root / "tools" / "windows").exists()


def test_wrong_typed_builtin_arguments_never_leak_host_exceptions():
    # A compact deterministic fuzz corpus across the public operation surface.
    # Every invalid call should fail with a MANA diagnostic, never raw Python.
    invalid_calls = (
        "shape('not-object', circle)",
        "move('not-object', 1 m)",
        "velocity('not-object', 2 m/s)",
        "accelerate('not-object', 2 m/s2)",
        "decelerate('not-object', 2 m/s2)",
        "heat('not-object', 2 K)",
        "cool('not-object', 2 K)",
        "detect('not-object')",
        "bind('not-object')",
        "combine('not-object', 'not-object')",
        "separate('not-object')",
        "transform('not-object', 'solid')",
        "compress('not-object', 2 Pa)",
        "expand('not-object', 2 m3)",
        "momentum('not-object')",
        "kinetic_energy('not-object')",
        "force('not-object')",
        "pressure('not-object', 1 m2)",
        "has_domain('not-object', 'strength')",
        "matter_to_mana('bad-mass')",
        "mana_to_matter('bad-mana')",
        "mana_to_energy('bad-mana')",
        "energy_to_mana('bad-energy')",
        "rotate('not-object', 1)",
        "scale('not-object', 2)",
        "push('not-object', 1 N)",
        "pull('not-object', 'not-object', 1 N)",
        "reflect('not-object', 1)",
        "split('not-object', 2)",
        "anchor('not-object')",
        "unanchor('not-object')",
        "dispel('not-object')",
        "last_collisions('extra')",
        "sqrt('bad-number')",
        "span('bad-number')",
        "advance_time('bad-duration')",
    )
    for source in invalid_calls:
        with pytest.raises(MagicLangError):
            run_source(source + "\n", filename="wrong_builtin_argument.mana")


def test_library_archive_uncompressed_size_limit_is_enforced(tmp_path):
    manifest = {
        "format": "manalib", "format_version": 1, "name": "largepack",
        "version": "1.0.0", "description": "test", "entry": "main.mana",
        "exports": ["identity"],
    }
    package_path = make_library_archive(tmp_path, "largepack", manifest)
    with zipfile.ZipFile(package_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("resources/large.txt", b"x" * 2_000_001)
    with pytest.raises(RuntimeErrorML, match="uncompressed size limit"):
        run_source('load largepack\n', project_root=tmp_path)


def test_incant_accepts_parenthesized_expressions():
    for expression in ("(a + b) / 2", "((a + b) / 2)"):
        runtime = run_source(
            f"def mid(a, b):\n    incant {expression}\nvalue = mid(2, 6)\n",
            filename="incant_expression.mana",
        )
        assert runtime.global_env.get("value") == 4


def test_span_zero_step_raises_located_mana_error():
    with pytest.raises(RuntimeErrorML, match=r"span\(\) step cannot be zero") as error:
        run_source("value = span(0, 10, 0)\n", filename="span_zero.mana")
    assert error.value.filename == "span_zero.mana"
    assert error.value.line == 1
    assert error.value.column == 1


def test_library_load_cycles_raise_mana_error_with_cycle(tmp_path):
    def package(name, source):
        libraries = tmp_path / "libraries"
        libraries.mkdir(exist_ok=True)
        path = libraries / f"{name}.manalib"
        manifest = {
            "format": "manalib", "format_version": 1, "name": name,
            "version": "1.0.0", "entry": "main.mana", "dependencies": [], "exports": ["identity"],
        }
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("mana-library.json", json.dumps(manifest))
            archive.writestr("main.mana", source + "\ndef identity(value):\n    incant value\n")
    package("cyc_a", "load cyc_b")
    package("cyc_b", "load cyc_a")
    with pytest.raises(RuntimeErrorML, match=r"cyc_a -> cyc_b -> cyc_a"):
        run_source("load cyc_a\n", filename="cycle.mana", project_root=tmp_path)


def test_self_loading_library_raises_mana_error(tmp_path):
    libraries = tmp_path / "libraries"
    libraries.mkdir()
    manifest = {
        "format": "manalib", "format_version": 1, "name": "self_cycle",
        "version": "1.0.0", "entry": "main.mana", "dependencies": [], "exports": ["identity"],
    }
    with zipfile.ZipFile(libraries / "self_cycle.manalib", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mana-library.json", json.dumps(manifest))
        archive.writestr("main.mana", "load self_cycle\ndef identity(value):\n    incant value\n")
    with pytest.raises(RuntimeErrorML, match=r"self_cycle -> self_cycle"):
        run_source("load self_cycle\n", filename="self_cycle.mana", project_root=tmp_path)


def test_planar_element_names_are_reserved_identifiers():
    for name in ("Ice", "Thunder", "Underworld", "Holy", "Shadow"):
        with pytest.raises(RuntimeErrorML, match="reserved"):
            run_source(f"{name} = 5\n", filename="reserved_element.mana")


def test_reopening_bidirectional_path_in_reverse_is_idempotent():
    runtime = Runtime()
    runtime.execute(Parser(Lexer("load planes\n").tokenize()).parse())
    planes = runtime.global_env.get("planes")
    assert planes.values["open_path"]("Fire", "Water") is True
    assert planes.values["open_path"]("Water", "Fire") is False


def test_span_with_extreme_bounds_raises_a_mana_error():
    with pytest.raises(RuntimeErrorML, match="safety iteration limit"):
        run_source("value = span(0, 10 ** 100)\n", filename="span_huge.mana")


def test_library_builder_reports_located_mana_errors_without_traceback(tmp_path):
    import subprocess
    import sys

    folder = tmp_path / "broken_library"
    folder.mkdir()
    manifest = {
        "format": "manalib", "format_version": 1, "name": "broken_library",
        "version": "1.0.0", "entry": "main.mana", "dependencies": [], "exports": ["identity"],
    }
    (folder / "mana-library.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "main.mana").write_text("def identity(value):\n    incant (value +\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "tools/library_builder.py", "validate", str(folder)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=10,
    )
    assert result.returncode != 0
    assert "main.mana" in result.stderr
    assert "SyntaxErrorML" in result.stderr or "expected" in result.stderr
    assert "Traceback" not in result.stderr


def test_vscode_grammar_highlights_geometry_libraries():
    grammar = Path(__file__).resolve().parents[1] / "tools/vscode-extension/syntaxes/mana.tmLanguage.json"
    content = grammar.read_text(encoding="utf-8")
    assert "geometry2d" in content
    assert "vector3d" in content


def test_documented_my_geometry_library_builds_and_loads(tmp_path):
    from tools.library_builder import build_library

    folder = tmp_path / "my_geometry"
    folder.mkdir()
    manifest = {
        "format": "manalib", "format_version": 1, "name": "my_geometry",
        "version": "1.0.0", "description": "Extra geometry helpers", "entry": "main.mana",
        "exports": ["twice", "midpoint_value"],
    }
    (folder / "mana-library.json").write_text(json.dumps(manifest), encoding="utf-8")
    (folder / "main.mana").write_text(
        "def twice(value):\n    incant value * 2\n\n"
        "def midpoint_value(a, b):\n    incant (a + b) / 2\n",
        encoding="utf-8",
    )
    package = build_library(folder, tmp_path / "libraries")
    runtime = run_source(
        "load my_geometry\na = my_geometry.twice(21)\nb = my_geometry.midpoint_value(2, 6)\n",
        filename="library_use.mana", project_root=tmp_path,
    )
    assert package.is_file()
    assert runtime.global_env.get("a") == 42
    assert runtime.global_env.get("b") == 4


def test_error_objects_expose_stable_machine_readable_diagnostics():
    with pytest.raises(RuntimeErrorML) as caught:
        run_source("show(misspelled_value)\n", filename="diagnostic.mana")
    diagnostic = caught.value.to_diagnostic()
    assert diagnostic["severity"] == "error"
    assert diagnostic["code"] == "M3000"
    assert diagnostic["filename"] == "diagnostic.mana"
    assert diagnostic["line"] == 1
    assert diagnostic["column"] == 1
    assert diagnostic["message"] == "'misspelled_value' is not identified"
    assert diagnostic["hint"] is None


def test_unknown_name_can_suggest_a_close_mana_name():
    with pytest.raises(RuntimeErrorML) as caught:
        run_source("show(heet)\n", filename="hint.mana")
    assert caught.value.hint == "Did you mean 'heat'?"


def test_span_fuzz_never_leaks_host_exceptions():
    import random

    rng = random.Random(0x4D414E41)
    atoms = ["0", "1", "-2", "3.5", "true", "false", "'bad'", "[1]", "span(2)"]
    for _ in range(2000):
        argc = rng.randint(0, 4)
        args = [rng.choice(atoms) for _ in range(argc)]
        source = f"result = span({', '.join(args)})\n"
        try:
            run_source(source, filename="span_fuzz.mana")
        except MagicLangError:
            continue
        except Exception as exc:  # Any host exception is a test failure.
            pytest.fail(f"raw {type(exc).__name__} for {source.strip()}: {exc}")


def test_operator_fuzz_never_leaks_host_exceptions():
    import random

    rng = random.Random(0x4552524F52)
    atoms = ["0", "1", "-3", "2.5", "true", "false", "'x'", "[1, 2]", "span(3)"]
    operators = ["+", "-", "*", "/", "%", "**", "==", "!=", "<", ">"]
    for _ in range(1000):
        left, right = rng.choice(atoms), rng.choice(atoms)
        operator = rng.choice(operators)
        source = f"value = ({left}) {operator} ({right})\n"
        try:
            run_source(source, filename="operator_fuzz.mana")
        except MagicLangError:
            continue
        except Exception as exc:
            pytest.fail(f"raw {type(exc).__name__} for {source.strip()}: {exc}")


def test_unsupported_words_use_plain_not_identified_diagnostics():
    for source, word in (
        ("import planes\n", "import"),
        ("return 5\n", "return"),
        ("print(1)\n", "print"),
        ("break\n", "break"),
        ("range(3)\n", "range"),
        ("x = None\n", "None"),
        ("x = [i for i in span(3)]\n", "for"),
    ):
        with pytest.raises(MagicLangError) as caught:
            run_source(source, filename="unsupported_word.mana")
        assert f"'{word}' is not identified" in caught.value.message
        assert not any(token_name in caught.value.message for token_name in ("IDENT", "NEWLINE", "KW_FOR"))
