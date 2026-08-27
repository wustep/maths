#!/usr/bin/env python3
"""Minimum |U| of a D5-root set with star-cover at least 5.

After every 4-star leftover host is empty, a remaining leftover 41-set
has U not contained in any 4-star union.  That is a hitting set of the
210 complements of those unions.  If the minimum such |U| is >= 20,
the leftover slices |U|=19 (and possibly 20) are empty by combinatorics.
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

from n1_leftover_sat import stars_of  # noqa: E402
from sphere import extras_and_groups  # noqa: E402


def main() -> int:
    G = extras_and_groups(4)
    stars = stars_of(G["D"])
    all_roots = (1 << 40) - 1
    unions = []
    for comb in combinations(range(10), 4):
        W = 0
        for s in comb:
            W |= stars[s]
        unions.append(W)
    comps = [all_roots ^ W for W in unions]
    sizes = sorted({W.bit_count() for W in unions})
    comp_sizes = sorted({c.bit_count() for c in comps})

    # greedy hitting set
    hit = 0
    rem = list(comps)
    greedy = []
    while rem:
        best_r, best_n = 0, -1
        for r in range(40):
            if (hit >> r) & 1:
                continue
            n = sum(1 for c in rem if (c >> r) & 1)
            if n > best_n:
                best_r, best_n = r, n
        hit |= 1 << best_r
        greedy.append(best_r)
        rem = [c for c in rem if (c & hit) == 0]

    # exact min hitting set via SAT
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Cadical195

    def vx(r):
        return r + 1

    cnf = CNF()
    for c in comps:
        cnf.append([vx(r) for r in range(40) if (c >> r) & 1])

    lo, hi = 1, len(greedy)
    exact = None
    witness = None
    bounds = []
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
        print(f"hitting-set |U|<={mid} sat={sat}", flush=True)
        if sat and model:
            true = {x for x in model if x > 0}
            witness = [r for r in range(40) if vx(r) in true]
            exact = len(witness)
            hi = mid - 1
        else:
            lo = mid + 1

    # also: min |U| contained in a 5-star but not in any 4-star
    five_unions = []
    for comb in combinations(range(10), 5):
        W = 0
        for s in comb:
            W |= stars[s]
        five_unions.append(W)
    five_sizes = sorted({W.bit_count() for W in five_unions})

    report = {
        "n_four_star_unions": len(unions),
        "four_star_union_sizes": sizes,
        "four_star_complement_sizes": comp_sizes,
        "n_five_star_unions": len(five_unions),
        "five_star_union_sizes": five_sizes,
        "greedy_hitting_set": greedy,
        "greedy_size": len(greedy),
        "min_star_cover_5": exact,
        "witness": witness,
        "binary_search": bounds,
        "k19_empty_by_cover": bool(exact is not None and exact >= 20),
        "k20_empty_by_cover": bool(exact is not None and exact >= 21),
        "comment": (
            "min |U| with star-cover >= 5 is the min hitting set of the "
            "complements of the 210 four-star unions.  If that minimum "
            "is >= 20, leftover |U|=19 with cover >= 5 is empty."
        ),
    }
    (HERE / "star_cover_min.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "greedy": len(greedy),
        "exact": exact,
        "k19_empty_by_cover": report["k19_empty_by_cover"],
        "k20_empty_by_cover": report["k20_empty_by_cover"],
        "four_star_union_sizes": sizes,
        "five_star_union_sizes": five_sizes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
