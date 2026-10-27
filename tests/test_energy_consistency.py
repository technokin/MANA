"""Regression tests for the physical energy ledger (no visualiser required)."""

import pytest

from magiclang.errors import PhysicsErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import PLANCK_TEMPERATURE_K, Vector3
from magiclang.runtime import Runtime, MagicObject
from magiclang.units import ENERGY, KG, K, VELOCITY, Quantity


def run(source):
    runtime = Runtime()
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    return runtime


def assert_energy_ledger(obj):
    properties = obj.properties
    assert properties["energy"].dimension == ENERGY
    assert properties["thermal_energy"].dimension == ENERGY
    assert properties["kinetic_energy"].dimension == ENERGY
    expected = (
        properties.get("thermal_energy", Quantity(0, ENERGY))
        + properties.get("kinetic_energy", Quantity(0, ENERGY))
        + properties.get("released_energy", Quantity(0, ENERGY))
        + properties.get("mana_energy", Quantity(0, ENERGY))
        + properties.get("bound_energy", Quantity(0, ENERGY))
    )
    assert properties["energy"].value == pytest.approx(expected.value, rel=1e-12, abs=1e-9)


def test_direct_temperature_assignment_updates_thermal_and_total_energy():
    runtime = run("stone = create Earth\nstone.temp = 900 K\n")
    stone = runtime.global_env.get("stone")
    assert stone.properties["thermal_energy"].value == pytest.approx(900_000.0)
    assert_energy_ledger(stone)


def test_direct_mass_assignment_recomputes_energy_and_density():
    runtime = run("stone = create Earth\nstone.mass = 2 kg\n")
    stone = runtime.global_env.get("stone")
    assert stone.properties["thermal_energy"].value == pytest.approx(586_300.0)
    assert stone.properties["density"].value == pytest.approx(2.0)
    assert_energy_ledger(stone)


def test_direct_velocity_assignment_updates_kinetic_and_total_energy():
    runtime = Runtime()
    stone = MagicObject("Earth")
    runtime.set_attr(stone, "vel", Vector3(100, 0, 0, VELOCITY))
    assert stone.properties["kinetic_energy"].value == pytest.approx(5000.0, rel=1e-8)
    assert stone.properties["momentum"].x == pytest.approx(100.0)
    assert_energy_ledger(stone)


def test_kinetic_energy_operation_does_not_overwrite_thermal_energy():
    runtime = Runtime()
    stone = MagicObject("Earth")
    before_thermal = stone.properties["thermal_energy"]
    value = runtime.op_velocity(stone, Quantity(100, VELOCITY))
    assert value is stone
    kinetic = runtime.op_kinetic_energy(stone)
    assert kinetic.value == pytest.approx(5000.0, rel=1e-8)
    assert stone.properties["thermal_energy"] == before_thermal
    assert_energy_ledger(stone)


def test_planck_temperature_limit_applies_to_heat_and_direct_assignment():
    runtime = Runtime()
    stone = MagicObject("Earth")
    too_hot = Quantity(PLANCK_TEMPERATURE_K * 1.01, K)
    with pytest.raises(PhysicsErrorML, match="Planck temperature.*causality library"):
        runtime.op_heat(stone, too_hot)
    with pytest.raises(PhysicsErrorML, match="Planck temperature.*causality library"):
        runtime.set_attr(stone, "temp", too_hot)


def test_energy_ledger_stays_consistent_after_combined_temperature_and_motion_changes():
    runtime = run("""
stone = create Earth
heat(stone, 800 K)
velocity(stone, 250 m/s)
stone.mass = 3 kg
stone.temp = 500 K
""")
    assert_energy_ledger(runtime.global_env.get("stone"))


def test_randomized_object_state_changes_preserve_energy_ledger_identity():
    import random

    rng = random.Random(20261011)
    for _ in range(100):
        runtime = run("stone = create Earth\n")
        stone = runtime.global_env.get("stone")
        runtime.set_attr(stone, "mass", Quantity(rng.uniform(1.0, 20.0), KG))
        runtime.set_attr(stone, "temp", Quantity(rng.uniform(1.0, 4000.0), K))
        runtime.set_attr(stone, "vel", Vector3(rng.uniform(-500, 500), rng.uniform(-500, 500), 0, VELOCITY))
        assert_energy_ledger(stone)
