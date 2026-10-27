from __future__ import annotations

import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import zipfile
from pathlib import Path

import pytest

from magiclang.errors import PhysicsErrorML, RuntimeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.runtime import Runtime
from magiclang.units import VELOCITY

ROOT = Path(__file__).resolve().parents[1]


def run(source: str, *, root: Path | None = None) -> Runtime:
    runtime = Runtime(project_root=root or ROOT)
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    return runtime


def test_core_2d_world_physics_works_without_geometry_library():
    runtime = run("stone = create Earth\nvelocity(stone, 10 m/s)\nadvance_time(1 s)\n")
    stone = runtime.global_env.get("stone")
    assert stone.properties["pos"].x == pytest.approx(10.0)
    assert "geometry2d" not in runtime.global_env.values
    assert "direction" not in runtime.global_env.values
    assert "launch" not in runtime.global_env.values


def test_advanced_geometry_is_unavailable_until_imported():
    with pytest.raises(RuntimeErrorML, match="direction"):
        run("v = direction(1, 0)\n")
    with pytest.raises(RuntimeErrorML, match="launch"):
        run("stone = create Earth\nlaunch(stone, 10 m/s, 0)\n")


def test_geometry2d_namespace_provides_coordinates_angles_and_units():
    runtime = run('load geometry2d\nnorth = geometry2d.direction(0, 1)\ntheta = geometry2d.angle(north)\nrotated = geometry2d.rotate_vector(geometry2d.polar(5 m/s, geometry2d.to_radians(0)), geometry2d.to_radians(90))\ncircle_area_result = geometry2d.circle_area(2 m)\nshow theta\n')
    north = runtime.global_env.get("north")
    rotated = runtime.global_env.get("rotated")
    assert isinstance(north, Vector3) and north.y == pytest.approx(1.0)
    assert runtime.global_env.get("theta") == pytest.approx(1.5707963267948966)
    assert rotated.dimension == VELOCITY
    assert rotated.x == pytest.approx(0.0, abs=1e-9)
    assert rotated.y == pytest.approx(5.0)
    assert runtime.global_env.get("circle_area_result").value == pytest.approx(4 * 3.141592653589793)


def test_geometry2d_rotate_and_scale_aliases_preserve_vector_units():
    runtime = run('load geometry2d\nv = geometry2d.scale(geometry2d.rotate(geometry2d.polar(2 m/s, 0), geometry2d.to_radians(90)), 3)\n')
    result = runtime.global_env.get("v")
    assert result.dimension == VELOCITY
    assert result.x == pytest.approx(0.0, abs=1e-9)
    assert result.y == pytest.approx(6.0)


def test_vector3d_rotate_lerp_and_midpoint_are_calculation_only_helpers():
    runtime = run('load vector3d\na = vector3d.position(1 m, 0 m, 0 m)\nb = vector3d.position(3 m, 4 m, 2 m)\nr = vector3d.rotate(a, 0, 0, 1.5707963267948966)\nm = vector3d.midpoint(a, b)\nl = vector3d.lerp(a, b, 0.25)\n')
    rotated = runtime.global_env.get("r")
    midpoint = runtime.global_env.get("m")
    lerped = runtime.global_env.get("l")
    assert rotated.x == pytest.approx(0.0, abs=1e-9)
    assert rotated.y == pytest.approx(1.0)
    assert midpoint.x == pytest.approx(2.0)
    assert midpoint.y == pytest.approx(2.0)
    assert midpoint.z == pytest.approx(1.0)
    assert lerped.x == pytest.approx(1.5)
    assert lerped.y == pytest.approx(1.0)
    assert lerped.z == pytest.approx(0.5)


def test_explicit_direction_uses_velocity_and_geometry2d_only_provides_geometry():
    runtime = run('load geometry2d\nstone = create Earth\nvelocity(stone, geometry2d.polar(20 m/s, geometry2d.to_radians(90)))\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x == pytest.approx(0.0, abs=1e-9)
    assert stone.properties["vel"].y == pytest.approx(20.0)
    assert stone.properties["released"] is False
    namespace = runtime.global_env.get("geometry2d")
    assert not hasattr(namespace, "launch")


def test_geometry2d_does_not_allow_z_coordinates():
    with pytest.raises(PhysicsErrorML, match="z = 0"):
        run('load geometry2d\nv = geometry2d.direction(1, 0, 2)\n')


def test_vector3d_requires_import_and_is_separate_from_world_dimensions():
    with pytest.raises(RuntimeErrorML, match="vector3d"):
        run("v = vector3d.vector(1, 2, 3)\n")
    runtime = run('load vector3d\nv = vector3d.vector(1, 2, 3)\nmag = vector3d.magnitude(v)\nshow mag\n')
    assert runtime.global_env.get("mag") == pytest.approx((14) ** 0.5)


def test_2d_and_3d_libraries_can_be_imported_together_without_name_collisions():
    runtime = run('load geometry2d\nload vector3d\np = geometry2d.point(1 m, 2 m)\nv = vector3d.vector(1, 2, 3)\nshow geometry2d.distance(p, geometry2d.point(4 m, 6 m))\nshow vector3d.magnitude(v)\n')
    assert isinstance(runtime.global_env.get("p"), Vector3)
    assert runtime.global_env.get("v").z == 3


def test_nonzero_z_3d_vector_is_rejected_when_used_for_world_motion():
    with pytest.raises(PhysicsErrorML, match="2D x-y world plane"):
        run('load vector3d\nstone = create Earth\nvelocity(stone, vector3d.velocity_vector(1 m/s, 2 m/s, 3 m/s))\n')


def test_library_builder_init_validate_build_and_import(tmp_path):
    source_root = tmp_path / "source"
    output_root = tmp_path / "libraries"
    from tools.library_builder import main as builder_main
    assert builder_main(["init", "mathkit", "--output", str(source_root)]) == 0
    folder = source_root / "mathkit"
    manifest_path = folder / "mana-library.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["exports"] = ["double", "add", "identity", "constant"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / "main.mana").write_text(
        "def double(value):\n    incant value * 2\n\ndef add(a, b):\n    incant a + b\n\ndef identity(element):\n    incant element\n\ndef constant():\n    incant 7\n",
        encoding="utf-8",
    )
    assert builder_main(["validate", str(folder)]) == 0
    assert builder_main(["build", str(folder), "--output", str(output_root)]) == 0
    package = output_root / "mathkit.manalib"
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
        assert "mana-library.json" in archive.namelist()
    runtime = run('load mathkit\nresult = mathkit.add(mathkit.double(20), 2)\nelement_named_parameter = mathkit.identity(41)\nconstant_value = mathkit.constant()\nshow result\n', root=tmp_path)
    assert runtime.global_env.get("result") == 42
    assert runtime.global_env.get("element_named_parameter") == 41
    assert runtime.global_env.get("constant_value") == 7


def test_user_library_dependencies_are_checked_before_import(tmp_path):
    source_root = tmp_path / "source"
    output_root = tmp_path / "libraries"
    from tools.library_builder import main as builder_main

    assert builder_main(["init", "plane_helpers", "--output", str(source_root)]) == 0
    folder = source_root / "plane_helpers"
    manifest_path = folder / "mana-library.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dependencies"] = ["planes"]
    manifest["exports"] = ["identity"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / "main.mana").write_text("def identity(value):\n    incant value\n", encoding="utf-8")
    assert builder_main(["validate", str(folder)]) == 0
    assert builder_main(["build", str(folder), "--output", str(output_root)]) == 0

    runtime_without_dependency = Runtime(project_root=tmp_path)
    with pytest.raises(RuntimeErrorML, match="plane_helpers needs planes loaded first"):
        runtime_without_dependency.execute(Parser(Lexer('load plane_helpers\n').tokenize()).parse())

    runtime = run('load planes\nload plane_helpers\nresult = plane_helpers.identity(7)\n', root=tmp_path)
    assert runtime.global_env.get("result") == 7


def test_user_library_cannot_execute_top_level_mutating_statements(tmp_path):
    lib_root = tmp_path / "libraries"
    lib_root.mkdir()
    folder = tmp_path / "source"
    folder.mkdir()
    (folder / "mana-library.json").write_text(json.dumps({
        "format": "manalib", "format_version": 1, "name": "unsafe", "version": "1.0.0",
        "description": "invalid", "entry": "main.mana", "exports": ["safe"]
    }), encoding="utf-8")
    (folder / "main.mana").write_text("result = create Fire\ndef safe():\n    incant 1\n", encoding="utf-8")
    from tools.library_builder import main as builder_main
    stdout, stderr = StringIO(), StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        status = builder_main(["build", str(folder), "--output", str(lib_root)])
    assert status == 1
    assert "only def declarations, loads, and skip" in stderr.getvalue()


def test_library_builder_rejects_reserved_library_names_before_creating_folder(tmp_path):
    from tools.library_builder import init_library

    with pytest.raises(ValueError, match="reserved by MANA"):
        init_library("shape", tmp_path)
    assert not (tmp_path / "shape").exists()


def test_library_documentation_covers_every_exported_api():
    from magiclang.libraries.geometry2d import build_library as build_geometry2d
    from magiclang.libraries.three_d import build_library as build_vector3d

    geometry_doc = (ROOT / "docs" / "current" / "libraries" / "GEOMETRY2D_LIBRARY.md").read_text(encoding="utf-8")
    vector_doc = (ROOT / "docs" / "current" / "libraries" / "VECTOR3D_LIBRARY.md").read_text(encoding="utf-8")
    geometry_api = build_geometry2d(Runtime())
    vector_api = build_vector3d()
    import re

    # Accept signatures written as `name(args...)`, namespaced examples such as
    # `vector3d.name(args...)`, and constants such as `vector3d.C`.
    def is_documented(name: str, text: str, namespace: str) -> bool:
        pattern = rf"`(?:{re.escape(namespace)}\.)?{re.escape(name)}(?:\s*\(|`)"
        return re.search(pattern, text) is not None

    missing_geometry = [name for name in geometry_api if not is_documented(name, geometry_doc, "geometry2d")]
    missing_vector = [name for name in vector_api if not is_documented(name, vector_doc, "vector3d")]
    assert missing_geometry == [], f"geometry2d exports missing from docs: {missing_geometry}"
    assert missing_vector == [], f"vector3d exports missing from docs: {missing_vector}"


@pytest.mark.parametrize("reserved", ["shape", "Light", "Life", "temp", "geometry2d", "vector3d", "incant"])
def test_library_builder_rejects_reserved_names_without_creating_a_library(tmp_path, reserved):
    from tools.library_builder import init_library

    with pytest.raises(ValueError, match="reserved by MANA"):
        init_library(reserved, tmp_path)
    assert not (tmp_path / reserved).exists()


def test_library_builder_rejects_reserved_export_names_before_packaging(tmp_path):
    from tools.library_builder import validate_library

    folder = tmp_path / "badexports"
    folder.mkdir()
    (folder / "mana-library.json").write_text(json.dumps({
        "format": "manalib", "format_version": 1, "name": "badexports", "version": "1.0.0",
        "description": "keyword export", "entry": "main.mana", "exports": ["load"]
    }), encoding="utf-8")
    (folder / "main.mana").write_text("def safe(value):\n    incant value\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-keyword MANA identifier"):
        validate_library(folder)


def test_importing_both_libraries_preserves_core_2d_world_operations():
    runtime = run('load geometry2d\nload vector3d\nstone = create Earth\nvelocity(stone, 10 m/s)\nmetric = geometry2d.distance(geometry2d.point(0 m, 0 m), geometry2d.point(3 m, 4 m))\nthree_d_length = vector3d.magnitude(vector3d.vector(1, 2, 2))\nadvance_time(0.1 s)\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["pos"].x == pytest.approx(1.0)
    assert runtime.global_env.get("metric").value == pytest.approx(5.0)
    assert runtime.global_env.get("three_d_length") == pytest.approx(3.0)
    assert "geometry2d" in runtime.global_env.values
    assert "vector3d" in runtime.global_env.values
    assert "launch" not in runtime.global_env.values


def test_component_reference_covers_token_ast_and_element_catalogue():
    import inspect
    import magiclang.ast_nodes as ast_nodes
    from magiclang.elements import ELEMENTS
    from magiclang.tokens import TokenType

    component_doc = (ROOT / "docs" / "current" / "internals" / "COMPONENT_REFERENCE.md").read_text(encoding="utf-8")
    element_doc = (ROOT / "docs" / "current" / "reference" / "ELEMENTS_AND_RULES.md").read_text(encoding="utf-8")
    for token in TokenType:
        assert f"`{token.name}`" in component_doc, f"token {token.name} missing from component reference"
    ast_names = [name for name, value in vars(ast_nodes).items()
                 if inspect.isclass(value) and value.__module__ == ast_nodes.__name__]
    for name in ast_names:
        assert f"`{name}`" in component_doc, f"AST node {name} missing from component reference"
    for element_name in ELEMENTS:
        assert f"`{element_name}`" in element_doc, f"element {element_name} missing from element reference"


def test_all_core_builtin_names_are_documented():
    import re
    from magiclang.runtime import Runtime

    ref = (ROOT / "docs" / "current" / "reference" / "FUNCTION_REFERENCE.md").read_text(encoding="utf-8")
    missing = [name for name in Runtime.BUILTIN_NAMES
               if re.search(r"`" + re.escape(name) + r"(?:`|\s*\()", ref) is None]
    assert missing == [], f"core built-in names missing from reference: {missing}"


def test_user_library_can_export_a_builtin_name_without_overwriting_global_operation(tmp_path):
    from tools.library_builder import init_library, validate_library, build_library

    project = tmp_path / "project"
    library_root = project / "libraries"
    source_root = tmp_path / "source"
    folder = init_library("mathkit", source_root)
    manifest_path = folder / "mana-library.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["exports"] = ["force"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / "main.mana").write_text("def force(value):\n    incant value * 2\n", encoding="utf-8")
    validate_library(folder)
    build_library(folder, library_root)

    runtime = run('load mathkit\nstone = create Earth\ncustom_result = mathkit.force(21)\nglobal_force = force(stone)\n', root=project)
    assert runtime.global_env.get("custom_result") == 42
    assert isinstance(runtime.global_env.get("global_force"), Vector3)
    assert runtime.global_env.get("force").__name__ == "op_force"


def test_library_builder_rejects_entry_symlink_outside_package(tmp_path):
    from tools.library_builder import init_library, validate_library

    folder = init_library("symlinkkit", tmp_path / "source")
    external = tmp_path / "external.mana"
    external.write_text("def identity(value):\n    incant value\n", encoding="utf-8")
    (folder / "main.mana").unlink()
    try:
        (folder / "main.mana").symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(ValueError, match="symbolic link"):
        validate_library(folder)


def test_library_builder_rejects_readme_symlink_outside_package(tmp_path):
    from tools.library_builder import build_library, init_library

    folder = init_library("readmelink", tmp_path / "source")
    external = tmp_path / "external-readme.md"
    external.write_text("must not be packaged", encoding="utf-8")
    (folder / "README.md").unlink()
    try:
        (folder / "README.md").symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(ValueError, match="symbolic link"):
        build_library(folder, tmp_path / "output")


def test_library_builder_rejects_oversized_manifest_before_json_parse(tmp_path):
    from tools.library_builder import MANIFEST_NAME, read_package_source, init_library
    from magiclang.runtime import MAX_LIBRARY_MANIFEST_BYTES

    folder = init_library("bigmanifest", tmp_path / "source")
    (folder / MANIFEST_NAME).write_bytes(b" " * (MAX_LIBRARY_MANIFEST_BYTES + 1))
    with pytest.raises(ValueError, match="safety limit"):
        read_package_source(folder)
