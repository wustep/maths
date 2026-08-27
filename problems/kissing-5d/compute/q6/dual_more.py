#!/usr/bin/env python3
"""q6 unrestricted dual hunt: exact 1-point ansätze below 44.

1-point Delsarte cannot beat Odlyzko–Sloane ≈ 46.34.  This file
searches a larger (t − 1/2) q(t)^2 dictionary than q2/q5, plus a
Gegenbauer-positive interpolation that is certified on [-1, 1/2]
by Sturm.  A numerical SDP without an exact positivity certificate
is residue.  Mittelmann–Vallentin s_14(5)=44.998… is the published
upper bound.
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
    q2 = [F(0)] * (2 * len(q) - 1)
    for i, x in enumerate(q):
        for j, y in enumerate(q):
            q2[i + j] += x * y
    mono = [F(0)] * (len(q2) + 1)
    for i, x in enumerate(q2):
        mono[i] += x * F(-1, 2)
        mono[i + 1] += x
    return mono


def ansatz_grid():
    """(t − 1/2) q^2, deg q ≤ 4, small rational coeffs not in q2/q5."""
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
        (F(1, 3), F(7, 4), F(10, 3), F(7, 4)),
        (1, 5, 10, 10),
    ):
        qs.append([F(1), F(a), F(b), F(c), F(d)])
    # unique
    seen = set()
    uniq = []
    for q in qs:
        key = tuple(q)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(q)

    jobs = []
    best = None
    for q in uniq:
        c = expand_gegenbauer(_times_half_q2(q))
        rec = {
            "q": [str(x) for x in q],
            "deg_q": len(q) - 1,
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


def _best_unrestricted(report, ansatz_best):
    best = ansatz_best
    for key in ("delsarte_deg12", "delsarte_deg14"):
        for t in report[key]["trials"]:
            if t["certified"] and t["bound"] is not None:
                b = F(t["bound"])
                if best is None or b < best[0]:
                    best = (b, t["bound"], t.get("float_bound"), key)
    if best is not None and len(best) == 3:
        best = (best[0], best[1], best[2], "ansatz_grid")
    return best


def main() -> int:
    jobs, ansatz_best = ansatz_grid()
    report = {
        "delsarte_deg12": try_rationalize(12, (100, 1000, 10000)),
        "delsarte_deg14": try_rationalize(14, (1000, 10000)),
        "n_certified_ansatz": len(jobs),
        "ansatz_certified": jobs[:12],
        "comment": (
            "1-point continuum Delsarte cannot go below Odlyzko–Sloane "
            "~46.34.  (t-1/2)q^2 duals that certify sit near 48 or "
            "higher.  No certified unrestricted dual below 44."
        ),
    }
    best = _best_unrestricted(report, ansatz_best)
    report["best_certified"] = None if best is None else best[1]
    report["best_certified_float"] = None if best is None else best[2]
    report["best_certified_source"] = None if best is None else best[3]
    report["below_44"] = bool(best is not None and best[0] < 44)
    (HERE / "dual_more.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "num12": report["delsarte_deg12"]["numerical"],
        "num14": report["delsarte_deg14"]["numerical"],
        "n_certified_ansatz": report["n_certified_ansatz"],
        "best_certified": report["best_certified"],
        "best_certified_float": report["best_certified_float"],
        "best_certified_source": report["best_certified_source"],
        "below_44": report["below_44"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
