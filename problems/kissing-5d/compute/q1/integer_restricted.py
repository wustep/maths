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


def box_volume(ranges):
    v = 1
    for r in ranges:
        v *= max(1, len(r) if not isinstance(r, range) else (r.stop - r.start))
    return v


def enumerate_box(T, N, box, deg=14, pad=1, max_scan=2_000_000):
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
    last_lo, last_hi = ranges[-1].start, ranges[-1].stop - 1
    # After choosing n_0..n_{m-2}, n_{last} = pairs - used must lie in
    # [last_lo, last_hi], so used must lie in [pairs-last_hi, pairs-last_lo].
    used_lo = pairs - last_hi
    used_hi = pairs - last_lo
    hits = []
    scanned = 0
    m = len(T)
    stopped = False

    def rec(j, acc, used):
        nonlocal scanned, stopped
        if stopped:
            return
        if j == m - 1:
            last = pairs - used
            if last < last_lo or last > last_hi:
                return
            ns = acc + [last]
            scanned += 1
            if delsarte_ok(N, ns, tables):
                hits.append({str(T[i]): ns[i] for i in range(m)})
                if len(hits) >= 3:
                    stopped = True
            return
        # remaining after this coordinate: at least the later mins
        later_min = sum(ranges[k].start for k in range(j + 1, m - 1))
        later_max = sum(ranges[k].stop - 1 for k in range(j + 1, m - 1))
        for v in ranges[j]:
            nu = used + v
            # used_so_far + later + last = pairs, last in [last_lo, last_hi]
            if nu + later_min > used_hi:
                continue
            if nu + later_max < used_lo:
                continue
            rec(j + 1, acc + [v], nu)
            if stopped:
                return

    rec(0, [], 0)
    return {
        "scanned": scanned,
        "n_hits": len(hits),
        "hits": hits[:3],
        "skipped": False,
        "used_window": [used_lo, used_hi],
    }


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    families = {"T_L5": T_L5, "T_Q5": T_Q5}
    if only:
        families = {k: v for k, v in families.items() if k in only}
    report = {}
    out = Path(__file__).resolve().parent / "integer_restricted.json"
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
            if name == "T_Q5" and N < 44:
                irec = {
                    "scanned": 0,
                    "n_hits": 0,
                    "hits": [],
                    "skipped": True,
                    "note": "box too large; not an emptiness proof. N=44 is searched in integer_q5_44.c",
                }
                print("  skipped (use integer_q5_44.c for N=44)", flush=True)
            else:
                print(f"  enumerating integer box ...", flush=True)
                irec = enumerate_box(T, N, boxrec["box"])
                print(f"  scanned={irec['scanned']} hits={irec['n_hits']} "
                      f"hits={irec.get('hits')}", flush=True)
            entry["N"][str(N)] = {**boxrec, "integer": irec}
            report[name] = entry
            out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
