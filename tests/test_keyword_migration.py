from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from magiclang.errors import SyntaxErrorML
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime
from magiclang.tokens import KEYWORDS

ROOT = Path(__file__).resolve().parents[1]


def run_source(source: str) -> str:
    output = StringIO()
    program = Parser(Lexer(source, "keyword_migration.mana").tokenize(), "keyword_migration.mana").parse()
    with redirect_stdout(output):
        Runtime(project_root=ROOT).execute(program)
    return output.getvalue()


def test_mana_uses_selected_language_words_not_python_aliases():
    assert {"def", "spldef", "load", "incant", "tgset", "skip"}.issubset(KEYWORDS)
    assert {"if", "elif", "else", "while", "for", "in", "and", "or", "not"}.issubset(KEYWORDS)
    assert not ({"import", "pass", "return", "range", "len"} & set(KEYWORDS))


def test_def_is_an_ordinary_computational_function():
    output = run_source(
        "def square(value):\n"
        "    incant value * value\n"
        "result = square(9)\n"
        "show result\n"
    )
    assert output.strip() == "81"


def test_spldef_remains_the_spell_definition_category():
    output = run_source(
        "spldef warm_stone():\n"
        "    stone = create Earth\n"
        "    heat(stone, 100 K)\n"
        "    incant stone\n"
        "post(warm_stone)\n"
    )
    assert "Trace" in output or "warm_stone" in output or output.strip() == ""


def test_load_skip_span_and_length_execute_together():
    output = run_source(
        "load geometry2d\n"
        "total = 0\n"
        "for i in span(1, 4):\n"
        "    total = total + i\n"
        "show total\n"
        "show length(\"mana\")\n"
        "def placeholder():\n"
        "    skip\n"
        "    incant geometry2d.direction(1, 0)\n"
        "show placeholder()\n"
    )
    assert "6" in output.splitlines()
    assert "4" in output.splitlines()
    assert "Vector3(1, 0, 0)" in output


def test_old_import_statement_and_return_statement_are_not_supported():
    with pytest.raises(SyntaxErrorML):
        Parser(Lexer("import geometry2d\n").tokenize()).parse()
    with pytest.raises(SyntaxErrorML):
        Parser(Lexer("def calculate():\n    return 3\n").tokenize()).parse()


def test_old_pass_statement_is_not_a_noop_but_skip_is():
    output = run_source("def empty():\n    skip\n    incant 7\nshow empty()\n")
    assert output.strip() == "7"
    # 'pass' is not interpreted as a no-op statement: it is an ordinary unresolved name.
    with pytest.raises(Exception, match="pass"):
        run_source("pass\n")


def test_old_range_and_len_are_not_registered_builtins():
    runtime = Runtime(project_root=ROOT)
    assert runtime.global_env.get("span") is not None
    assert runtime.global_env.get("length") is not None
    assert "range" not in runtime.global_env.values
    assert "len" not in runtime.global_env.values
    with pytest.raises(Exception, match="range"):
        runtime.execute(Parser(Lexer("show range(3)\n").tokenize()).parse())
    with pytest.raises(Exception, match="len"):
        runtime.execute(Parser(Lexer("show len([1])\n").tokenize()).parse())
