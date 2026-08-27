#!/usr/bin/env python3
"""q7 unrestricted dual hunt: one more exact 1-point family, then stop.

1-point Delsarte cannot beat Odlyzko–Sloane ≈ 46.34.  q6 certified
(t − 1/2) q^2 sit near 59.  This file retries numerical Delsarte at
degrees 12 and 14, the q6 (t − 1/2) q^2 grid, and a double-root
(t − 1/2)^2 q^2 dictionary.  A numerical SDP without an exact
positivity certificate is residue.  Mittelmann–Vallentin
s_14(5)=44.998… is the published upper bound.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q2 = ROOT / "q2"
Q4 = ROOT / "q4"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Q2))
sys.path.insert(0, str(Q4))

from delsarte import eval_poly, gegenbauer_dim5  # noqa: E402
from unrestricted_dual import (  # noqa: E402
    certify_interval,
    expand_gegenbauer,
    rationalize,
)

F = Fraction


def numerical_delsarte(deg: int, ngrid: int = 241):
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


def _times_poly(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _times_half_qk(q, power=1):
    q2 = _times_poly(q, q)
    half = [F(-1, 2), F(1)]
    factor = [F(1)]
    for _ in range(power):
        factor = _times_poly(factor, half)
    return _times_poly(factor, q2)


def ansatz_grid(power=1):
    qs = []
    for a, b, c in product((0, 1, 2, 3, F(1, 2), F(5, 2), F(8, 3)), repeat=3):
        qs.append([F(1), F(a), F(b), F(c)])
    for a, b, c, d in (
        (1, 0, 0, 0),
        (0, 1, 0, 1),
        (2, 3, 2, 1),
        (5, 10, 10, 5),
        (1, 4, 6, 4),
        (F(1, 3), F(17, 6), F(10, 3), F(0)),
        (1, 5, 10, 10),
    ):
        qs.append([F(1), F(a), F(b), F(c), F(d)])
    seen = set()
    jobs = []
    best = None
    for q in qs:
        key = tuple(q)
        if key in seen:
            continue
        seen.add(key)
        c = expand_gegenbauer(_times_half_qk(q, power=power))
        rec = {
            "q": [str(x) for x in q],
            "deg_q": len(q) - 1,
            "power": power,
            "c_k_nonneg": all(x >= 0 for x in c),
            "unrestricted": True,
        }
        if rec["c_k_nonneg"] and c and c[0] > 0:
            cert = certify_interval(c)
            rec["certified"] = bool(cert.get("certified"))
            rec["bound"] = cert.get("bound")
            rec["float_bound"] = cert.get("float_bound")
            if rec["certified"] and rec["bound"] is not None:
                b = F(rec["bound"])
                if best is None or b < best[0]:
                    best = (b, rec["bound"], rec.get("float_bound"))
        else:
            rec["certified"] = False
            rec["bound"] = None
            rec["float_bound"] = None
        if rec["certified"]:
            jobs.append(rec)
    return jobs, best


def _best_unrestricted(report, *bests):
    best = None
    for b in bests:
        if b is None:
            continue
        if best is None or b[0] < best[0]:
            best = b
    for key in ("delsarte_deg12", "delsarte_deg14"):
        for t in report[key]["trials"]:
            if t["certified"] and t["bound"] is not None:
                b = (F(t["bound"]), t["bound"], t.get("float_bound"), key)
                if best is None or b[0] < best[0]:
                    best = b
    if best is not None and len(best) == 3:
        best = (best[0], best[1], best[2], "ansatz_grid")
    return best


def main() -> int:
    jobs1, best1 = ansatz_grid(power=1)
    jobs2, best2 = ansatz_grid(power=2)
    if best1 is not None:
        best1 = (best1[0], best1[1], best1[2], "half_q2")
    if best2 is not None:
        best2 = (best2[0], best2[1], best2[2], "half2_q2")
    report = {
        "delsarte_deg12": try_rationalize(12, (100, 1000, 10000)),
        "delsarte_deg14": try_rationalize(14, (1000, 10000)),
        "n_certified_half_q2": len(jobs1),
        "n_certified_half2_q2": len(jobs2),
        "ansatz_certified": (jobs1[:6] + jobs2[:6]),
        "comment": (
            "1-point continuum Delsarte cannot go below Odlyzko–Sloane "
            "~46.34.  Exact (t-1/2)^p q^2 duals that certify sit above "
            "44.  No certified unrestricted dual below 44."
        ),
    }
    best = _best_unrestricted(report, best1, best2)
    report["best_certified"] = None if best is None else best[1]
    report["best_certified_float"] = None if best is None else best[2]
    report["best_certified_source"] = None if best is None else best[3]
    report["below_44"] = bool(best is not None and best[0] < 44)
    (HERE / "dual_more.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "num12": report["delsarte_deg12"]["numerical"],
        "num14": report["delsarte_deg14"]["numerical"],
        "n_certified_half_q2": report["n_certified_half_q2"],
        "n_certified_half2_q2": report["n_certified_half2_q2"],
        "best_certified": report["best_certified"],
        "best_certified_float": report["best_certified_float"],
        "best_certified_source": report["best_certified_source"],
        "below_44": report["below_44"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
