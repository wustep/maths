#!/usr/bin/env python3
"""Fold-and-repair on geometric orbits whose n/k is closest to 7/2."""

from __future__ import annotations

import time
from pathlib import Path

from c7_common import encode, format_word, greedy_mis_fast, residual_of
from reconstruct_polak import induced_edges, isolated_vertices, max_independent_set
from search_orbits import min_max_circ
from verify_set import first_conflict

HERE = Path(__file__).resolve().parent

# Closest (n,q,k) from the wide orbit scan
TARGETS = [
    (317, 31, 90),
    (382, 7, 108),
    (309, 72, 87),
    (303, 14, 85),
    (301, 10, 83),
    (339, 18, 93),
    (367, 87, 98),
    (362, 11, 96),
]


def fold_orbit(n, q, shift, den):
    pows = [pow(q, i, n) for i in range(5)]
    out = []
    for t in range(n):
        coords = [((t * p + shift[j]) % n) * 2 // den for j, p in enumerate(pows)]
        if any(c < 0 or c > 6 for c in coords):
            return []
        out.append(encode(coords))
    return out


def main() -> None:
    t0 = time.time()
    best = 0
    lines = []
    for n, q, k in TARGETS:
        # Only denominators that can actually produce digits 0..6.
        dens = sorted(set([109, 108, 110, n * 2 // 7, (2 * (n - 1) + 5) // 6]))
        shifts = [
            (0, 0, 0, 0, 0),
            (1, 0, 0, 0, 0),
            (n // 9, n // 3, n // 9, n // 3, n // 9),
            (40 % n, 123 % n, 40 % n, 123 % n, 40 % n),
            (3, 11, 3, 11, 3),
            (5, 17, 29, 41, 53),
        ]
        print(f"n={n} q={q} k={k} dens={dens}", flush=True)
        for den in dens:
            if den <= 0:
                continue
            for shift in shifts:
                folded = fold_orbit(n, q, shift, den)
                if not folded:
                    continue
                M = isolated_vertices(folded)
                residual = residual_of(M)
                I = greedy_mis_fast(residual)
                # Exact MIS only for the published-scale leftover (already known: 40).
                if len(M) >= 320 and 60 <= len(residual) <= 75:
                    if len(induced_edges(residual)) <= 90:
                        I = max_independent_set(residual)
                total = len(M) + len(I)
                if total > best:
                    best = total
                    print(
                        f"  best {best} n={n} q={q} den={den} shift={shift} "
                        f"M={len(M)} res={len(residual)} I={len(I)}",
                        flush=True,
                    )
                lines.append(
                    f"{n} {q} {den} {shift} M={len(M)} res={len(residual)} I={len(I)} total={total}"
                )
                if total >= 368:
                    R = sorted(set(M) | set(I))
                    if first_conflict(R) is None:
                        out = HERE / f"R{len(R)}_foldnear.txt"
                        out.write_text("\n".join(format_word(v) for v in R) + "\n")
                        print(f"WROTE {out}")
    (HERE / "fold_near.txt").write_text(
        f"best {best}\nseconds {time.time()-t0:.1f}\n" + "\n".join(lines) + "\n"
    )
    print(f"done best={best} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
