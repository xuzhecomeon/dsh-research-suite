#!/usr/bin/env python3
"""Thin executable facade for the literature-search backend."""

import sys
from pathlib import Path


_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from literature_search.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
