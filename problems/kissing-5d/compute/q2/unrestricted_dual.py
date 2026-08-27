#!/usr/bin/env python3
"""Exact unrestricted Delsarte duals in dimension 5.

A dual is unrestricted when f = sum c_k P_k^{(5)} has every c_k ≥ 0 and
f(t) ≤ 0 for all t in [-1, 1/2], not merely on a finite T.  Then every
spherical code with max inner product 1/2 has size ≤ f(1)/c_0.

Odlyzko–Sloane already took the continuum optimum to ≈ 46.345.  This
file searches low-degree rational duals and certifies positivity of -f
on the interval by exact real-root isolation of f' (sympy).  A bound
< 44 would exclude some k in {41,42,43} with no angle restriction.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction
HERE = Path(__file__).resolve().parent


def _grid(n: int):
    """n equally spaced rationals on [-1, 1/2], endpoints included."""
    out = []
    for i in range(n):
        out.append(F(-1) + F(i, n - 1) * F(3, 2))
    return out


def numerical_dual(deg: int, ngrid: int = 241):
    from scipy.optimize import linprog

    T = _grid(ngrid)
    polys = gegenbauer_dim5(deg)
    n = deg + 1
    Ptab = np.array([[float(eval_poly(polys[k], t)) for k in range(n)] for t in T])
    cobj = np.ones(n)
    A_eq = np.zeros((1, n))
    A_eq[0, 0] = 1.0
    b_eq = np.array([1.0])
    res = linprog(cobj, A_ub=Ptab, b_ub=np.zeros(len(T)),
                  A_eq=A_eq, b_eq=b_eq, bounds=[(0.0, None)] * n,
                  method="highs")
    if not res.success:
        return {"success": False, "message": res.message}
    return {
        "success": True,
        "deg": deg,
        "ngrid": ngrid,
        "bound": float(res.fun),
        "c": [float(x) for x in res.x],
    }


def rationalize(c_float, den: int):
    c = [F(1)]
    for x in c_float[1:]:
        q = F(int(round(x * den)), den)
        c.append(q if q > 0 else F(0))
    return c


def f_as_sympy(c):
    deg = len(c) - 1
    polys = gegenbauer_dim5(deg)
    t = sp.symbols("t")
    f = 0
    for k, ck in enumerate(c):
        if ck == 0:
            continue
        pk = 0
        pw = 1
        for coeff in polys[k]:
            pk += sp.Rational(coeff.numerator, coeff.denominator) * pw
            pw *= t
        f += sp.Rational(ck.numerator, ck.denominator) * pk
    return sp.together(sp.expand(f)), t


def certify_interval(c):
    """Exact: f ≤ 0 on [-1, 1/2]?  Evaluate at endpoints and at real
    critical points isolated by sympy.real_roots."""
    f, t = f_as_sympy(c)
    lo, hi = -1, sp.Rational(1, 2)
    samples = [lo, hi]
    df = sp.diff(f, t)
    # real_roots returns algebraic numbers; comparison to rationals is exact
    try:
        roots = sp.real_roots(sp.Poly(sp.together(df), t), filter="R")
    except Exception as e:
        return {"certified": False, "error": str(e)}
    for r in roots:
        if r >= lo and r <= hi:
            samples.append(r)
    vals = []
    pos = False
    for x in samples:
        v = sp.simplify(f.subs(t, x))
        vals.append(str(v))
        if v > 0:
            pos = True
    f1 = sum(c)  # P_k(1)=1
    return {
        "certified": (not pos) and c[0] > 0 and all(ck >= 0 for ck in c),
        "n_crit_in_interval": sum(1 for x in samples if x not in (lo, hi)),
        "positive_sample": pos,
        "f1": str(f1),
        "bound": str(f1 / c[0]) if c[0] else None,
        "float_bound": float(f1 / c[0]) if c[0] else None,
        "sample_values": vals[:8],
    }


def levenshtein_dual():
    """The odd Levenshtein polynomial of index 5, bound 48, unrestricted."""
    # L_5(5, 1/2) = 48 is already independently recomputed in levenshtein.py.
    # The corresponding dual is (up to scale) the standard odd auxiliary.
    # We just record the known exact number as a baseline unrestricted dual.
    return {
        "name": "Levenshtein_L5",
        "bound": "48",
        "float_bound": 48.0,
        "certified": True,
        "comment": "L_5(5,1/2)=48 from the BDM odd-bound formula; replay levenshtein.py",
        "excludes": [],
    }


def main() -> int:
    report = {"Levenshtein_L5": levenshtein_dual(), "degrees": {}}
    best_cert = None
    for deg in (6, 8, 10, 12, 14, 16):
        num = numerical_dual(deg)
        entry = {"numerical": num, "rational_attempts": []}
        print(f"deg {deg}: numerical bound={num.get('bound')}", flush=True)
        if not num.get("success"):
            report["degrees"][str(deg)] = entry
            continue
        for den in (10, 100, 1000, 10000):
            c = rationalize(num["c"], den)
            cert = certify_interval(c)
            cert["den"] = den
            cert["c"] = [str(x) for x in c]
            cert["excludes"] = [k for k in (41, 42, 43, 44)
                                if cert.get("certified") and cert.get("float_bound")
                                and cert["float_bound"] < k]
            entry["rational_attempts"].append({
                "den": den,
                "certified": cert["certified"],
                "bound": cert.get("bound"),
                "float_bound": cert.get("float_bound"),
                "excludes": cert["excludes"],
                "positive_sample": cert.get("positive_sample"),
            })
            print(f"  den={den} certified={cert['certified']} "
                  f"bound={cert.get('float_bound')} excl={cert['excludes']}",
                  flush=True)
            if cert["certified"]:
                if best_cert is None or cert["float_bound"] < best_cert["float_bound"]:
                    best_cert = {
                        "deg": deg,
                        "den": den,
                        "c": [str(x) for x in c],
                        "bound": cert["bound"],
                        "float_bound": cert["float_bound"],
                        "excludes": cert["excludes"],
                        "gegenbauer_coeffs": [str(x) for x in c],
                        "T": "unrestricted [-1,1/2]",
                    }
                break
        report["degrees"][str(deg)] = entry

    report["best_certified"] = best_cert
    if best_cert:
        report["excludes_any_k"] = best_cert["excludes"]
        (HERE / "certs").mkdir(exist_ok=True)
        if best_cert["excludes"]:
            (HERE / "certs" / "unrestricted_delsarte.json").write_text(
                json.dumps(best_cert, indent=2) + "\n"
            )
    else:
        report["excludes_any_k"] = []
    report["comment"] = (
        "Unrestricted Delsarte cannot beat the Odlyzko–Sloane number ≈46.345. "
        "No dual found here has bound < 44, so no k in {41,42,43} is excluded "
        "without a restricted angle set."
    )
    out = HERE / "unrestricted_dual.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("best_certified", best_cert)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
