from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import zipfile

import pytest

from magiclang.errors import MagicErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.runtime import Runtime
from magiclang.units import ENERGY, FORCE, K, M, M2, Quantity
from magiclang.libraries import geometry2d, three_d

ROOT = Path(__file__).resolve().parents[1]


def run(source: str, *, root: Path | None = None, filename: str = "<input>") -> Runtime:
    runtime = Runtime(project_root=root or ROOT)
    program = Parser(Lexer(source, filename).tokenize(), filename).parse()
    runtime.execute(program)
    return runtime


def test_list_indexing_len_nested_assignment_and_function_calls_work_together():
    runtime = run('\nload geometry2d\nmatrix = [[1, 2], [3, 4]]\nmatrix[0][1] = 8\nvalues = [matrix[0][1], matrix[1][0], length(matrix), length("mana"), length(span(5))]\npoint_value = geometry2d.point(values[0] * 1 m, values[1] * 1 m)\nshow values[0] + length(values)\n')
    matrix = runtime.global_env.get("matrix")
    values = runtime.global_env.get("values")
    point_value = runtime.global_env.get("point_value")
    assert matrix == [[1, 8], [3, 4]]
    assert values == [8, 3, 2, 4, 5]
    assert isinstance(point_value, Vector3)
    assert point_value.x == pytest.approx(8)
    assert point_value.y == pytest.approx(3)


def test_list_reads_support_negative_indices_and_strings_and_ranges():
    runtime = run('\nitems = [10, 20, 30]\nlast_item = items[-1]\nlast_letter = "mana"[-1]\nrange_value = span(6)[-2]\n')
    assert runtime.global_env.get("last_item") == 30
    assert runtime.global_env.get("last_letter") == "a"
    assert runtime.global_env.get("range_value") == 4


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("items = [1, 2]\nvalue = items[2]\n", "out of range"),
        ("items = [1, 2]\nvalue = items[1.5]\n", "index must be an integer"),
        ("items = [1, 2]\nitems[2] = 3\n", "out of range"),
        ("items = [1, 2]\nitems[0.5] = 3\n", "index must be an integer"),
        ('value = length(4)\n', r"length\(\) expects a list, string, or span"),
    ],
)
def test_invalid_indexing_and_length_inputs_are_mana_errors(source: str, message: str):
    with pytest.raises((RuntimeErrorML, TypeErrorML), match=message):
        run(source)


def test_block_variables_are_visible_to_the_enclosing_definition_but_not_callers():
    runtime = run('\ndef compute():\n    if true:\n        result = 17\n    for index in span(2):\n        loop_value = index + 4\n    incant result + loop_value\nanswer = compute()\n')
    assert runtime.global_env.get("answer") == 22
    with pytest.raises(RuntimeErrorML, match="not identified"):
        runtime.global_env.get("result")


def test_direct_definition_call_can_calculate_but_cannot_create_world_objects():
    runtime = run('''
def calculate():
    local_value = 9 * 7
    incant local_value + 1
answer = calculate()
''')
    assert runtime.global_env.get("answer") == 64

    with pytest.raises(MagicErrorML, match="cannot create objects"):
        run('\ndef invalid():\n    item = create Earth\n    incant item\nresult = invalid()\n')


def test_library_definition_cannot_bypass_direct_call_purity(tmp_path):
    library_dir = tmp_path / "libraries"
    library_dir.mkdir()
    package = library_dir / "unsafe.manalib"
    manifest = {
        "format": "manalib",
        "format_version": 1,
        "name": "unsafe",
        "version": "0.1.0",
        "description": "purity regression test",
        "entry": "main.mana",
        "exports": ["create_item"],
    }
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("mana-library.json", json.dumps(manifest))
        archive.writestr("main.mana", "def create_item():\n    item = create Earth\n    incant item\n")
    with pytest.raises(MagicErrorML, match="cannot create objects"):
        run('load unsafe\nresult = unsafe.create_item()\n', root=tmp_path)


def test_simul_is_repeatable_and_executes_independent_operations_in_source_order():
    source = '\nspldef pulse():\n    a = create Fire\n    b = create Fire\n    c = create Water\n    d = create Earth\n    simul:\n        heat(a, 200 K)\n        heat(b, 300 K)\n        heat(c, 100 K)\n        heat(d, 50 K)\n    incant [a.temp, b.temp, c.temp, d.temp]\nrelease(pulse)\n'
    outputs = []
    final_temps = []
    for _ in range(100):
        output = StringIO()
        runtime = Runtime(project_root=ROOT)
        with redirect_stdout(output):
            runtime.execute(Parser(Lexer(source).tokenize()).parse())
        outputs.append(output.getvalue())
        final_temps.append(tuple(
            round(obj.properties["temp"].value, 9)
            for obj in runtime.active_objects if obj.element in {"Fire", "Water", "Earth"}
        ))
    assert len(set(outputs)) == 1
    assert len(set(final_temps)) == 1


def test_simul_rolls_back_earlier_changes_if_a_later_operation_fails():
    runtime = Runtime(project_root=ROOT)
    program = Parser(Lexer("""stone = create Earth
simul:
    heat(stone, 100 K)
    accelerate(stone, 5 m)
""").tokenize()).parse()
    with pytest.raises(UnitErrorML):
        runtime.execute(program)
    stone = runtime.global_env.get("stone")
    assert stone.properties["temp"].value == pytest.approx(293.15)
    assert [entry["operation"] for entry in runtime.energy_ledger] == ["create Earth"]


def test_integrity_is_material_based_and_stabilizers_are_deduplicated():
    baseline = run("stone = create Earth\nheat(stone, 1000000000 K)\n")
    stabilised = run('''
stone = create Earth
stone.stabilizers = ["Earth", "Water", "Earth"]
heat(stone, 1000000000 K)
''')
    base_object = baseline.global_env.get("stone")
    strong_object = stabilised.global_env.get("stone")
    assert base_object.properties["integrity_break_energy"].value == pytest.approx(3.0e12)
    assert strong_object.properties["integrity_break_energy"].value == pytest.approx(4.5e12)
    assert strong_object.properties["stabilizers"] == ["Earth", "Water"]
    assert strong_object.properties["integrity"] > base_object.properties["integrity"]
    assert strong_object.properties["integrity"] > 0


def test_integrity_collapse_transfers_physical_energy_to_thermal_release_carrier():
    runtime = run("stone = create Earth\nheat(stone, 4000000000 K)\n")
    stone = runtime.global_env.get("stone")
    carrier = stone.properties["collapsed_into"]
    assert stone.properties["integrity"] == 0
    assert stone.properties["active"] is False
    assert carrier is not None and carrier.element == "ThermalRelease"
    assert carrier.properties["released_energy"].value == pytest.approx(stone.properties["energy"].value)
    assert carrier.properties["energy"].dimension == ENERGY
    assert carrier.properties["integrity_collapsed"] is True


def test_celsius_absolute_temperature_and_kelvin_change_semantics():
    runtime = run("cold = -10 C\nroom = 20 C\nchange = room - cold\n")
    assert runtime.global_env.get("cold").value == pytest.approx(263.15)
    assert runtime.global_env.get("room").value == pytest.approx(293.15)
    assert runtime.global_env.get("change").value == pytest.approx(30.0)
    with pytest.raises(UnitErrorML, match="absolute Celsius"):
        run("stone = create Earth\nheat(stone, 20 C)\n")



def test_absolute_celsius_values_cannot_be_scaled_or_exponentiated():
    for source in ("value = 20 C * 2\n", "value = 20 C / 2\n", "value = 20 C ** 2\n"):
        with pytest.raises(UnitErrorML, match="absolute temperature"):
            run(source)


def test_geometry2d_collinear_segments_and_polygon_boundary_are_stable():
    p = geometry2d.point
    overlap = geometry2d.segment_intersection(p(0, 0), p(2, 0), p(1, 0), p(3, 0))
    disjoint = geometry2d.segment_intersection(p(0, 0), p(1, 0), p(2, 0), p(3, 0))
    touching = geometry2d.segment_intersection(p(0, 0), p(1, 0), p(1, 0), p(1, 1))
    assert isinstance(overlap, Vector3) and (overlap.x, overlap.y) == pytest.approx((1, 0))
    assert disjoint is False
    assert isinstance(touching, Vector3) and (touching.x, touching.y) == pytest.approx((1, 0))
    polygon = [p(0, 0), p(2, 0), p(2, 2), p(0, 2)]
    assert geometry2d.point_in_polygon(Vector3(1, 0.5e-13, 0, M), polygon) is True
    assert geometry2d.point_in_polygon(p(3, 1), polygon) is False
    huge_a = Vector3(1e308, 1e308, 0, M)
    huge_b = Vector3(1e308, -1e308, 0, M)
    assert geometry2d.angle_between(huge_a, huge_b) == pytest.approx(1.5707963267948966)


def test_vector3d_dimensions_pressure_and_displacement_are_consistent():
    position = three_d.position(1, 2, 3)
    force_vector = Vector3(10, 0, 0, FORCE)
    dot_value = three_d.dot(position, force_vector)
    pressure_scalar = three_d.pressure(Quantity(10, FORCE), Quantity(2, M2))
    pressure_vector = three_d.pressure(force_vector, Quantity(2, M2))
    next_position = three_d.displacement(position, three_d.direction(0, 3, 4), Quantity(10, M))

    assert dot_value.dimension == ENERGY
    assert dot_value.value == pytest.approx(10)
    assert pressure_scalar.value == pytest.approx(5)
    assert pressure_vector.value == pytest.approx(5)
    assert pressure_scalar.dimension == pressure_vector.dimension
    assert (next_position.x, next_position.y, next_position.z) == pytest.approx((1, 8, 11))
    with pytest.raises(UnitErrorML, match="area must use m2"):
        three_d.pressure(Quantity(10, FORCE), Quantity(2, M))


def test_vector3d_normalization_handles_large_finite_components():
    huge = Vector3(1e308, 1e308, 0, M)
    normalized = three_d.normalize(huge)
    assert normalized.x == pytest.approx(2 ** -0.5)
    assert normalized.y == pytest.approx(2 ** -0.5)
    assert normalized.z == 0
    huge_position = Vector3(1e308, 1e308, 0, M)
    orthogonal = Vector3(1e308, -1e308, 0, M)
    assert three_d.angle_between(huge_position, orthogonal) == pytest.approx(1.5707963267948966)


def test_integrity_system_properties_are_read_only():
    with pytest.raises(MagicErrorML, match="calculated by the integrity system"):
        run("stone = create Earth\nstone.integrity = 0\n")


def test_geometry2d_large_vectors_midpoints_and_segments_avoid_intermediate_overflow():
    huge = 1.7e308
    vector = Vector3(huge, huge, 0, M)
    unit = geometry2d.normalize(vector)
    direction = geometry2d.direction(huge, huge)
    assert unit.x == pytest.approx(2 ** -0.5)
    assert unit.y == pytest.approx(2 ** -0.5)
    assert direction.x == pytest.approx(unit.x)
    assert direction.y == pytest.approx(unit.y)
    assert geometry2d.angle_between(vector, Vector3(huge, -huge, 0, M)) == pytest.approx(1.5707963267948966)

    start = geometry2d.point(-huge, 0)
    end = geometry2d.point(huge, 0)
    middle = geometry2d.midpoint(start, end)
    interpolation = geometry2d.lerp(start, end, 0.5)
    closest = geometry2d.closest_point_on_segment(geometry2d.point(0, 10), start, end)
    assert (middle.x, middle.y) == pytest.approx((0, 0))
    assert (interpolation.x, interpolation.y) == pytest.approx((0, 0))
    assert (closest.x, closest.y) == pytest.approx((0, 0))


def test_vector3d_projection_handles_direction_magnitude_beyond_float_range():
    huge = 1.7e308
    axis = Vector3(huge, huge, huge, M)
    projected = three_d.project(Vector3(3, 3, 3, M), axis)
    assert projected.x == pytest.approx(3)
    assert projected.y == pytest.approx(3)
    assert projected.z == pytest.approx(3)


def test_geometry2d_closest_point_handles_tiny_segments_and_distant_points():
    start = geometry2d.point(0, 0)
    end = geometry2d.point(1e-308, 0)
    point = geometry2d.point(1e308, 1e308)
    closest = geometry2d.closest_point_on_segment(point, start, end)
    assert (closest.x, closest.y) == pytest.approx((1e-308, 0))


def test_2d_and_3d_projection_and_reflection_avoid_overflowing_intermediate_dots():
    huge = 1.7e308
    planar = Vector3(huge, huge, 0, M)
    projected_2d = geometry2d.project(planar, planar)
    reflected_2d = geometry2d.reflect_vector(planar, planar)
    assert (projected_2d.x, projected_2d.y) == pytest.approx((huge, huge))
    assert (reflected_2d.x, reflected_2d.y) == pytest.approx((-huge, -huge))

    spatial = Vector3(huge, huge, huge, M)
    projected_3d = three_d.project(spatial, spatial)
    reflected_3d = three_d.reflect(spatial, spatial)
    assert (projected_3d.x, projected_3d.y, projected_3d.z) == pytest.approx((huge, huge, huge))
    assert (reflected_3d.x, reflected_3d.y, reflected_3d.z) == pytest.approx((-huge, -huge, -huge))
