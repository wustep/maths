#!/usr/bin/env python3
"""Integer distance-distribution search for T = {-1, -1/2, 0, 1/2}.

The real Delsarte relaxation allows N ≤ 42.  Realizable codes have
n_t = N A_t / 2 an integer (unordered pairs) with sum_t n_t = C(N,2)
and n_{-1} ≤ floor(N/2).  This file enumerates those integer points for
N in {41,42,43,44} and tests the Gegenbauer inequalities exactly.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction


def _tables(deg: int):
    """Integer tables for N + 2 Σ n_t P_k(t) ≥ 0.

    For each k we store (D, a_{-1}, a_{-1/2}, a_0, a_{1/2}) with
    P_k(t) = a_t / D, so the inequality is
        N D + 2 (n_{-1} a_{-1} + ...) ≥ 0.
    """
    polys = gegenbauer_dim5(deg)
    ts = [F(-1), F(-1, 2), F(0), F(1, 2)]
    rows = []
    for pk in polys:
        vals = [eval_poly(pk, t) for t in ts]
        dens = [v.denominator for v in vals]
        D = 1
        for d in dens:
            D = D * d // math_gcd(D, d)
        coeffs = tuple(int(v * D) for v in vals)
        rows.append((D,) + coeffs)
    return rows


def math_gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def search_N(N: int, deg: int = 8):
    rows = _tables(deg)
    pairs = comb(N, 2)
    max_m1 = N // 2
    for n_m1 in range(0, max_m1 + 1):
        rest = pairs - n_m1
        for n_mh in range(0, rest + 1):
            # n_h + n0 = rest - n_mh; scan n_h
            top = rest - n_mh
            for n_h in range(0, top + 1):
                n0 = top - n_h
                ok = True
                for D, am1, amh, a0, ah in rows:
                    s = N * D + 2 * (n_m1 * am1 + n_mh * amh + n0 * a0 + n_h * ah)
                    if s < 0:
                        ok = False
                        break
                if ok:
                    return [{
                        "n_{-1}": n_m1,
                        "n_{-1/2}": n_mh,
                        "n_0": n0,
                        "n_{1/2}": n_h,
                    }]
    return []


def search_N_cap_antipodes(N: int, max_m1: int, deg: int = 8):
    rows = _tables(deg)
    pairs = comb(N, 2)
    for n_m1 in range(0, max_m1 + 1):
        rest = pairs - n_m1
        for n_mh in range(0, rest + 1):
            top = rest - n_mh
            for n_h in range(0, top + 1):
                n0 = top - n_h
                ok = True
                for D, am1, amh, a0, ah in rows:
                    s = N * D + 2 * (n_m1 * am1 + n_mh * amh + n0 * a0 + n_h * ah)
                    if s < 0:
                        ok = False
                        break
                if ok:
                    return [{
                        "n_{-1}": n_m1,
                        "n_{-1/2}": n_mh,
                        "n_0": n0,
                        "n_{1/2}": n_h,
                    }]
    return []


def main() -> int:
    report = {}
    for N in (40, 41, 42, 43, 44):
        hits = search_N(N)
        report[str(N)] = {
            "n_hits_recorded": len(hits),
            "first_hit": hits[0] if hits else None,
            "delsarte_integer_feasible": bool(hits),
        }
        print(f"N={N}: integer-Delsarte feasible={bool(hits)} hit={hits[:1]}")
    # For N=41, check whether any feasible distribution has fewer than
    # 20 antipodal pairs (those would not contain a 40-point T_D5 subset).
    print("scanning N=41 with n_{-1} ≤ 19 ...")
    hits_small = search_N_cap_antipodes(41, 19)
    report["41_n_{-1}_le_19"] = {
        "feasible": bool(hits_small),
        "first_hit": hits_small[0] if hits_small else None,
    }
    print("N=41 n_{-1}≤19 feasible=", bool(hits_small))
    out = Path(__file__).resolve().parent / "integer_d5.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
