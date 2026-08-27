#!/usr/bin/env python3
"""Further exact unrestricted dual attempts for τ5.

q4 already has exact S_k^5 over Q and failed to certify a value < 44.
This file retries a short list of 1-point Delsarte rationalizations,
then two exact attempts q4 did not run:

  1. (t − 1/2) q(t)^2 with q of degree 3 or 4 over Q, certified on
     [-1, 1/2] by q2/unrestricted_dual.certify_interval.  q2 already
     tried a few cubic monomials; the list below is a different set.
  2. A tiny interpolation on T_{Q_5} \\ {-1}.  f may be positive at
     the antipode.  That certificate is *not* unrestricted (residue).

A numerical SDP without an exact positivity certificate is residue.
Mittelmann–Vallentin s_14(5)=44.998… is the published upper bound.
1-point Delsarte cannot beat Odlyzko–Sloane ≈ 46.34.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q2 = ROOT / "q2"
Q4 = ROOT / "q4"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Q2))
sys.path.insert(0, str(Q4))

from delsarte import eval_poly, gegenbauer_dim5  # noqa: E402
from unrestricted_dual import (  # noqa: E402  # q2
    certify_interval,
    expand_gegenbauer,
    rationalize,
)

F = Fraction


def numerical_delsarte(deg: int, ngrid: int = 241):
    import numpy as np
    from scipy.optimize import linprog

    T = [F(-1) + F(i, ngrid - 1) * F(3, 2) for i in range(ngrid)]
    polys = gegenbauer_dim5(deg)
    n = deg + 1
    Ptab = [[float(eval_poly(polys[k], t)) for k in range(n)] for t in T]
    res = linprog(
        [1.0] * n,
        A_ub=Ptab,
        b_ub=[0.0] * len(T),
        A_eq=[[1.0] + [0.0] * deg],
        b_eq=[1.0],
        bounds=[(0.0, None)] * n,
        method="highs",
    )
    return {
        "success": bool(res.success),
        "value": None if not res.success else float(res.fun),
        "c": None if not res.success else [float(x) for x in res.x],
    }


def try_rationalize(deg: int, dens):
    rec = numerical_delsarte(deg)
    out = {"numerical": rec["value"], "trials": []}
    if not rec["success"]:
        return out
    for den in dens:
        c = rationalize(rec["c"], den)
        cert = certify_interval(c)
        out["trials"].append({
            "den": den,
            "certified": bool(cert.get("certified")),
            "bound": cert.get("bound"),
            "float_bound": cert.get("float_bound"),
            "error": cert.get("error"),
        })
    return out


def _times_half_q2(q):
    """Monomial coefficients of (t − 1/2) q(t)^2."""
    q2 = [F(0)] * (2 * len(q) - 1)
    for i, x in enumerate(q):
        for j, y in enumerate(q):
            q2[i + j] += x * y
    mono = [F(0)] * (len(q2) + 1)
    for i, x in enumerate(q2):
        mono[i] += x * F(-1, 2)
        mono[i + 1] += x
    return mono


def ansatz_q34():
    """Short (t − 1/2) q^2 list, deg q ∈ {3, 4}, not the q2 cubics.

    q2 already tried (1,0,0,1), (1,2,0,1), (1,0,2,1) and the deg-2
    Levenshtein-like [1/3, 17/6, 10/3].  The first cubic below is
    P_0 + (5/2) P_1 + (8/3) P_2 + P_3 in the monomial basis.
    """
    qs = (
        [F(1, 3), F(7, 4), F(10, 3), F(7, 4)],
        [F(1), F(3), F(3), F(1)],
        [F(1), F(3), F(4), F(2)],
        [F(1), F(0), F(0), F(0), F(1)],
        [F(1), F(2), F(2), F(2), F(1)],
    )
    jobs = []
    for q in qs:
        c = expand_gegenbauer(_times_half_q2(q))
        rec = {
            "q": [str(x) for x in q],
            "deg_q": len(q) - 1,
            "c": [str(x) for x in c],
            "c_k_nonneg": all(x >= 0 for x in c),
            "unrestricted": True,
        }
        if rec["c_k_nonneg"] and c and c[0] > 0:
            cert = certify_interval(c)
            rec["certified"] = bool(cert.get("certified"))
            rec["bound"] = cert.get("bound")
            rec["float_bound"] = cert.get("float_bound")
            rec["n_squarefree_roots"] = cert.get("n_squarefree_roots")
        else:
            rec["certified"] = False
            rec["bound"] = None
            rec["float_bound"] = None
        jobs.append(rec)
    return jobs


def _ge_q(A, b):
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


def gapped_q5_interpolation():
    """Exact interpolant vanishing on T_{Q_5} \\ {-1}.

    NOT unrestricted: f is allowed to be (and here is) positive at t = −1.
    A dual that is positive on a gap does not bound every kissing code.
    """
    T_zero = [F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
    free = [1, 2, 3, 4, 5, 6]
    deg = 6
    polys = gegenbauer_dim5(deg)
    A = [[eval_poly(polys[k], t) for k in free] for t in T_zero]
    b = [-F(1)] * len(T_zero)
    x = _ge_q(A, b)
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val

    def f_at(t):
        return sum(ck * eval_poly(polys[k], t) for k, ck in enumerate(c) if ck)

    f_gap = f_at(F(-1))
    f_T = {str(t): str(f_at(t)) for t in T_zero}
    c_ok = all(ck >= 0 for ck in c) and c[0] > 0
    on_T = all(f_at(t) <= 0 for t in T_zero)
    bound = sum(c) / c[0]
    return {
        "name": "Q5_minus_antipode",
        "unrestricted": False,
        "label": "NOT unrestricted — f may be positive on the antipodal gap",
        "T_zero": [str(t) for t in T_zero],
        "c": [str(ck) for ck in c],
        "c_k_nonneg": c_ok,
        "f_le_0_on_T_zero": on_T,
        "f_at_minus_1": str(f_gap),
        "f_at_minus_1_float": float(f_gap),
        "f_on_T_zero": f_T,
        "bound_on_T_zero": str(bound),
        "float_bound_on_T_zero": float(bound),
        "certified_unrestricted": False,
        "comment": (
            "Exact interpolation on the published Q5 angles except t=−1.  "
            "Positive at the antipode, so this is not an unrestricted dual "
            "and does not move τ5."
        ),
    }


def _best_unrestricted(report):
    best = None
    for key in ("delsarte_deg12", "delsarte_deg16"):
        for t in report[key]["trials"]:
            if t["certified"] and t["bound"] is not None:
                b = F(t["bound"])
                if best is None or b < best[0]:
                    best = (b, t["bound"], t.get("float_bound"), key)
    for rec in report["ansatz_q34"]:
        if rec.get("certified") and rec.get("bound") is not None:
            b = F(rec["bound"])
            if best is None or b < best[0]:
                best = (b, rec["bound"], rec.get("float_bound"), "ansatz_q34")
    return best


def main() -> int:
    report = {
        "delsarte_deg12": try_rationalize(12, (100, 1000, 10000)),
        "delsarte_deg16": try_rationalize(16, (1000, 10000)),
        "ansatz_q34": ansatz_q34(),
        "gapped_interpolation": gapped_q5_interpolation(),
        "comment": (
            "1-point continuum Delsarte cannot go below Odlyzko–Sloane "
            "~46.34.  Degree-3/4 (t-1/2)q^2 duals that certify sit near "
            "52 or higher.  The Q5-minus-antipode interpolant is NOT "
            "unrestricted.  No certified unrestricted dual below 44."
        ),
    }
    best = _best_unrestricted(report)
    report["best_certified"] = None if best is None else best[1]
    report["best_certified_float"] = None if best is None else best[2]
    report["best_certified_source"] = None if best is None else best[3]
    report["below_44"] = bool(best is not None and best[0] < 44)
    (HERE / "dual_more.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "num12": report["delsarte_deg12"]["numerical"],
        "num16": report["delsarte_deg16"]["numerical"],
        "best_certified": report["best_certified"],
        "best_certified_float": report["best_certified_float"],
        "best_certified_source": report["best_certified_source"],
        "below_44": report["below_44"],
        "gapped_unrestricted": report["gapped_interpolation"]["unrestricted"],
        "gapped_f_at_minus_1": report["gapped_interpolation"]["f_at_minus_1"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
