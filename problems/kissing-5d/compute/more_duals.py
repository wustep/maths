#!/usr/bin/env python3
"""Try interpolating exact duals for a few larger inner-product sets."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import eval_poly, gegenbauer_dim5
from exact_duals import certify_dual, ge_q

F = Fraction


def interpolate(T_zero, free, T_all, name):
    deg = max(free)
    polys = gegenbauer_dim5(deg)
    A, b = [], []
    for t in T_zero:
        A.append([eval_poly(polys[k], t) for k in free])
        b.append(-F(1))
    try:
        x = ge_q(A, b)
    except ValueError as e:
        return {"name": name, "certified": False, "error": str(e)}
    c = [F(0)] * (deg + 1)
    c[0] = F(1)
    for k, val in zip(free, x):
        c[k] = val
    return certify_dual(c, T_all, name)


def main() -> int:
    jobs = []
    # Q5 angles, vanish on T except possibly -1
    Tq = [F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
    jobs.append(interpolate(
        Tq, [1, 2, 3, 4, 5, 9],
        [F(-1)] + Tq, "Q5_c0_to_c5_c9",
    ))
    # L5 plus 1/5
    Tl = [F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 5), F(1, 2)]
    jobs.append(interpolate(
        Tl, [1, 2, 3, 4, 5, 9],
        [F(-1)] + Tl, "L5_plus_1_5",
    ))
    # L5 plus -4/5
    Tl2 = [F(-4, 5), F(-3, 4), F(-1, 2), F(-1, 4), F(0), F(1, 2)]
    jobs.append(interpolate(
        Tl2, [1, 2, 3, 4, 5, 9],
        [F(-1)] + Tl2, "L5_plus_m4_5",
    ))
    # D5 plus ±1/4
    Td = [F(-1, 2), F(-1, 4), F(0), F(1, 4), F(1, 2)]
    jobs.append(interpolate(
        Td, [1, 2, 3, 4, 5],
        [F(-1)] + Td, "D5_plus_pm_1_4",
    ))
    report = {j["name"]: j for j in jobs}
    out = Path(__file__).resolve().parent / "more_duals.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for j in jobs:
        print(f"{j['name']}: certified={j.get('certified')} "
              f"bound={j.get('float_bound')} excludes={j.get('excludes')} "
              f"err={j.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
