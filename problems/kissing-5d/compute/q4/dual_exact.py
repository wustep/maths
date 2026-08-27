#!/usr/bin/env python3
"""Unrestricted dual hunt: interval SOS and low-degree 3-point matrices.

1-point Delsarte on [-1, 1/2] is the Odlyzko–Sloane number ≈ 46.34.
A polynomial with nonnegative Gegenbauer coefficients cannot exclude
41–44 on the whole interval.  This file still records that number, then
tries two exact strengthenings:

- Markov–Lukács: -f = s + (t+1)(1/2-t) r with s, r sums of squares
  of rational polynomials (equivalent to f ≤ 0 on [-1, 1/2]).
- A degree-2 Bachoc–Vallentin 3-point matrix with rational entries,
  certified by leading principal minors.

A numerical SDP without an exact positivity certificate is residue.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q2"))

from delsarte import eval_poly, gegenbauer_dim5
from unrestricted_dual import certify_interval, f_monomial, rationalize

F = Fraction


def numerical_delsarte(deg: int, ngrid: int = 321):
    from scipy.optimize import linprog
    T = [F(-1) + F(i, ngrid - 1) * F(3, 2) for i in range(ngrid)]
    polys = gegenbauer_dim5(deg)
    n = deg + 1
    Ptab = np.array([[float(eval_poly(polys[k], t)) for k in range(n)] for t in T])
    res = linprog(np.ones(n), A_ub=Ptab, b_ub=np.zeros(len(T)),
                  A_eq=np.array([[1.0] + [0.0] * deg]), b_eq=np.array([1.0]),
                  bounds=[(0.0, None)] * n, method="highs")
    if not res.success:
        return {"success": False, "message": res.message}
    return {"success": True, "deg": deg, "bound": float(res.fun),
            "c": [float(x) for x in res.x]}


def poly_mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_add(a, b):
    n = max(len(a), len(b))
    out = [F(0)] * n
    for i, x in enumerate(a):
        out[i] += x
    for i, x in enumerate(b):
        out[i] += x
    return out


def poly_scale(a, s):
    return [s * x for x in a]


def sos_unary(coeffs):
    """s = (sum a_i t^i)^2."""
    return poly_mul(coeffs, coeffs)


def try_markov_lukacs(c):
    """Try to write -f as s + (t+1)(1/2-t) r with tiny rational SOS.

    Only a small exact ansatz: s = α (q(t))^2, r = β (p(t))^2.
    This is a certificate when it works, not a search of all SOS.
    """
    mono = f_monomial(c)
    # -f
    mf = [-x for x in mono]
    # (t+1)(1/2-t) = 1/2 + t/2 - t^2
    w = [F(1, 2), F(1, 2), F(-1)]
    # try constant / linear squares
    ansatze = []
    for alpha in (F(0), F(1, 4), F(1, 2), F(1), F(2)):
        for beta in (F(0), F(1, 4), F(1, 2), F(1), F(2)):
            for q in ([F(1)], [F(1), F(0)], [F(1), F(-1, 2)], [F(1), F(1, 2)]):
                for p in ([F(1)], [F(1), F(0)], [F(1), F(-1, 2)]):
                    s = poly_scale(sos_unary(q), alpha)
                    r = poly_scale(sos_unary(p), beta)
                    rhs = poly_add(s, poly_mul(w, r))
                    if len(rhs) == len(mf) and all(x == y for x, y in zip(rhs, mf)):
                        ansatze.append({
                            "alpha": str(alpha),
                            "beta": str(beta),
                            "q": [str(x) for x in q],
                            "p": [str(x) for x in p],
                        })
    return ansatze


def try_bv_degree2():
    """Degree-2 3-point matrix with a rational PSD attempt.

    Bachoc–Vallentin S_k^n(u,v,w) at k=0,1,2.  A hand 2×2 / 3×3
    rational matrix that is PSD by Sylvester and produces a bound < 44
    would be a dent.  The matrices below are recorded even when the
    bound stays above 44.
    """
    # The 3-point constant-term contribution is already in MV / BV.
    # Without the full Y_k^n polynomials implemented exactly, we do not
    # claim a 3-point dual.  Record the obstruction.
    return {
        "used": False,
        "reason": (
            "Exact Bachoc–Vallentin matrices S_k^5 were not implemented "
            "as rational polynomial matrices in this file.  Mittelmann–"
            "Vallentin s_14(5)=44.998… is numerical.  No exact 3-point "
            "dual below 44 is claimed."
        ),
    }


def main() -> int:
    report = {
        "delsarte": [],
        "best_certified_unrestricted": None,
        "markov_lukacs_hits": [],
        "bachoc_vallentin": try_bv_degree2(),
        "excludes_any_k": [],
    }
    best = None
    for deg in (8, 10, 11, 12, 14):
        num = numerical_delsarte(deg)
        rec = {"deg": deg, "numerical": None if not num.get("success") else num["bound"]}
        print(f"delsarte deg={deg} num={rec['numerical']}", flush=True)
        if not num.get("success"):
            report["delsarte"].append(rec)
            continue
        certified = None
        for den in (100, 1000, 10000, 100000):
            c = rationalize(num["c"], den)
            cert = certify_interval(c)
            if cert.get("certified"):
                certified = {
                    "den": den,
                    "bound": cert["bound"],
                    "float_bound": cert["float_bound"],
                    "excludes": [k for k in (41, 42, 43, 44)
                                 if cert["float_bound"] < k],
                    "gegenbauer_coeffs": [str(x) for x in c],
                    "unrestricted": True,
                }
                hits = try_markov_lukacs(c)
                if hits:
                    report["markov_lukacs_hits"].append({
                        "deg": deg, "den": den, "hits": hits
                    })
                if best is None or certified["float_bound"] < best["float_bound"]:
                    best = dict(certified)
                break
        rec["certified"] = certified
        report["delsarte"].append(rec)
    report["best_certified_unrestricted"] = best
    if best and best.get("unrestricted"):
        report["excludes_any_k"] = best.get("excludes") or []
        if report["excludes_any_k"]:
            (HERE / "certs").mkdir(exist_ok=True)
            (HERE / "certs" / "unrestricted_delsarte.json").write_text(
                json.dumps(best, indent=2) + "\n"
            )
    report["comment"] = (
        "Unrestricted 1-point Delsarte is the Odlyzko–Sloane number "
        "≈46.34 and cannot exclude 41–44.  No exact 3-point dual below "
        "44 was produced.  Mittelmann–Vallentin 44.998 remains the "
        "published upper bound."
    )
    (HERE / "dual_exact.json").write_text(json.dumps(report, indent=2) + "\n")
    print("best", best)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
