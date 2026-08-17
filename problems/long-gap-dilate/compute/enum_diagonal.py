#!/usr/bin/env python3
"""Independently recompute G(p, round sqrt p) by enumeration where feasible."""

from __future__ import annotations

import json
import math
from math import comb

from enum_G import G_enum
from gaplib import primes_upto


def main():
    out = []
    for p in primes_upto(50):
        if p < 5:
            continue
        n = max(2, int(round(p**0.5)))
        ways = comb(p - 2, n - 2) if n >= 2 else 1
        if ways > 300_000:
            print(f"skip p={p} n={n} C={ways}")
            continue
        rec = G_enum(p, n)
        out.append(rec)
        print(
            f"ENUM p={p} n={n} G={rec['G']} ratio={rec['ratio']:.3f} "
            f"C={ways} sec={rec['sec']}",
            flush=True,
        )
    with open("compute/certs/enum_diagonal.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
