import re
import pytest
from magiclang.errors import MagicErrorML, PhysicsErrorML, RuntimeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime
from magiclang.units import Quantity, KG, M3, DENSITY


def run(source):
    rt=Runtime(project_root=ROOT if "ROOT" in globals() else None)
    if re.search(r"(?<!\.)\bdirection\s*\(", source):
        if not source.lstrip().startswith('load geometry2d'):
            source = 'load geometry2d\n' + source
        source = re.sub(r"(?<!\.)\bdirection(?=\s*\()", "geometry2d.direction", source)
    rt.execute(Parser(Lexer(source).tokenize()).parse())
    return rt


def test_show_and_no_mana_print(capsys):
    run('value = 12\nshow("result:", value)\n')
    assert capsys.readouterr().out.strip() == 'result: 12'
    with pytest.raises(RuntimeErrorML):
        run('print("no")\n')


def test_scale_preserves_mass_and_recalculates_volume_density():
    rt=run('stone = create Earth\nstone.mass = 2 kg\nscale(stone, 0.5)\n')
    stone=rt.global_env.get('stone')
    assert stone.properties['mass'] == Quantity(2, KG)
    assert stone.properties['volume'] == Quantity(0.125, M3)
    assert stone.properties['density'] == Quantity(16, DENSITY)


def test_rotation_explicit_velocity_and_reflection():
    rt=run('''stone = create Earth
velocity(stone, direction(0, 1) * 10 m/s)
reflect(stone, direction(0, 1))
rotate(stone, 1.0)
''')
    stone=rt.global_env.get('stone')
    assert stone.properties['vel'].y == pytest.approx(-10)
    assert stone.properties['rot'] == pytest.approx(1.0)


def test_launch_is_not_an_active_mana_operation():
    with pytest.raises(RuntimeErrorML, match="launch"):
        run("rock = create Earth\nlaunch(rock, 25 m/s)\n")


def test_target_context_velocity_auto_aims_and_post_rolls_back(capsys):
    source = 'npc = tgset:\n    hp = 250\n    max_hp = 250\n    defence = 0\n    distance = 10 m\n\nspldef fireball():\n    fire = create Fire\n    shape(fire, circle)\n    velocity(fire, 100 m/s)\n    incant fire\n\ntgset(npc):\n    post(fireball)\n'
    rt = run(source)
    npc = rt.global_env.get("npc")
    assert npc.properties["hp"] == pytest.approx(250)
    assert rt.active_objects == []
    output = capsys.readouterr().out
    assert "collision: npc" in output
    assert "hit: fire hit npc" in output
    assert "hits: npc" in output


def test_target_context_release_auto_aims_and_commits_hit():
    source = 'npc = tgset:\n    hp = 250\n    max_hp = 250\n    defence = 0\n    distance = 10 m\n\nspldef fireball():\n    fire = create Fire\n    shape(fire, circle)\n    velocity(fire, 100 m/s)\n    incant fire\n\ntgset(npc):\n    release(fireball)\n'
    rt = run(source)
    npc = rt.global_env.get("npc")
    assert npc.properties["hp"] < 250
    fire = next(obj for obj in rt.active_objects if obj.element == "Fire")
    assert fire.properties["vel"].x > 0
    assert fire.properties["vel"].y == pytest.approx(0)
    assert any(item["object_a"] == "npc" or item["object_b"] == "npc" for item in rt.last_collisions)


def test_target_context_aims_at_actual_2d_position_not_positive_x():
    rt = run('npc = tgset:\n    hp = 250\n    max_hp = 250\n    pos = direction(0, 1) * 10 m\n\nspldef arrow():\n    rock = create Earth\n    velocity(rock, 100 m/s)\n    incant rock\n\ntgset(npc):\n    release(arrow)\n')
    rock = next(obj for obj in rt.active_objects if obj.element == "Earth" and obj is not rt.global_env.get("npc"))
    assert rock.properties["vel"].y > 0
    assert abs(rock.properties["vel"].x) < 1e-9


def test_anchor_blocks_motion_until_unanchor():
    with pytest.raises(MagicErrorML, match='anchored'):
        run('''stone = create Earth
anchor(stone)
move(stone, 1 m)
''')
    rt=run('''stone = create Earth
anchor(stone)
unanchor(stone)
move(stone, 1 m)
''')
    assert rt.global_env.get('stone').properties['pos'].x == pytest.approx(1.0)


def test_split_conserves_mass_and_volume():
    rt=run('''stone = create Earth
stone.mass = 6 kg
stone.volume = 3 m3
pieces = split(stone, 3)
''')
    pieces=rt.global_env.get('pieces')
    assert sum(p.properties['mass'].value for p in pieces) == pytest.approx(6)
    assert sum(p.properties['volume'].value for p in pieces) == pytest.approx(3)
    assert rt.global_env.get('stone').properties['active'] is False


def test_push_is_force_based_and_unit_checked():
    rt=run('''stone = create Earth
push(stone, 10 N, direction(0, 1, 0))
''')
    assert rt.global_env.get('stone').properties['acc'].y == pytest.approx(10)
    with pytest.raises(Exception):
        run('''stone = create Earth
push(stone, 10 K, direction(1, 0, 0))
''')
