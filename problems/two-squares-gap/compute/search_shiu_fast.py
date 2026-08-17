#!/usr/bin/env python3
"""Faster occupancy check for the Shiu family.

For each even m, decide whether [n, n+2m) contains a two-square by
scanning u from floor(sqrt(n+2m-1)) downward and asking whether
[n-u^2, n+2m-1-u^2] contains a square. First hit wins. This is exact
and does not use floating-point bounds as a filter.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt, phi_bc, shiu_family_n  # noqa: E402


def first_hit(n: int, window: int):
    """Return (u, v, s) with n <= u^2+v^2 < n+window, or None."""
    umax = isqrt(n + window - 1)
    for u in range(umax, -1, -1):
        lo = n - u * u
        hi = n + window - 1 - u * u
        if hi < 0:
            continue
        if lo < 0:
            lo = 0
        s = isqrt(lo)
        if s * s < lo:
            s += 1
        vs = s * s
        if vs <= hi:
            return (u, s, u * u + vs)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-max", type=int, default=800)
    ap.add_argument("--m-min", type=int, default=2)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    empty = []
    fails_a3 = []
    n_two = 0
    max_ratio = -1.0
    argmax = None
    rows = []

    for m in range(args.m_min if args.m_min % 2 == 0 else args.m_min + 1, args.m_max + 1, 2):
        u, n, gap = shiu_family_n(m)
        phi = phi_bc(n)
        hit = first_hit(n, gap)
        if hit is None:
            empty.append(m)
            actual_gap = gap
            witness = [u + 1, 0, n + gap]
            beats = False
        else:
            uu, vv, s = hit
            actual_gap = s - n
            witness = [uu, vv, s]
            beats = actual_gap < phi - 3.0
            if actual_gap == 0:
                n_two += 1
        ratio = actual_gap / (n ** 0.25)
        if ratio > max_ratio:
            max_ratio = ratio
            argmax = m
        if not beats:
            fails_a3.append(m)
        if m <= 80 or not beats or hit is None:
            rows.append(
                {
                    "m": m,
                    "n": n,
                    "actual_gap": actual_gap,
                    "ratio": ratio,
                    "witness": witness,
                    "beats_a3": beats,
                }
            )

    summary = {
        "m_min": args.m_min,
        "m_max": args.m_max,
        "empty": empty,
        "fails_a3": fails_a3,
        "n_is_two_square": n_two,
        "max_actual_ratio": max_ratio,
        "argmax_m": argmax,
        "sample_rows": rows,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {k: summary[k] for k in summary if k != "sample_rows"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
