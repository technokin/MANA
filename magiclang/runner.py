from __future__ import annotations

from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .runtime import Runtime


def _find_project_root(source_path: Path) -> Path:
    """Locate the MANA project root without requiring the source to sit at its root."""
    resolved = source_path.resolve()
    for candidate in (resolved.parent, *resolved.parent.parents):
        if (candidate / "mana.py").is_file() or (candidate / "libraries").is_dir():
            return candidate
    return resolved.parent


def run_file(path: str, *, runtime: Runtime | None = None) -> Runtime:
    """Parse and execute a MANA file, optionally using an existing runtime.

    The command-line interface and editor tasks use this same runner. Passing an
    existing Runtime remains useful for tests and embedding.
    """
    source_path = Path(path).expanduser().resolve()
    source = source_path.read_text(encoding="utf-8-sig")
    tokens = Lexer(source, str(source_path)).tokenize()
    program = Parser(tokens, str(source_path)).parse()
    engine = runtime or Runtime(project_root=_find_project_root(source_path))
    engine.execute(program)
    return engine
