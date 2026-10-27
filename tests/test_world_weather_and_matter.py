from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from magiclang.errors import MagicErrorML, PhysicsErrorML
from magiclang.physics import Vector3
from magiclang.runtime import Runtime
from magiclang.units import KG, M, Quantity, S, VELOCITY

ROOT = Path(__file__).resolve().parents[1]


def test_weather_is_a_parameter_namespace_not_a_spell_catalogue():
    runtime = Runtime()
    namespace = runtime.global_env.get("weather")
    assert {"configure", "set", "current", "clear", "wind", "precipitation", "temperature",
            "humidity", "fog", "clouds", "heat", "lightning"}.issubset(namespace.values)

    weather = namespace.values
    storm = weather["configure"]("storm", intensity=0.82, wind_speed=Quantity(13, VELOCITY),
                                  wind_direction="northwest", duration=Quantity(10, S))
    assert storm["kind"] == "storm"
    assert storm["precipitation"] == "rain"
    assert storm["wind_speed_mps"] == 13
    assert storm["indefinite"] is False

    snow = weather["precipitation"]("snow", intensity=0.6)
    assert snow["precipitation"] == "snow"
    assert snow["wind_speed_mps"] == 13
    assert snow["until"] == storm["until"]  # composable controls preserve the countdown

    clouds = weather["clouds"](0.95)
    assert clouds["clouds"] == 0.95
    assert clouds["precipitation"] == "snow"
    assert clouds["wind_speed_mps"] == 13
    assert weather["current"]()["clouds"] == 0.95


def test_rain_changes_material_world_state():
    runtime = Runtime()
    weather = runtime.global_env.get("weather").values
    weather["configure"]("rain", intensity=0.8)
    wood = runtime.op_conjure("wood", mass=Quantity(1, KG))
    assert wood.properties["wetness"] == 0 if "wetness" in wood.properties else True
    runtime._apply_environment_step(1.0, [wood])
    assert wood.properties["wetness"] > 0


def test_conjure_transmute_and_transfigure_keep_distinct_responsibilities():
    runtime = Runtime()
    metal = runtime.op_conjure("metal", mass=Quantity(2, KG),
                               position=Vector3(2, 1, 0, M), shape="sphere", name="Test metal")
    object_id = metal.object_id
    original_volume = metal.properties["volume"].value
    assert metal.properties["material"] == "metal"
    assert "scale" in metal.properties  # retain the runtime's full object-property template

    runtime.op_transmute(metal, "gold")
    assert metal.object_id == object_id
    assert metal.properties["material"] == "Gold"
    assert metal.properties["mass"].value == pytest.approx(2)
    assert metal.properties["volume"].value < original_volume

    runtime.op_transfigure(metal, "knight", scale=1.0)
    assert metal.object_id == object_id
    assert metal.properties["visual_form"] == "knight"

    with pytest.raises(MagicErrorML):
        runtime.op_conjure("Fire")


def test_weather_and_conjuration_example_runs_as_mana_source():
    result = subprocess.run(
        [sys.executable, str(ROOT / "mana.py"), str(ROOT / "examples" / "world_weather_conjuration.mana")],
        cwd=ROOT, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert "northwest" in result.stdout


def test_timed_weather_expires_nonprecipitation_atmosphere_parameters():
    runtime = Runtime()
    weather = runtime.global_env.get("weather").values
    weather["configure"]("clear", clouds=0.35, fog=0.2, humidity=0.8, duration=Quantity(2, S))
    assert runtime.environment_state["clouds"] == pytest.approx(0.35)
    runtime.advance_time(Quantity(3, S), timestep=Quantity(0.1, S))
    assert runtime.environment_state["kind"] == "clear"
    assert runtime.environment_state["clouds"] == 0
    assert runtime.environment_state["fog"] == 0
    assert runtime.environment_state["humidity"] == pytest.approx(0.45)
    assert runtime.environment_state["until"] is None


def test_world_namespace_exposes_real_physics_laws_and_validates_configuration():
    from magiclang.units import ACCELERATION, DENSITY

    runtime = Runtime()
    world = runtime.global_env.get("world").values
    assert {"configure", "current", "laws", "reset", "set_gravity", "set_air_density", "set_restitution", "set_friction"}.issubset(world)
    settings = world["configure"](
        gravity=Vector3(0, -9.81, 0, ACCELERATION),
        air_density=Quantity(1.1, DENSITY),
        restitution=0.35,
        friction=0.7,
        drag=False,
        thermal_exchange=False,
        phase_changes=True,
        wetting=False,
    )
    assert settings["gravity_m_s2"] == [0, -9.81]
    assert settings["air_density_kg_m3"] == pytest.approx(1.1)
    assert settings["default_restitution"] == pytest.approx(0.35)
    assert settings["friction_coefficient"] == pytest.approx(0.7)
    assert settings["drag_enabled"] is False
    assert settings["wetting_enabled"] is False
    laws = {entry["name"]: entry for entry in world["laws"]()}
    assert laws["Aerodynamic drag"]["active"] is False
    assert laws["Material phase"]["active"] is True
    assert laws["Contact friction"]["active"] is True
    assert "Matter conservation" in laws
    with pytest.raises(PhysicsErrorML, match="air_density"):
        world["configure"](air_density=-1)
    world["reset"]()
    assert world["current"]()["gravity_m_s2"] == [0, 0]


def test_configured_world_gravity_is_the_default_for_time_advancement():
    from magiclang.ast_nodes import Program
    from magiclang.lexer import Lexer
    from magiclang.parser import Parser

    runtime = Runtime()
    source = (
        "load geometry2d\n"
        "stone = create Earth\n"
        "world.configure(gravity=geometry2d.direction(0, -1) * 9.81 m/s2)\n"
        "advance_time(1 s, timestep=0.05 s)\n"
    )
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    stone = runtime.global_env.get("stone")
    assert stone.properties["pos"].y < 0


def test_wind_speed_applies_drag_even_without_a_separate_intensity_setting():
    runtime = Runtime()
    weather = runtime.global_env.get("weather").values
    wood = runtime.op_conjure("wood", mass=Quantity(1, KG), position=Vector3(1, 0, 0, M))
    weather["wind"](Quantity(12, VELOCITY), "east")
    assert runtime.environment_state["intensity"] == pytest.approx(0)
    runtime._apply_environment_step(1.0, [wood])
    assert wood.properties["vel"].x > 0


def test_periodic_table_and_material_composition_are_available_to_the_world_engine():
    runtime = Runtime()
    periodic = runtime.global_env.get("periodic").values
    assert periodic["count"] == 118
    iron_data = periodic["lookup"]("Fe")
    assert iron_data["name"] == "Iron"
    assert iron_data["atomic_number"] == 26
    assert iron_data["density_kg_m3"] > 7000

    steel = runtime.op_conjure("steel", mass=Quantity(2, KG))
    composition = steel.properties["composition"]
    assert composition["kind"] == "alloy"
    assert composition["estimated"] is True
    runtime.op_transmute(steel, "gold")
    assert steel.properties["composition"]["kind"] == "element"
    assert steel.properties["composition"]["symbol"] == "Au"
    assert steel.properties["mass"].value == pytest.approx(2)


def test_shape_changes_geometry_but_transfiguration_requires_living_or_conjured_matter():
    from magiclang.lexer import Lexer
    from magiclang.parser import Parser

    runtime = Runtime()
    runtime.execute(Parser(Lexer("ordinary = create Earth\n").tokenize()).parse())
    ordinary = runtime.global_env.get("ordinary")
    runtime.op_shape(ordinary, "polygon")
    assert ordinary.properties["shape"] == "polygon"
    with pytest.raises(MagicErrorML, match="living beings or matter made by conjure"):
        runtime.op_transfigure(ordinary, "knight")

    conjured = runtime.op_conjure("iron", mass=Quantity(1, KG))
    geometry_before = conjured.properties["shape"]
    runtime.op_transfigure(conjured, "knight")
    assert conjured.properties["visual_form"] == "knight"
    assert conjured.properties["shape"] == geometry_before


def test_world_configuration_is_atomic_when_a_later_argument_is_invalid():
    from magiclang.units import ACCELERATION, DENSITY

    runtime = Runtime()
    world = runtime.global_env.get("world").values
    before = world["current"]()
    with pytest.raises(Exception, match="air_density"):
        world["configure"](
            gravity=Vector3(0, -9.81, 0, ACCELERATION),
            air_density=Quantity(-1, DENSITY),
        )
    assert world["current"]() == before


def test_long_world_advances_aggregate_continuous_energy_entries():
    from magiclang.lexer import Lexer
    from magiclang.parser import Parser

    runtime = Runtime()
    source = '''
load geometry2d
stone = create Earth
world.configure(gravity=geometry2d.direction(0, -1) * 9.81 m/s2)
advance_time(5 s, timestep=0.001 s)
'''
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    integration_entries = [entry for entry in runtime.energy_ledger
                           if entry.get("operation") == "physics integration"]
    assert len(integration_entries) <= 2
    assert integration_entries
    assert all(entry.get("aggregation") == "advance_time" for entry in integration_entries)
    assert sum(entry["delta_j"] for entry in runtime.energy_ledger) == pytest.approx(
        runtime.energy_input_j - runtime.energy_output_j, rel=1e-9, abs=1e-5
    )


def test_weather_work_and_heat_are_accounted_without_per_tick_ledger_growth():
    from magiclang.lexer import Lexer
    from magiclang.parser import Parser

    runtime = Runtime()
    source = '''
load geometry2d
stone = conjure("wood", mass=1 kg, position=geometry2d.point(1 m, 0 m))
weather.configure("heatwave", intensity=1, wind_speed=2 m/s, wind_direction="east", duration=2 s)
advance_time(2 s, timestep=0.02 s)
'''
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    weather_entries = [entry for entry in runtime.energy_ledger
                       if entry.get("operation") in {"wind work", "atmospheric thermal exchange"}]
    assert weather_entries
    assert len(weather_entries) <= 4
    assert all(entry.get("aggregation") == "advance_time" for entry in weather_entries)
    active_energy = sum(obj.properties["energy"].value for obj in runtime._collect_physics_objects()
                        if obj.properties.get("active", True))
    assert active_energy == pytest.approx(
        runtime.energy_input_j - runtime.energy_output_j, rel=1e-8, abs=1e-4
    )
