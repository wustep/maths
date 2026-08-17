#!/usr/bin/env python3
"""Replay the elementary parameter identities for a putative PP(12)."""

from __future__ import annotations

import json
import math
import sys


def main() -> None:
    n = 12
    v = n * n + n + 1
    pairs = v * (v - 1) // 2
    line_pairs = v * (n * (n + 1) // 2)
    # BB^T = n I + J, eigenvalues n+1 once and n with mult v-1
    # det(BB^T) = (n+1)^2 * n^{v-1}
    # |det B| = (n+1) * n^{(v-1)/2} = 13 * 12^78
    detB = (n + 1) * n ** ((v - 1) // 2)
    report = {
        "n": n,
        "v": v,
        "block_size": n + 1,
        "pairs": pairs,
        "line_pairs": line_pairs,
        "pairs_match": pairs == line_pairs,
        "detB": detB,
        "detB_formula": "13 * 12**78",
        "detB_ok": detB == 13 * 12**78,
        "bruck_ryser_applies": n % 4 in (1, 2),
        "12_is_sum_of_two_squares": any(
            a * a + b * b == n for a in range(n + 1) for b in range(n + 1)
        ),
        "v_mod_2": v % 2,
        "v_mod_3": v % 3,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    ok = report["v"] == 157 and report["pairs_match"] and report["detB_ok"]
    ok = ok and not report["bruck_ryser_applies"]
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
