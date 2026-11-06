#!/usr/bin/env python3
"""Check journal-article ratio from a TSV or CSV reference table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def normalize(value: str) -> str:
    return value.strip().lower()


def is_journal(row: dict[str, str]) -> bool:
    fields = " ".join(normalize(v) for v in row.values())
    return any(marker in fields for marker in ("journal", "[j]", "期刊", "journal article"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("table", help="CSV/TSV file with reference rows")
    parser.add_argument("--min-ratio", type=float, default=0.8)
    args = parser.parse_args()

    path = Path(args.table)
    sample = path.read_text(encoding="utf-8").splitlines()[:3]
    delimiter = "\t" if any("\t" in line for line in sample) else ","

    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=delimiter))

    total = len(rows)
    journals = sum(1 for row in rows if is_journal(row))
    ratio = journals / total if total else 0.0
    passed = ratio >= args.min_ratio

    print(f"total_references: {total}")
    print(f"journal_references: {journals}")
    print(f"journal_ratio: {ratio:.3f}")
    print(f"min_ratio: {args.min_ratio:.3f}")
    print(f"passed: {passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
