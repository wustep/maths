#!/usr/bin/env python3
"""Replay the published record this campaign is not allowed to regress."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
Q1 = PARENT / "q1"
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(Q1))

from ladders import named  # noqa: E402
from posetlib import W10, balance, pair_counts_fb  # noqa: E402
from verify_gupta import check, ladder_poset, n_ordinal_summands  # noqa: E402


def main():
    print("published record (must not regress)")
    check("W10", W10(), (6, 17), 187, 3)
    check("L14,1,9", ladder_poset(14, (1, 9)), (254, 725), 725, 2)
    check("L10,1,5", ladder_poset(10, (1, 5)), (37, 106), 106, 2)
    check("L21,1,5,8,9,12,16", ladder_poset(21, (1, 5, 8, 9, 12, 16)), (5402, 15485), 30970, None)
    row = named(21, (1, 5, 8, 9, 12, 16))
    if row["n_summands"] != 1:
        raise AssertionError("L21 splits")
    print("PUBLISHED RECORD OK")


if __name__ == "__main__":
    main()
