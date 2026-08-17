#!/usr/bin/env python3
"""Singer difference sets at prime q with p=q^2+q+1 prime."""

from __future__ import annotations

import json
import time

from constructions import singer_difference_set
from gaplib import is_prime, max_gap_dilates, shakan_lower


def main():
    rows = []
    for q in range(2, 20):
        if not is_prime(q):
            continue
        p = q * q + q + 1
        if not is_prime(p):
            continue
        t0 = time.time()
        try:
            D = singer_difference_set(q)
        except Exception as e:
            print(f"q={q} p={p} FAIL {e}")
            continue
        g, d = max_gap_dilates(D, p)
        n = len(D)
        rec = {
            "q": q,
            "p": p,
            "n": n,
            "expected_n": q + 1,
            "g": g,
            "d": d,
            "shakan": shakan_lower(p, n),
            "ratio_mean": g * n / p,
            "ratio_sqrt": g / (p**0.5),
            "sec": round(time.time() - t0, 3),
            "D": D,
        }
        rows.append(rec)
        print(
            f"q={q:2d} p={p:4d} n={n:2d} g={g:4d} sh={rec['shakan']:7.2f} "
            f"ratio={rec['ratio_mean']:.3f} C={rec['ratio_sqrt']:.3f} sec={rec['sec']}",
            flush=True,
        )
    with open("compute/certs/singer.json", "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
