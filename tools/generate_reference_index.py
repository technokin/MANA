"""Generate API and glossary-usage indexes from the current references."""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/current"
FUNCTIONS = DOCS / "reference/FUNCTION_REFERENCE.md"
GLOSSARY = DOCS / "foundations/GLOSSARY_AND_DESIGN_TERMS.md"
RUNTIME = ROOT / "magiclang/runtime.py"


def anchor(text: str) -> str:
    text = re.sub(r"[`*_]", "", text).casefold()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"\s+", "-", text.strip())


def generate_api_index() -> str:
    source = FUNCTIONS.read_text(encoding="utf-8")
    headings = re.findall(r"^###\s+(.+)$", source, flags=re.MULTILINE)
    functions = []
    for heading in headings:
        name_match = re.match(r"`([^`]+)`", heading)
        if name_match:
            name = name_match.group(1)
            description = (
                heading.split("—", 1)[-1].strip()
                if "—" in heading
                else "Language construct"
            )
            functions.append((name, description, heading))
    runtime = RUNTIME.read_text(encoding="utf-8")
    event_match = re.search(r"MANA_EVENT_NAMES\s*=\s*\{([^}]+)\}", runtime)
    events = sorted(re.findall(r"['\"]([^'\"]+)['\"]", event_match.group(1))) if event_match else []
    errors = ["MagicLangError", "SyntaxErrorML", "TypeErrorML", "UnitErrorML", "RuntimeErrorML", "MagicErrorML", "PhysicsErrorML"]
    lines = ["# Generated MANA API Index", "", "**Page kind:** Reference", "", "This page is generated from the current function reference and runtime event/error definitions. Run `python tools/generate_reference_index.py` after changing those sources.", "", "## Functions and language constructs", "", "| Name | Description | Reference |", "|---|---|---|"]
    for name, description, heading in functions:
        escaped_description = description.replace("|", "\\|")
        lines.append(
            f"| `{name}` | {escaped_description} | "
            f"[Function reference](FUNCTION_REFERENCE.md#{anchor(heading)}) |"
        )
    lines += ["", "## Events", "", "| Event | Reference |", "|---|---|"]
    for event in events:
        lines.append(f"| `{event}` | [Event names and rules](../foundations/EXECUTION_TIME_AND_EVENTS.md) |")
    lines += ["", "## Error classes", "", "| Error class | Reference |", "|---|---|"]
    for error in errors:
        lines.append(f"| `{error}` | [Error catalogue](ERROR_CATALOGUE.md) |")
    return "\n".join(lines) + "\n"


def generate_glossary_usage() -> str:
    glossary = GLOSSARY.read_text(encoding="utf-8")
    terms = []
    for row in re.findall(r"^\| \*\*(.+?)\*\* \| (.+?) \|$", glossary, flags=re.MULTILINE):
        terms.append(row)
    pages = sorted(
        DOCS.rglob("*.md"),
        key=lambda page: (
            page.relative_to(DOCS).as_posix().casefold(),
            page.relative_to(DOCS).as_posix(),
        ),
    )
    lines = ["# Generated Glossary Usage Index", "", "**Page kind:** Reference", "", "Generated from the glossary and current documentation. This index shows where terms occur; it is a consistency-review aid, not an automatic proof that every sentence uses a term correctly.", "", "| Term | Glossary meaning | Pages mentioning the term |", "|---|---|---|"]
    for term, meaning in terms:
        matches = []
        needle = re.sub(r"`", "", term).casefold()
        for page in pages:
            if page == GLOSSARY:
                continue
            text = page.read_text(encoding="utf-8").casefold()
            if needle and needle in text:
                rel = Path(os.path.relpath(page, GLOSSARY.parent)).as_posix()
                matches.append(f"[{page.stem}]({rel})")
        lines.append(f"| **{term}** | {meaning} | {', '.join(matches) if matches else 'No other current page yet'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if either generated index is stale")
    args = parser.parse_args()
    outputs = {
        DOCS / "reference/API_INDEX.md": generate_api_index(),
        DOCS / "foundations/GLOSSARY_USAGE_INDEX.md": generate_glossary_usage(),
    }
    stale = []
    for path, generated in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != generated:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(generated, encoding="utf-8")
    if stale:
        print("Generated indexes are stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    print("Generated indexes are current." if args.check else "Generated API index and glossary usage index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
