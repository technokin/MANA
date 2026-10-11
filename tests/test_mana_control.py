from __future__ import annotations

import pytest

from pathlib import Path

from magiclang.errors import MagicErrorML, TypeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime


def run(source: str, *, filename: str = "mana-control-test.mana") -> Runtime:
    runtime = Runtime(project_root=".")
    program = Parser(Lexer(source, filename).tokenize(), filename).parse()
    runtime.execute(program)
    return runtime


def test_mana_type_and_namespace_are_both_available():
    runtime = run('''
raw_mana = create Mana
construct = mana.form()
''')
    raw = runtime.global_env.get("raw_mana")
    construct = runtime.global_env.get("construct")
    assert raw.element == "Mana"
    assert construct.element == "Mana"
    assert construct.properties["material"] == "PureMana"
    assert construct.properties["mass"].value == 0
    assert construct.properties["mana_energy"].value == pytest.approx(1000)
    assert construct.properties["pos"].x == pytest.approx(10)
    assert construct.properties["collision_radius"].value == pytest.approx(1)
    assert runtime.total_mana_used == pytest.approx(1000)


def test_mana_burst_and_emit_defaults_are_easy_to_call():
    runtime = run('''
burst_result = mana.burst()
emit_result = mana.emit()
''')
    burst = runtime.global_env.get("burst_result")
    emit = runtime.global_env.get("emit_result")
    assert burst["energy_j"] == pytest.approx(1000)
    assert burst["radius_m"] == pytest.approx(1)
    assert burst["position_m"] == pytest.approx([10, 0])
    assert emit["power_w"] == pytest.approx(1000)
    assert emit["duration_s"] == pytest.approx(1)
    assert emit["energy_j"] == pytest.approx(1000)
    assert emit["range_m"] == pytest.approx(10)
    assert emit["position_m"] == pytest.approx([10, 0])


def test_mana_emit_can_use_named_overrides_without_filling_optional_parameters():
    runtime = run('\nload geometry2d\nresult = mana.emit(power=250 W, duration=2 s, position=geometry2d.point(4 m, 3 m))\n')
    result = runtime.global_env.get("result")
    assert result["power_w"] == pytest.approx(250)
    assert result["duration_s"] == pytest.approx(2)
    assert result["energy_j"] == pytest.approx(500)
    assert result["position_m"] == pytest.approx([4, 3])


def test_tgset_material_profiles_infer_wood_combustion_and_rock_powdering():
    runtime = run('''
stick = tgset:
    kind = "stick"
    material = "Wood"
    mass = 0.5 kg
    volume = 0.001 m3
    shape = line
    state = "solid"

rock = tgset:
    kind = "rock"
    material = "Rock"
    mass = 2 kg
    volume = 0.001 m3
    shape = circle
    state = "solid"

heat(stick, 300 K)
transform(rock, "powder")
''')
    stick = runtime.global_env.get("stick")
    rock = runtime.global_env.get("rock")
    assert stick.properties["kind"] == "stick"
    assert stick.properties["material"] == "Wood"
    assert stick.properties["combustible"] is True
    assert stick.properties["state"] == "burning"
    assert rock.properties["kind"] == "rock"
    assert rock.properties["powderable"] is True
    assert rock.properties["state"] == "powder"
    assert rock.properties["mass"].value == pytest.approx(2)


def test_tgset_material_can_override_inferred_combustibility_and_powderability():
    runtime = run('''
sealed_wood = tgset:
    material = "Wood"
    combustible = false
    powderable = false
''')
    obj = runtime.global_env.get("sealed_wood")
    assert obj.properties["combustible"] is False
    assert obj.properties["powderable"] is False
    with pytest.raises(MagicErrorML, match="not defined as powderable"):
        run('''
rock = tgset:
    material = "Rock"
    powderable = false
transform(rock, "powder")
''')


def test_mana_toward_uses_active_tgset_target_when_destination_is_omitted():
    runtime = run('\nload geometry2d\nstone = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(0 m, 0 m)\nmarker = tgset:\n    pos = geometry2d.point(5 m, 0 m)\ntgset(marker):\n    mana.toward(stone)\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x > 0
    assert stone.properties["vel"].y == pytest.approx(0)


def test_mana_away_uses_active_tgset_target_when_source_is_omitted():
    runtime = run('\nload geometry2d\nstone = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(0 m, 0 m)\nmarker = tgset:\n    pos = geometry2d.point(5 m, 0 m)\ntgset(marker):\n    mana.away(stone)\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x < 0


def test_mana_collect_defaults_to_caster_position_outside_tgset():
    runtime = run('\nload geometry2d\nstone = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(5 m, 0 m)\nmana.collect([stone])\n')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x < 0


def test_mana_stop_and_hold_conserve_kinetic_energy_as_heat():
    runtime = run('''
stone = tgset:
    material = "Rock"
    mass = 2 kg
    volume = 0.001 m3
velocity(stone, 10 m/s)
energy_before = stone.energy
mana.hold(stone)
energy_after = stone.energy
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["anchored"] is True
    assert stone.properties["vel"].magnitude() == pytest.approx(0)
    assert runtime.global_env.get("energy_after").value == pytest.approx(runtime.global_env.get("energy_before").value)
    assert any(entry.get("operation") == "mana.stop" and entry.get("direction") == "internal_transfer"
               for entry in runtime.energy_ledger)


def test_mana_control_requires_a_destination_if_no_tgset_context_exists():
    with pytest.raises(TypeErrorML, match="destination"):
        run('''
stone = tgset:
    material = "Rock"
    mass = 1 kg
    volume = 0.001 m3
mana.toward(stone)
''')


def test_mana_namespace_side_effects_are_blocked_inside_direct_helper_calls():
    with pytest.raises(MagicErrorML, match="cannot run inside a directly called helper"):
        run('\ndef bad_helper():\n    mana.form()\n    incant 1\nanswer = bad_helper()\n')


def test_mana_namespace_import_is_optional_but_supported():
    runtime = run('\nload mana\norb = mana.form("sphere", energy=5 J, radius=0.2 m)\n')
    orb = runtime.global_env.get("orb")
    assert orb.properties["mana_energy"].value == pytest.approx(5)
    assert orb.properties["collision_radius"].value == pytest.approx(0.2)


def test_mana_projectile_transfers_its_energy_on_collision():
    runtime = run('\nload geometry2d\nstone = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(12 m, 0 m)\norb = mana.form("projectile", energy=100 J, radius=0.1 m, position=geometry2d.point(10 m, 0 m))\nvelocity(orb, 5 m/s)\nadvance_time(0.5 s, timestep=0.01 s)\n')
    stone = runtime.global_env.get("stone")
    orb = runtime.global_env.get("orb")
    impact = [entry for entry in runtime.energy_ledger if entry.get("operation") == "mana_projectile_impact"]
    assert len(impact) == 1
    assert impact[0]["amount_j"] == pytest.approx(100)
    assert impact[0]["source_delta_j"] == pytest.approx(-100)
    assert impact[0]["target_delta_j"] == pytest.approx(100)
    assert stone.properties["temp"].value == pytest.approx(293.25)
    assert orb.properties["active"] is False
    assert orb.properties["mana_energy"].value == pytest.approx(0)


def test_collect_handles_multiple_objects_and_already_collected_item():
    runtime = run('\nload geometry2d\nnear = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(0 m, 0 m)\nfar = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(5 m, 0 m)\nresult = mana.collect([near, far])\n')
    near = runtime.global_env.get("near")
    far = runtime.global_env.get("far")
    result = runtime.global_env.get("result")
    assert result == [near, far]
    assert near.properties["vel"].magnitude() == pytest.approx(0)
    assert far.properties["vel"].x < 0


def test_burst_and_emit_transfer_energy_to_recipients():
    burst_runtime = run('\nload geometry2d\nrock = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(10 m, 0 m)\nresult = mana.burst(energy=100 J, radius=1 m)\n')
    rock = burst_runtime.global_env.get("rock")
    result = burst_runtime.global_env.get("result")
    assert result["affected"] == 1
    assert result["delivered_j"] == pytest.approx(100)
    assert rock.properties["vel"].x > 0
    assert any(entry.get("operation") == "mana.burst" and entry.get("amount_j") == pytest.approx(100)
               for entry in burst_runtime.energy_ledger)

    emit_runtime = run('\nload geometry2d\nrock = tgset:\n    material = "Rock"\n    mass = 1 kg\n    volume = 0.001 m3\n    pos = geometry2d.point(12 m, 0 m)\nresult = mana.emit(power=100 W, duration=2 s)\n')
    rock = emit_runtime.global_env.get("rock")
    result = emit_runtime.global_env.get("result")
    assert result["energy_j"] == pytest.approx(200)
    assert result["delivered_j"] == pytest.approx(200)
    assert rock.properties["temp"].value == pytest.approx(293.35)


def test_all_mana_namespace_exports_are_documented():
    from magiclang.libraries.mana import build_library

    reference = Path("docs/current/libraries/MANA_LIBRARY.md").read_text(encoding="utf-8")
    exports = build_library(Runtime())
    omitted = [name for name in exports if f"`mana.{name}" not in reference]
    assert omitted == [], f"mana namespace functions missing from the library guide: {omitted}"


def test_combustible_material_already_above_ignition_threshold_ignites_on_heat_operation():
    runtime = run("""
stick = tgset:
    material = "Wood"
    mass = 0.5 kg
    volume = 0.001 m3
    temp = 600 K
heat(stick, 0 K)
""")
    stick = runtime.global_env.get("stick")
    assert stick.properties["state"] == "burning"
    assert stick.properties["burning"] is True
