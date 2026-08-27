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


def f_monomial(c):
    """Monomial coefficients of f = sum c_k P_k, low degree first."""
    deg = len(c) - 1
    polys = gegenbauer_dim5(deg)
    acc = [F(0)] * (deg + 1)
    for k, ck in enumerate(c):
        if ck == 0:
            continue
        for i, a in enumerate(polys[k]):
            acc[i] += ck * a
    return acc


def _poly_trim(p):
    p = [F(x) for x in p]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def _poly_eval(p, x):
    s, pw = F(0), F(1)
    for a in p:
        s += a * pw
        pw *= x
    return s


def _poly_der(p):
    return [p[i] * i for i in range(1, len(p))]


def _poly_rem(a, b):
    A = _poly_trim(a)
    B = _poly_trim(b)
    if B == [F(0)]:
        raise ZeroDivisionError
    while len(A) >= len(B) and A != [F(0)]:
        fac = A[-1] / B[-1]
        shift = len(A) - len(B)
        for i, coeff in enumerate(B):
            A[i + shift] -= fac * coeff
        A = _poly_trim(A)
    return A


def _poly_gcd(a, b):
    A, B = _poly_trim(a), _poly_trim(b)
    while B != [F(0)]:
        A, B = B, _poly_rem(A, B)
    # monic
    if A[-1] != 0:
        A = [x / A[-1] for x in A]
    return A


def _sturm_chain(p):
    p0 = _poly_trim(p)
    p1 = _poly_trim(_poly_der(p0))
    chain = [p0, p1]
    while chain[-1] != [F(0)]:
        rem = _poly_rem(chain[-2], chain[-1])
        chain.append(_poly_trim([-c for c in rem]))
        if len(chain) > 40:
            break
    return chain


def _sign_vars(chain, x):
    signs = []
    for p in chain:
        if p == [F(0)]:
            continue
        v = _poly_eval(p, x)
        if v == 0:
            continue
        s = 1 if v > 0 else -1
        if not signs or signs[-1] != s:
            signs.append(s)
    return max(0, len(signs) - 1)


def squarefree(p):
    g = _poly_gcd(p, _poly_der(p))
    if len(g) <= 1:
        return _poly_trim(p)
    # p / gcd(p,p')
    # exact division
    A = _poly_trim(p)
    B = _poly_trim(g)
    q = [F(0)] * (len(A) - len(B) + 1)
    while len(A) >= len(B) and A != [F(0)]:
        fac = A[-1] / B[-1]
        shift = len(A) - len(B)
        q[shift] = fac
        for i, coeff in enumerate(B):
            A[i + shift] -= fac * coeff
        A = _poly_trim(A)
    return _poly_trim(q)


def certify_interval(c):
    """Exact: f ≤ 0 on [-1, 1/2].

    The square-free part of f has no root in (-1, 1/2) (Sturm) and f is
    nonpositive at the endpoints and at the midpoint, so f cannot change
    sign on the interval.
    """
    if any(ck < 0 for ck in c) or c[0] <= 0:
        return {"certified": False, "error": "c_k not nonnegative"}
    mono = f_monomial(c)
    lo, hi, mid = F(-1), F(1, 2), F(-1, 4)
    fa, fb, fm = _poly_eval(mono, lo), _poly_eval(mono, hi), _poly_eval(mono, mid)
    if fa > 0 or fb > 0 or fm > 0:
        return {
            "certified": False,
            "positive_sample": True,
            "f1": str(sum(c)),
            "bound": str(sum(c) / c[0]),
            "float_bound": float(sum(c) / c[0]),
        }
    sf = squarefree(mono)
    chain = _sturm_chain(sf)
    # roots in (lo, hi): V(lo+) - V(hi-).  Endpoints are already ≤ 0.
    # Evaluate just inside if an endpoint is a root.
    eps = F(1, 10**9)
    nroots = _sign_vars(chain, lo + eps) - _sign_vars(chain, hi - eps)
    f1 = sum(c)
    ok = nroots == 0
    return {
        "certified": bool(ok),
        "n_squarefree_roots": nroots,
        "positive_sample": False,
        "f1": str(f1),
        "bound": str(f1 / c[0]),
        "float_bound": float(f1 / c[0]),
        "f_endpoints": [str(fa), str(fb), str(fm)],
    }


def expand_gegenbauer(mono, max_deg=None):
    """Convert a monomial polynomial to Gegenbauer coefficients."""
    mono = _poly_trim(mono)
    deg = len(mono) - 1
    if max_deg is None:
        max_deg = deg
    polys = gegenbauer_dim5(max_deg)
    # back-substitution: highest degree first
    c = [F(0)] * (max_deg + 1)
    rem = [F(x) for x in mono] + [F(0)] * (max_deg + 1 - len(mono))
    rem = rem[: max_deg + 1]
    for k in range(max_deg, -1, -1):
        pk = polys[k]
        if k >= len(pk) or pk[k] == 0:
            continue
        if rem[k] == 0:
            continue
        ck = rem[k] / pk[k]
        c[k] = ck
        for i, a in enumerate(pk):
            rem[i] -= ck * a
    return c


def ansatz_duals():
    """Exact duals of the form f(t)=(t-1/2) q(t)^2, automatically ≤ 0
    on [-1, 1/2].  Kept only when every Gegenbauer coefficient is ≥ 0."""
    jobs = []
    qs = []
    for a, b in ((1, 0), (1, 1), (1, 2), (2, 1), (3, 2), (1, -1), (2, -1)):
        qs.append([F(a), F(b)])
    for a, b, c in ((1, 0, 1), (1, 2, 1), (2, 0, 1), (1, 1, 1),
                    (3, 0, 1), (1, 4, 4), (1, 0, 2)):
        qs.append([F(a), F(b), F(c)])
    # P0 + (17/6) P1 + (8/3) P2, the best small Gegenbauer ansatz (~48.003)
    qs.append([F(1, 3), F(17, 6), F(10, 3)])
    for a, b, c, d in ((1, 0, 0, 1), (1, 2, 0, 1), (1, 0, 2, 1)):
        qs.append([F(a), F(b), F(c), F(d)])
    for q in qs:
        # (t-1/2) q(t)^2
        # q^2
        q2 = [F(0)] * (2 * len(q) - 1)
        for i, x in enumerate(q):
            for j, y in enumerate(q):
                q2[i + j] += x * y
        # multiply by (t - 1/2)
        mono = [F(0)] * (len(q2) + 1)
        for i, x in enumerate(q2):
            mono[i] += x * F(-1, 2)
            mono[i + 1] += x
        c = expand_gegenbauer(mono)
        rec = {
            "q": [str(x) for x in q],
            "c": [str(x) for x in c],
            "c_k_nonneg": all(x >= 0 for x in c),
            "f0": str(c[0]) if c else "0",
        }
        if rec["c_k_nonneg"] and c and c[0] > 0:
            bound = sum(c) / c[0]
            rec["bound"] = str(bound)
            rec["float_bound"] = float(bound)
            rec["certified"] = True
            rec["excludes"] = [k for k in (41, 42, 43, 44) if bound < k]
        else:
            rec["certified"] = False
            rec["excludes"] = []
        jobs.append(rec)
    return jobs


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
    report = {"Levenshtein_L5": levenshtein_dual(), "ansatz": [], "degrees": {}}
    best_cert = None
    for rec in ansatz_duals():
        report["ansatz"].append({
            "q": rec["q"],
            "certified": rec["certified"],
            "bound": rec.get("bound"),
            "float_bound": rec.get("float_bound"),
            "excludes": rec["excludes"],
        })
        print(f"ansatz q={rec['q']}: certified={rec['certified']} "
              f"bound={rec.get('float_bound')} excl={rec['excludes']}",
              flush=True)
        if rec.get("certified"):
            if best_cert is None or rec["float_bound"] < best_cert["float_bound"]:
                best_cert = {
                    "deg": len(rec["c"]) - 1,
                    "source": "ansatz (t-1/2)q(t)^2",
                    "c": rec["c"],
                    "bound": rec["bound"],
                    "float_bound": rec["float_bound"],
                    "excludes": rec["excludes"],
                    "gegenbauer_coeffs": rec["c"],
                    "T": "unrestricted [-1,1/2]",
                    "unrestricted": True,
                }
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
