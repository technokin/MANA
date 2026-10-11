from __future__ import annotations

import math
import re

from .errors import SyntaxErrorML
from .tokens import KEYWORDS, Token, TokenType


class Lexer:
    _number = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
    _ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    def __init__(self, source: str, filename: str = "<input>"):
        self.original_source = source
        # The existing language defines a tab as four indentation spaces.
        self.source = source.replace("\t", "    ")
        self.filename = filename

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        indent_stack = [0]
        expanded_lines = self.source.splitlines()
        original_lines = self.original_source.splitlines()
        bracket_depth = 0
        indentation_style: str | None = None

        for line_index, raw in enumerate(expanded_lines):
            line_no = line_index + 1
            original = original_lines[line_index] if line_index < len(original_lines) else raw
            continuation_line = bracket_depth > 0
            if not raw.strip():
                # Physical blank lines inside brackets are ignored as part of the
                # same logical line; elsewhere they remain irrelevant whitespace.
                continue

            leading = len(raw) - len(raw.lstrip(" "))
            if not continuation_line and leading:
                original_prefix = original[:len(original) - len(original.lstrip(" \t"))]
                has_tabs = "\t" in original_prefix
                has_spaces = " " in original_prefix
                if has_tabs and has_spaces:
                    raise SyntaxErrorML("mixed tabs and spaces in indentation", self.filename, line_no, 1)
                current_style = "tabs" if has_tabs else "spaces"
                if indentation_style is None:
                    indentation_style = current_style
                elif current_style != indentation_style:
                    raise SyntaxErrorML(
                        "mixed tabs and spaces in indentation; use one style consistently",
                        self.filename, line_no, 1,
                    )

            if not continuation_line:
                if leading > indent_stack[-1]:
                    indent_stack.append(leading)
                    tokens.append(Token(TokenType.INDENT, leading, line_no, 1))
                elif leading < indent_stack[-1]:
                    while leading < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(Token(TokenType.DEDENT, leading, line_no, leading + 1))
                    if leading != indent_stack[-1]:
                        raise SyntaxErrorML("inconsistent indentation", self.filename, line_no, leading + 1)

            i = leading
            col = leading + 1

            while i < len(raw):
                ch = raw[i]

                if ch == "#":
                    break

                if ch in " \r":
                    i += 1
                    col += 1
                    continue

                if ch in "\"'":
                    quote = ch
                    start_col = col
                    i += 1
                    col += 1
                    chars = []
                    escaped = False
                    while i < len(raw):
                        ch = raw[i]
                        if escaped:
                            mapping = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", quote: quote}
                            chars.append(mapping.get(ch, ch))
                            escaped = False
                        elif ch == "\\":
                            escaped = True
                        elif ch == quote:
                            break
                        else:
                            chars.append(ch)
                        i += 1
                        col += 1
                    if i >= len(raw) or raw[i] != quote:
                        raise SyntaxErrorML("unterminated string", self.filename, line_no, start_col)
                    i += 1
                    col += 1
                    tokens.append(Token(TokenType.STRING, "".join(chars), line_no, start_col))
                    continue

                m = self._number.match(raw, i)
                if m:
                    text = m.group(0)
                    try:
                        value = float(text) if any(c in text for c in ".eE") else int(text)
                    except (OverflowError, ValueError) as exc:
                        raise SyntaxErrorML(
                            "numeric literal exceeds the supported input range",
                            self.filename, line_no, col,
                        ) from exc
                    if isinstance(value, float) and not math.isfinite(value):
                        raise SyntaxErrorML(
                            "numeric literal is outside the supported finite range",
                            self.filename, line_no, col,
                        )
                    tokens.append(Token(TokenType.NUMBER, value, line_no, col))
                    i = m.end()
                    col += len(text)
                    continue

                m = self._ident.match(raw, i)
                if m:
                    text = m.group(0)
                    tokens.append(Token(KEYWORDS.get(text, TokenType.IDENT), text, line_no, col))
                    i = m.end()
                    col += len(text)
                    continue

                two = raw[i:i+2]
                if two == "==":
                    tokens.append(Token(TokenType.EQEQ, two, line_no, col))
                    i += 2
                    col += 2
                    continue
                if two == "!=":
                    tokens.append(Token(TokenType.NE, two, line_no, col))
                    i += 2
                    col += 2
                    continue
                if two == "<=":
                    tokens.append(Token(TokenType.LE, two, line_no, col))
                    i += 2
                    col += 2
                    continue
                if two == ">=":
                    tokens.append(Token(TokenType.GE, two, line_no, col))
                    i += 2
                    col += 2
                    continue
                if two == "**":
                    tokens.append(Token(TokenType.POWER, two, line_no, col))
                    i += 2
                    col += 2
                    continue

                single = {
                    "(": TokenType.LPAREN, ")": TokenType.RPAREN,
                    "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
                    ",": TokenType.COMMA, ".": TokenType.DOT, ":": TokenType.COLON,
                    "+": TokenType.PLUS, "-": TokenType.MINUS,
                    "*": TokenType.STAR, "/": TokenType.SLASH,
                    "%": TokenType.PERCENT, "=": TokenType.EQ,
                    "<": TokenType.LT, ">": TokenType.GT,
                }
                token_type = single.get(ch)
                if token_type is None:
                    raise SyntaxErrorML(f"unexpected character {ch!r}", self.filename, line_no, col)
                if token_type in (TokenType.LPAREN, TokenType.LBRACKET):
                    bracket_depth += 1
                elif token_type in (TokenType.RPAREN, TokenType.RBRACKET):
                    bracket_depth = max(0, bracket_depth - 1)
                tokens.append(Token(token_type, ch, line_no, col))
                i += 1
                col += 1

            if bracket_depth == 0:
                tokens.append(Token(TokenType.NEWLINE, "\\n", line_no, len(raw) + 1))

        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, indent_stack[-1], len(expanded_lines) + 1, 1))

        tokens.append(Token(TokenType.EOF, None, len(expanded_lines) + 1, 1))
        return tokens
