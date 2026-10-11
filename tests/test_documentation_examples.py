from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import re

from magiclang.lexer import Lexer
from magiclang.parser import Parser
from magiclang.runtime import Runtime

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "current"
MANA_FENCE = re.compile(r"```mana\s*\n(.*?)\n```", re.DOTALL)
EXPECTED_OUTPUT = re.compile(r"Expected output:\s*\n\s*```text\s*\n(.*?)\n```", re.DOTALL)
NON_STANDALONE_MARKERS = (
    "not standalone",
    "expected failure",
    "intentionally invalid",
    "fragment",
)


def test_current_documentation_mana_blocks_run_or_are_explicitly_marked():
    checked = 0
    skipped = []
    failures = []

    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(MANA_FENCE.finditer(text))
        headings = list(re.finditer(r"^#{1,6}\s+", text, flags=re.MULTILINE))
        for index, match in enumerate(matches):
            code = match.group(1)
            line = text.count("\n", 0, match.start()) + 1
            preceding = text[max(0, match.start() - 400):match.start()].casefold()
            if any(marker in preceding for marker in NON_STANDALONE_MARKERS):
                skipped.append(f"{path.relative_to(ROOT)}:{line}")
                continue

            checked += 1
            try:
                filename = f"{path.relative_to(ROOT)}:{line}"
                stdout = StringIO()
                with redirect_stdout(stdout), redirect_stderr(StringIO()):
                    program = Parser(Lexer(code, filename).tokenize(), filename).parse()
                    Runtime(project_root=ROOT).execute(program)
                boundary = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                next_heading = next((heading.start() for heading in headings if heading.start() >= match.end()), len(text))
                boundary = min(boundary, next_heading)
                expected = EXPECTED_OUTPUT.search(text[match.end():boundary])
                if expected:
                    actual_output = stdout.getvalue().rstrip("\n")
                    expected_output = expected.group(1).rstrip("\n")
                    if expected_output == "(no output)":
                        expected_output = ""
                    actual_output = re.sub(r"(<[^<>#]+#)\d+(>)", r"\1*\2", actual_output)
                    expected_output = re.sub(r"(<[^<>#]+#)\d+(>)", r"\1*\2", expected_output)
                    assert actual_output == expected_output, (
                        f"expected output {expected_output!r}, got {actual_output!r}"
                    )
            except Exception as exc:  # Report each independent docs failure together.
                failures.append(
                    f"{path.relative_to(ROOT)}:{line}: {type(exc).__name__}: {exc}"
                )

    assert checked >= 100, f"Expected to find the current MANA examples, checked only {checked}"
    assert not failures, "MANA documentation examples failed:\n" + "\n".join(failures)
    # The remaining snippets are library-source/package integration examples or
    # intentionally invalid examples and must be labelled as such before their fence.
    assert all(skipped), "Unlabelled non-standalone MANA examples were skipped"
