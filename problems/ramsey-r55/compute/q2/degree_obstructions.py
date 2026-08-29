#!/usr/bin/env python3
"""Elementary degree obstruction for prime-order automorphisms on 43 vertices."""

from __future__ import annotations

import json
from pathlib import Path


N = 43
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43)
OUT = Path(__file__).resolve().parent / "certs" / "degree_obstructions.json"


def main() -> int:
    rows = []
    for p in PRIMES:
        for cycles in range(1, N // p + 1):
            fixed = N - cycles * p
            # For a fixed vertex, each p-cycle contributes either 0 or p to
            # its degree; its neighbours among the other fixed vertices
            # contribute any integer between 0 and fixed-1 at this necessary-
            # condition stage.
            possible = sorted(
                {
                    p * k + d
                    for k in range(cycles + 1)
                    for d in range(fixed)
                    if 18 <= p * k + d <= 24
                }
            )
            rows.append(
                {
                    "p": p,
                    "cycles": cycles,
                    "fixed": fixed,
                    "cycle_type": f"{p}^{cycles} 1^{fixed}",
                    "possible_fixed_vertex_degrees": possible,
                    "excluded_by_fixed_vertex_degree": fixed > 0 and not possible,
                }
            )
    rec = {
        "n": N,
        "degree_window": [18, 24],
        "rows": rows,
        "excluded_cycle_types": [
            row["cycle_type"]
            for row in rows
            if row["excluded_by_fixed_vertex_degree"]
        ],
        "note": (
            "For each possible number of p-cycles in an order-p permutation, "
            "a fixed vertex has degree p*k+d, where k counts adjacent p-cycles "
            "and 0<=d<fixed. R(4,5)=25 forces every degree into [18,24]. "
            "This is only a necessary condition for cycle types not listed "
            "as excluded."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
