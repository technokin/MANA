"""Inventory error constructors in the interpreter source for documentation review."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "magiclang"
OUTPUT = ROOT / "docs/current/reference/ERROR_MESSAGE_INDEX.md"
ERROR_NAMES = {"MagicLangError", "SyntaxErrorML", "TypeErrorML", "UnitErrorML", "RuntimeErrorML", "MagicErrorML", "PhysicsErrorML"}


def message_template(node: ast.AST) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return repr(node.value)
    if isinstance(node, ast.JoinedStr):
        pieces = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                pieces.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                pieces.append("{" + ast.unparse(value.value) + "}")
        return "f\"" + "".join(pieces).replace('"', '\\"') + "\""
    return "<message supplied by expression: " + ast.unparse(node) + ">"


def render() -> str:
    entries = []
    for path in sorted(SOURCE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if name not in ERROR_NAMES:
                continue
            message = message_template(node.args[0]) if node.args else "<no explicit message>"
            rel = path.relative_to(ROOT).as_posix()
            entries.append((name, rel, node.lineno, message))
    entries.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    lines = [
        "# Generated MANA Error Message Index", "", "**Page kind:** Reference", "",
        "Generated from direct error-constructor calls in `magiclang/`. Run `python tools/generate_error_catalogue.py` after changing error messages. Dynamic templates show expressions in braces. Errors raised indirectly through a variable are listed as expression-supplied messages where statically visible; runtime-composed details depend on the values involved.",
        "", f"**Indexed call sites:** {len(entries)}", "", "| Error class | Source | Line | Message template |", "|---|---|---:|---|"
    ]
    for name, rel, line, message in entries:
        safe = message.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{name}` | [`{rel}`](../../../{rel}) | {line} | `{safe}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != generated:
            print("Error message index is stale; run python tools/generate_error_catalogue.py", file=sys.stderr)
            return 1
        print("Error message index is current.")
        return 0
    OUTPUT.write_text(generated, encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
