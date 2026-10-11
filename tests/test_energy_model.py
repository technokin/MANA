"""Regression tests for MANA's independent matter/mana/energy model."""

import random

import pytest

from magiclang.errors import MagicErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.runtime import MagicObject, Runtime
from magiclang.units import ENERGY, KG, K, MANA, VELOCITY, Quantity, matter_to_mana, mana_to_energy, mana_to_matter


def execute(source: str) -> Runtime:
    runtime = Runtime()
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    return runtime


def active_objects_from_runtime(runtime: Runtime):
    seen = set()
    found = []

    def walk(value):
        if isinstance(value, MagicObject):
            if id(value) not in seen:
                seen.add(id(value))
                if value.properties.get("active", True):
                    found.append(value)
                for child in value.properties.values():
                    walk(child)
        elif isinstance(value, (list, tuple, set)):
            for child in value:
                walk(child)
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)

    walk(runtime.global_env.values)
    walk(runtime.active_objects)
    return found


def assert_object_energy_is_derived(obj):
    expected = (
        obj.properties["thermal_energy"]
        + obj.properties["kinetic_energy"]
        + obj.properties.get("released_energy", Quantity(0, ENERGY))
    )
    assert obj.properties["energy"].value == pytest.approx(expected.value, rel=1e-11, abs=1e-7)


def assert_world_energy_matches_ledger(runtime):
    active_energy = sum(obj.properties["energy"].value for obj in active_objects_from_runtime(runtime))
    net_transfers = runtime.energy_input_j - runtime.energy_output_j
    assert active_energy == pytest.approx(net_transfers, rel=1e-9, abs=1e-5)


def test_fundamental_element_start_temperatures_and_delta_heat_cool():
    starts = {"Fire": 1000.0, "Water": 273.15, "Earth": 293.15, "Air": 288.15}
    runtime = Runtime()
    for element, start in starts.items():
        obj = MagicObject(element)
        assert obj.properties["temp"].value == pytest.approx(start)
        runtime.op_heat(obj, Quantity(100, K))
        assert obj.properties["temp"].value == pytest.approx(start + 100)
        runtime.op_cool(obj, Quantity(25, K))
        assert obj.properties["temp"].value == pytest.approx(start + 75)
        assert_object_energy_is_derived(obj)


def test_creation_rate_is_matter_only_and_energy_rate_is_independent():
    assert matter_to_mana(Quantity(10, KG)) == Quantity(1, MANA)
    assert mana_to_matter(Quantity(1, MANA)) == Quantity(10, KG)
    assert mana_to_energy(Quantity(1, MANA)) == Quantity(1, ENERGY)
    assert mana_to_energy(matter_to_mana(Quantity(10, KG))) == Quantity(1, ENERGY)

    runtime = execute("stone = create Earth\n")
    stone = runtime.global_env.get("stone")
    assert stone.properties["creation_mana_cost"] == pytest.approx(0.1)
    assert runtime.total_mana_used == pytest.approx(0.1)
    # Initial heat exists as part of the created object's state, but is not billed
    # as an extra energy-conversion cost during creation.
    assert runtime.energy_input_j == pytest.approx(stone.properties["energy"].value)


def test_energy_derived_fields_reject_direct_assignment():
    runtime = Runtime()
    stone = MagicObject("Earth")
    for prop, value in (
        ("energy", Quantity(1, ENERGY)),
        ("thermal_energy", Quantity(1, ENERGY)),
        ("kinetic_energy", Quantity(1, ENERGY)),
        ("released_energy", Quantity(1, ENERGY)),
        ("released_mana", 1.0),
        ("local_released_energy", Quantity(1, ENERGY)),
        ("local_released_mana", 1.0),
        ("local_energy_origin", "fake"),
        ("local_energy_sources", []),
        ("mana_used", -1.0),
        ("mana_cost", -1.0),
        ("creation_mana_cost", -1.0),
        ("energy_origin", "forged_source"),
        ("energy_sources", []),
        ("active", False),
        ("released", True),
    ):
        with pytest.raises(MagicErrorML, match="derived|managed"):
            runtime.set_attr(stone, prop, value)
    with pytest.raises(MagicErrorML, match="runtime-managed"):
        stone.set("energy", Quantity(1, ENERGY))


def test_combine_and_split_preserve_total_energy_and_release_origin():
    runtime = execute("""
fire = create Fire
water = create Water
thermal = combine(fire, water, mana_a=100, mana_b=100)
parts = split(thermal, 2)
""")
    fire, water, thermal = (runtime.global_env.get(name) for name in ("fire", "water", "thermal"))
    parts = runtime.global_env.get("parts")
    assert not fire.properties["active"] and not water.properties["active"]
    assert not thermal.properties["active"]
    assert len(parts) == 2
    assert thermal.properties["released_energy"] == Quantity(200, ENERGY)
    assert thermal.properties["energy_origin"] == "mana_to_energy"
    assert thermal.properties["energy"].value == pytest.approx(
        fire.properties["energy"].value + water.properties["energy"].value + 200
    )
    assert sum(p.properties["released_energy"].value for p in parts) == pytest.approx(200)
    assert all(p.properties["energy_origin"] == "mana_to_energy" for p in parts)
    for obj in parts:
        assert_object_energy_is_derived(obj)
    assert_world_energy_matches_ledger(runtime)


def test_release_commits_all_active_objects_created_inside_spell():
    runtime = execute('\nspldef spell():\n    stone = create Earth\n    flame = create Fire\n    heat(stone, 100 K)\n    velocity(flame, 50 m/s)\n    incant flame\nrelease(spell)\n')
    created = [obj for obj in runtime.active_objects if isinstance(obj, MagicObject)]
    assert {obj.element for obj in created} >= {"Earth", "Fire"}
    assert all(obj.properties["active"] for obj in created)
    assert_world_energy_matches_ledger(runtime)


def test_combine_defaults_to_object_intensity_not_a_mana_budget():
    runtime = execute("""
fire = create Fire
water = create Water
fire.mana_intensity = 100
water.mana_intensity = 100
thermal = combine(fire, water)
""")
    thermal = runtime.global_env.get("thermal")
    assert thermal.properties["released_energy"] == Quantity(200, ENERGY)
    assert thermal.properties["energy_origin"] == "mana_to_energy"
    assert_world_energy_matches_ledger(runtime)


def test_thermal_release_keeps_mixed_conversion_provenance():
    runtime = Runtime()
    matter_release = MagicObject("ThermalRelease")
    mana_release = MagicObject("ThermalRelease")
    for obj, origin, amount in (
        (matter_release, "matter_to_energy", 5.0),
        (mana_release, "mana_to_energy", 7.0),
    ):
        obj.properties["released_energy"] = Quantity(amount, ENERGY)
        obj.properties["energy_origin"] = origin
        obj.properties["energy_sources"] = [{"origin": origin, "energy_j": amount}]
        runtime.update_total_energy(obj)
    combined = runtime.op_combine(matter_release, mana_release)
    assert combined.properties["released_energy"] == Quantity(12, ENERGY)
    assert combined.properties["energy_origin"] == "mixed"
    assert {source["origin"] for source in combined.properties["energy_sources"]} == {
        "matter_to_energy", "mana_to_energy"
    }
    assert sum(source["energy_j"] for source in combined.properties["energy_sources"]) == pytest.approx(12)


def test_separate_restores_inputs_and_preserves_released_energy_without_duplication():
    runtime = execute("""
fire = create Fire
water = create Water
thermal = combine(fire, water, mana_a=100, mana_b=100)
parts = separate(thermal)
""")
    fire = runtime.global_env.get("fire")
    water = runtime.global_env.get("water")
    thermal = runtime.global_env.get("thermal")
    parts = runtime.global_env.get("parts")
    assert fire.properties["active"] and water.properties["active"]
    assert not thermal.properties["active"]
    carrier = next(obj for obj in parts if obj.element == "ThermalRelease")
    assert carrier.properties["mass"] == Quantity(0, KG)
    assert carrier.properties["released_energy"] == Quantity(200, ENERGY)
    assert carrier.properties["energy_origin"] == "mana_to_energy"
    assert_world_energy_matches_ledger(runtime)


def test_separate_does_not_duplicate_release_inherited_from_sources():
    runtime = Runtime()
    matter_release = MagicObject("ThermalRelease", {
        "mass": Quantity(0, KG), "volume": Quantity(0, "m3"),
        "density": Quantity(0, "kg/m3"), "temp": Quantity(0, K),
        "thermal_energy": Quantity(0, ENERGY), "kinetic_energy": Quantity(0, ENERGY),
        "released_energy": Quantity(5, ENERGY), "energy": Quantity(5, ENERGY),
        "energy_origin": "matter_to_energy",
        "energy_sources": [{"origin": "matter_to_energy", "energy_j": 5.0}],
        "energy_state_initialized": True,
    })
    mana_release = MagicObject("ThermalRelease", {
        "mass": Quantity(0, KG), "volume": Quantity(0, "m3"),
        "density": Quantity(0, "kg/m3"), "temp": Quantity(0, K),
        "thermal_energy": Quantity(0, ENERGY), "kinetic_energy": Quantity(0, ENERGY),
        "released_energy": Quantity(7, ENERGY), "energy": Quantity(7, ENERGY),
        "energy_origin": "mana_to_energy",
        "energy_sources": [{"origin": "mana_to_energy", "energy_j": 7.0}],
        "energy_state_initialized": True,
    })
    combined = runtime.op_combine(matter_release, mana_release)
    assert combined.properties["released_energy"] == Quantity(12, ENERGY)
    separated = runtime.op_separate(combined)
    assert separated == [matter_release, mana_release]
    assert matter_release.properties["active"] and mana_release.properties["active"]
    assert not combined.properties["active"]
    assert sum(obj.properties["energy"].value for obj in separated) == pytest.approx(12)


def test_removed_objects_cannot_change_energy_and_removal_is_ledgered():
    runtime = execute("""
stone = create Earth
dispel(stone)
""")
    stone = runtime.global_env.get("stone")
    assert not stone.properties["active"]
    assert_world_energy_matches_ledger(runtime)
    with pytest.raises(MagicErrorML, match="inactive object"):
        runtime.set_attr(stone, "temp", Quantity(400, K))
    with pytest.raises(MagicErrorML, match="inactive object"):
        runtime.op_heat(stone, Quantity(20, K))


def test_dispel_removal_is_recorded_as_energy_output():
    runtime = execute("""stone = create Earth
dispel(stone)
""")
    assert not runtime.global_env.get("stone").properties["active"]
    assert_world_energy_matches_ledger(runtime)


def test_energy_ledger_balances_through_state_changes_and_one_thousand_random_cases():
    # This deterministic randomized sweep exercises 1,000 created objects and
    # 3,000 direct state updates while checking the same world-level ledger rule.
    count = 1000
    source = "".join(f"obj_{i} = create Earth\n" for i in range(count))
    runtime = execute(source)
    rng = random.Random(602)
    for i in range(count):
        obj = runtime.global_env.get(f"obj_{i}")
        runtime.set_attr(obj, "temp", Quantity(rng.uniform(1, 5000), K))
        runtime.set_attr(obj, "vel", Vector3(rng.uniform(-2500, 2500), rng.uniform(-2500, 2500), 0, VELOCITY))
        runtime.set_attr(obj, "mass", Quantity(rng.uniform(1.001, 10), KG))
        assert_object_energy_is_derived(obj)
    # A malformed self-combine must fail without duplicating the object's matter
    # or energy in the deterministic randomized ledger sweep.
    obj0 = runtime.global_env.get("obj_0")
    with pytest.raises(MagicErrorML, match="two distinct objects"):
        runtime.op_combine(obj0, obj0)
    assert_world_energy_matches_ledger(runtime)


def test_heat_and_cool_are_readouts_not_spendable_mana_limits():
    runtime = execute('\nstone = create Earth\nspldef warm():\n    heat(stone, 100 K)\n    incant stone\nrelease(warm)\ncool(stone, 25 K)\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["temp"].value == pytest.approx(368.15)
    assert runtime.total_mana_used > 100000
    assert_world_energy_matches_ledger(runtime)
