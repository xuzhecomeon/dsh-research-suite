#!/usr/bin/env python3
"""Report references that do not appear as in-text numeric citations."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: detect_uncited_references.py path/to/document.md", file=sys.stderr)
        return 2

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    refs = {int(n) for n in re.findall(r"(?m)^\s*\[(\d+)\]\s+", text)}
    body = re.sub(r"(?ms)^\s*参考文献\s*$.*", "", text)
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", body)}
    uncited = sorted(refs - cited)

    print(f"uncited_references: {uncited}")
    return 1 if uncited else 0


if __name__ == "__main__":
    raise SystemExit(main())
