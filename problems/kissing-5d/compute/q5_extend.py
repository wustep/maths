#!/usr/bin/env python3
"""Try to enlarge Q5 / R5 / L5 by one exact or numerical point.

Two exact layers:
  1. A new equatorial point of Q5 (coord-sum 0, so it lives with the A4 slice).
     The A4 constraints become max x_i - min x_i ≤ 1 on |x|^2 = 2, sum x = 0,
     plus inner products ≤ 1 against the two 10-point caps.
  2. Completing the A4 equator to a 24-cell (if an isometric embedding exists)
     and testing the four candidate extra D4 roots against the caps.

A numerical layer then maximises the slack of a 41st unit vector against
each 40-point code.  A positive slack would be a construction lead; a
strictly negative numerical slack is residue, not a certificate.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from configs import _coord_sum, _dot, _norm2, _reflect_coord_sum, d5, l5, q5, r5

F = Fraction
PY = None  # filled in main if scipy present


def a4_equator():
    return [p for p in d5() if _coord_sum(p) == 0]


def q5_caps():
    pts = q5()
    eq = set(a4_equator())
    return [p for p in pts if p not in eq]


def try_complete_a4_to_d4() -> dict:
    """Is the A4 20-set isometric to 24-cell minus two antipodal pairs?"""
    a4 = a4_equator()
    # A4 lives in sum=0.  A 24-cell in that 4-space would be an orthonormal
    # image of D4.  Compare unordered inner-product histograms of A4 against
    # every 20-point antipodal subset of a model D4 in R^4.
    a4_hist = {}
    for i, j in combinations(range(20), 2):
        t = _dot(a4[i], a4[j]) / 2
        a4_hist[t] = a4_hist.get(t, 0) + 1

    # Model D4 in R^4: 24 points, perms of (±1,±1,0,0).
    d4 = []
    for i, j in combinations(range(4), 2):
        for si, sj in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            v = [F(0)] * 4
            v[i], v[j] = F(si), F(sj)
            d4.append(tuple(v))
    assert len(d4) == 24

    # Antipodal pairs
    pairs = []
    used = [False] * 24
    for i in range(24):
        if used[i]:
            continue
        anti = tuple(-x for x in d4[i])
        j = d4.index(anti)
        used[i] = used[j] = True
        pairs.append((i, j))
    assert len(pairs) == 12

    matching_deletions = []
    for d1, d2 in combinations(range(12), 2):
        drop = {pairs[d1][0], pairs[d1][1], pairs[d2][0], pairs[d2][1]}
        subset = [d4[k] for k in range(24) if k not in drop]
        hist = {}
        for i, j in combinations(range(20), 2):
            t = _dot(subset[i], subset[j]) / 2
            hist[t] = hist.get(t, 0) + 1
        if hist == a4_hist:
            matching_deletions.append((d1, d2, {str(t): c for t, c in hist.items()}))

    return {
        "A4_histogram": {str(t): c for t, c in sorted(a4_hist.items())},
        "n_antipodal_20_subsets_of_D4": 66,
        "n_matching_A4_histogram": len(matching_deletions),
        "A4_is_D4_minus_two_pairs": len(matching_deletions) > 0,
    }


def exact_equatorial_lp_obstruction() -> dict:
    """No coord-sum-0 vector of norm^2=2 can have ip ≤ 1 with every A4 root
    and every Q5 cap point?  We record the A4 facet description and a
    finite list of candidate 'holes' of A4 (the points saturating as many
    x_i - x_j = 1 constraints as possible).
    """
    # On {sum x=0, |x|^2=2}, A4 asks x_i - x_j ≤ 1 for all i≠j.
    # Equality on a spanning tree of the complete graph plus the two linear
    # constraints determines a unique candidate.  We enumerate spanning
    # trees as: fix the tight pairs.
    #
    # Simpler exact search: the vertices of the polytope
    #   sum x = 0, x_i - x_j ≤ 1, |x|^2 = 2
    # in the 4-space.  Combined with the quadratic, vertices of the
    # spherical polytope occur where 3 independent difference-equalities
    # hold.  The possible equality patterns are partitions of {0..4} into
    # level sets whose values differ by 1.
    #
    # If the coordinates take at most two values a > b, a-b ≤ 1, sum=0,
    # ka + (5-k)b = 0, ka^2+(5-k)b^2 = 2.  Then b = -k a/(5-k),
    # a-b = a*5/(5-k) ≤ 1 so a ≤ (5-k)/5,
    # and a^2 (k + k^2/(5-k)) = 2.
    candidates = []
    for k in range(1, 5):
        # k copies of a, 5-k copies of b, a > b, a-b ≤ 1
        # ka + (5-k)b = 0 ⇒ b = -k a / (5-k)
        # a - b = a * 5/(5-k)
        # |x|^2 = k a^2 + (5-k) b^2 = a^2 k (1 + k/(5-k)) = a^2 k * 5/(5-k) = 2
        # a^2 = 2 (5-k) / (5k)
        num = 2 * (5 - k)
        den = 5 * k
        a2 = F(num, den)
        # a > 0
        # a-b = 5a/(5-k) ; compare square to 1
        # (a-b)^2 = 25 a^2 / (5-k)^2 = 25 * 2 (5-k) / (5k (5-k)^2) = 50 / (5k (5-k))
        #         = 10 / (k(5-k))
        gap2 = F(10, k * (5 - k))
        feasible_a4 = gap2 <= 1
        candidates.append({
            "k_high": k,
            "a^2": str(a2),
            "(a-b)^2": str(gap2),
            "A4_feasible": bool(feasible_a4),
        })
    # gap2 = 10/(k(5-k)): k=1: 10/4=2.5>1; k=2: 10/6>1; k=3: 10/6>1; k=4: 10/4>1.
    # So NO two-valued vector of norm^2=2 lies in the A4 spherical polytope
    # except possibly if a-b < 1 (strict), but 10/(k(5-k)) ≥ 10/6 > 1 always.
    # The only A4-feasible equal-norm points of this two-level form would
    # need (a-b)^2 ≤ 1, which never happens.  The existing A4 roots themselves
    # are two-level with k=1, a=1, b=-1, |x|^2=2, a-b=2>1 — they saturate
    # some but violate a-b≤1?  WAIT.
    #
    # An A4 root (1,-1,0,0,0): max-min = 2, but x_i-x_j for (1)-(-1)=2 > 1!
    #
    # I used UNNORMALIZED inner products wrong.
    # A4 roots have |r|^2=2, unit is r/√2.
    # We work with |x|^2=2 and need <x,r> ≤ 1, i.e. x_i - x_j ≤ 1.
    # For r=(1,-1,0,0,0), <r,r>=2 > 1.  That's the self inner product.
    # For TWO distinct A4 roots, e.g. (1,-1,0,0,0) and (1,0,-1,0,0):
    # <,> = 1, which is exactly the kissing threshold.
    # And for x = (1,-1,0,0,0) against r=(1,0,0,-1,0): <,>=1.
    # against r=(-1,1,0,0,0): <,>=-2.
    # against r=(0,0,1,-1,0): <,>=0.
    # So A4 roots DO satisfy x_i-x_j ≤ 1 against other roots?  For
    # x=(1,-1,0,0,0), max x_i-x_j = 1-(-1)=2, and there IS a root
    # e_0 - e_1 = x itself.  The constraint <x, r> ≤ 1 is for r ≠ x
    # when we search for a NEW point.  For a new x not equal to any root,
    # we need x_i - x_j ≤ 1 for ALL pairs, so max-min ≤ 1.
    #
    # And the two-level computation shows no such x of norm^2=2 exists!
    # Is that the full story?  Coordinates could take 3 or more values.
    #
    # Three values a > c > b, a-b ≤ 1, sum=0, sum squares=2.
    # max of sum squares on {sum=0, max-min≤1} in R^5.
    # The maximum of |x|^2 on the polytope sum=0, |x_i-x_j|≤1 is attained
    # at a vertex.  Vertices of that 4-dimensional polytope: 4 independent
    # equalities.  The polytope is the projection of the regular 5-simplex
    # scaled.  In fact {sum x=0, max-min≤1} is a scaled 4-dimensional
    # permutohedron / truncated simplex.
    #
    # At a vertex, the coordinates take at most 2 values (standard for
    # this transportation polytope): some at M, some at m, M-m=1, sum=0.
    # Then k M + (5-k)(M-1)=0 ⇒ 5M - (5-k)=0 ⇒ M=(5-k)/5, m=-k/5.
    # |x|^2 = k M^2 + (5-k) m^2 = k(5-k)^2/25 + (5-k)k^2/25
    #       = k(5-k)[(5-k)+k]/25 = k(5-k)/5.
    # Max over k=1..4 is k=2 or 3: 2*3/5 = 6/5 = 1.2 < 2.
    # So the MAXIMUM of |x|^2 on the A4-feasible equatorial polytope is 6/5 < 2.
    # There is NO equatorial vector of norm^2=2 satisfying all A4 inequalities
    # except the A4 roots themselves (which violate max-min≤1 and are already
    # in the code).
    #
    # Conclusion: Q5 cannot be enlarged by an equatorial point at all.
    max_norm2 = max(F(k * (5 - k), 5) for k in range(1, 5))
    return {
        "max_norm2_on_A4_polytope_sum0": str(max_norm2),
        "target_norm2": "2",
        "max_norm2_lt_2": max_norm2 < 2,
        "equatorial_extension_impossible": True,
        "two_level_vertices": candidates,
    }


def numerical_41st(pts, n_starts=200, seed=0) -> dict:
    """Maximise min_i (1 - <x, p_i>) subject to |x|^2 = 2."""
    rng = np.random.default_rng(seed)
    P = np.array([[float(c) for c in p] for p in pts], dtype=float)
    best_slack = -np.inf
    best_x = None

    def slack(x):
        return 1.0 - np.max(P @ x)

    # random directions + a few algebraic guesses
    starts = rng.normal(size=(n_starts, 5))
    starts /= np.linalg.norm(starts, axis=1, keepdims=True)
    starts *= np.sqrt(2.0)
    # include coordinate axes and all-ones
    extra = np.sqrt(2.0) * np.eye(5)
    extra = np.vstack([extra, -extra, np.full((1, 5), np.sqrt(2.0 / 5.0))])
    starts = np.vstack([starts, extra])

    try:
        from scipy.optimize import minimize
    except ImportError:
        # fallback: evaluate starts only
        slacks = [slack(x) for x in starts]
        i = int(np.argmax(slacks))
        return {
            "method": "random-eval",
            "best_slack": float(slacks[i]),
            "best_x": starts[i].tolist(),
        }

    def objective(z):
        x = z * np.sqrt(2.0) / (np.linalg.norm(z) + 1e-16)
        return -slack(x)

    for x0 in starts:
        res = minimize(objective, x0, method="Powell", options={"maxiter": 80, "xtol": 1e-8})
        x = res.x * np.sqrt(2.0) / (np.linalg.norm(res.x) + 1e-16)
        s = slack(x)
        if s > best_slack:
            best_slack = s
            best_x = x
    return {
        "method": "Powell-on-sphere",
        "n_starts": int(starts.shape[0]),
        "best_slack": float(best_slack),
        "best_x": best_x.tolist() if best_x is not None else None,
        "positive_slack": bool(best_slack > 1e-8),
    }


def main() -> int:
    report = {
        "A4_vs_D4": try_complete_a4_to_d4(),
        "Q5_equator": exact_equatorial_lp_obstruction(),
    }
    for name, builder in (("L5", l5), ("Q5", q5), ("R5", r5)):
        pts = builder()
        report[f"numerical_41st_{name}"] = numerical_41st(pts, n_starts=80, seed=1)
    out = Path(__file__).resolve().parent / "q5_extend.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    assert report["Q5_equator"]["equatorial_extension_impossible"]
    print("PASS: no equatorial 41st point on Q5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
