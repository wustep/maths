#!/usr/bin/env python3
"""Re-export the q1 sequential-counter encoder."""

from __future__ import annotations

import sys
from pathlib import Path

Q1 = Path(__file__).resolve().parent.parent / "q1"
sys.path.insert(0, str(Q1))

from encode import encode, main, sinz_atleast, sinz_atmost, sinz_exactly, var_id, write_cnf

__all__ = [
    "encode",
    "main",
    "sinz_atleast",
    "sinz_atmost",
    "sinz_exactly",
    "var_id",
    "write_cnf",
]


if __name__ == "__main__":
    main()
