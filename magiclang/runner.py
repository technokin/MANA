from __future__ import annotations

from pathlib import Path
import stat

from .errors import SyntaxErrorML

from .lexer import Lexer
from .parser import Parser
from .runtime import Runtime

MAX_SOURCE_FILE_BYTES = 2 * 1024 * 1024


def read_mana_source(path: Path) -> str:
    """Read a regular UTF-8 MANA file without unbounded file allocation."""
    resolved = path.expanduser().resolve()
    try:
        info = resolved.stat()
        if not stat.S_ISREG(info.st_mode):
            raise SyntaxErrorML("MANA source must be a regular file", str(resolved), 1, 1)
        if info.st_size > MAX_SOURCE_FILE_BYTES:
            raise SyntaxErrorML(
                f"source exceeds the {MAX_SOURCE_FILE_BYTES:,}-byte safety limit",
                str(resolved), 1, 1,
            )
        with resolved.open("rb") as handle:
            raw = handle.read(MAX_SOURCE_FILE_BYTES + 1)
    except OSError as exc:
        raise SyntaxErrorML(f"cannot read source file: {exc.strerror or exc.__class__.__name__}", str(resolved), 1, 1) from exc
    if len(raw) > MAX_SOURCE_FILE_BYTES:
        raise SyntaxErrorML(
            f"source exceeds the {MAX_SOURCE_FILE_BYTES:,}-byte safety limit",
            str(resolved), 1, 1,
        )
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SyntaxErrorML("source file is not valid UTF-8", str(resolved), 1, 1) from exc


def _find_project_root(source_path: Path) -> Path:
    """Locate the MANA project root without requiring the source to sit at its root."""
    resolved = source_path.resolve()
    for candidate in (resolved.parent, *resolved.parent.parents):
        if (candidate / "mana.py").is_file() or (candidate / "libraries").is_dir():
            return candidate
    return resolved.parent


def run_file(path: str, *, runtime: Runtime | None = None, observe_file: str | Path | None = None) -> Runtime:
    """Parse and execute a MANA file, optionally using an existing runtime.

    The command-line interface and editor tasks use this same runner. Passing an
    existing Runtime remains useful for tests and embedding.
    """
    source_path = Path(path).expanduser().resolve()
    source = read_mana_source(source_path)
    tokens = Lexer(source, str(source_path)).tokenize()
    program = Parser(tokens, str(source_path)).parse()
    owns_runtime = runtime is None
    engine = runtime or Runtime(project_root=_find_project_root(source_path), observe_file=observe_file)
    try:
        engine.execute(program)
    except BaseException:
        if owns_runtime:
            engine.close_observer()
        raise
    return engine
