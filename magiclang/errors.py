class MagicLangError(Exception):
    """Base class for language errors with optional source locations."""

    DEFAULT_CODE = "M0000"

    def __init__(self, message: str, filename: str = "<input>", line: int | None = None,
                 column: int | None = None, *, code: str | None = None,
                 hint: str | None = None, severity: str = "error"):
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        self.code = code or self.DEFAULT_CODE
        self.hint = hint
        self.severity = severity
        super().__init__(self._format())

    def to_diagnostic(self) -> dict[str, object]:
        """Return a stable machine-readable diagnostic for editors and tools."""
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "filename": self.filename,
            "line": self.line,
            "column": self.column,
            "hint": self.hint,
        }

    def _format(self) -> str:
        location = self.filename
        if self.line is not None:
            location += f":{self.line}"
            if self.column is not None:
                location += f":{self.column}"
        return f"{self.__class__.__name__}: {location}: {self.message}"

    def attach_location(self, filename: str, line: int | None, column: int | None = None) -> None:
        """Attach the closest source statement location to a runtime error."""
        if self.line is None:
            self.filename = filename or self.filename
            self.line = line
            self.column = column
            self.args = (self._format(),)
        elif self.column is None and column is not None:
            self.column = column
            self.args = (self._format(),)


class SyntaxErrorML(MagicLangError):
    DEFAULT_CODE = "M1000"


class TypeErrorML(MagicLangError):
    DEFAULT_CODE = "M2000"


class UnitErrorML(MagicLangError):
    DEFAULT_CODE = "M2100"


class RuntimeErrorML(MagicLangError):
    DEFAULT_CODE = "M3000"


class MagicErrorML(MagicLangError):
    DEFAULT_CODE = "M4000"


class PhysicsErrorML(MagicLangError):
    DEFAULT_CODE = "M5000"
