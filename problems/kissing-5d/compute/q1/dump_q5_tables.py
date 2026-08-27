#!/usr/bin/env python3
"""Write integer Gegenbauer tables for T_Q5 as a C header."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delsarte import eval_poly, gegenbauer_dim5

F = Fraction
T = [F(-1), F(-4, 5), F(-1, 2), F(-3, 10), F(0), F(1, 5), F(1, 2)]


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def main() -> int:
    deg = 14
    polys = gegenbauer_dim5(deg)
    Ds, rows = [], []
    for pk in polys:
        vals = [eval_poly(pk, t) for t in T]
        D = 1
        for v in vals:
            D = D * v.denominator // gcd(D, v.denominator)
        Ds.append(D)
        rows.append([int(v * D) for v in vals])
    out = Path(__file__).resolve().parent / "integer_q5_44_tables.h"
    lines = [
        f"#define NROWS {len(rows)}",
        f"static const i64 ROW_D[NROWS] = {{{', '.join(str(d) for d in Ds)}}};",
        "static const i64 ROW_A[NROWS][7] = {",
    ]
    for r in rows:
        lines.append("  {" + ", ".join(str(a) for a in r) + "},")
    lines.append("};")
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out, "nrows", len(rows))
    # Q5's own histogram must pass (N=40, published pair counts).
    n_q5 = [10, 30, 180, 60, 250, 10, 240]
    assert sum(n_q5) == 780
    for D, coeffs in zip(Ds, rows):
        s = 40 * D + 2 * sum(n * a for n, a in zip(n_q5, coeffs))
        if s < 0:
            raise SystemExit(f"Q5 witness fails k-row D={D} s={s}")
    print("Q5 N=40 witness passes all", len(rows), "rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
