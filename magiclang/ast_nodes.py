from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Program:
    statements: list[Any]
    filename: str = "<input>"
    locations: dict[int, tuple[str, int, int]] = field(default_factory=dict)


@dataclass(slots=True)
class Block:
    statements: list[Any]


@dataclass(slots=True)
class LoadLibrary:
    """Load an approved built-in or user-packaged MANA library."""
    name: str


@dataclass(slots=True)
class Literal:
    value: Any


@dataclass(slots=True)
class Name:
    name: str


@dataclass(slots=True)
class ListLiteral:
    items: list[Any]


@dataclass(slots=True)
class Attribute:
    obj: Any
    name: str


@dataclass(slots=True)
class Subscript:
    obj: Any
    index: Any


@dataclass(slots=True)
class Unary:
    op: str
    operand: Any


@dataclass(slots=True)
class Binary:
    left: Any
    op: str
    right: Any


@dataclass(slots=True)
class Call:
    callee: Any
    args: list[Any]
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WeatherStatement:
    """Native climate statement, e.g. weather rain, radius=80 m."""
    kind: str
    fields: list[tuple[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class Create:
    type_name: str


@dataclass(slots=True)
class Assignment:
    target: Any
    value: Any


@dataclass(slots=True)
class ExpressionStatement:
    expression: Any


@dataclass(slots=True)
class FunctionDef:
    name: str
    params: list[str]
    body: Block
    defaults: dict[str, Any] = field(default_factory=dict)
    library_function: bool = False
    is_spell: bool = False


@dataclass(slots=True)
class Incant:
    """Yield a value from the current function or spell definition."""
    value: Any | None


@dataclass(slots=True)
class TargetSet:
    """Create a configurable target/profile using `name = tgset:`."""
    name: str
    fields: list[tuple[str, Any]]


@dataclass(slots=True)
class WeaveMana:
    """Shape ambient mana into a named construct using an optional field block."""
    name: str
    fields: list[tuple[str, Any]]




@dataclass(slots=True)
class TargetContext:
    """Temporarily select a target while executing statements such as release(spell)."""
    target: Any
    body: Block


@dataclass(slots=True)
class If:
    branches: list[tuple[Any, Block]]
    else_block: Block | None


@dataclass(slots=True)
class While:
    condition: Any
    body: Block


@dataclass(slots=True)
class For:
    name: str
    iterable: Any
    body: Block


@dataclass(slots=True)
class Simul:
    body: Block


@dataclass(slots=True)
class Wait:
    duration: Any


@dataclass(slots=True)
class After:
    duration: Any
    body: Block


@dataclass(slots=True)
class Event:
    event_name: str
    args: list[Any]
    body: Block


@dataclass(slots=True)
class Every:
    interval: Any
    body: Block


@dataclass(slots=True)
class SpellModeStatement:
    """Standalone post/release command; deliberately not an expression.

    ``post`` may request a text report (the default) or a visual-only preview.
    ``release`` always performs a normal committed execution.
    """
    mode: str
    spell: Any
    presentation: str = "text"


@dataclass(slots=True)
class TuneAssignment:
    """Update an existing operation for a named object inside a spell instance."""
    spell: Any
    operation: str
    target_name: str
    value: Any


@dataclass(slots=True)
class SkipStatement:
    """A MANA ``skip`` statement that intentionally does nothing."""
    pass
