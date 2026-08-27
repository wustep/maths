#!/usr/bin/env python3
"""Independent replay of a polar max-vertex, using Fraction GE (not Cramer).

Reads polar_*.json, rebuilds the five tight planes from configs.py, solves
A x = 1 over Q, checks |x|^2 and every inequality.  Different linear-algebra
path from polar.c / polar_vertices.cramer_column.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import CONFIGS, _dot, _norm2
from exact_duals import ge_q

F = Fraction
HERE = Path(__file__).resolve().parent


def replay_one(name, rec):
    pts = CONFIGS[name]()
    mv = rec["max_vertex"]
    idxs = mv["support"]
    A = [[pts[i][j] for j in range(5)] for i in idxs]
    b = [F(1)] * 5
    x = ge_q(A, b)
    x = tuple(x)
    n2 = _norm2(x)
    claimed = F(rec["max_norm2"])
    ips = [_dot(x, p) for p in pts]
    ok_ineq = all(ip <= 1 for ip in ips)
    tight = sum(1 for ip in ips if ip == 1)
    ok = (n2 == claimed) and ok_ineq and n2 < 2
    return {
        "name": name,
        "x": [str(c) for c in x],
        "norm2": str(n2),
        "claimed_norm2": rec["max_norm2"],
        "norm2_match": n2 == claimed,
        "all_ip_le_1": ok_ineq,
        "n_tight": tight,
        "max_ip": str(max(ips)),
        "norm2_lt_2": n2 < 2,
        "ok": ok,
    }


def main() -> int:
    polar = json.loads((HERE / "polar_vertices.json").read_text())
    report = {}
    ok_all = True
    for name, rec in polar.items():
        r = replay_one(name, rec)
        report[name] = r
        print(f"{name}: ok={r['ok']} x={r['x']} |x|^2={r['norm2']} "
              f"tight={r['n_tight']}")
        if not r["ok"]:
            ok_all = False
    out = HERE / "replay_max_vertex.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
