from __future__ import annotations

import math
import sys
from .ast_nodes import (
    After,
    Assignment,
    Attribute,
    Binary,
    Block,
    Call,
    Create,
    Event,
    Every,
    ExpressionStatement,
    For,
    FunctionDef,
    If,
    LoadLibrary,
    Incant,
    ListLiteral,
    Literal,
    Name,
    SkipStatement,
    Program,
    Simul,
    SpellModeStatement,
    Subscript,
    TargetContext,
    TargetSet,
    WeaveMana,
    WeatherStatement,
    TuneAssignment,
    Unary,
    Wait,
    While,
)
from .errors import SyntaxErrorML, UnitErrorML
from .tokens import Token, TokenType
from .units import Quantity, parse_unit_info


class Parser:
    def __init__(self, tokens: list[Token], filename: str = "<input>", *, allow_library_parameters: bool = False):
        self.tokens = tokens
        self.filename = filename
        self.allow_library_parameters = allow_library_parameters
        self.i = 0
        self.locations: dict[int, tuple[str, int, int]] = {}

    @property
    def current(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        token = self.current
        self.i += 1
        return token

    def check(self, *types: TokenType) -> bool:
        return self.current.type in types

    def expect(self, token_type: TokenType, message: str | None = None) -> Token:
        if not self.check(token_type):
            raise SyntaxErrorML(
                message or self._unexpected_token_message(token_type),
                self.filename,
                self.current.line,
                self.current.column,
            )
        return self.advance()

    def _unexpected_token_message(self, expected: TokenType) -> str:
        """Describe syntax failures without leaking internal token enum names."""
        expected_names = {
            TokenType.NEWLINE: "end of line",
            TokenType.INDENT: "an indented block",
            TokenType.DEDENT: "the end of the block",
            TokenType.RPAREN: "')'",
            TokenType.RBRACKET: "']'",
            TokenType.LPAREN: "'('",
            TokenType.LBRACKET: "'['",
            TokenType.COLON: "':'",
            TokenType.COMMA: "','",
            TokenType.IDENT: "a name",
            TokenType.EOF: "the end of the file",
        }
        actual_names = {
            TokenType.INDENT: "an indentation marker",
            TokenType.DEDENT: "the end of an indented block",
            TokenType.KW_FOR: "'for'",
            TokenType.KW_IN: "'in'",
            TokenType.KW_IF: "'if'",
            TokenType.KW_ELSE: "'else'",
            TokenType.KW_ELIF: "'elif'",
        }
        token = self.current
        if token.type == TokenType.IDENT:
            return f"'{token.value}' is not identified"
        if token.type == TokenType.KW_FOR:
            return "'for' is not identified"
        if token.type == TokenType.KW_IN:
            return "'in' is not identified"
        if token.type == TokenType.EOF:
            actual = "the end of the file"
        elif token.type == TokenType.NEWLINE:
            actual = "the end of the line"
        elif token.type == TokenType.IDENT:
            actual = f"name '{token.value}'"
        elif token.type in {TokenType.NUMBER, TokenType.STRING}:
            actual = repr(token.value)
        else:
            actual = actual_names.get(token.type, "a syntax marker")
        return f"expected {expected_names.get(expected, 'a valid value')}, found {actual}"

    def skip_newlines(self) -> None:
        while self.check(TokenType.NEWLINE):
            self.advance()

    def parse(self) -> Program:
        try:
            return self._parse_program()
        except RecursionError as exc:
            token = self.current
            raise SyntaxErrorML(
                "expression or block nesting exceeds MANA's parser safety limit",
                self.filename, token.line, token.column,
            ) from exc

    def _parse_program(self) -> Program:
        statements = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            statements.append(self.parse_statement())
            self.skip_newlines()
        return Program(statements, self.filename, dict(self.locations))

    def parse_statement(self):
        start = self.current
        statement = self._parse_statement()
        self.locations[id(statement)] = (self.filename, start.line, start.column)
        return statement

    def _parse_statement(self):
        start = self.current
        t = self.current.type
        if (t == TokenType.IDENT and self.current.value in {"show", "post", "release"}
                and self.i + 1 < len(self.tokens) and self.tokens[self.i + 1].type == TokenType.EQ):
            raise SyntaxErrorML(
                f"'{self.current.value}' is reserved and cannot be used as an identifier",
                self.filename, self.current.line, self.current.column,
            )
        if t == TokenType.KW_DEF:
            return self.parse_def(is_spell=False)
        if t == TokenType.KW_SPLDEF:
            return self.parse_def(is_spell=True)
        if (t == TokenType.IDENT and self.current.value == "spell"
                and self.i + 2 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.IDENT
                and self.tokens[self.i + 2].type == TokenType.LPAREN):
            # Contextual declaration keyword: ``spell name():``. Keeping it
            # contextual preserves existing programs that use ``spell`` as a
            # perfectly ordinary variable or spell name.
            return self.parse_def(is_spell=True)
        # `spell name():` is the readable primary spelling; `spldef` remains
        # accepted for compatibility with existing MANA projects. Both use the
        # language's indentation-based blocks, never curly braces.
        if (t == TokenType.IDENT and self.current.value == "weather"
                and self.i + 1 < len(self.tokens)
                and self.tokens[self.i + 1].type in {TokenType.IDENT, TokenType.STRING}):
            return self.parse_weather_statement()
        # Native spell-language verbs keep common magical operations readable
        # without forcing every source line to look like a library invocation.
        # Parenthesised destinations allow dynamic expressions when needed.
        if (t == TokenType.IDENT and self.current.value in {"shape", "transmute", "transfigure", "transform"}
                and self.i + 2 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.IDENT
                and self.tokens[self.i + 2].type == TokenType.IDENT
                and str(self.tokens[self.i + 2].value).casefold() == "into"):
            return self.parse_native_transformation()
        # Primary spell execution verbs. post()/release() stay available for
        # existing code; appraise/cast express the same actions in domain terms.
        if (t == TokenType.IDENT and self.current.value in {"appraise", "cast"}
                and self.i + 1 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.IDENT
                and self.i + 2 < len(self.tokens)
                and self.tokens[self.i + 2].type in {TokenType.NEWLINE, TokenType.EOF}):
            mode = self.advance().value
            spell_name = self.advance().value
            self.expect(TokenType.NEWLINE)
            return SpellModeStatement(mode, Name(str(spell_name)))
        if t == TokenType.KW_LOAD:
            return self.parse_load()
        if t == TokenType.KW_SKIP:
            self.advance()
            self.expect(TokenType.NEWLINE)
            return SkipStatement()
        # Firing modes are statements, not value-producing function calls.
        if (t == TokenType.IDENT and self.current.value in {"post", "release"}
                and self.i + 1 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.LPAREN):
            return self.parse_spell_mode_statement()
        if t == TokenType.KW_INCANT:
            return self.parse_incant()
        if t == TokenType.KW_TGSET and self.i + 1 < len(self.tokens) and self.tokens[self.i + 1].type == TokenType.LPAREN:
            return self.parse_target_context()
        if (t == TokenType.IDENT and self.i + 2 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.EQ
                and self.tokens[self.i + 2].type == TokenType.KW_TGSET):
            return self.parse_tgset()
        if (t == TokenType.IDENT and self.i + 2 < len(self.tokens)
                and self.tokens[self.i + 1].type == TokenType.EQ
                and self.tokens[self.i + 2].type == TokenType.KW_WEAVE):
            return self.parse_weave_mana()
        if t == TokenType.KW_IF:
            return self.parse_if()
        if t == TokenType.KW_WHILE:
            return self.parse_while()
        if t == TokenType.KW_FOR:
            return self.parse_for()
        if t == TokenType.KW_SIMUL:
            return self.parse_simul()
        if t == TokenType.KW_WAIT:
            return self.parse_wait()
        if t == TokenType.KW_AFTER:
            return self.parse_after()
        if t == TokenType.KW_EVERY:
            return self.parse_every()
        if t == TokenType.KW_WHEN:
            return self.parse_event()
        # Print-style syntax: `show value`. Parenthesized `show(value)` remains valid.
        if (t == TokenType.IDENT and self.current.value == "show"
                and self.i + 1 < len(self.tokens)
                and self.tokens[self.i + 1].type != TokenType.LPAREN):
            self.advance()
            if self.check(TokenType.NEWLINE):
                raise SyntaxErrorML("show needs a value, for example 'show stone.temp'", self.filename, self.current.line)
            values = [self.parse_expression()]
            while self.check(TokenType.COMMA):
                self.advance()
                values.append(self.parse_expression())
            if any(self.contains_statement_call(value) for value in values):
                raise SyntaxErrorML("show/post/release/tune cannot be nested inside another expression", self.filename, self.current.line)
            if any(self.contains_create(value) for value in values):
                raise SyntaxErrorML("create must be assigned to a name first, for example 'fire = create Fire'", self.filename, self.current.line)
            self.expect(TokenType.NEWLINE)
            return ExpressionStatement(Call(Name("show"), values))

        expr = self.parse_expression()
        if isinstance(expr, Name) and self.current.type not in {TokenType.EQ, TokenType.NEWLINE, TokenType.EOF}:
            raise SyntaxErrorML(
                f"'{expr.name}' is not identified",
                self.filename, start.line, start.column,
            )
        if self.check(TokenType.EQ):
            self.advance()
            # tune(spell.operation) = target_name, replacement_value
            if (isinstance(expr, Call) and isinstance(expr.callee, Name)
                    and expr.callee.name == "tune"):
                if expr.kwargs or len(expr.args) != 1 or not isinstance(expr.args[0], Attribute):
                    raise SyntaxErrorML(
                        "write tuning as 'tune(spell.operation) = target, value'",
                        self.filename, self.current.line,
                    )
                target_attr = expr.args[0]
                if not isinstance(target_attr.obj, Name):
                    raise SyntaxErrorML("tune must identify a named spell instance", self.filename, self.current.line)
                target_name = self.expect(
                    TokenType.IDENT,
                    "tune expects the target variable name after '='",
                ).value
                self.expect(TokenType.COMMA, "tune syntax is 'tune(spell.operation) = target, value'")
                value = self.parse_expression()
                self.validate_value_expression(value, "tune value")
                self.expect(TokenType.NEWLINE)
                return TuneAssignment(target_attr.obj, target_attr.name, target_name, value)
            if isinstance(expr, Attribute) and expr.name == "tune":
                raise SyntaxErrorML(
                    "the old '.tune' syntax is removed; use 'tune(spell.operation) = target, value'",
                    self.filename, self.current.line,
                )
            if (isinstance(expr, Name) and self.check(TokenType.IDENT)
                    and self.current.value == "conjure"
                    and self.i + 1 < len(self.tokens)
                    and self.tokens[self.i + 1].type != TokenType.LPAREN):
                value = self.parse_conjure_expression()
            elif (isinstance(expr, Name) and self.check(TokenType.IDENT)
                    and self.current.value == "summon"
                    and self._looks_like_native_summon()):
                value = self.parse_summon_expression()
            else:
                value = self.parse_expression()
            if self.contains_statement_call(expr) or self.contains_statement_call(value):
                raise SyntaxErrorML(
                    "show/post/release cannot be assigned to variables; tune is only valid as a special assignment form",
                    self.filename, self.current.line,
                )
            if isinstance(value, Create) and not isinstance(expr, Name):
                raise SyntaxErrorML("create results must be assigned directly to a variable name, for example 'fire = create Fire'", self.filename, self.current.line)
            if self.contains_create(value) and not isinstance(value, Create):
                raise SyntaxErrorML("create results must be assigned directly, for example 'fire = create Fire'", self.filename, self.current.line)
            self.expect(TokenType.NEWLINE)
            return Assignment(expr, value)

        self.expect(TokenType.NEWLINE)
        if self.contains_create(expr):
            raise SyntaxErrorML("create results must be assigned directly, for example 'fire = create Fire'", self.filename, self.current.line)
        if self.contains_statement_call(expr):
            if not (isinstance(expr, Call) and isinstance(expr.callee, Name) and expr.callee.name == "show"):
                raise SyntaxErrorML("show/post/release must be standalone commands; tune must be used as an assignment", self.filename, self.current.line)
            if any(self.contains_statement_call(arg) for arg in expr.args) or any(self.contains_statement_call(arg) for arg in expr.kwargs.values()):
                raise SyntaxErrorML("show/post/release/tune cannot be nested inside another command", self.filename, self.current.line)
        return ExpressionStatement(expr)

    def parse_spell_mode_statement(self):
        mode = self.advance().value
        self.expect(TokenType.LPAREN)
        spell = self.parse_expression()
        if not isinstance(spell, Name):
            raise SyntaxErrorML(f"{mode} expects a named spell, for example '{mode}(fireball)'", self.filename, self.current.line)

        presentation = "text"
        if self.check(TokenType.COMMA):
            comma = self.advance()
            if mode != "post":
                raise SyntaxErrorML("release accepts only the spell name; visual presentation is available with post(spell, visual)", self.filename, comma.line, comma.column)
            option = self.expect(TokenType.IDENT, "post's second argument must be 'text' or 'visual'")
            if option.value not in {"text", "visual"}:
                raise SyntaxErrorML("post's second argument must be 'text' or 'visual'", self.filename, option.line, option.column)
            presentation = option.value
            if self.check(TokenType.COMMA):
                extra = self.current
                raise SyntaxErrorML("post accepts at most two arguments: the spell name and optional 'text' or 'visual'", self.filename, extra.line, extra.column)

        self.expect(TokenType.RPAREN, f"{mode} expects a named spell and an optional post presentation")
        self.expect(TokenType.NEWLINE)
        return SpellModeStatement(mode, spell, presentation)

    def validate_value_expression(self, expr, context: str) -> None:
        if self.contains_statement_call(expr):
            raise SyntaxErrorML(
                f"{context} cannot contain show/post/release; these are standalone commands",
                self.filename, self.current.line
            )
        if self.contains_create(expr):
            raise SyntaxErrorML(
                f"{context} cannot contain an unassigned create; use 'name = create Element'",
                self.filename, self.current.line
            )

    @staticmethod
    def contains_statement_call(expr):
        """Whether an expression contains a command that cannot be used as a value."""
        if isinstance(expr, Call):
            if isinstance(expr.callee, Name) and expr.callee.name in {"show", "post", "release", "tune"}:
                return True
            return (Parser.contains_statement_call(expr.callee)
                    or any(Parser.contains_statement_call(arg) for arg in expr.args)
                    or any(Parser.contains_statement_call(arg) for arg in expr.kwargs.values()))
        if isinstance(expr, Attribute):
            return Parser.contains_statement_call(expr.obj)
        if isinstance(expr, Subscript):
            return Parser.contains_statement_call(expr.obj) or Parser.contains_statement_call(expr.index)
        if isinstance(expr, Unary):
            return Parser.contains_statement_call(expr.operand)
        if isinstance(expr, Binary):
            return Parser.contains_statement_call(expr.left) or Parser.contains_statement_call(expr.right)
        if isinstance(expr, ListLiteral):
            return any(Parser.contains_statement_call(item) for item in expr.items)
        return False

    @staticmethod
    def contains_create(expr):
        """Whether an expression tries to create an object outside direct assignment."""
        if isinstance(expr, Create):
            return True
        if isinstance(expr, Call):
            return (Parser.contains_create(expr.callee)
                    or any(Parser.contains_create(arg) for arg in expr.args)
                    or any(Parser.contains_create(arg) for arg in expr.kwargs.values()))
        if isinstance(expr, Attribute):
            return Parser.contains_create(expr.obj)
        if isinstance(expr, Subscript):
            return Parser.contains_create(expr.obj) or Parser.contains_create(expr.index)
        if isinstance(expr, Unary):
            return Parser.contains_create(expr.operand)
        if isinstance(expr, Binary):
            return Parser.contains_create(expr.left) or Parser.contains_create(expr.right)
        if isinstance(expr, ListLiteral):
            return any(Parser.contains_create(item) for item in expr.items)
        return False

    def parse_native_transformation(self):
        """Parse ``transmute iron into silver`` and sibling native verb forms.

        A bare destination is a domain name (material, geometry, phase, or form).
        Parenthesise an expression to use a computed destination, e.g.
        ``transmute ingot into (desired_material)``. The long-form API calls
        remain available for advanced options such as preserve_mass=False.
        """
        operation = str(self.advance().value)
        target_token = self.expect(TokenType.IDENT, f"{operation} expects an object name before 'into'")
        into = self.expect(TokenType.IDENT, f"write '{operation} {target_token.value} into ...'")
        if str(into.value).casefold() != "into":
            raise SyntaxErrorML(f"expected 'into' in {operation} statement", self.filename, into.line, into.column)
        if self.check(TokenType.STRING):
            destination = Literal(self.advance().value)
        elif self.check(TokenType.IDENT):
            destination = Literal(str(self.advance().value))
        elif self.check(TokenType.LPAREN):
            self.advance()
            destination = self.parse_expression()
            self.expect(TokenType.RPAREN, "close the parenthesised transformation destination")
            self.validate_value_expression(destination, f"{operation} destination")
        else:
            token = self.current
            raise SyntaxErrorML(
                f"{operation} needs a destination after 'into'; use a name or a parenthesised expression",
                self.filename, token.line, token.column,
            )
        self.expect(TokenType.NEWLINE, f"{operation} must be a standalone statement")
        call = Call(Name(operation), [Name(str(target_token.value)), destination])
        return ExpressionStatement(call)

    def _looks_like_native_summon(self) -> bool:
        """Distinguish ``summon (dynamic_name) from plane`` from ``summon(...)``.

        Parenthesised values are native summon syntax only when followed by
        the explicit source-plane marker. This preserves normal function calls.
        """
        if self.i + 1 >= len(self.tokens):
            return False
        if self.tokens[self.i + 1].type != TokenType.LPAREN:
            return True
        depth = 0
        for j in range(self.i + 1, len(self.tokens)):
            token_type = self.tokens[j].type
            if token_type == TokenType.LPAREN:
                depth += 1
            elif token_type == TokenType.RPAREN:
                depth -= 1
                if depth == 0:
                    return (j + 1 < len(self.tokens)
                            and self.tokens[j + 1].type == TokenType.IDENT
                            and str(self.tokens[j + 1].value).casefold() == "from")
            elif token_type in {TokenType.NEWLINE, TokenType.EOF}:
                return False
        return False

    def parse_summon_expression(self):
        """Parse ``guardian = summon Griffin from Wild Realm, position=...``.

        A single bare name or quoted label is a being name; a parenthesised
        expression can supply a dynamic name/record. Source plane is optional
        for indexed beings and may also be parenthesised when computed.
        """
        token = self.advance()  # summon
        being = self._parse_summon_value("being name")
        args = [being]
        if self.check(TokenType.IDENT) and str(self.current.value).casefold() == "from":
            self.advance()
            args.append(self._parse_summon_value("source plane"))
        kwargs: dict[str, Any] = {}
        if self.check(TokenType.COMMA):
            self.advance()
        allowed = {"position", "requirements"}
        while not self.check(TokenType.NEWLINE, TokenType.EOF):
            key = self.expect(TokenType.IDENT, "summon options must use position=value or requirements=[...]")
            if key.value in kwargs:
                raise SyntaxErrorML(f"summon option '{key.value}' is specified more than once", self.filename, key.line, key.column)
            self.expect(TokenType.EQ, "summon options must use name=value")
            value = self.parse_expression()
            self.validate_value_expression(value, f"summon option '{key.value}'")
            kwargs[key.value] = value
            if self.check(TokenType.COMMA):
                self.advance()
                if self.check(TokenType.NEWLINE, TokenType.EOF):
                    raise SyntaxErrorML("summon options cannot end with a comma", self.filename, self.current.line, self.current.column)
            elif not self.check(TokenType.NEWLINE, TokenType.EOF):
                raise SyntaxErrorML("separate summon options with commas", self.filename, self.current.line, self.current.column)
        unknown = sorted(set(kwargs) - allowed)
        if unknown:
            raise SyntaxErrorML("unknown summon option(s): " + ", ".join(unknown), self.filename, token.line, token.column)
        # Assignment parsing owns the newline, just as it does for conjure.
        return Call(Name("summon"), args, kwargs)

    def _parse_summon_value(self, label: str):
        if self.check(TokenType.STRING):
            return Literal(self.advance().value)
        if self.check(TokenType.IDENT):
            return Literal(str(self.advance().value))
        if self.check(TokenType.LPAREN):
            self.advance()
            value = self.parse_expression()
            self.expect(TokenType.RPAREN, f"close the parenthesised {label}")
            self.validate_value_expression(value, f"summon {label}")
            return value
        token = self.current
        raise SyntaxErrorML(f"summon needs a {label}; use a name or a parenthesised expression", self.filename, token.line, token.column)

    def parse_weather_statement(self):
        """Parse a native area/global climate declaration in statement position.

        Example: ``weather rain, intensity=0.8, radius=80 m``. Bare enum
        values for precipitation and compass direction are accepted, while all
        other values use ordinary MANA expressions and units.
        """
        start = self.advance()
        kind_token = self.advance()
        if kind_token.type == TokenType.STRING:
            kind = str(kind_token.value)
        else:
            kind = str(kind_token.value)
        if not kind.strip():
            raise SyntaxErrorML("weather needs a named climate preset", self.filename, kind_token.line, kind_token.column)
        fields: list[tuple[str, Any]] = []
        names: set[str] = set()
        if self.check(TokenType.COMMA):
            self.advance()
        while not self.check(TokenType.NEWLINE, TokenType.EOF):
            key = self.expect(TokenType.IDENT, "weather options must use name=value, for example radius=80 m")
            if key.value in names:
                raise SyntaxErrorML(f"weather option '{key.value}' is specified more than once", self.filename, key.line, key.column)
            names.add(key.value)
            self.expect(TokenType.EQ, "weather options must use name=value")
            if (key.value in {"precipitation", "wind_direction"}
                    and self.check(TokenType.IDENT)):
                value = Literal(self.advance().value)
            else:
                value = self.parse_expression()
            self.validate_value_expression(value, f"weather option '{key.value}'")
            fields.append((key.value, value))
            if self.check(TokenType.COMMA):
                self.advance()
                if self.check(TokenType.NEWLINE, TokenType.EOF):
                    raise SyntaxErrorML("weather options cannot end with a comma", self.filename, self.current.line, self.current.column)
            elif not self.check(TokenType.NEWLINE, TokenType.EOF):
                raise SyntaxErrorML("separate weather options with commas", self.filename, self.current.line, self.current.column)
        self.expect(TokenType.NEWLINE, "weather change must be a standalone statement")
        allowed = {"intensity", "precipitation", "wind_speed", "wind_direction", "temperature",
                   "humidity", "clouds", "fog", "heat", "lightning", "duration", "radius", "center"}
        unknown = sorted(names - allowed)
        if unknown:
            raise SyntaxErrorML("unknown weather option(s): " + ", ".join(unknown), self.filename, start.line, start.column)
        return WeatherStatement(kind.strip(), fields)

    def parse_conjure_expression(self):
        """Parse ``conjure steel, mass=5 kg`` as a language-level matter expression."""
        keyword = self.advance()  # conjure
        material_token = self.current
        if material_token.type not in {TokenType.IDENT, TokenType.STRING}:
            raise SyntaxErrorML("conjure needs a material name, e.g. 'iron = conjure steel, mass=5 kg'",
                                self.filename, material_token.line, material_token.column)
        material = str(self.advance().value)
        kwargs: dict[str, Any] = {}
        allowed = {"mass", "position", "shape", "name", "temperature", "density", "state",
                   "velocity", "anchored", "collidable", "restitution", "friction", "drag_coefficient",
                   "material", "item", "length", "width", "thickness", "durability", "payload"}
        if self.check(TokenType.COMMA):
            self.advance()
        while not self.check(TokenType.NEWLINE, TokenType.EOF):
            key = self.expect(TokenType.IDENT, "conjure options must use name=value, e.g. shape=cube")
            if key.value in kwargs:
                raise SyntaxErrorML(f"conjure option '{key.value}' is specified more than once", self.filename, key.line, key.column)
            self.expect(TokenType.EQ, "conjure options must use name=value")
            if key.value in {"shape", "state", "name", "material", "item", "payload"} and self.check(TokenType.IDENT):
                value = Literal(self.advance().value)
            else:
                value = self.parse_expression()
            self.validate_value_expression(value, f"conjure option '{key.value}'")
            kwargs[key.value] = value
            if self.check(TokenType.COMMA):
                self.advance()
                if self.check(TokenType.NEWLINE, TokenType.EOF):
                    raise SyntaxErrorML("conjure options cannot end with a comma", self.filename, self.current.line, self.current.column)
            elif not self.check(TokenType.NEWLINE, TokenType.EOF):
                raise SyntaxErrorML("separate conjure options with commas", self.filename, self.current.line, self.current.column)
        unknown = sorted(set(kwargs) - allowed)
        if unknown:
            raise SyntaxErrorML("unknown conjure option(s): " + ", ".join(unknown), self.filename, keyword.line, keyword.column)
        return Call(Name("conjure"), [Literal(material)], kwargs)

    def parse_load(self):
        self.advance()
        name = self.expect(TokenType.IDENT, "load expects a library name, such as geometry2d or vector3d").value
        self.expect(TokenType.NEWLINE, "load must be a standalone statement")
        return LoadLibrary(name)

    def parse_def(self, *, is_spell: bool):
        self.advance()
        name = self.expect(TokenType.IDENT, "function name must be an identifier").value
        self.expect(TokenType.LPAREN)
        params = []
        defaults = {}
        saw_default = False
        if not self.check(TokenType.RPAREN):
            while True:
                param = self.expect(TokenType.IDENT, "parameter must be an identifier").value
                if param in params:
                    raise SyntaxErrorML(f"parameter '{param}' is defined more than once", self.filename, self.current.line)
                params.append(param)
                if self.check(TokenType.EQ):
                    self.advance()
                    defaults[param] = self.parse_expression()
                    self.validate_value_expression(defaults[param], "parameter default")
                    saw_default = True
                elif saw_default:
                    raise SyntaxErrorML("required parameters must come before parameters with defaults", self.filename, self.current.line)
                if not self.check(TokenType.COMMA):
                    break
                self.advance()
        self.expect(TokenType.RPAREN)
        # `def` is an ordinary computational function. The contextual `spell`
        # declaration is the v2 spelling; `spldef` remains a legacy token alias.
        if is_spell and params and params != ["element"]:
            raise SyntaxErrorML(
                "spell definitions accept no parameters or one element selector: use spell name(element):",
                self.filename, self.current.line,
            )
        if is_spell and params == ["element"] and defaults:
            raise SyntaxErrorML("the spell element selector cannot have a default value", self.filename, self.current.line)
        if self.allow_library_parameters and is_spell:
            raise SyntaxErrorML("library modules may export ordinary def functions, not spell definitions", self.filename, self.current.line)
        library_function = self.allow_library_parameters
        body = self.parse_block()
        if is_spell and self._contains_target_context(body):
            raise SyntaxErrorML(
                "target selection belongs outside a spell; use `tgset(target): release(spell)` around the cast",
                self.filename, self.locations.get(id(body), (self.filename, self.current.line, 1))[1],
            )
        return FunctionDef(name, params, body, defaults, library_function, is_spell)

    @staticmethod
    def _contains_target_context(value):
        """Find target-selection statements nested anywhere in a parsed spell body."""
        from dataclasses import fields, is_dataclass
        if isinstance(value, TargetContext):
            return True
        if isinstance(value, (str, int, float, bool)) or value is None:
            return False
        if isinstance(value, list):
            return any(Parser._contains_target_context(item) for item in value)
        if isinstance(value, tuple):
            return any(Parser._contains_target_context(item) for item in value)
        if is_dataclass(value):
            return any(Parser._contains_target_context(getattr(value, item.name)) for item in fields(value))
        return False

    def parse_incant(self):
        self.advance()
        if self.check(TokenType.LPAREN):
            depth = 0
            for token in self.tokens[self.i:]:
                if token.type == TokenType.LPAREN:
                    depth += 1
                elif token.type == TokenType.RPAREN:
                    depth -= 1
                    if depth == 0:
                        break
                elif token.type == TokenType.COMMA and depth == 1:
                    raise SyntaxErrorML(
                        "incant accepts one value expression; function-call syntax is not supported",
                        self.filename, token.line, token.column,
                    )
                elif token.type in {TokenType.NEWLINE, TokenType.EOF} and depth > 0:
                    break
        if self.check(TokenType.NEWLINE):
            self.advance()
            return Incant(None)
        value = self.parse_expression()
        if self.check(TokenType.COMMA):
            raise SyntaxErrorML(
                "incant accepts one value expression; function-call syntax is not supported",
                self.filename, self.current.line, self.current.column,
            )
        if self.contains_create(value):
            raise SyntaxErrorML("create results must be assigned directly before use with incant", self.filename, self.current.line)
        if self.contains_statement_call(value):
            raise SyntaxErrorML("show/post/release are commands and tune is not an incant value", self.filename, self.current.line)
        self.expect(TokenType.NEWLINE)
        return Incant(value)

    def parse_target_context(self):
        """Temporarily select a target for a casting block: tgset(npc): release(spell)."""
        self.expect(TokenType.KW_TGSET)
        self.expect(TokenType.LPAREN)
        target = self.parse_expression()
        self.validate_value_expression(target, "target selection")
        self.expect(TokenType.RPAREN, "expected ')' after target name in tgset(target)")
        body = self.parse_block()
        return TargetContext(target, body)

    def parse_tgset(self):
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.EQ)
        self.expect(TokenType.KW_TGSET)
        if self.check(TokenType.COLON):
            self.advance()
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT, "expected an indented target definition after tgset")
        fields: list[tuple[str, object]] = []
        seen: set[str] = set()
        self.skip_newlines()
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            field_name = self.expect(TokenType.IDENT, "target fields must use names such as hp, defence, resist_fire, or distance").value
            if field_name in seen:
                raise SyntaxErrorML(f"target field '{field_name}' is defined more than once", self.filename, self.current.line)
            seen.add(field_name)
            self.expect(TokenType.EQ, "target field must use '='")
            value = self.parse_expression()
            self.validate_value_expression(value, "target field")
            self.expect(TokenType.NEWLINE)
            fields.append((field_name, value))
            self.skip_newlines()
        self.expect(TokenType.DEDENT)
        return TargetSet(name, fields)

    def parse_weave_mana(self):
        """Parse `orb = weave mana` and its optional indented options block."""
        name = self.expect(TokenType.IDENT, "woven construct needs a variable name").value
        self.expect(TokenType.EQ)
        self.expect(TokenType.KW_WEAVE)
        selector = self.expect(TokenType.IDENT, "write `weave mana`, followed by optional construct settings")
        if selector.value != "mana":
            raise SyntaxErrorML("weave currently accepts only `mana`", self.filename, selector.line, selector.column)

        fields: list[tuple[str, object]] = []
        seen: set[str] = set()
        has_block = self.check(TokenType.COLON)
        if has_block:
            self.advance()
        self.expect(TokenType.NEWLINE)
        if has_block:
            self.expect(TokenType.INDENT, "expected indented settings after `weave mana:`")
            self.skip_newlines()
            while not self.check(TokenType.DEDENT, TokenType.EOF):
                field_token = self.expect(TokenType.IDENT, "construct settings must use names such as shape, radius, energy, position, collidable, or anchored")
                field_name = field_token.value
                if field_name in seen:
                    raise SyntaxErrorML(f"construct setting '{field_name}' is defined more than once", self.filename, field_token.line, field_token.column)
                seen.add(field_name)
                self.expect(TokenType.EQ, "construct settings must use '='")
                value = self.parse_expression()
                self.validate_value_expression(value, "construct setting")
                self.expect(TokenType.NEWLINE)
                fields.append((field_name, value))
                self.skip_newlines()
            self.expect(TokenType.DEDENT)
        return WeaveMana(name, fields)

    def parse_if(self):
        branches = []
        self.advance()
        condition = self.parse_expression()
        self.validate_value_expression(condition, "if condition")
        body = self.parse_block()
        branches.append((condition, body))

        while self.check(TokenType.KW_ELIF):
            self.advance()
            condition = self.parse_expression()
            self.validate_value_expression(condition, "elif condition")
            body = self.parse_block()
            branches.append((condition, body))

        else_block = None
        if self.check(TokenType.KW_ELSE):
            self.advance()
            else_block = self.parse_block()

        return If(branches, else_block)

    def parse_while(self):
        self.advance()
        condition = self.parse_expression()
        self.validate_value_expression(condition, "while condition")
        body = self.parse_block()
        return While(condition, body)

    def parse_for(self):
        self.advance()
        name = self.expect(TokenType.IDENT, "for-loop variable must be an identifier").value
        self.expect(TokenType.KW_IN)
        iterable = self.parse_expression()
        self.validate_value_expression(iterable, "for iterable")
        body = self.parse_block()
        return For(name, iterable, body)

    def parse_simul(self):
        self.advance()
        body = self.parse_block()
        return Simul(body)

    def parse_wait(self):
        self.advance()
        duration = self.parse_expression()
        self.validate_value_expression(duration, "wait duration")
        self.expect(TokenType.NEWLINE)
        return Wait(duration)

    def parse_after(self):
        self.advance()
        duration = self.parse_expression()
        self.validate_value_expression(duration, "after duration")
        body = self.parse_block()
        return After(duration, body)

    def parse_every(self):
        self.advance()
        interval = self.parse_expression()
        self.validate_value_expression(interval, "every interval")
        body = self.parse_block()
        return Every(interval, body)

    def parse_event(self):
        self.advance()
        name = self.expect(TokenType.IDENT, "event name must be an identifier").value
        args = []
        if self.check(TokenType.LPAREN):
            self.advance()
            if not self.check(TokenType.RPAREN):
                while True:
                    argument = self.parse_expression()
                    self.validate_value_expression(argument, "event argument")
                    args.append(argument)
                    if not self.check(TokenType.COMMA):
                        break
                    self.advance()
            self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return Event(name, args, body)

    def parse_block(self) -> Block:
        if self.check(TokenType.COLON):
            self.advance()
        self.expect(TokenType.NEWLINE)
        self.expect(TokenType.INDENT, "expected an indented block")

        statements = []
        self.skip_newlines()
        while not self.check(TokenType.DEDENT, TokenType.EOF):
            statements.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)
        for index, statement in enumerate(statements[:-1]):
            if isinstance(statement, Incant):
                line = self.locations.get(id(statement), (self.filename, None, None))[1]
                column = self.locations.get(id(statement), (self.filename, line, 1))[2]
                print(
                    f"Warning: {self.filename}:{line}:{column}: statement after incant is unreachable in this block",
                    file=sys.stderr,
                )
                break
        return Block(statements)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expr = self.parse_and()
        while self.check(TokenType.KW_OR):
            self.advance()
            expr = Binary(expr, "or", self.parse_and())
        return expr

    def parse_and(self):
        expr = self.parse_not()
        while self.check(TokenType.KW_AND):
            self.advance()
            expr = Binary(expr, "and", self.parse_not())
        return expr

    def parse_not(self):
        if self.check(TokenType.KW_NOT):
            self.advance()
            return Unary("not", self.parse_not())
        return self.parse_compare()

    def parse_compare(self):
        expr = self.parse_term()
        while self.check(TokenType.EQEQ, TokenType.NE, TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.advance().value
            expr = Binary(expr, op, self.parse_term())
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            expr = Binary(expr, op, self.parse_factor())
        return expr

    def parse_factor(self):
        expr = self.parse_power()
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            expr = Binary(expr, op, self.parse_power())
        return expr

    def parse_power(self):
        expr = self.parse_unary()
        if self.check(TokenType.POWER):
            op = self.advance().value
            expr = Binary(expr, op, self.parse_power())
        return expr

    def parse_unary(self):
        if self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            return Unary(op, self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.DOT):
                self.advance()
                # `create` is a language keyword in statement position, but
                # library namespaces must still be able to expose a creator
                # operation as `drafter.create(...)`.
                if self.check(TokenType.IDENT):
                    name = self.advance().value
                elif self.check(TokenType.KW_CREATE):
                    name = self.advance().value
                else:
                    raise SyntaxErrorML(
                        "property name must be an identifier",
                        self.filename, self.current.line, self.current.column,
                    )
                expr = Attribute(expr, name)
                continue

            if self.check(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET, "indexing requires a closing ']' bracket")
                expr = Subscript(expr, index)
                continue

            if self.check(TokenType.LPAREN):
                self.advance()
                args = []
                kwargs = {}
                if not self.check(TokenType.RPAREN):
                    while True:
                        if self.check(TokenType.IDENT) and self.tokens[self.i + 1].type == TokenType.EQ:
                            key = self.advance().value
                            self.advance()
                            kwargs[key] = self.parse_expression()
                        else:
                            args.append(self.parse_expression())

                        if not self.check(TokenType.COMMA):
                            break
                        self.advance()
                self.expect(TokenType.RPAREN)
                expr = Call(expr, args, kwargs)
                continue
            break

        return expr

    def parse_primary(self):
        t = self.current

        if t.type == TokenType.NUMBER:
            self.advance()
            value = t.value

            # A number followed by an identifier is a unit literal. Supported
            # prefixes are converted to SI immediately; an unknown unit is
            # reported directly rather than surfacing later as an RPAREN error.
            if self.check(TokenType.IDENT):
                first = str(self.current.value)
                candidate = first
                consume_count = 1
                if (self.i + 2 < len(self.tokens)
                        and self.tokens[self.i + 1].type == TokenType.SLASH
                        and self.tokens[self.i + 2].type == TokenType.IDENT):
                    candidate = f"{first}/{self.tokens[self.i + 2].value}"
                    consume_count = 3
                try:
                    dimension, scale = parse_unit_info(candidate)
                except UnitErrorML as exc:
                    raise UnitErrorML(
                        f"unknown unit '{candidate}'",
                        self.filename, self.current.line, self.current.column,
                    ) from exc
                is_celsius_literal = candidate == "C"
                for _ in range(consume_count):
                    self.advance()
                try:
                    numeric_value = float(value)
                    si_value = numeric_value * scale
                    if is_celsius_literal:
                        si_value += 273.15
                except (OverflowError, ValueError) as exc:
                    raise UnitErrorML(
                        "numeric literal is outside the supported range for unit conversion",
                        self.filename, t.line, t.column,
                    ) from exc
                if not math.isfinite(si_value):
                    raise UnitErrorML(
                        "numeric literal is outside the supported finite range for unit conversion",
                        self.filename, t.line, t.column,
                    )
                return Literal(Quantity(
                    si_value, dimension,
                    is_absolute_temperature=is_celsius_literal,
                    celsius_input_value=numeric_value if is_celsius_literal else None,
                ))

            return Literal(value)

        if t.type == TokenType.STRING:
            self.advance()
            return Literal(t.value)

        if t.type == TokenType.KW_TRUE:
            self.advance()
            return Literal(True)

        if t.type == TokenType.KW_FALSE:
            self.advance()
            return Literal(False)

        if t.type == TokenType.IDENT:
            self.advance()
            return Name(t.value)

        if t.type == TokenType.KW_CREATE:
            self.advance()
            type_name = self.expect(TokenType.IDENT, "create must be followed by an element/object type").value
            return Create(type_name)

        if t.type == TokenType.LBRACKET:
            self.advance()
            items = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    items.append(self.parse_expression())
                    if not self.check(TokenType.COMMA):
                        break
                    self.advance()
            self.expect(TokenType.RBRACKET)
            return ListLiteral(items)

        if t.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        if t.type == TokenType.KW_FOR:
            message = "'for' is not identified"
        elif t.type == TokenType.KW_IN:
            message = "'in' is not identified"
        elif t.type == TokenType.IDENT:
            message = f"'{t.value}' is not identified"
        else:
            message = f"unexpected {self._unexpected_token_message(TokenType.EOF).removeprefix('expected the end of the file, found ').replace('the end of the line', 'end of line').replace('the end of the file', 'end of file')}"
        raise SyntaxErrorML(message, self.filename, t.line, t.column)

