#!/usr/bin/env python3
"""Exact rational Delsarte duals for finite inner-product sets in dimension 5.

The numerical L5 dual of degree 9 uses only c0,c1,c2,c3,c4,c9 and vanishes
on T \\ {-1}.  We solve that interpolation problem over Q and obtain a
fully exact bound.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction


def ge_q(A, b):
    """Solve A x = b over Q.  A is n×n list of Fractions, b length n."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            raise ValueError("singular")
        M[col], M[pivot] = M[pivot], M[col]
        piv = M[col][col]
        M[col] = [v / piv for v in M[col]]
        for r in range(n):
            if r == col:
                continue
            fac = M[r][col]
            if fac == 0:
                continue
            M[r] = [M[r][k] - fac * M[col][k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


def eval_f(c, polys, t):
    return sum(ck * eval_poly(polys[k], t) for k, ck in enumerate(c) if ck)


def certify_dual(c, T, name):
    deg = len(c) - 1
    polys = gegenbauer_dim5(deg)
    fT = {}
    ok_T = True
    for t in T:
        val = eval_f(c, polys, t)
        fT[str(t)] = str(val)
        if val > 0:
            ok_T = False
    f1 = eval_f(c, polys, F(1))
    f0 = c[0]
    bound = f1 / f0
    nonneg = all(ck >= 0 for ck in c)
    return {
        "name": name,
        "c": [str(ck) for ck in c],
        "f_on_T": fT,
        "f(1)": str(f1),
        "f0": str(f0),
        "bound": str(bound),
        "float_bound": float(bound),
        "c_k_nonneg": nonneg,
        "f_le_0_on_T": ok_T,
        "certified": bool(nonneg and ok_T and f0 > 0),
        "excludes": [k for k in (41, 42, 43, 44) if nonneg and ok_T and bound < k],
    }


def l5_interpolating_dual():
    T_zero = [F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 2)]
    T = [F(-1)] + T_zero
    free = [1, 2, 3, 4, 9]  # c0 fixed to 1
    deg = 9
    polys = gegenbauer_dim5(deg)
    A = []
    b = []
    for t in T_zero:
        row = [eval_poly(polys[k], t) for k in free]
        A.append(row)
        # f(t) = c0 P0(t) + sum_free = 0, P0=1
        b.append(-F(1))
    x = ge_q(A, b)
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val
    return certify_dual(c, T, "L5_interp_c0c1c2c3c4c9")


def d5_deg6_dual():
    """Numerical dual suggested c2=28/3, c4=32/3, c5=1991/100-ish, c1=1.088...

    Force f=0 on {-1,-1/2,0,1/2} with a short support and see what N we get.
    Four zeros, so four free coeffs besides c0?  That would overdetermine
    if we also fix c0.  Use free = c1,c2,c4,c5 (the deg-6 numerical support
    without the zeros).
    """
    T = [F(-1), F(-1, 2), F(0), F(1, 2)]
    free = [1, 2, 4, 5]
    deg = 5
    polys = gegenbauer_dim5(deg)
    A = []
    b = []
    for t in T:
        row = [eval_poly(polys[k], t) for k in free]
        A.append(row)
        b.append(-F(1))
    try:
        x = ge_q(A, b)
    except ValueError:
        return {"name": "D5_interp", "certified": False, "error": "singular"}
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val
    return certify_dual(c, T, "D5_interp_c0c1c2c4c5")


def d5_even_dual():
    """Even polynomial vanishing at -1/2, 0, 1/2 (auto at the negatives of
    those among {-1,-1/2,0,1/2} except -1).  Free c2,c4,c6 with c0=1.
    """
    T = [F(-1), F(-1, 2), F(0), F(1, 2)]
    zeros = [F(-1, 2), F(0), F(1, 2)]
    free = [2, 4, 6]
    deg = 6
    polys = gegenbauer_dim5(deg)
    A = []
    b = []
    for t in zeros:
        row = [eval_poly(polys[k], t) for k in free]
        A.append(row)
        b.append(-F(1))
    try:
        x = ge_q(A, b)
    except ValueError:
        return {"name": "D5_even_c0c2c4c6", "certified": False, "error": "singular"}
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val
    return certify_dual(c, T, "D5_even_c0c2c4c6")


def integer_distance_lp(T, N, deg=12):
    """Feasibility of a *realizable* distance distribution at size N.

    A_t * N is an even integer (ordered-pair count).  We search over
    integer n_t = N A_t / 2 (unordered pairs) with sum n_t = C(N,2)
    and n_{-1} ≤ N/2, then test Delsarte.  For |T| small and N~40 this
    is still a large knapsack; we only do a sliced search when |T|≤4
    by looping n_{-1} and using the LP-suggested ratios as a centre.
    Here we just evaluate the Delsarte cone on the *rounded* LP
    distribution and on the D5-like proportional one.
    """
    from math import comb

    polys = gegenbauer_dim5(deg)
    pairs = comb(N, 2)
    # D5-like: A_{-1}=1, A_{1/2}=A_{-1/2}, rest on 0.
    reports = []
    if F(-1) in T and N % 2 == 0:
        n_m1 = N // 2
        rest = pairs - n_m1
        # try n_{1/2} = n_{-1/2} near 12*N/2 = 6N, i.e. n = 6N
        # A = 2n/N so A_{1/2}=12 ⇒ n=6N
        candidates = []
        if F(-1, 2) in T and F(1, 2) in T and F(0) in T:
            for n_half in range(5 * N, 8 * N + 1):
                n_mh = n_half  # force symmetry
                n0 = rest - n_half - n_mh
                if n0 < 0:
                    continue
                A = {
                    F(-1): F(2 * n_m1, N),
                    F(-1, 2): F(2 * n_mh, N),
                    F(0): F(2 * n0, N),
                    F(1, 2): F(2 * n_half, N),
                }
                ok = True
                vals = []
                for k in range(deg + 1):
                    s = eval_poly(polys[k], F(1))
                    for t, at in A.items():
                        s += at * eval_poly(polys[k], t)
                    vals.append(s)
                    if s < 0:
                        ok = False
                if ok:
                    candidates.append({
                        "n": {str(t): int(2 * at * N / 2) for t, at in A.items()},
                        "A": {str(t): str(at) for t, at in A.items()},
                        "delsarte_ok": True,
                    })
                    break
            reports.append({
                "N": N,
                "symmetric_half_search_first_hit": candidates[:1],
                "any_symmetric_hit": bool(candidates),
            })
    return reports


def main() -> int:
    report = {
        "L5_exact_dual": l5_interpolating_dual(),
        "D5_interp_dual": d5_deg6_dual(),
        "D5_even_dual": d5_even_dual(),
        "D5_integer_N42": integer_distance_lp(
            [F(-1), F(-1, 2), F(0), F(1, 2)], 42
        ),
        "D5_integer_N44": integer_distance_lp(
            [F(-1), F(-1, 2), F(0), F(1, 2)], 44
        ),
    }
    out = Path(__file__).resolve().parent / "exact_duals.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for key in ("L5_exact_dual", "D5_interp_dual", "D5_even_dual"):
        r = report[key]
        print(f"{key}: certified={r.get('certified')} bound={r.get('float_bound')} "
              f"excludes={r.get('excludes')}")
        if r.get("c_k_nonneg") is False:
            print("  c=", r.get("c"))
        if r.get("f_le_0_on_T") is False:
            print("  fT=", r.get("f_on_T"))
    print("D5 integer N=42", report["D5_integer_N42"])
    print("D5 integer N=44", report["D5_integer_N44"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
