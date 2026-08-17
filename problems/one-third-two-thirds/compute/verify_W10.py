#!/usr/bin/env python3
"""Replay the 10-element width-3 record breaker W10.

Published width-3 record through 9 elements: 14/39 (Saks; TGF 1992;
Olson–Sagan 2018). W10 has delta = 6/17 < 14/39, e = 187, width 3.
"""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from posetlib import (
    Poset,
    balance,
    count_le_ideals,
    count_le_mins,
    pair_counts_by_adding,
    pair_counts_fb,
)

DOWN = [0, 0, 1, 1, 7, 11, 23, 87, 95, 255]


def main():
    P = Poset(10, DOWN)
    e1 = count_le_ideals(P)
    e2 = count_le_mins(P)
    e3, C = pair_counts_fb(P)
    e4, C2 = pair_counts_by_adding(P)
    assert e1 == e2 == e3 == e4 == 187, (e1, e2, e3, e4)
    for x in range(10):
        for y in range(10):
            assert C[x][y] == C2[x][y]
    num, den, e, pair, _ = balance(P, C, e3)
    g = gcd(num, den)
    assert (num // g, den // g) == (6, 17)
    assert e == 187
    assert pair[2] + pair[3] == 187
    assert min(pair[2], pair[3]) == 66
    assert P.width_lower() == 3
    assert 6 * 39 < 17 * 14  # 6/17 < 14/39
    assert 6 * 3 > 17        # 6/17 > 1/3
    out = {
        "e": 187,
        "delta": [6, 17],
        "pair": list(pair),
        "width": 3,
        "beats_14_39": True,
        "above_1_3": True,
    }
    Path(__file__).resolve().parent.joinpath("W10_verify.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print("W10 OK", out)


if __name__ == "__main__":
    main()
