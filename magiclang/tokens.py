from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENT = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    POWER = auto()

    EQ = auto()
    EQEQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    KW_DEF = auto()
    KW_SPLDEF = auto()
    KW_LOAD = auto()
    KW_INCANT = auto()
    KW_TGSET = auto()
    KW_IF = auto()
    KW_ELIF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_IN = auto()
    KW_AND = auto()
    KW_OR = auto()
    KW_NOT = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_CREATE = auto()
    KW_WEAVE = auto()
    KW_SIMUL = auto()
    KW_WAIT = auto()
    KW_AFTER = auto()
    KW_EVERY = auto()
    KW_WHEN = auto()
    KW_SKIP = auto()


KEYWORDS = {
    "def": TokenType.KW_DEF,
    "spldef": TokenType.KW_SPLDEF,
    "load": TokenType.KW_LOAD,
    "incant": TokenType.KW_INCANT,
    "tgset": TokenType.KW_TGSET,
    "if": TokenType.KW_IF,
    "elif": TokenType.KW_ELIF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE,
    "for": TokenType.KW_FOR,
    "in": TokenType.KW_IN,
    "and": TokenType.KW_AND,
    "or": TokenType.KW_OR,
    "not": TokenType.KW_NOT,
    "true": TokenType.KW_TRUE,
    "false": TokenType.KW_FALSE,
    "create": TokenType.KW_CREATE,
    "weave": TokenType.KW_WEAVE,
    "simul": TokenType.KW_SIMUL,
    "wait": TokenType.KW_WAIT,
    "after": TokenType.KW_AFTER,
    "every": TokenType.KW_EVERY,
    "when": TokenType.KW_WHEN,
    "skip": TokenType.KW_SKIP,
}


@dataclass(slots=True)
class Token:
    type: TokenType
    value: object
    line: int
    column: int
