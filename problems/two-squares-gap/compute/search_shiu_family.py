#!/usr/bin/env python3
"""Search Shiu's even-m family for a two-square in (u^2+m^2, u^2+(m+1)^2).

On this family the Bambah–Chowla point and (u+1)^2 both sit at n+2m,
and 2m+2 < 2*sqrt(2)*n^{1/4} < 2m+3. So Jameson's a=2 already holds
from the BC point, while a=3 is exactly: the open interval of length
2m between u^2+m^2 and u^2+(m+1)^2 contains another two-square.

If the interval is empty for infinitely many even m, Bambah–Chowla is
sharp and Green's 1/10 fails infinitely often. If it is always occupied
for large even m, a=3 holds on the only infinite obstruction Shiu wrote
down.

Outputs JSON to stdout; write a copy with --out.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import (  # noqa: E402
    first_two_square_ge,
    is_sum_of_two_squares,
    nearby_two_squares,
    phi_bc,
    shiu_family_n,
)


def occupy(m: int) -> dict:
    u, n, gap = shiu_family_n(m)
    prev_s = n - 1  # u^2 + m^2
    next_bc = n + gap  # u^2 + (m+1)^2 = (u+1)^2
    phi = phi_bc(n)
    # Anything in [n, n+gap) is a strict improvement on BC.
    hit = first_two_square_ge(n, gap)
    empty = hit is None
    rec = {
        "m": m,
        "u": u,
        "n": n,
        "prev": prev_s,
        "bc": next_bc,
        "gap_bc": gap,
        "phi": phi,
        "phi_minus_3": phi - 3.0,
        "bc_fails_a3": gap > phi - 3.0,
        "empty_open_interval": empty,
        "n_is_two_square": is_sum_of_two_squares(n),
    }
    if hit is None:
        rec["actual_next"] = next_bc
        rec["actual_gap"] = gap
        rec["ratio"] = gap / (n ** 0.25)
        rec["witness"] = [u + 1, 0, next_bc]
    else:
        uu, vv, s = hit
        rec["actual_next"] = s
        rec["actual_gap"] = s - n
        rec["ratio"] = (s - n) / (n ** 0.25) if s > n else 0.0
        rec["witness"] = [uu, vv, s]
        rec["beats_a3"] = (s - n) < phi - 3.0
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-max", type=int, default=400)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    rows = []
    empty = []
    fails_a3 = []
    for m in range(2, args.m_max + 1, 2):
        rec = occupy(m)
        rows.append(rec)
        if rec["empty_open_interval"]:
            empty.append(m)
        if rec.get("beats_a3") is False or (
            rec["empty_open_interval"] and rec["bc_fails_a3"]
        ):
            fails_a3.append(m)

    summary = {
        "m_max": args.m_max,
        "n_family": len(rows),
        "empty_open_intervals": empty,
        "fails_a3": fails_a3,
        "max_actual_ratio": max(r["ratio"] for r in rows),
        "argmax_m": max(rows, key=lambda r: r["ratio"])["m"],
        "n_is_two_square_count": sum(1 for r in rows if r["n_is_two_square"]),
        "rows": rows,
    }
    text = json.dumps(summary, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}", file=sys.stderr)
    print(
        json.dumps(
            {
                "m_max": args.m_max,
                "empty": empty,
                "fails_a3": fails_a3,
                "max_actual_ratio": summary["max_actual_ratio"],
                "argmax_m": summary["argmax_m"],
                "n_is_two_square_count": summary["n_is_two_square_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
