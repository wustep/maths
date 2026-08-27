#!/usr/bin/env python3
"""Unrestricted Delsarte duals with a forced gap around t = -1.

A 41-point code has an odd number of points, so it cannot be a union of
antipodal pairs.  The integer identity n_{-1} = N A_{-1}/2 still allows
n_{-1} <= 20.  The case n_{-1} = 20 is a 40-point antipodal code plus one
point; those 40 equal-length roots in rank <= 5 are D5, whose polar has
max |x|^2 = 5/4 < 2.  So every 41-point kissing code has n_{-1} <= 19
and, more usefully for a dual, *some* codes of size 41–44 may be forced
off a neighbourhood of t = -1.

This file does *not* claim that geometric gap.  It only asks: if one
requires f <= 0 on [-1+δ, 1/2] rather than on [-1, 1/2], does an exact
dual drop below 44?  A yes with a proved gap would be a dent.  A yes
without a gap, or a numerical dual without Sturm positivity, is residue.

Also tries Pfender's diagonal-dominance extra function at α = π/3, as a
linear combination with Gegenbauer, certified exactly when possible.
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
from unrestricted_dual import (
    certify_interval, expand_gegenbauer, f_monomial, rationalize,
)

F = Fraction


def numerical_gap_dual(deg: int, lo: F, ngrid: int = 241):
    from scipy.optimize import linprog
    T = [lo + F(i, ngrid - 1) * (F(1, 2) - lo) for i in range(ngrid)]
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
        "lo": str(lo),
        "bound": float(res.fun),
        "c": [float(x) for x in res.x],
    }


def certify_gap(c, lo: F):
    """f <= 0 on [lo, 1/2], c_k >= 0.  Sturm on that interval."""
    if any(ck < 0 for ck in c) or c[0] <= 0:
        return {"certified": False, "error": "c_k not nonnegative"}
    # Reuse unrestricted_dual.certify_interval by an affine remap?  Simpler:
    # evaluate on a dense rational grid AND at critical points via Sturm
    # of f' on (lo, 1/2).  We import certify_interval only for the
    # unrestricted case lo=-1.  For lo>-1, do Sturm of f on (lo, 1/2).
    from unrestricted_dual import (
        _poly_eval, _sign_vars, _sturm_chain, squarefree,
    )
    mono = f_monomial(c)
    fa = _poly_eval(mono, lo)
    fb = _poly_eval(mono, F(1, 2))
    fm = _poly_eval(mono, (lo + F(1, 2)) / 2)
    if fa > 0 or fb > 0 or fm > 0:
        return {
            "certified": False,
            "positive_sample": True,
            "bound": str(sum(c) / c[0]),
            "float_bound": float(sum(c) / c[0]),
        }
    sf = squarefree(mono)
    chain = _sturm_chain(sf)
    eps = F(1, 10**9)
    nroots = _sign_vars(chain, lo + eps) - _sign_vars(chain, F(1, 2) - eps)
    return {
        "certified": nroots == 0,
        "n_squarefree_roots": nroots,
        "bound": str(sum(c) / c[0]),
        "float_bound": float(sum(c) / c[0]),
        "gap": str(lo),
    }


def pfender_f_pi3_monomial():
    """Pfender's f_{π/3} as a piecewise object is not a polynomial.

    The paper adds a diagonally-dominant kernel, not a Gegenbauer
    combination.  A polynomial proxy that is nonpositive on [-1,1/2]
    is already covered by unrestricted Delsarte.  We record that the
    extra function is not a Gegenbauer dual and do not claim a bound.
    """
    return {
        "used": False,
        "reason": (
            "Pfender f_α is a diagonally-dominant kernel, not a polynomial "
            "in the Gegenbauer basis.  An exact SOS/matrix certificate of "
            "that kernel was not produced.  Residue, not a dual below 44."
        ),
    }


def main() -> int:
    report = {"gaps": [], "pfender": pfender_f_pi3_monomial(),
              "best_certified": None, "excludes_any_k": []}
    best = None
    # Gaps just above -1.  lo = -1 is the unrestricted problem (≈46.34).
    for lo in (F(-1), F(-19, 20), F(-9, 10), F(-4, 5), F(-3, 4), F(-2, 3)):
        for deg in (8, 10, 12):
            num = numerical_gap_dual(deg, lo)
            rec = {
                "lo": str(lo),
                "deg": deg,
                "numerical": None if not num.get("success") else num["bound"],
            }
            print(f"gap lo={lo} deg={deg} num={rec['numerical']}", flush=True)
            if not num.get("success"):
                report["gaps"].append(rec)
                continue
            certified = None
            for den in (100, 1000, 10000):
                c = rationalize(num["c"], den)
                if lo == F(-1):
                    cert = certify_interval(c)
                else:
                    cert = certify_gap(c, lo)
                if cert.get("certified"):
                    certified = {
                        "den": den,
                        "bound": cert["bound"],
                        "float_bound": cert["float_bound"],
                        "excludes": [k for k in (41, 42, 43, 44)
                                     if cert["float_bound"] < k],
                        "gegenbauer_coeffs": [str(x) for x in c],
                        "gap": str(lo),
                        "unrestricted": lo == F(-1),
                    }
                    print(f"  certified den={den} bound={cert['float_bound']} "
                          f"excl={certified['excludes']}", flush=True)
                    if certified["excludes"] and lo == F(-1):
                        (HERE / "certs" / "unrestricted_delsarte.json").write_text(
                            json.dumps(certified, indent=2) + "\n"
                        )
                    if best is None or certified["float_bound"] < best["float_bound"]:
                        # Only an *unrestricted* (lo=-1) dual may exclude k
                        # on the whole interval.  Gapped duals are recorded
                        # but do not move the unrestricted range.
                        if lo == F(-1) or certified["excludes"]:
                            best = dict(certified)
                            best["lo"] = str(lo)
                    break
            rec["certified"] = certified
            report["gaps"].append(rec)
    report["best_certified"] = best
    if best and best.get("unrestricted"):
        report["excludes_any_k"] = best.get("excludes") or []
    report["comment"] = (
        "Unrestricted (lo=-1) Delsarte is the Odlyzko–Sloane number ≈46.34; "
        "it cannot exclude 41–44.  Gapped duals (lo>-1) are not unrestricted "
        "certificates unless a geometric lemma forbids t in [-1, lo).  "
        "No such lemma is claimed here.  Pfender's kernel was not certified."
    )
    (HERE / "dual_gap.json").write_text(json.dumps(report, indent=2) + "\n")
    print("best_certified", best)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
