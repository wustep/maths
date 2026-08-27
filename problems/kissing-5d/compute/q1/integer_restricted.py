#!/usr/bin/env python3
"""Integer distance distributions for T_L5 and T_Q5 at N in {41,42,43,44}.

Real Delsarte on T_L5 is 239925/5456 < 44, so 44 is already excluded there.
T_Q5 is ≈ 44.67, so 44 is allowed by the real relaxation.  This file first
computes, for each (T, N), the real box min/max of each n_t subject to the
Gegenbauer inequalities, then enumerates the integer points in that box
(last coordinate fixed by the pair-count) and tests them exactly.

An empty integer slice is an exact obstruction in that inner-product class.
A nonempty slice is not a construction.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction

T_L5 = [F(-1), F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 2)]
T_Q5 = [F(-1), F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]


def _rows(T, deg):
    polys = gegenbauer_dim5(deg)
    return [[eval_poly(pk, t) for t in T] for pk in polys]


def real_box(T, N, deg=14):
    """min/max of each n_t over the real Delsarte polytope at this N."""
    from scipy.optimize import linprog

    rows = _rows(T, deg)
    m = len(T)
    pairs = comb(N, 2)
    # variables n_0 .. n_{m-1}
    # sum n = pairs
    A_eq = np.ones((1, m))
    b_eq = np.array([float(pairs)])
    A_ub = []
    b_ub = []
    for k, pk in enumerate(rows):
        if k == 0:
            continue
        # N + 2 sum n_t P_k(t) ≥ 0  ⇒  -sum n_t P_k(t) ≤ N/2
        A_ub.append([-float(pk[j]) for j in range(m)])
        b_ub.append(N / 2.0)
    bounds = []
    for t in T:
        if t == F(-1):
            bounds.append((0.0, float(N // 2)))
        else:
            bounds.append((0.0, None))
    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)
    box = []
    feasible = True
    for j in range(m):
        cmin = np.zeros(m)
        cmin[j] = 1.0
        rmin = linprog(cmin, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                       bounds=bounds, method="highs")
        rmax = linprog(-cmin, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                       bounds=bounds, method="highs")
        if (not rmin.success) or (not rmax.success):
            feasible = False
            box.append({"t": str(T[j]), "min": None, "max": None})
        else:
            box.append({
                "t": str(T[j]),
                "min": float(rmin.fun),
                "max": float(-rmax.fun),
            })
    return {"real_feasible": feasible, "box": box, "pairs": pairs, "deg": deg}


def integer_tables(T, deg):
    polys = gegenbauer_dim5(deg)
    rows = []
    for pk in polys:
        vals = [eval_poly(pk, t) for t in T]
        D = 1
        for v in vals:
            D = D * v.denominator // _gcd(D, v.denominator)
        rows.append((D, tuple(int(v * D) for v in vals)))
    return rows


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def delsarte_ok(N, ns, tables):
    for D, coeffs in tables:
        s = N * D + 2 * sum(n * a for n, a in zip(ns, coeffs))
        if s < 0:
            return False
    return True


def enumerate_box(T, N, box, deg=14, pad=1):
    """Integer points in the real box (padded), last n fixed by pair-count."""
    tables = integer_tables(T, deg)
    pairs = comb(N, 2)
    ranges = []
    for j, t in enumerate(T):
        lo = 0
        hi = pairs if t != F(-1) else N // 2
        if box[j]["min"] is not None:
            lo = max(lo, int(np.floor(box[j]["min"])) - pad)
            hi = min(hi, int(np.ceil(box[j]["max"])) + pad)
        ranges.append(range(max(0, lo), hi + 1))
    hits = []
    scanned = 0
    # Recurse on the first m-1 coordinates.
    m = len(T)

    def rec(j, acc, used):
        nonlocal scanned
        if j == m - 1:
            last = pairs - used
            if last < 0 or last not in ranges[j]:
                return
            ns = acc + [last]
            scanned += 1
            if delsarte_ok(N, ns, tables):
                hits.append({str(T[i]): ns[i] for i in range(m)})
            return
        for v in ranges[j]:
            if used + v > pairs:
                continue
            rec(j + 1, acc + [v], used + v)
            if len(hits) >= 3:
                return

    rec(0, [], 0)
    return {"scanned": scanned, "n_hits": len(hits), "hits": hits[:3]}


def main() -> int:
    families = {"T_L5": T_L5, "T_Q5": T_Q5}
    report = {}
    for name, T in families.items():
        entry = {"T": [str(t) for t in T], "N": {}}
        for N in (41, 42, 43, 44):
            print(f"{name} N={N}: real box ...", flush=True)
            boxrec = real_box(T, N)
            print(f"  feasible={boxrec['real_feasible']} box={boxrec['box']}",
                  flush=True)
            if not boxrec["real_feasible"]:
                entry["N"][str(N)] = {
                    **boxrec,
                    "integer": {
                        "scanned": 0,
                        "n_hits": 0,
                        "hits": [],
                        "note": "real Delsarte already empty",
                    },
                }
                continue
            print(f"  enumerating integer box ...", flush=True)
            irec = enumerate_box(T, N, boxrec["box"])
            print(f"  scanned={irec['scanned']} hits={irec['n_hits']}",
                  flush=True)
            entry["N"][str(N)] = {**boxrec, "integer": irec}
        report[name] = entry
    out = Path(__file__).resolve().parent / "integer_restricted.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
