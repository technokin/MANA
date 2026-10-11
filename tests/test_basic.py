from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime, SpellInstance


def test_basic_element_template_program():
    source = '\nspldef e_ball(element):\n    fire = create element\n    heat(fire, 1200 K)\n    incant fire\n\nfire_ball = e_ball(Fire)\npost(fire_ball)\n'
    program = Parser(Lexer(source).tokenize()).parse()
    rt = Runtime()
    result = rt.execute(program)
    assert isinstance(rt.global_env.get("fire_ball"), SpellInstance)
    assert result.ok
    assert result.incant_value.element == "Fire"
    assert rt.active_objects == []
