#!/usr/bin/env python3
"""Further exact unrestricted dual attempts for τ5.

q4 already has exact S_k^5 over Q and failed to certify a value < 44.
This file retries a short list of 1-point Delsarte rationalizations and
a gapped interpolation that is *not* unrestricted (recorded as residue).

A numerical SDP without an exact positivity certificate is residue.
Mittelmann–Vallentin s_14(5)=44.998… is the published upper bound.
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
from unrestricted_dual import certify_interval, rationalize  # noqa: E402  # q2

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


def main() -> int:
    report = {
        "delsarte_deg12": try_rationalize(12, (100, 1000, 10000)),
        "delsarte_deg16": try_rationalize(16, (1000, 10000)),
        "comment": (
            "1-point continuum Delsarte cannot go below Odlyzko–Sloane "
            "~46.34.  No certified unrestricted dual below 44."
        ),
    }
    best = None
    for key in ("delsarte_deg12", "delsarte_deg16"):
        for t in report[key]["trials"]:
            if t["certified"] and t["bound"] is not None:
                b = F(t["bound"])
                if best is None or b < best:
                    best = b
    report["best_certified"] = None if best is None else str(best)
    report["below_44"] = bool(best is not None and best < 44)
    (HERE / "dual_more.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "num12": report["delsarte_deg12"]["numerical"],
        "num16": report["delsarte_deg16"]["numerical"],
        "best_certified": report["best_certified"],
        "below_44": report["below_44"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
