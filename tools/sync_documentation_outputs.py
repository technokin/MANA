"""Add captured expected-output blocks beside standalone runnable MANA examples."""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DOCS = ROOT / "docs/current"
FENCE = re.compile(r"```mana\s*\n(.*?)\n```", re.DOTALL)
EXPECTED = re.compile(r"Expected output:\s*\n\s*```text\s*\n(.*?)\n```", re.DOTALL)
SKIP_MARKERS = ("not standalone", "expected failure", "intentionally invalid", "fragment", "manifest")


def captured_output(code: str, filename: str) -> str:
    from magiclang.lexer import Lexer
    from magiclang.parser import Parser
    from magiclang.runtime import Runtime

    stdout, stderr = StringIO(), StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        program = Parser(Lexer(code, filename).tokenize(), filename).parse()
        Runtime(project_root=ROOT).execute(program)
    output = stdout.getvalue().rstrip("\n")
    return output if output else "(no output)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report examples missing captured expected output")
    args = parser.parse_args()
    changed = []
    missing = []
    for path in sorted(DOCS.rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        matches = list(FENCE.finditer(original))
        headings = list(re.finditer(r"^#{1,6}\s+", original, flags=re.MULTILINE))
        additions = []
        for index, match in enumerate(matches):
            boundary = matches[index + 1].start() if index + 1 < len(matches) else len(original)
            next_heading = next((heading.start() for heading in headings if heading.start() >= match.end()), len(original))
            boundary = min(boundary, next_heading)
            following = original[match.end():boundary]
            if EXPECTED.search(following):
                continue
            preceding = original[max(0, match.start() - 400):match.start()].casefold()
            if any(marker in preceding for marker in SKIP_MARKERS):
                continue
            label = f"{path.relative_to(ROOT)}:{original.count(chr(10), 0, match.start()) + 1}"
            if args.check:
                # A check is a consistency check, not an execution pass. Running
                # every uncaptured snippet here can be slow and may trigger
                # intentional long-running examples. Generation is responsible
                # for executing the snippet and capturing its output.
                missing.append(f"{label}: runnable example lacks captured output")
                continue
            try:
                output = captured_output(match.group(1), label)
            except Exception as exc:
                # Existing documentation tests should explicitly mark these as
                # fragments or expected failures rather than freezing an error.
                missing.append(f"{label}: cannot capture output ({type(exc).__name__}: {exc})")
                continue
            rendered = "(no output)" if output == "(no output)" else output
            additions.append((match.end(), f"\n\nExpected output:\n\n```text\n{rendered}\n```"))
        if args.check:
            missing.extend(f"{path.relative_to(ROOT)}: runnable example lacks expected output" for _ in additions)
            continue
        updated = original
        for offset, addition in reversed(additions):
            updated = updated[:offset] + addition + updated[offset:]
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append((path.relative_to(ROOT).as_posix(), len(additions)))
    if missing:
        print("Documentation output sync needs attention:\n" + "\n".join(missing), file=sys.stderr)
        return 1
    if args.check:
        print("All standalone runnable MANA examples have expected-output blocks.")
    else:
        print("Added expected output to:")
        for path, count in changed:
            print(f"  {path}: {count} example(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
