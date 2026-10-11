"""Bounded pre-release stress regressions for numeric and nesting boundaries."""
from __future__ import annotations

import pytest

from magiclang.errors import MagicLangError, PhysicsErrorML, RuntimeErrorML, SyntaxErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime


def parse_source(source: str, filename: str = "stress.mana"):
    return Parser(Lexer(source, filename).tokenize(), filename).parse()


def run_source(source: str, filename: str = "stress.mana"):
    program = parse_source(source, filename)
    runtime = Runtime()
    runtime.execute(program)
    return runtime


def test_numeric_literal_boundaries_never_leak_python_conversion_errors():
    with pytest.raises(SyntaxErrorML, match="numeric literal exceeds the supported input range") as huge_int:
        parse_source("value = " + "9" * 5000 + "\n", "huge-int.mana")
    assert huge_int.value.filename == "huge-int.mana"
    assert huge_int.value.line == 1
    assert huge_int.value.column == 9

    for literal in ("1e999", "9.99e9999", "1e1000000000"):
        with pytest.raises(SyntaxErrorML, match="outside the supported finite range"):
            parse_source(f"value = {literal}\n")


def test_extreme_unit_literals_report_mana_errors_with_locations():
    source = "distance = " + "9" * 400 + " m\n"
    with pytest.raises(UnitErrorML, match="outside the supported range for unit conversion") as error:
        parse_source(source, "unit-overflow.mana")
    assert error.value.filename == "unit-overflow.mana"
    assert error.value.line == 1
    assert error.value.column == len("distance = ") + 1


def test_excessive_parser_nesting_reports_syntax_error_not_recursion_error():
    for source in (
        "value = " + "(" * 1500 + "1" + ")" * 1500 + "\n",
        "value = " + "-" * 1500 + "1\n",
        "value = " + "[" * 1500 + "1" + "]" * 1500 + "\n",
    ):
        with pytest.raises(SyntaxErrorML, match="parser safety limit"):
            parse_source(source, "deep-input.mana")


def test_excessively_long_flat_expression_is_rejected_as_mana_syntax():
    source = "value = " + " + ".join(["1"] * 1500) + "\n"
    with pytest.raises(SyntaxErrorML, match="parser safety limit"):
        parse_source(source, "wide-expression.mana")


def test_exponentiation_chain_is_capped_before_pathological_allocation():
    # Right-associative towers can make the exponent itself enormous even with
    # a short source file. The guard must stop this before host memory is at risk.
    source = "value = " + " ** ".join(["2"] * 7) + "\n"
    with pytest.raises(PhysicsErrorML, match="exponent exceeds the MANA safety limit") as error:
        run_source(source, "power-tower.mana")
    assert error.value.filename == "power-tower.mana"
    assert error.value.line == 1



def test_extreme_field_values_never_leak_overflow_errors():
    cases = (
        ("dummy = tgset:\n    hp = 2 ** 2000\n", PhysicsErrorML, "target field 'hp'"),
        ("dummy = tgset:\n    defence = 2 ** 2000\n", PhysicsErrorML, "target field 'defence'"),
        ("stone = create Earth\nstone.mass = 2 ** 2000\n", PhysicsErrorML, "outside the supported numeric range"),
        ("stone = create Earth\nstone.restitution = 2 ** 2000\n", PhysicsErrorML, "outside the supported numeric range"),
        ("after (2 ** 2000):\n    show(1)\n", RuntimeErrorML, "timing value is outside the supported numeric range"),
    )
    for source, error_class, message in cases:
        with pytest.raises(error_class, match=message):
            run_source(source, "field-boundary.mana")


def test_complex_arithmetic_is_rejected_as_non_real_mana_physics():
    with pytest.raises(PhysicsErrorML, match="MANA supports real-valued numbers only"):
        run_source("value = (-1) ** 0.5\n", "complex-result.mana")


def test_numeric_boundary_values_that_fit_remain_accepted():
    runtime = run_source(
        "zero = 0\n"
        "negative_zero = -0.0\n"
        "finite_limit = 1.7976931348623157e308\n"
        "unit_value = 1e100 m\n"
    )
    assert runtime.global_env.get("zero") == 0
    assert runtime.global_env.get("negative_zero") == 0.0
    assert runtime.global_env.get("finite_limit") == 1.7976931348623157e308
    assert runtime.global_env.get("unit_value").value == pytest.approx(1e100)



def test_geometry_vector_and_custom_plane_builders_guard_huge_numeric_fields():
    cases = (
        "load geometry2d\npoint_value = geometry2d.point(2 ** 2000, 0)\n",
        "load vector3d\nvector_value = vector3d.vector(2 ** 2000, 0, 0)\n",
        "load planes\nload drafter\ndraft = drafter.begin(\"StressPlane\")\n"
        "being = drafter.add_being(draft, \"StressBeing\", hp=2 ** 2000)\n",
        "load geometry2d\nunit_vec = geometry2d.direction(1, 0)\n"
        "large_vec = unit_vec * (2 ** 2000)\n",
    )
    for source in cases:
        with pytest.raises(MagicLangError):
            run_source(source, "numeric-api-stress.mana")


def test_failed_scale_keeps_all_object_fields_unchanged():
    runtime = Runtime()
    runtime.execute(parse_source("stone = create Earth\n", "scale-rollback.mana"))
    stone = runtime.global_env.get("stone")
    before = {
        key: stone.properties[key]
        for key in ("scale", "volume", "area", "density", "collision_radius")
    }
    with pytest.raises(PhysicsErrorML, match=r"scale\(\) result"):
        runtime.execute(parse_source("scale(stone, 1e200)\n", "scale-rollback.mana"))
    for key, value in before.items():
        assert stone.properties[key] == value


def test_seeded_numeric_expression_stress_never_leaks_host_exceptions():
    import random

    rng = random.Random(0xB0A7D4)
    operators = ("+", "-", "*", "/", "%", "**")
    for _ in range(1200):
        left = rng.randint(-25, 25)
        op = rng.choice(operators)
        right = rng.randint(-4, 12) if op == "**" else rng.randint(-25, 25)
        source = f"value = ({left}) {op} ({right})\n"
        try:
            run_source(source, "numeric-fuzz.mana")
        except MagicLangError:
            pass


def test_runtime_expression_guard_is_also_safe_for_embedded_ast_users():
    from magiclang.ast_nodes import Binary, Literal

    expression = Literal(1)
    for _ in range(300):
        expression = Binary(expression, "+", Literal(1))
    runtime = Runtime()
    with pytest.raises(RuntimeErrorML, match="expression evaluation exceeds the safety limit"):
        runtime.eval_expr(expression, runtime.global_env)


def test_deterministic_malformed_source_fuzz_does_not_leak_host_exceptions():
    import random
    import string

    rng = random.Random(0x4D414E41)
    alphabet = string.ascii_letters + string.digits + " +-*/%=<>!()[]:,.#'\\\"\\\\\\t\\n_\\x00éλ"
    for _ in range(1500):
        source = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 140)))
        try:
            run_source(source, "fuzz.mana")
        except MagicLangError:
            pass
        # Any non-MANA exception intentionally fails this test.


def test_power_result_size_is_checked_before_large_integer_allocation():
    with pytest.raises(PhysicsErrorML, match="integer power result exceeds the MANA size limit"):
        run_source("value = (10 ** 100000) ** 100000\n", "power-allocation.mana")


def test_string_and_list_repetition_are_bounded_before_allocation():
    for source in (
        'value = "x" * 1000000000\n',
        'value = 1000000000 * "x"\n',
        'value = [1, 2, 3] * 1000000000\n',
        'value = 1000000000 * [1, 2, 3]\n',
    ):
        with pytest.raises(RuntimeErrorML, match="MANA size limit"):
            run_source(source, "collection-size.mana")


def test_collection_size_guard_still_allows_small_repetitions():
    runtime = run_source('text = "mana" * 3\nitems = [1, 2] * 3\n')
    assert runtime.global_env.get("text") == "manamanamana"
    assert runtime.global_env.get("items") == [1, 2, 1, 2, 1, 2]


def test_rejected_targeted_velocity_does_not_mutate_aim_direction():
    from magiclang.physics import C, Vector3
    from magiclang.units import M, Quantity, VELOCITY

    runtime = Runtime()
    runtime.execute(parse_source(
        "stone = create Earth\nvictim = tgset:\n    distance = 10 m\n",
        "aim-rollback.mana",
    ))
    stone = runtime.global_env.get("stone")
    victim = runtime.global_env.get("victim")
    victim.properties["pos"] = Vector3(0, 10, 0, M)
    original_direction = stone.properties["direction"]
    runtime._target_context_stack.append(victim)
    try:
        with pytest.raises(PhysicsErrorML, match="exceeds c"):
            runtime.op_velocity(stone, Quantity(C * 2, VELOCITY))
    finally:
        runtime._target_context_stack.pop()
    assert stone.properties["direction"] == original_direction
