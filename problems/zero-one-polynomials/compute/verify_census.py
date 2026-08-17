#!/usr/bin/env python3
"""Independent checks of census.json against closed forms and internal consistencies."""

from __future__ import annotations

import json
import os
import sys

from closed_forms import I2, xplus1_count


def main() -> int:
    path = os.path.join(os.path.dirname(__file__), "census.json")
    with open(path) as f:
        data = json.load(f)
    rows = data["rows"]
    errors = []
    for r in rows:
        n = r["n"]
        tot = 1 << (n - 1)
        if r["total"] != tot:
            errors.append(f"n={n} total {r['total']} != {tot}")
        if r["irreducible"] + r["reducible"] != tot:
            errors.append(f"n={n} irred+red != total")
        xp = xplus1_count(n)
        if r["div_by_x_plus_1"] != xp:
            errors.append(
                f"n={n} x+1 {r['div_by_x_plus_1']} != closed form {xp}"
            )
        if n > 1:
            i2 = I2(n)
            if r["irreducible"] < i2:
                errors.append(f"n={n} irred {r['irreducible']} < I2={i2}")
            if r["div_by_x_plus_1"] > r["reducible"]:
                errors.append(f"n={n} x+1 exceeds reducible")
        if n < 11 and r["nonrecip_part_reducible"] != 0:
            errors.append(f"n={n} nr_red should be 0")
        if r["nonrecip_part_reducible"] % 4 != 0:
            errors.append(
                f"n={n} nr_red={r['nonrecip_part_reducible']} not divisible by 4"
            )
        parts = (
            r["nonrecip_part_is_1"]
            + r["nonrecip_part_irreducible"]
            + r["nonrecip_part_reducible"]
        )
        if parts != tot:
            errors.append(f"n={n} nr parts {parts} != total {tot}")
    if errors:
        print("FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print(f"OK  {len(rows)} rows n={rows[0]['n']}..{rows[-1]['n']}")
    for r in rows:
        red_not = r["reducible"] - r["div_by_x_plus_1"]
        if r["n"] == 1:
            red_not = 0
        print(
            f"  n={r['n']:2d}  p={r['p_irred']:.6f}  "
            f"x+1={r['div_by_x_plus_1']}  "
            f"red_not_x1={red_not}  "
            f"nr_red={r['nonrecip_part_reducible']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
