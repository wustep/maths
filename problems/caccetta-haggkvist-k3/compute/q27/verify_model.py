#!/usr/bin/env python3
"""Check a SAT model against the exact CH-triangle statement."""

from __future__ import annotations

import sys
from pathlib import Path

Q1 = Path(__file__).resolve().parent.parent / "q1"
sys.path.insert(0, str(Q1))

from verify_model import check, main, parse_model

__all__ = ["check", "parse_model"]


if __name__ == "__main__":
    main()
