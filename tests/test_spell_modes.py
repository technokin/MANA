import pytest

from magiclang.errors import MagicErrorML, SyntaxErrorML, TypeErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime, SpellInstance, SpellResult


def make_runtime(source):
    runtime = Runtime()
    runtime.execute(Parser(Lexer(source).tokenize()).parse())
    return runtime


def run_last_statement(source):
    runtime = Runtime()
    result = runtime.execute(Parser(Lexer(source).tokenize()).parse())
    return runtime, result


BASE = '\nspldef warm_stone():\n    stone = create Earth\n    heat(stone, 1200 K)\n    incant stone\n\n'

TEMPLATE = '\nspldef e_ball(element):\n    ball = create element\n    shape(ball, circle)\n    heat(ball, 500 K)\n    velocity(ball, 300 m/s)\n    incant ball\n\nfire_ball = e_ball(Fire)\nearth_ball = e_ball(Earth)\n'


def test_show_prints_a_spell_reference_without_running_it(capsys):
    rt = make_runtime(BASE + 'show(warm_stone)\n')
    assert 'spell:warm_stone' in capsys.readouterr().out
    assert rt.active_objects == []


def test_post_is_a_standalone_trial_and_returns_record_to_host(capsys):
    rt, result = run_last_statement(BASE + 'post(warm_stone)\n')
    output = capsys.readouterr().out
    assert isinstance(result, SpellResult)  # Host API only; MANA source cannot assign it.
    assert result.ok and not result.committed
    assert '[POST warm_stone]' in output
    assert 'stone.temp: 293.15 K -> 1493.15 K' in output
    assert result.changes
    assert result.incant_value.properties['temp'].value == pytest.approx(1493.15)
    assert rt.active_objects == []


def test_release_is_a_standalone_command_and_commits_state():
    rt, result = run_last_statement(BASE + 'release(warm_stone)\n')
    assert isinstance(result, SpellResult)
    assert result.ok and result.committed
    assert len(rt.active_objects) == 1
    assert rt.active_objects[0].properties['temp'].value == pytest.approx(1493.15)


def test_release_and_post_cannot_be_assigned_or_nested():
    with pytest.raises(SyntaxErrorML, match='cannot be assigned'):
        make_runtime(BASE + 'report = release(warm_stone)\n')
    with pytest.raises(SyntaxErrorML, match='cannot be assigned'):
        make_runtime(BASE + 'trial = post(warm_stone)\n')
    with pytest.raises(SyntaxErrorML, match='nested'):
        make_runtime('show(post(warm_stone))\n')


def test_show_cannot_be_assigned_to_a_variable():
    with pytest.raises(SyntaxErrorML, match='cannot be assigned'):
        make_runtime('value = show(4)\n')


def test_post_accepts_optional_presentation_and_release_does_not():
    _, default_result = run_last_statement(BASE + 'post(warm_stone)\n')
    assert default_result.presentation == 'text'
    _, text_result = run_last_statement(BASE + 'post(warm_stone, text)\n')
    assert text_result.presentation == 'text'
    _, visual_result = run_last_statement(BASE + 'post(warm_stone, visual)\n')
    assert visual_result.presentation == 'visual'
    assert visual_result.ok and not visual_result.committed

    with pytest.raises(SyntaxErrorML, match='text.*visual'):
        make_runtime(BASE + 'post(warm_stone, 900 K)\n')
    with pytest.raises(SyntaxErrorML, match='release accepts only the spell name'):
        make_runtime(BASE + 'release(warm_stone, visual)\n')
    with pytest.raises(SyntaxErrorML, match='expects a named spell'):
        make_runtime(BASE + 'post("warm_stone")\n')


def test_parameterized_def_call_creates_an_instance_without_running_spell(capsys):
    rt = make_runtime(TEMPLATE)
    fire_ball = rt.global_env.get('fire_ball')
    earth_ball = rt.global_env.get('earth_ball')
    assert isinstance(fire_ball, SpellInstance)
    assert fire_ball.element.name == 'Fire'
    assert earth_ball.element.name == 'Earth'
    assert rt.active_objects == []
    assert capsys.readouterr().out == ''


def test_create_element_uses_template_element_parameter():
    rt, result = run_last_statement(TEMPLATE + 'post(fire_ball)\n')
    assert isinstance(result, SpellResult) and result.ok
    assert result.incant_value.element == 'Fire'
    assert result.incant_value.properties['shape'] == 'circle'
    assert result.incant_value.properties['temp'].value == pytest.approx(1500.0)
    assert result.incant_value.properties['vel'].magnitude() == pytest.approx(300.0)
    assert rt.active_objects == []


def test_tune_updates_existing_operation_only_for_selected_instance(capsys):
    source = TEMPLATE + '''
tune(fire_ball.velocity) = ball, 2300 m/s
tune(fire_ball.heat) = ball, 600 K
post(fire_ball)
post(earth_ball)
'''
    rt, result = run_last_statement(source)
    output = capsys.readouterr().out
    assert isinstance(result, SpellResult) and result.ok
    assert 'ball.vel:' in output and 'Vector3(2300, 0, 0)' in output
    assert 'inputs: element=Earth' in output
    assert '293.15 K -> 793.15 K' in output  # Earth remains at its original 500 K delta.
    assert rt.global_env.get('fire_ball').tuned_operations[('velocity', 'ball')].value == pytest.approx(2300)
    assert rt.global_env.get('earth_ball').tuned_operations == {}


def test_tune_fails_when_operation_or_target_does_not_exist():
    with pytest.raises(TypeErrorML, match='do not exist'):
        make_runtime(TEMPLATE + 'tune(fire_ball.accelerate) = ball, 20 m/s2\n')
    with pytest.raises(TypeErrorML, match='do not exist'):
        make_runtime(TEMPLATE + 'tune(fire_ball.velocity) = flame, 20 m/s\n')


def test_tune_fails_when_multiple_matching_operations_are_ambiguous():
    source = '\nspldef twin_ball(element):\n    ball = create element\n    velocity(ball, 300 m/s)\n    velocity(ball, 400 m/s)\n    incant ball\n\ntwin = twin_ball(Fire)\ntune(twin.velocity) = ball, 500 m/s\n'
    with pytest.raises(TypeErrorML, match='multiple matching operations'):
        make_runtime(source)


def test_tune_requires_configured_instance_and_new_syntax():
    with pytest.raises(TypeErrorML, match='configured spell instance'):
        make_runtime('\nspldef e_ball(element):\n    ball = create element\n    velocity(ball, 300 m/s)\n    incant ball\n\ntune(e_ball.velocity) = ball, 500 m/s\n')
    with pytest.raises(SyntaxErrorML, match=r"old '\.tune' syntax is removed"):
        make_runtime(BASE + 'warm_stone.tune = heat_change: 900 K\n')


def test_element_template_accepts_only_the_four_locked_base_elements():
    with pytest.raises(MagicErrorML, match='four base element types'):
        make_runtime(TEMPLATE.replace('e_ball(Fire)', 'e_ball(Life)'))
    with pytest.raises(SyntaxErrorML, match='spell definitions currently accept no parameters or one element selector'):
        make_runtime('spldef bad_ball(element, speed):\n    skip\n')
    with pytest.raises(SyntaxErrorML, match='spell definitions currently accept no parameters or one element selector'):
        make_runtime('spldef bad_ball(speed):\n    skip\n')


def test_skip_is_no_operation_statement_and_pass_is_an_ordinary_identifier():
    rt, result = run_last_statement('\nspldef unfinished_spell():\n    skip\npost(unfinished_spell)\n')
    assert isinstance(result, SpellResult) and result.ok
    assert rt.active_objects == []
    rt2, _ = run_last_statement('pass = 5\nshow(pass)\n')
    assert rt2.global_env.get('pass') == 5


def test_return_is_not_a_language_keyword_and_can_be_an_identifier():
    rt, _ = run_last_statement('return = 5\nshow(return)\n')
    assert rt.global_env.get('return') == 5


def test_incant_is_not_a_function_call():
    with pytest.raises(SyntaxErrorML, match='function-call syntax is not supported'):
        Parser(Lexer('incant(some_spell, other)\n').tokenize()).parse()


def test_create_must_be_assigned_directly_to_a_name():
    with pytest.raises(SyntaxErrorML, match='assigned directly'):
        make_runtime('create Fire\n')
    with pytest.raises(SyntaxErrorML, match='assigned directly'):
        make_runtime('show(create Fire)\n')
    with pytest.raises(SyntaxErrorML, match='variable name'):
        make_runtime('stone = create Earth\nstone.inner = create Fire\n')


def test_statement_commands_are_rejected_in_conditions_and_defaults():
    with pytest.raises(SyntaxErrorML, match='standalone commands'):
        make_runtime('if show(1):\n    stone = create Earth\n')
    with pytest.raises(SyntaxErrorML, match='standalone commands'):
        make_runtime('def f(value=post(some_spell)):\n    incant value\n')
