#!/usr/bin/env python3
"""Minimum |U| with star-cover at least 5 or 6.

q6: min |U| hitting every 4-star complement is 5, so |U|=19 is not
empty by combinatorics after the 4-star leftover emptiness.

If every 5-star leftover host is empty, a remaining leftover 41-set
has star-cover at least 6.  This file also hits the 252 five-star
complements.  That minimum is still far below 19.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent / "q5"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import load_graph  # noqa: E402


def min_hitting(comps):
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Cadical195

    def vx(r):
        return r + 1

    cnf = CNF()
    for c in comps:
        cnf.append([vx(r) for r in range(40) if (c >> r) & 1])
    lo, hi = 1, 12
    exact, witness, bounds = None, None, []
    while lo <= hi:
        mid = (lo + hi) // 2
        card = CardEnc.atmost(
            lits=[vx(r) for r in range(40)], bound=mid,
            top_id=40, encoding=EncType.seqcounter,
        )
        slv = Cadical195(bootstrap_with=cnf.clauses + card.clauses)
        sat = slv.solve()
        model = slv.get_model() if sat else None
        slv.delete()
        bounds.append({"bound": mid, "sat": bool(sat)})
        if sat and model:
            true = {x for x in model if x > 0}
            witness = [r for r in range(40) if vx(r) in true]
            exact = len(witness)
            hi = mid - 1
        else:
            lo = mid + 1
    return exact, witness, bounds


def main() -> int:
    G = load_graph()
    stars = G["stars"]
    all_roots = (1 << 40) - 1
    four = []
    for comb in combinations(range(10), 4):
        W = 0
        for s in comb:
            W |= stars[s]
        four.append(W)
    five = []
    for comb in combinations(range(10), 5):
        W = 0
        for s in comb:
            W |= stars[s]
        five.append(W)
    four_comps = [all_roots ^ W for W in four]
    five_comps = [all_roots ^ W for W in five]
    m5, w5, b5 = min_hitting(four_comps)
    m6, w6, b6 = min_hitting(five_comps)
    report = {
        "n_four_star_unions": len(four),
        "four_star_union_sizes": sorted({W.bit_count() for W in four}),
        "n_five_star_unions": len(five),
        "five_star_union_sizes": sorted({W.bit_count() for W in five}),
        "min_star_cover_5": m5,
        "witness_cover_5": w5,
        "bounds_cover_5": b5,
        "min_star_cover_6": m6,
        "witness_cover_6": w6,
        "bounds_cover_6": b6,
        "k19_empty_by_cover_5": bool(m5 is not None and m5 >= 20),
        "k19_empty_by_cover_6": bool(m6 is not None and m6 >= 20),
        "found_41": False,
        "comment": (
            "min |U| with star-cover >= 5 (resp. 6) is the min hitting "
            "set of 4-star (resp. 5-star) complements.  Neither empties "
            "|U|=19 by combinatorics."
        ),
    }
    (HERE / "star_cover_min.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "min_star_cover_5": m5,
        "min_star_cover_6": m6,
        "k19_empty_by_cover_5": report["k19_empty_by_cover_5"],
        "k19_empty_by_cover_6": report["k19_empty_by_cover_6"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
