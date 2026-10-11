from __future__ import annotations

import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import mana
from magiclang.runner import run_file

ROOT = Path(__file__).resolve().parents[1]


def run_source_file(path: Path) -> str:
    """Run an example in a fresh Runtime and return what it printed."""
    output = StringIO()
    with redirect_stdout(output):
        run_file(str(path))
    return output.getvalue()


def invoke_cli(path: Path, monkeypatch) -> tuple[int, str, str]:
    """Exercise the public command-line entry function without spawning a process."""
    monkeypatch.setattr(sys, "argv", ["mana.py", str(path)])
    stdout, stderr = StringIO(), StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        status = mana.main()
    return status, stdout.getvalue(), stderr.getvalue()


def test_all_public_examples_parse_and_run():
    examples = sorted((ROOT / "examples").glob("*.mana"))
    assert len(examples) == 15
    failures = []
    for example in examples:
        stdout, stderr = StringIO(), StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                run_file(str(example))
        except Exception as exc:
            failures.append(
                f"{example.name}: {type(exc).__name__}: {exc}\n"
                f"stdout:\n{stdout.getvalue()}\nstderr:\n{stderr.getvalue()}"
            )
    assert not failures, "Example failures:\n" + "\n".join(failures)


def test_fireball_example_uses_element_templates_and_operation_tuning():
    output = run_source_file(ROOT / "examples" / "fireball.mana")
    assert "[POST fire_ball] inputs: element=Fire" in output
    assert "[POST earth_ball] inputs: element=Earth" in output
    assert "Vector3(600, 0, 0)" in output
    assert "Vector3(300, 0, 0)" in output
    assert "Committed objects:" in output
    assert "SpellResult:" not in output


def test_physics_example_runs_actual_deterministic_motion():
    output = run_source_file(ROOT / "examples" / "physics_demo.mana")
    assert "Position after 1 second:" in output
    assert "Velocity after 1 second:" in output
    assert "Kinetic energy:" in output
    assert "Creation cost for 1 kg:" in output


def test_collision_example_applies_impact_damage():
    output = run_source_file(ROOT / "examples" / "collision_demo.mana")
    assert "Target remaining HP: 975" in output
    assert "Target velocity after impact:" in output
    assert "Recent collision records:" in output


def test_failed_release_prints_error_and_does_not_crash_runner(monkeypatch):
    status, stdout, stderr = invoke_cli(ROOT / "tests" / "release_failure_test.mana", monkeypatch)
    assert status == 0, stderr
    assert "[RELEASE impossible_spell] ERROR:" in stdout
    assert "Traceback" not in stderr


def test_sqrt_uses_mana_specific_error_for_negative_number(tmp_path, monkeypatch):
    source = tmp_path / "negative_sqrt.mana"
    source.write_text("show(sqrt(-1))\n", encoding="utf-8")
    status, _stdout, stderr = invoke_cli(source, monkeypatch)
    assert status == 1
    assert "PhysicsError" in stderr
    assert "Traceback" not in stderr


def test_sqrt_rejects_dimensional_quantity(tmp_path, monkeypatch):
    source = tmp_path / "dimensional_sqrt.mana"
    source.write_text("show(sqrt(4 m))\n", encoding="utf-8")
    status, _stdout, stderr = invoke_cli(source, monkeypatch)
    assert status == 1
    assert "UnitError" in stderr
    assert "Traceback" not in stderr


def test_new_plane_entity_and_three_d_bridge_examples():
    drafter_output = run_source_file(ROOT / "examples" / "drafter_define_plane.mana")
    assert "ordinary" in drafter_output
    assert "2" in drafter_output

    summoning_output = run_source_file(ROOT / "examples" / "summoning_example.mana")
    assert "Wild Realm" in summoning_output
    assert "True" in summoning_output

    necromancy_output = run_source_file(ROOT / "examples" / "necromancy_example.mana")
    assert "True" in necromancy_output
    assert "Bone Guard" in necromancy_output

    summon_skeleton_output = run_source_file(ROOT / "examples" / "summon_skeleton_spell.mana")
    assert "Skeleton" in summon_skeleton_output
    assert "True" in summon_skeleton_output

    combined_output = run_source_file(ROOT / "examples" / "drafter_summoning_necromancy_3d_bridge.mana")
    assert "Aerie" in combined_output
    assert combined_output.count("True") >= 2
