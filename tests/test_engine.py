import pytest

from magiclang.elements import ELEMENTS, FUNDAMENTAL_ELEMENTS, interaction, DOMAIN_OWNER
from magiclang.errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML, TypeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3, kinetic_energy, momentum
from magiclang.runtime import Runtime, MagicObject
from magiclang.units import (
    Quantity, KG, MANA, ENERGY, FORCE, M2, PRESSURE, VELOCITY,
    matter_to_mana, mana_to_energy, mana_to_matter, energy_to_mana,
)


def run(source):
    program = Parser(Lexer(source).tokenize()).parse()
    runtime = Runtime()
    runtime.execute(program)
    return runtime


def test_fundamental_elements_and_removed_energy_gravity():
    assert FUNDAMENTAL_ELEMENTS == {"Fire", "Water", "Earth", "Air"}
    assert "Energy" not in ELEMENTS
    assert "Gravity" not in ELEMENTS
    assert "Null" not in ELEMENTS


def test_fire_air_result_does_not_depend_on_argument_order():
    fa = interaction("Fire", 100, "Air", 20)
    af = interaction("Air", 20, "Fire", 100)
    assert fa.kind == af.kind == "element"
    assert fa.name == af.name == "Fire"
    assert fa.mana == af.mana == 110


def test_water_earth_then_mud_life_makes_wood():
    mud = interaction("Water", 100, "Earth", 100)
    assert mud.kind == "material" and mud.name == "Mud"
    premature = interaction("Earth", 100, "Life", 100)
    assert premature.kind == "compound" and premature.name == "EarthLifeCompound"
    wood = interaction("Mud", 100, "Life", 50)
    assert wood.kind == "material" and wood.name == "Wood"


def test_water_air_requires_heat_to_make_ice():
    assert interaction("Water", 10, "Air", 10, available_heat=False).name == "Compound"
    ice = interaction("Air", 10, "Water", 10, available_heat=True)
    assert ice.kind == "material" and ice.name == "Ice"


def test_cancellation_tolerance_and_ratio():
    near_equal = interaction("Fire", 100, "Water", 99.5)
    assert near_equal.name == "ThermalRelease"
    partial = interaction("Fire", 150, "Water", 100)
    assert partial.kind == "element" and partial.name == "Fire"
    assert partial.mana == 50
    assert partial.ratio == pytest.approx(50 / 150)
    light = interaction("Light", 150, "Darkness", 100)
    assert light.ratio == pytest.approx(50 / 150)


def test_runtime_cancel_releases_energy_not_null():
    rt = run("""
fire = create Fire
water = create Water
result = combine(fire, water, mana_a=100, mana_b=100)
""")
    result = rt.global_env.get("result")
    assert result.element == "ThermalRelease"
    assert result.properties["released_energy"] == Quantity(200, ENERGY)
    assert result.properties["energy_origin"] == "mana_to_energy"
    assert result.properties["energy_sources"] == [{"origin": "mana_to_energy", "energy_j": 200.0}]


def test_explicit_si_units_and_dimension_aliases():
    rt = run('\nspldef projectile():\n    stone = create Earth\n    heat(stone, 1200 K)\n    velocity(stone, 300 m/s)\n    incant stone\nrelease(projectile)\n')
    rock = next(obj for obj in rt.active_objects if obj.properties.get("display_name") == "stone")
    assert rock.properties["temp"] == Quantity(1493.15, "K")
    assert rock.properties["vel"] == Vector3(300, 0, 0, VELOCITY)


def test_units_exponents_and_division_by_zero():
    assert Quantity(1, "N").dimension == FORCE
    assert Quantity(1, "Pa").dimension == PRESSURE
    assert Quantity(1, "m2").dimension == M2
    with pytest.raises(PhysicsErrorML):
        _ = Quantity(1, "m") / 0
    with pytest.raises(TypeErrorML):
        from magiclang.physics import scalar
        scalar(True)


def test_mass_and_absolute_temperature_are_validated_at_boundaries():
    rt = Runtime()
    obj = MagicObject("Earth")
    with pytest.raises(PhysicsErrorML):
        rt.op_heat(obj, -1)
    with pytest.raises(PhysicsErrorML):
        rt.set_attr(obj, "mass", Quantity(-1, KG))


def test_relativistic_energy_and_speed_limit():
    m = Quantity(1, KG)
    slow = Vector3(100, 0, 0, VELOCITY)
    energy = kinetic_energy(m, slow)
    assert energy.value == pytest.approx(0.5 * 100 * 100, rel=1e-8)
    p = momentum(m, slow)
    assert p.dimension == Quantity(1, "kg*m/s").dimension
    with pytest.raises(PhysicsErrorML):
        kinetic_energy(m, Vector3(299792458, 0, 0, VELOCITY))


def test_force_returns_vector_and_magnitude_is_available():
    obj = MagicObject("Earth")
    obj.properties["acc"] = Vector3(2, 0, 0, "m/s2")
    result = Runtime().op_force(obj)
    assert isinstance(result, Vector3)
    assert result.magnitude() == pytest.approx(2)


def test_two_rate_mana_conversions():
    assert matter_to_mana(Quantity(2, KG)) == Quantity(0.2, MANA)
    assert mana_to_matter(Quantity(20, MANA)) == Quantity(200, KG)
    assert mana_to_energy(Quantity(1, MANA)) == Quantity(1, ENERGY)
    assert energy_to_mana(Quantity(5000, ENERGY)) == Quantity(5000, MANA)
    assert mana_to_energy(matter_to_mana(Quantity(10, KG))) == Quantity(1, ENERGY)


def test_spell_needs_no_mana_budget_parameter():
    rt = run('\nspldef tiny():\n    fire = create Fire\n    heat(fire, 1000 K)\n    incant fire\nrelease(tiny)\n')
    created = [obj for obj in rt.active_objects if obj.element == "Fire"]
    assert len(created) == 1
    assert created[0].properties["temp"] == Quantity(2000, "K")
    # Creation and energy cost values are readouts, not a depleted pool or cap.
    assert rt.total_mana_used > 1_000_000


def test_simul_allows_separate_properties_and_rejects_conflict():
    run("""
stone = create Earth
simul:
    heat(stone, 500)
    accelerate(stone, 2)
""")
    with pytest.raises(MagicErrorML, match="same (temp|energy|thermal_energy)"):
        run("""
stone = create Earth
simul:
    heat(stone, 500)
    cool(stone, 10)
""")


def test_domains_have_single_primary_owner():
    seen = {}
    for name, profile in ELEMENTS.items():
        for domain in profile.domains:
            assert domain not in seen or seen[domain] == name
            seen[domain] = name
    assert DOMAIN_OWNER["temperature"] == "Fire"
    assert DOMAIN_OWNER["pressure"] == "Air"


def test_reserved_property_names_and_local_updates():
    with pytest.raises(RuntimeErrorML, match="reserved"):
        run("mass = 5\n")
    rt = run("""
def count_up():
    count = 0
    while count < 3:
        count = count + 1
    incant count
answer = count_up()
""")
    assert rt.global_env.get("answer") == 3


def test_heat_requires_property_and_forbidden_operation_errors_are_distinct():
    rt = Runtime()
    no_temp = MagicObject("Spirit")
    no_temp.properties.pop("temp")
    with pytest.raises(TypeErrorML, match="property 'temp'"):
        rt.op_heat(no_temp, 100)
    blocked = MagicObject("Earth")
    blocked.properties["forbidden_ops"].add("heat")
    with pytest.raises(MagicErrorML, match="forbidden"):
        rt.op_heat(blocked, 100)


def test_virtual_timing_uses_safety_cap_not_mana_upkeep():
    rt = run('\nspldef pulse():\n    fire = create Fire\n    every 1 s:\n        heat(fire, 400)\nrelease(pulse)\nadvance_time(2 s)\n')
    assert rt.elapsed_virtual_time == pytest.approx(2.0)
    assert rt.total_mana_used > 10
    assert len(rt.timers) == 1
    rt.advance_time(58)
    assert len(rt.timers) == 0


def test_event_handler_can_run_against_world_state():
    rt = run('\nstone = create Earth\ndef setup():\n    when impact:\n        heat(stone, 500)\nsetup()\nemit("impact")\n')
    stone = rt.global_env.get("stone")
    assert stone.properties["temp"] == Quantity(793.15, "K")
    assert len(rt.event_handlers) == 1


def test_combination_consumes_inputs_and_conserves_mass_in_result():
    rt = run("""
water = create Water
earth = create Earth
mud = combine(water, earth)
""")
    water = rt.global_env.get("water")
    earth = rt.global_env.get("earth")
    mud = rt.global_env.get("mud")
    assert not water.properties["active"]
    assert not earth.properties["active"]
    assert mud.properties["mass"] == Quantity(2, KG)


def test_unit_mismatch_is_rejected_by_magic_operation():
    with pytest.raises(UnitErrorML):
        run("""
fire = create Fire
heat(fire, 10 m)
""")


def test_clamp_speed_rejects_real_violation_but_repairs_float_overshoot():
    from magiclang.physics import clamp_speed, C
    near = Vector3(C * (1 + 5e-13), 0, 0, VELOCITY)
    fixed = clamp_speed(near)
    assert fixed.magnitude() == pytest.approx(C)
    with pytest.raises(PhysicsErrorML):
        clamp_speed(Vector3(C * (1 + 1e-6), 0, 0, VELOCITY))
