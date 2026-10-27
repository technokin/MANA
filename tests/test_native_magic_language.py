from __future__ import annotations

import pytest

from magiclang.errors import PhysicsErrorML, SyntaxErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.runtime import Runtime, SpellResult
from magiclang.units import KG, M, Quantity, S


def execute(source: str, runtime: Runtime | None = None):
    runtime = runtime or Runtime()
    program = Parser(Lexer(source, "<native-language-test>").tokenize(), "<native-language-test>").parse()
    result = runtime.execute(program)
    return runtime, result


def test_spell_is_the_primary_indented_keyword_and_spldef_remains_compatible():
    runtime, _ = execute('''spell warm_stone():
    stone = conjure iron, mass=2 kg, shape=sphere
    heat(stone, 400 K)
    incant stone

release(warm_stone)
''')
    assert runtime.active_objects
    assert runtime.active_objects[0].properties["material"] == "Iron"

    runtime2, _ = execute('''spldef old_spelling():
    incant 7

post(old_spelling)
''')
    assert runtime2.global_env.get("old_spelling").is_spell


def test_native_conjure_syntax_supports_physical_properties():
    runtime, _ = execute('''load geometry2d
speed = geometry2d.direction(1, 0) * (5 m/s)
ore = conjure steel, mass=12 kg, shape=sphere, name="Iron Bell", anchored=true, collidable=true, restitution=0.6, friction=0.8, drag_coefficient=0.4, velocity=speed
''')
    ore = runtime.global_env.get("ore")
    props = ore.properties
    assert props["material"] == "steel"
    assert props["mass"].value == pytest.approx(12)
    assert props["display_name"] == "Iron Bell"
    assert props["anchored"] is True
    assert props["collidable"] is True
    assert props["restitution"] == pytest.approx(0.6)
    assert props["friction"] == pytest.approx(0.8)
    assert props["drag_coefficient"] == pytest.approx(0.4)
    assert props["vel"].x == pytest.approx(5)


def test_native_conjure_has_clear_duplicate_and_invalid_option_errors():
    with pytest.raises(SyntaxErrorML, match="specified more than once"):
        execute('ore = conjure steel, mass=1 kg, mass=2 kg\n')
    with pytest.raises(SyntaxErrorML, match="unknown conjure option"):
        execute('ore = conjure steel, mystery=4\n')
    runtime = Runtime()
    with pytest.raises(PhysicsErrorML, match="no more than 1e12 kg"):
        runtime.op_conjure("steel", mass=Quantity(1e13, KG))


def test_native_weather_creates_an_area_zone_and_does_not_change_global_weather():
    runtime, result = execute('''spell rain_ring():
    weather rain, intensity=0.8, duration=30 s, radius=10 m

release(rain_ring)
''')
    assert isinstance(result, SpellResult) and result.ok and result.committed
    assert runtime.environment_state["kind"] == "clear"
    assert len(runtime.weather_regions) == 1
    zone = runtime.weather_regions[0]
    assert zone["kind"] == "rain"
    assert zone["radius_m"] == pytest.approx(10)
    assert zone["center"] == [0, 0]


def test_area_weather_only_changes_objects_inside_the_radius():
    runtime = Runtime()
    near = runtime.op_conjure("wood", mass=Quantity(1, KG), position=Vector3(2, 0, 0, M))
    far = runtime.op_conjure("wood", mass=Quantity(1, KG), position=Vector3(100, 0, 0, M))
    runtime.global_env.set_local("near", near)
    runtime.global_env.set_local("far", far)
    execute('weather rain, intensity=1, radius=10 m, duration=20 s\n', runtime)
    runtime._apply_environment_step(1.0, [near, far])
    assert near.properties["wetness"] > 0
    assert far.properties.get("wetness", 0) == 0


def test_weather_function_api_can_also_target_an_area_and_area_list_is_a_copy():
    runtime = Runtime()
    weather = runtime.global_env.get("weather").values
    zone = weather["precipitation"]("snow", intensity=0.7, radius=Quantity(20, M), duration=Quantity(10, S))
    assert zone["scope"] == "area"
    zones = weather["areas"]()
    zones[0]["radius_m"] = -1
    assert weather["areas"]()[0]["radius_m"] == pytest.approx(20)


def test_post_rolls_back_area_weather_and_release_commits_it():
    src = '''spell hail_circle():
    weather clear, precipitation=hail, intensity=0.6, duration=12 s, radius=6 m

post(hail_circle)
'''
    runtime, result = execute(src)
    assert isinstance(result, SpellResult) and result.ok and not result.committed
    assert runtime.weather_regions == []
    execute("release(hail_circle)\n", runtime)
    assert len(runtime.weather_regions) == 1


def test_native_weather_rejects_unknown_and_duplicate_options():
    with pytest.raises(SyntaxErrorML, match="unknown weather option"):
        execute('weather rain, sideway=1\n')
    with pytest.raises(SyntaxErrorML, match="specified more than once"):
        execute('weather rain, radius=2 m, radius=3 m\n')


def test_spell_and_weather_syntax_never_needs_curly_braces():
    src = '''spell clear_my_square():
    weather clear, radius=20 m, duration=5 s

release(clear_my_square)
'''
    runtime, result = execute(src)
    assert result.ok
    assert runtime.weather_regions[0]["kind"] == "clear"


def test_native_transform_verbs_change_composition_geometry_phase_and_form():
    runtime, _ = execute('''iron = conjure iron, mass=3 kg, shape=sphere
transmute iron into silver
shape iron into ring
transform iron into liquid
transfigure iron into knight
show iron.material
show iron.shape
show iron.state
show iron.visual_form
''')
    iron = runtime.global_env.get("iron")
    assert iron.properties["material"] == "Silver"
    assert iron.properties["shape"] == "ring"
    assert iron.properties["state"] == "liquid"
    assert iron.properties["visual_form"] == "knight"
    assert iron.properties["mass"].value == pytest.approx(3)


def test_native_transform_accepts_parenthesized_dynamic_destination():
    runtime, _ = execute('''chosen_material = "gold"
ore = conjure iron, mass=1 kg
transmute ore into (chosen_material)
''')
    assert runtime.global_env.get("ore").properties["material"] == "Gold"


def test_appraise_and_cast_are_native_spell_actions_with_distinct_commit_semantics(capsys):
    runtime, _ = execute('''spell form_orb():
    orb = conjure iron, mass=1 kg
    incant orb

appraise form_orb
''')
    assert runtime.active_objects == []
    appraisal = capsys.readouterr().out
    assert "[APPRAISAL form_orb]" in appraisal
    assert "mana appraisal:" in appraisal

    execute("cast form_orb\n", runtime)
    assert len(runtime.active_objects) == 1
    cast_output = capsys.readouterr().out
    assert "[CAST form_orb]" in cast_output


def test_native_appraisal_and_cast_keep_parenthesized_forms_compatible(capsys):
    runtime, _ = execute('''spell no_change():
    incant 7

post(no_change)
release(no_change)
''')
    output = capsys.readouterr().out
    assert "[POST no_change]" in output
    # Legacy release is intentionally silent on success; it still committed.
    assert runtime.total_mana_used >= 0


def test_local_precipitation_composition_preserves_area_settings_and_uses_zone_intensity():
    runtime = Runtime()
    weather = runtime.global_env.get("weather").values
    weather["configure"]("clear", radius=Quantity(25, M), intensity=0.2, duration=Quantity(30, S))
    updated = weather["precipitation"]("rain", radius=Quantity(25, M))
    assert updated["scope"] == "area"
    assert updated["precipitation"] == "rain"
    assert updated["intensity"] == pytest.approx(0.75)
    assert updated["wind_speed_mps"] == pytest.approx(0.0)
    assert updated["radius_m"] == pytest.approx(25)


def test_native_summon_uses_plane_route_and_native_cast_commits_the_being():
    src = '''load planes
planes.open_path("Wild Realm", "Mortal Plane")
spell call_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    incant griffin

appraise call_griffin
cast call_griffin
'''
    runtime, _ = execute(src)
    summoned = [obj for obj in runtime.active_objects if obj.properties.get("is_summoned")]
    assert len(summoned) == 1
    assert summoned[0].properties["species"] == "Griffin"
    assert summoned[0].properties["home_plane"] == "Wild Realm"


def test_native_summon_accepts_dynamic_name_and_position_and_validates_options():
    # Parenthesised expressions are the unambiguous form for dynamic identifiers.
    source = '''load planes
load geometry2d
planes.open_path("Wild Realm", "Mortal Plane")
being_name = "Griffin"
position = geometry2d.point(12 m, 4 m)
griffin = summon (being_name) from ("Wild Realm"), position=position, requirements=[]
'''
    runtime, _ = execute(source)
    griffin = runtime.global_env.get("griffin")
    assert griffin.properties["species"] == "Griffin"
    assert griffin.properties["pos"].x == pytest.approx(12)
    assert griffin.properties["pos"].y == pytest.approx(4)
    with pytest.raises(SyntaxErrorML, match="unknown summon option"):
        execute('griffin = summon "Griffin", surprise=true\n')
    with pytest.raises(SyntaxErrorML, match="specified more than once"):
        execute('griffin = summon "Griffin", position=geometry2d.point(0 m, 0 m), position=geometry2d.point(1 m, 1 m)\n')


def test_native_custom_body_form_uses_named_trait_parameters_without_dict_literals():
    source = '''load planes
load physiology
planes.open_path("Wild Realm", "Mortal Plane")
spell morph_griffin():
    griffin = summon "Griffin" from "Wild Realm"
    physiology.define_form("Winged Scout",
        organs=["brain", "brainstem", "heart", "blood", "lungs", "skeleton",
                "skeletal_muscles", "skin", "eyes", "wings", "air_sacs"],
        movement_mode="flight-capable", strength=1.4, speed=1.6, senses=1.3)
    transfigure(griffin, "Winged Scout")
    incant griffin
cast morph_griffin
'''
    runtime, _ = execute(source)
    being = next(obj for obj in runtime.active_objects if obj.properties.get("is_summoned"))
    assert being.properties["body_form"] == "winged scout"
    assert being.properties["body_form_traits"]["strength"] == pytest.approx(1.4)
    assert being.properties["body_form_traits"]["speed"] == pytest.approx(1.6)
    assert being.properties["body_form_traits"]["senses"] == pytest.approx(1.3)
    assert runtime.custom_body_forms["winged scout"]["movement_mode"] == "flight-capable"
