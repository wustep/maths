#!/usr/bin/env python3
"""Zip the 617 residue cycle (Herwig–Heule) and check 7-AP-freeness.

Published tables say 0 zips for W(2,7). This recomputes that claim and
tries both colors of the two special points 0 and p.
"""

from __future__ import annotations

import json
from pathlib import Path

from vdw import first_mono_ap, format_ab, max_monochrome_run, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent
P = 617


def zip_herwig(cycle_1indexed: list[int], turn: bool) -> list[int]:
    """cycle_1indexed[j] is the color of j for j=1..p (length p).

    Returns a coloring of [1, 2p] as a 0-based list of length 2p.
    """
    p = len(cycle_1indexed)
    # spread onto odds: color(2j-1) = color(j)
    odds = [0] * (2 * p)
    for j in range(1, p + 1):
        odds[2 * j - 2] = cycle_1indexed[j - 1]  # 1-based 2j-1 -> index 2j-2
    turned = [1 - c if turn else c for c in odds]
    evens = [0] * (2 * p)
    for j in range(1, p + 1):
        src = 2 * j - 1  # 1-based odd
        dest = (src - p) % (2 * p)
        if dest == 0:
            dest = 2 * p
        evens[dest - 1] = turned[src - 1]
    merged = [0] * (2 * p)
    for i in range(2 * p):
        if (i + 1) % 2 == 1:
            merged[i] = odds[i]
        else:
            merged[i] = evens[i]
    return merged


def main() -> None:
    cycle = quadratic_residue_cycle(P, zero_color=0)
    # 1-based [1,p]: map residue of 1..p with p -> zero color
    cycle_1 = [cycle[j % P] for j in range(1, P + 1)]
    reports = []
    for turn in (False, True):
        zipped = zip_herwig(cycle_1, turn=turn)
        hit = first_mono_ap(zipped, k=7, cyclic=True)
        lin = first_mono_ap(zipped, k=7, cyclic=False)
        rec = {
            "turn": turn,
            "length": len(zipped),
            "max_run": max_monochrome_run(zipped, cyclic=True),
            "cyclic_7ap_free": hit is None,
            "linear_7ap_free": lin is None,
            "cyclic_hit": None if hit is None else {"start": hit[0], "diff": hit[1]},
        }
        reports.append(rec)
        if hit is None:
            (HERE / f"zip_1234_turn{int(turn)}.txt").write_text(
                format_ab(zipped) + "\n", encoding="ascii"
            )
    (HERE / "zip_try.json").write_text(json.dumps(reports, indent=2) + "\n", encoding="ascii")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
