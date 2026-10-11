from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from magiclang.runner import run_file
from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.errors import MagicLangError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or check a MANA source file.")
    parser.add_argument("--check", action="store_true", help="parse and validate the file without executing it")
    parser.add_argument("file", type=Path, help="path to a .mana source file")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    source = args.file.expanduser()
    if source.suffix.lower() != ".mana":
        print("Error: expected a file ending in .mana", file=sys.stderr)
        return 2
    if not source.is_file():
        print(f"Error: file not found: {source}", file=sys.stderr)
        return 2

    try:
        if args.check:
            text = source.read_text(encoding="utf-8-sig")
            Parser(Lexer(text, str(source.resolve())).tokenize(), str(source.resolve())).parse()
            print(f"MANA check passed: {source}")
        else:
            run_file(str(source))
    except MagicLangError as exc:
        location = f"{exc.filename}:{exc.line}:{exc.column}" if exc.line is not None else exc.filename
        print(f"{exc.code} {type(exc).__name__}: {location}: {exc.message}", file=sys.stderr)
        if exc.hint:
            print(f"Hint: {exc.hint}", file=sys.stderr)
        return 1
    except Exception:
        # Do not expose host-language tracebacks to normal language users. Developers
        # can opt in to the complete traceback when debugging the interpreter.
        import os
        if os.environ.get("MANA_DEBUG", "").casefold() in {"1", "true", "yes"}:
            traceback.print_exc(file=sys.stderr)
        else:
            print("M9000: internal MANA error; rerun with MANA_DEBUG=1 for details", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
