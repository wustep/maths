#!/usr/bin/env python3
"""Re-evaluate the integer hits / claimed infeasibilities at high Gegenbauer degree."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction

HITS = {
    40: {"n_{-1}": 19, "n_{-1/2}": 239, "n_0": 277, "n_{1/2}": 245},
    41: {"n_{-1}": 20, "n_{-1/2}": 254, "n_0": 289, "n_{1/2}": 257},
}

D5 = {"n_{-1}": 20, "n_{-1/2}": 240, "n_0": 280, "n_{1/2}": 240}


def spectrum(N, n, deg):
    polys = gegenbauer_dim5(deg)
    A = {
        F(-1): F(2 * n["n_{-1}"], N),
        F(-1, 2): F(2 * n["n_{-1/2}"], N),
        F(0): F(2 * n["n_0"], N),
        F(1, 2): F(2 * n["n_{1/2}"], N),
    }
    vals = []
    ok = True
    for k, pk in enumerate(polys):
        s = eval_poly(pk, F(1))
        for t, at in A.items():
            s += at * eval_poly(pk, t)
        vals.append(str(s))
        if s < 0:
            ok = False
    assert n["n_{-1}"] + n["n_{-1/2}"] + n["n_0"] + n["n_{1/2}"] == comb(N, 2)
    return {"ok": ok, "spectrum": vals, "A": {str(t): str(a) for t, a in A.items()}}


def main() -> int:
    report = {
        "D5_N40": spectrum(40, D5, 20),
        "hit_N40": spectrum(40, HITS[40], 20),
        "hit_N41": spectrum(41, HITS[41], 20),
    }
    out = Path(__file__).resolve().parent / "check_integer_hits.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for k, v in report.items():
        print(f"{k}: ok={v['ok']}")
        if not v["ok"]:
            print("  first negative at", next(i for i, s in enumerate(v["spectrum"]) if F(s) < 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
