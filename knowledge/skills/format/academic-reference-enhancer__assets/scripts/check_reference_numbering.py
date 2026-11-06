#!/usr/bin/env python3
"""Check simple numeric citation/reference consistency in plain text or Markdown."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def expand_citation_token(token: str) -> set[int]:
    values: set[int] = set()
    for part in token.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            if left.strip().isdigit() and right.strip().isdigit():
                start, end = int(left), int(right)
                if start <= end:
                    values.update(range(start, end + 1))
            continue
        if part.isdigit():
            values.add(int(part))
    return values


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_reference_numbering.py path/to/document.md", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    reference_numbers = {int(n) for n in re.findall(r"(?m)^\s*\[(\d+)\]\s+", text)}
    citation_numbers: set[int] = set()
    for raw in re.findall(r"\[((?:\d+\s*(?:-\s*\d+)?)(?:\s*,\s*\d+\s*(?:-\s*\d+)?)*)\]", text):
        citation_numbers.update(expand_citation_token(raw.replace(" ", "")))

    missing_references = sorted(citation_numbers - reference_numbers)
    uncited_references = sorted(reference_numbers - citation_numbers)
    expected = set(range(1, max(reference_numbers or {0}) + 1))
    numbering_gaps = sorted(expected - reference_numbers)

    print(f"citation_numbers: {sorted(citation_numbers)}")
    print(f"reference_numbers: {sorted(reference_numbers)}")
    print(f"missing_references: {missing_references}")
    print(f"uncited_references: {uncited_references}")
    print(f"numbering_gaps: {numbering_gaps}")

    return 1 if missing_references or numbering_gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
