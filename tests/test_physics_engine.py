import re
import math

import pytest

from magiclang.errors import PhysicsErrorML, RuntimeErrorML, UnitErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.physics import Vector3
from magiclang.libraries.three_d import Vector3 as LibraryVector3, kinetic_energy as library_kinetic_energy
from magiclang.physics_engine import _collision_radius
from magiclang.runtime import MagicObject, Runtime
from magiclang.units import ACCELERATION, KG, M2, Quantity, VELOCITY


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def execute(source):
    runtime = Runtime(project_root=ROOT)
    if re.search(r"(?<!\.)\bdirection\s*\(", source):
        if not source.lstrip().startswith('load geometry2d'):
            source = 'load geometry2d\n' + source
        source = re.sub(r"(?<!\.)\bdirection(?=\s*\()", "geometry2d.direction", source)
    program = Parser(Lexer(source).tokenize()).parse()
    runtime.execute(program)
    return runtime


def test_vector_can_be_scaled_by_a_quantity_and_composes_units():
    runtime = execute('acceleration_vector = direction(0, -1, 0) * 9.81 m/s2\n')
    acceleration = runtime.global_env.get("acceleration_vector")
    assert isinstance(acceleration, Vector3)
    assert acceleration.dimension == ACCELERATION
    assert acceleration.x == pytest.approx(0)
    assert acceleration.y == pytest.approx(-9.81)


def test_advance_time_integrates_persistent_acceleration_and_position():
    runtime = execute('''
stone = create Earth
accelerate(stone, direction(1, 0, 0) * 2 m/s2)
advance_time(1 s, timestep=0.01 s)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x == pytest.approx(2.0, abs=1e-8)
    assert stone.properties["pos"].x == pytest.approx(1.0, abs=1e-8)
    assert stone.properties["kinetic_energy"].value == pytest.approx(2.0, rel=1e-6)
    assert stone.properties["momentum"].x == pytest.approx(2.0, rel=1e-6)


def test_world_gravity_is_explicit_and_uses_vector_units():
    runtime = execute('''
stone = create Earth
advance_time(1 s, timestep=0.01 s, gravity=direction(0, -1, 0) * 9.81 m/s2)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].y == pytest.approx(-9.81, abs=1e-8)
    assert stone.properties["pos"].y == pytest.approx(-4.905, abs=1e-8)


def test_swept_collision_resolves_fast_projectile_and_applies_target_damage():
    runtime = execute('''
projectile = create Fire
projectile.collision_radius = 0.25 m
velocity(projectile, geometry2d.direction(1, 0, 0) * 100 m/s)
target = tgset:
    hp = 1000
    max_hp = 1000
    defence = 0
    resist_fire = 0
target.collision_radius = 0.25 m
move(target, 2 m, direction(1, 0, 0))
advance_time(0.05 s, timestep=0.05 s)
''')
    projectile = runtime.global_env.get("projectile")
    target = runtime.global_env.get("target")
    assert target.properties["hp"] == pytest.approx(975.0)
    assert len(runtime.last_collisions) == 1
    assert runtime.last_collisions[0]["impact_energy_j"] == pytest.approx(2500.0)
    assert runtime.last_collisions[0]["converted_to_heat_j"] > 0
    # The collision occurs when the projectile reaches x=1.5 m, at 0.015 s.
    assert runtime.last_collisions[0]["time_s"] == pytest.approx(0.015, abs=1e-9)
    assert target.properties["temp"].value > 293.15
    assert projectile.properties["vel"].x < 100
    assert target.properties["vel"].x > 0


def test_target_resistance_and_defence_reduce_collision_damage():
    runtime = execute('''
projectile = create Fire
projectile.collision_radius = 0.25 m
velocity(projectile, direction(1, 0, 0) * 100 m/s)
target = tgset:
    hp = 1000
    max_hp = 1000
    defence = 5
    resist_fire = 0.5
target.collision_radius = 0.25 m
move(target, 2 m, direction(1, 0, 0))
advance_time(0.05 s, timestep=0.05 s)
''')
    target = runtime.global_env.get("target")
    # 2500 J -> 25 base damage; half resistance -> 12.5; defence removes 5.
    assert target.properties["hp"] == pytest.approx(992.5)


def test_collision_disable_does_not_disable_motion():
    runtime = execute('''
stone = create Earth
stone.collidable = false
velocity(stone, direction(1, 0, 0) * 10 m/s)
advance_time(1 s, timestep=0.01 s)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["pos"].x == pytest.approx(10.0, abs=1e-8)


def test_invalid_collision_radius_restitution_and_gravity_are_rejected():
    with pytest.raises(PhysicsErrorML):
        execute('stone = create Earth\nstone.collision_radius = -1 m\n')
    with pytest.raises(PhysicsErrorML):
        execute('stone = create Earth\nstone.restitution = 1.5\n')
    with pytest.raises(UnitErrorML):
        execute('advance_time(1 s, gravity=direction(0, -1, 0) * 9.81 m/s)\n')


def test_world_physics_rejects_z_motion_but_3d_vector_math_remains_available():
    # Three-dimensional vectors remain usable as ordinary library values.
    runtime = execute('load vector3d\nthree_d = vector3d.vector(1, 2, 3)\nshow vector3d.magnitude(three_d)\n')
    assert runtime.global_env.get("three_d").z != 0

    with pytest.raises(PhysicsErrorML, match="2D x-y world plane"):
        execute('load vector3d\nstone = create Earth\nvelocity(stone, vector3d.velocity_vector(10 m/s, 0 m/s, 10 m/s))\n')
    with pytest.raises(PhysicsErrorML, match="2D x-y world plane"):
        execute('load vector3d\nadvance_time(1 s, gravity=vector3d.acceleration_vector(0 m/s2, -9.81 m/s2, 1 m/s2))\n')
    with pytest.raises(PhysicsErrorML, match="2D x-y world plane"):
        execute('load vector3d\nstone = create Earth\nstone.pos = vector3d.position(0 m, 0 m, 1 m)\n')


def test_zero_collision_radius_uses_projected_area_not_volume():
    obj = MagicObject("Earth")
    obj.properties["area"] = Quantity(math.pi * 4, M2)
    obj.properties["volume"] = Quantity(1000, obj.properties["volume"].dimension)
    assert _collision_radius(obj) == pytest.approx(2.0)


def test_post_runs_physics_trial_against_existing_world_then_rolls_it_back(capsys):
    runtime = execute('\nprojectile = create Fire\nprojectile.collision_radius = 0.25 m\nvelocity(projectile, direction(1, 0) * 100 m/s)\ntarget = tgset:\n    hp = 1000\n    max_hp = 1000\n    defence = 0\n    resist_fire = 0\ntarget.collision_radius = 0.25 m\nmove(target, 2 m, direction(1, 0))\n\nspldef trial_hit():\n    advance_time(0.05 s, timestep=0.05 s)\n    incant target\n')
    projectile = runtime.global_env.get("projectile")
    target = runtime.global_env.get("target")
    start_position = projectile.properties["pos"]
    start_velocity = projectile.properties["vel"]
    start_target_position = target.properties["pos"]
    result = runtime.op_post(runtime.global_env.get("trial_hit"))
    output = capsys.readouterr().out

    assert result.ok is True
    assert result.committed is False
    assert result.hits
    assert result.hits[0].properties["hp"] < 1000
    assert "collision:" in output and "hit:" in output
    assert projectile.properties["pos"] == start_position
    assert projectile.properties["vel"] == start_velocity
    assert target.properties["pos"] == start_target_position
    assert target.properties["hp"] == pytest.approx(1000)
    assert runtime.last_collisions == []


def test_post_trials_motion_of_a_preexisting_object_but_keeps_hypothetical_result():
    runtime = execute('\nstone = create Earth\nvelocity(stone, direction(1, 0) * 10 m/s)\nspldef preview_motion():\n    advance_time(1 s, timestep=0.01 s)\n    incant stone\n')
    stone = runtime.global_env.get("stone")
    start_pos = stone.properties["pos"]
    start_vel = stone.properties["vel"]

    result = runtime.op_post(runtime.global_env.get("preview_motion"))

    assert result.ok and not result.committed
    assert result.incant_value.properties["pos"].x == pytest.approx(10.0, abs=1e-8)
    assert stone.properties["pos"] == start_pos
    assert stone.properties["vel"] == start_vel
    assert runtime.elapsed_virtual_time == pytest.approx(0.0)


def test_physics_failure_rolls_back_time_and_state():
    runtime = execute('''
stone = create Earth
accelerate(stone, direction(1, 0, 0) * 1e10 m/s2)
''')
    stone = runtime.global_env.get("stone")
    before_position = stone.properties["pos"]
    before_velocity = stone.properties["vel"]
    with pytest.raises(PhysicsErrorML, match="speed"):
        runtime.advance_time(1, timestep=0.1)
    assert runtime.elapsed_virtual_time == pytest.approx(0.0)
    assert stone.properties["pos"] == before_position
    assert stone.properties["vel"] == before_velocity


def test_collision_in_post_is_rolled_back_but_trace_contains_hit():
    runtime = execute('\nspldef strike():\n    projectile = create Fire\n    projectile.collision_radius = 0.25 m\n    velocity(projectile, direction(1, 0, 0) * 100 m/s)\n    target = tgset:\n        hp = 1000\n        max_hp = 1000\n        defence = 0\n        resist_fire = 0\n    target.collision_radius = 0.25 m\n    move(target, 2 m, direction(1, 0, 0))\n    advance_time(0.05 s, timestep=0.05 s)\n    incant target\n')
    spell = runtime.global_env.get("strike")
    result = runtime.op_post(spell)
    assert result.ok
    assert result.hits
    assert result.hits[0].properties["hp"] == pytest.approx(975.0)
    assert runtime.elapsed_virtual_time == pytest.approx(0.0)
    assert runtime.active_objects == []
    assert runtime.last_collisions == []


def test_push_is_one_time_action_and_does_not_repeat_during_later_ticks():
    runtime = execute('''
stone = create Earth
push(stone, 10 N, direction(1, 0, 0))
advance_time(1 s, timestep=0.01 s)
''')
    stone = runtime.global_env.get("stone")
    # push() applies its documented one-second action immediately. Advancing
    # the world should then move at the resulting speed, not apply the force again.
    assert stone.properties["vel"].x == pytest.approx(10.0, abs=1e-8)
    assert stone.properties["pos"].x == pytest.approx(10.0, abs=1e-6)


def test_explicit_acceleration_remains_persistent_until_changed():
    runtime = execute('''
stone = create Earth
stone.acc = direction(1, 0, 0) * 2 m/s2
advance_time(1 s, timestep=0.01 s)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["vel"].x == pytest.approx(2.0, abs=1e-8)
    assert stone.properties["pos"].x == pytest.approx(1.0, abs=1e-8)


def test_anchored_target_uses_projectile_mass_for_impact_energy():
    runtime = execute('''
projectile = create Fire
projectile.collision_radius = 0.25 m
velocity(projectile, direction(1, 0, 0) * 100 m/s)
target = tgset:
    hp = 1000
    max_hp = 1000
    defence = 0
    resist_fire = 0
target.collision_radius = 0.25 m
anchor(target, direction(1, 0, 0) * 2 m)
advance_time(0.05 s, timestep=0.05 s)
''')
    target = runtime.global_env.get("target")
    projectile = runtime.global_env.get("projectile")
    assert len(runtime.last_collisions) == 1
    assert runtime.last_collisions[0]["impact_energy_j"] == pytest.approx(5000.0)
    assert target.properties["hp"] == pytest.approx(950.0)
    assert target.properties["pos"].x == pytest.approx(2.0)
    assert projectile.properties["vel"].x < 0


def test_collision_converts_lost_kinetic_energy_to_heat_without_losing_total_energy():
    runtime = Runtime()
    runtime.execute(Parser(Lexer('\nload geometry2d\nprojectile = create Fire\nprojectile.collision_radius = 0.25 m\nvelocity(projectile, geometry2d.direction(1, 0, 0) * 100 m/s)\ntarget = tgset:\n    hp = 1000\n    max_hp = 1000\n    defence = 0\n    resist_fire = 0\ntarget.collision_radius = 0.25 m\nmove(target, 2 m, geometry2d.direction(1, 0, 0))\n').tokenize()).parse())
    projectile = runtime.global_env.get("projectile")
    target = runtime.global_env.get("target")
    energy_before = projectile.properties["energy"].value + target.properties["energy"].value
    runtime.advance_time(0.05, timestep=0.05)
    energy_after = projectile.properties["energy"].value + target.properties["energy"].value
    assert energy_after == pytest.approx(energy_before, abs=1e-6)
    assert runtime.last_collisions[0]["converted_to_heat_j"] > 0


def test_perfectly_elastic_equal_mass_collision_conserves_momentum_and_kinetic_energy():
    runtime = execute('''
a = create Earth
a.collision_radius = 0.25 m
a.restitution = 1
velocity(a, direction(1, 0, 0) * 10 m/s)
b = create Earth
b.collision_radius = 0.25 m
b.restitution = 1
move(b, 1.5 m, direction(1, 0, 0))
advance_time(0.1 s, timestep=0.1 s)
''')
    a = runtime.global_env.get("a")
    b = runtime.global_env.get("b")
    assert a.properties["vel"].x == pytest.approx(0.0, abs=1e-8)
    assert b.properties["vel"].x == pytest.approx(10.0, abs=1e-8)
    assert a.properties["momentum"].x + b.properties["momentum"].x == pytest.approx(10.0, abs=1e-8)
    assert a.properties["kinetic_energy"].value + b.properties["kinetic_energy"].value == pytest.approx(50.0, abs=1e-8)
    assert runtime.last_collisions[0]["converted_to_heat_j"] == pytest.approx(0.0, abs=1e-8)


def test_same_physics_input_produces_same_position_collision_and_damage():
    source = '''
projectile = create Fire
projectile.collision_radius = 0.25 m
velocity(projectile, direction(1, 0, 0) * 100 m/s)
target = tgset:
    hp = 1000
    max_hp = 1000
    defence = 0
    resist_fire = 0
target.collision_radius = 0.25 m
move(target, 2 m, direction(1, 0, 0))
advance_time(0.05 s, timestep=0.01 s)
'''
    first = execute(source)
    second = execute(source)
    for runtime in (first, second):
        projectile = runtime.global_env.get("projectile")
        target = runtime.global_env.get("target")
        assert target.properties["hp"] == pytest.approx(975.0)
        assert target.properties["pos"].x > 2.0
    assert first.global_env.get("projectile").properties["pos"] == second.global_env.get("projectile").properties["pos"]
    assert first.global_env.get("projectile").properties["vel"] == second.global_env.get("projectile").properties["vel"]
    assert first.global_env.get("target").properties["pos"] == second.global_env.get("target").properties["pos"]
    assert first.last_collisions == second.last_collisions


def test_collision_pair_budget_rejects_excessive_work_and_rolls_back(monkeypatch):
    import magiclang.runtime as runtime_module

    runtime = execute('''
a = create Earth
a.collision_radius = 1 m
b = create Earth
b.collision_radius = 1 m
velocity(a, direction(1, 0, 0) * 10 m/s)
move(b, 3 m, direction(1, 0, 0))
''')
    a = runtime.global_env.get("a")
    before_pos = a.properties["pos"]
    monkeypatch.setattr(runtime_module, "MAX_COLLISION_PAIR_CHECKS_PER_ADVANCE", 0)
    with pytest.raises(RuntimeErrorML, match="collision pairs"):
        runtime.advance_time(0.1, timestep=0.1)
    assert runtime.elapsed_virtual_time == pytest.approx(0.0)
    assert a.properties["pos"] == before_pos


def test_internal_acceleration_persistence_flag_cannot_be_assigned():
    from magiclang.errors import MagicErrorML

    with pytest.raises(MagicErrorML, match="internal physics flag"):
        execute("stone = create Earth\nstone.acceleration_persistent = false\n")


def test_physics_collision_events_run_registered_handlers():
    runtime = execute('\nprojectile = create Fire\nprojectile.collision_radius = 0.25 m\nvelocity(projectile, direction(1, 0, 0) * 100 m/s)\ntarget = tgset:\n    hp = 1000\n    max_hp = 1000\n    defence = 0\n    resist_fire = 0\ntarget.collision_radius = 0.25 m\nmove(target, 2 m, direction(1, 0, 0))\ndef register_events():\n    when impact:\n        heat(target, 10 K)\n    when damaged:\n        heat(target, 20 K)\nregister_events()\nadvance_time(0.05 s, timestep=0.05 s)\n')
    target = runtime.global_env.get("target")
    assert target.properties["hp"] == pytest.approx(975.0)
    # Both handlers ran after the ordinary collision heat was applied.
    assert target.properties["temp"].value > 323.15


def test_perfectly_inelastic_coincident_objects_are_separated_after_contact():
    runtime = execute('''
a = create Earth
a.collision_radius = 0.5 m
a.restitution = 0
velocity(a, direction(1, 0, 0) * 10 m/s)
b = create Earth
b.collision_radius = 0.5 m
b.restitution = 0
advance_time(0.1 s, timestep=0.1 s)
''')
    a = runtime.global_env.get("a")
    b = runtime.global_env.get("b")
    separation = (b.properties["pos"] - a.properties["pos"]).magnitude()
    assert separation >= 1.0 - 1e-6
    assert len(runtime.last_collisions) == 1
    assert a.properties["vel"].x == pytest.approx(5.0, abs=1e-8)
    assert b.properties["vel"].x == pytest.approx(5.0, abs=1e-8)


def test_area_property_scales_by_square_and_changes_2d_collision_bound():
    runtime = execute('''
stone = create Earth
stone.area = 4 m2
scale(stone, 2)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["area"].value == pytest.approx(16.0)
    assert _collision_radius(stone) == pytest.approx(math.sqrt(16.0 / math.pi))


def test_three_d_library_remains_available_without_enabling_3d_world_motion():
    velocity = LibraryVector3(3, 4, 12, VELOCITY)
    energy = library_kinetic_energy(Quantity(2, KG), velocity)
    assert energy.value > 0
    # The same vector math remains available, but world-object motion is planar.
    with pytest.raises(PhysicsErrorML, match="2D x-y world plane"):
        execute('load vector3d\nstone = create Earth\nvelocity(stone, vector3d.velocity_vector(3 m/s, 4 m/s, 12 m/s))\n')


def test_post_and_release_simulate_same_spell_but_only_release_commits():
    runtime = execute('\nstone = create Earth\nspldef move_stone():\n    velocity(stone, direction(1, 0) * 10 m/s)\n    advance_time(1 s, timestep=0.01 s)\n    incant stone\n')
    stone = runtime.global_env.get("stone")
    spell = runtime.global_env.get("move_stone")
    trial = runtime.op_post(spell)
    assert trial.ok and not trial.committed
    assert trial.incant_value.properties["pos"].x == pytest.approx(10.0, abs=1e-8)
    assert stone.properties["pos"].x == pytest.approx(0.0)
    fired = runtime.op_release(spell)
    assert fired.ok and fired.committed
    assert fired.incant_value.properties["pos"].x == pytest.approx(10.0, abs=1e-8)
    assert stone.properties["pos"].x == pytest.approx(10.0, abs=1e-8)


def test_explicit_collision_radius_scales_with_the_object():
    runtime = execute('''
stone = create Earth
stone.collision_radius = 2 m
scale(stone, 3)
''')
    stone = runtime.global_env.get("stone")
    assert stone.properties["area"].value == pytest.approx(9.0)
    assert stone.properties["collision_radius"].value == pytest.approx(6.0)
    assert _collision_radius(stone) == pytest.approx(6.0)
