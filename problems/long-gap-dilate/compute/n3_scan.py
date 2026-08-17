#!/usr/bin/env python3
"""Exact G(p,3) by enumerating {0,1,a}. Checks how close n=3 is to Shakan."""

from __future__ import annotations

import json

from gaplib import max_gap_dilates, primes_upto, shakan_lower


def G_n3(p: int) -> dict:
    best_g = p
    best_a = 2
    for a in range(2, p):
        g, d = max_gap_dilates([0, 1, a], p)
        if g < best_g:
            best_g, best_a = g, a
    sh = shakan_lower(p, 3)
    return {
        "p": p,
        "n": 3,
        "G": best_g,
        "a": best_a,
        "shakan": sh,
        "extra": best_g - sh,
        "ratio": best_g * 3 / p,
    }


def main():
    rows = []
    for p in primes_upto(200):
        if p < 5:
            continue
        rec = G_n3(p)
        rows.append(rec)
        print(
            f"p={p:3d} G={rec['G']:4d} sh={rec['shakan']:7.3f} extra={rec['extra']:6.3f} ratio={rec['ratio']:.3f} a={rec['a']}",
            flush=True,
        )
    with open("compute/certs/G_n3.json", "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
