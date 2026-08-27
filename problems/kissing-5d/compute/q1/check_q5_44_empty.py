#!/usr/bin/env python3
"""Replay the T_Q5 N=44 emptiness certificate without re-enumerating.

Checks: Gegenbauer tables in the C header match delsarte.py; the published
Q5 histogram passes; integer_q5_44.json records an empty scan.
"""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction
T = [F(-1), F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]
HERE = Path(__file__).resolve().parent


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def python_tables(deg=14):
    Ds, rows = [], []
    for pk in gegenbauer_dim5(deg):
        vals = [eval_poly(pk, t) for t in T]
        D = 1
        for v in vals:
            D = D * v.denominator // gcd(D, v.denominator)
        Ds.append(D)
        rows.append([int(v * D) for v in vals])
    return Ds, rows


def parse_header(path: Path):
    text = path.read_text()
    d = [int(x) for x in re.search(r"ROW_D\[NROWS\] = \{([^}]+)\}", text).group(1).split(",")]
    rows = []
    for m in re.finditer(r"\{([^{}]+)\}", text.split("ROW_A")[1]):
        rows.append([int(x) for x in m.group(1).split(",")])
    return d, rows


def main() -> int:
    Ds, rows = python_tables()
    hD, hrows = parse_header(HERE / "integer_q5_44_tables.h")
    if Ds != hD or rows != hrows:
        print("FAIL: C header does not match delsarte.py tables")
        return 1
    n_q5 = [10, 30, 180, 60, 250, 10, 240]
    for D, coeffs in zip(Ds, rows):
        s = 40 * D + 2 * sum(n * a for n, a in zip(n_q5, coeffs))
        if s < 0:
            print("FAIL: Q5 witness", D, s)
            return 1
    scan = json.loads((HERE / "integer_q5_44.json").read_text())
    if not scan.get("empty") or scan.get("n_hits") != 0 or scan.get("N") != 44:
        print("FAIL: integer_q5_44.json", scan)
        return 1
    rec = {
        "tables_match": True,
        "q5_witness_ok": True,
        "c_scan_empty": True,
        "c_scanned": scan["scanned"],
    }
    (HERE / "check_q5_44_empty.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))
    print("PASS: T_Q5 N=44 integer slice empty (C scan replayed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
