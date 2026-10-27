"""Focused behavioural tests for the integrated MANA 2.0.0 examples.

These tests deliberately assert final runtime state, not just syntax acceptance or
printed output, so examples continue to demonstrate real supported behaviour.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from magiclang.runner import run_file
from magiclang.units import ENERGY, Quantity

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def run_example(name: str):
    return run_file(str(EXAMPLES / name))


def test_preview_commit_boundary_preserves_world_until_release():
    runtime = run_example("preview_commit_boundary.mana")

    assert runtime.global_env.get("before") == 0
    assert runtime.global_env.get("after_preview") == 0
    assert runtime.global_env.get("after_release") == 1


def test_one_way_plane_path_is_removed_in_both_directions_after_close():
    runtime = run_example("plane_path_lifecycle.mana")

    assert runtime.global_env.get("opened") is True
    assert runtime.global_env.get("forward_while_open") is True
    assert runtime.global_env.get("reverse_while_open") is False
    assert runtime.global_env.get("closed") is True
    assert runtime.global_env.get("forward_after_close") is False
    assert runtime.global_env.get("reverse_after_close") is False


def test_mixed_thermal_and_kinetic_changes_keep_energy_ledger_consistent():
    runtime = run_example("kinetic_thermal_ledger.mana")
    stone = runtime.global_env.get("stone")
    props = stone.properties

    assert props["mass"] == Quantity(2, "kg")
    assert props["temp"] == Quantity(450, "K")
    assert props["kinetic_energy"].value == pytest.approx(144.0)
    assert props["thermal_energy"].value == pytest.approx(900_000.0)
    assert props["energy"].dimension == ENERGY
    accounted = sum(
        props.get(name, Quantity(0, ENERGY)).value
        for name in ("thermal_energy", "kinetic_energy", "released_energy", "mana_energy", "bound_energy")
    )
    assert props["energy"].value == pytest.approx(accounted, rel=1e-12, abs=1e-8)


def test_target_context_applies_cast_only_to_the_selected_target():
    runtime = run_example("selective_two_target_cast.mana")
    near_guard = runtime.global_env.get("near_guard")
    far_guard = runtime.global_env.get("far_guard")

    assert near_guard.properties["hp"] == pytest.approx(107.5)
    assert far_guard.properties["hp"] == pytest.approx(120.0)
    collisions = runtime.last_collisions
    assert collisions
    assert "near_guard" in str(collisions[0])
    assert "far_guard" not in str(collisions[0])


def test_impact_handler_counts_a_real_collision_once():
    runtime = run_example("impact_handler_counter.mana")
    target = runtime.global_env.get("target")

    assert runtime.global_env.get("reported_impacts") == 1
    assert target.properties["hp"] == pytest.approx(95.5)
    assert len(runtime.last_collisions) == 1
