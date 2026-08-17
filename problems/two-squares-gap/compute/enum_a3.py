#!/usr/bin/env python3
"""Enumerate every two-point a=3 failure via Shiu ladders, and save each.

For each u >= 1 the interval I_u = [u^2, (u+1)^2) is a sequence of
descending ladders (Shiu, Integers 2019, Lemma). Two-point a=3 can
fail only near the top of a ladder, because h decreases and Phi
increases as one walks down.

We loop u and m, test the top n = u^2+m^2+1 and the next few rungs,
and for each two-point failure search a third lattice point in
[n, Phi-3).

Integer comparison for "min(h,h2) >= Phi-3":
    min(h,h2)+3 >= 2*sqrt(2)*n^{1/4}
    (min(h,h2)+3)^4 >= 64 n
which is exact when the left side is positive.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt  # noqa: E402


def any_hit(n: int, window: int):
    """Some two-square in [n, n+window), or None. Prefers large first coordinate."""
    if window <= 0:
        r = isqrt(n)
        return (r, 0, n) if r * r == n else None
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


def two_point_fails(h: int, h2: int, n: int) -> bool:
    m = min(h, h2)
    if m + 3 <= 0:
        return True
    # (m+3)^4 >= 64 n  <=> m+3 >= 2*sqrt(2)*n^{1/4}
    lhs = m + 3
    # compare lhs^4 and 64 n
    return lhs ** 4 >= 64 * n


def thresh_int_window(n: int) -> int:
    """Largest integer leftover strictly less than Phi-3.

    leftover <= W  iff  leftover + 3 < 2*sqrt(2)*n^{1/4}
                    iff  (leftover+3)^4 < 64 n
    W = max { w >= 0 : (w+3)^4 < 64 n }
    """
    # Phi-3 = 2*sqrt(2)*n^{1/4} - 3, W = ceil(Phi-3) - 1 = floor(Phi-4) wait
    # leftover < Phi-3 iff leftover + 3 < Phi iff (leftover+3)^4 < 64n
    # max leftover is the largest w with (w+3)^4 < 64n
    target = 64 * n
    # w+3 < (64n)^{1/4} = 2 * 2^{1/4} * n^{1/4} wait (64n)^{1/4} = (2^6 n)^{1/4} = 2^{3/2} n^{1/4} = 2*sqrt(2)*n^{1/4}=Phi
    # so w+3 < Phi, w < Phi-3. Same.
    # integer: largest w>=-2 with (w+3)^4 < 64n
    # start from floor(Phi-3)
    phi = 2.0 * math.sqrt(2.0) * n ** 0.25
    w = math.floor(phi - 3.0)
    # nudge to exact
    while w + 3 > 0 and (w + 3) ** 4 >= target:
        w -= 1
    while (w + 4) > 0 and (w + 4) ** 4 < target:
        w += 1
    return w


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--u-max", type=int, default=5000)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    fails = []
    unsaved = []

    # n=1 is a square; leftover 0. Phi-3 < 0, so 0 >= Phi-3. "Fails" two-point
    # but is already a two-square. Record as saved.
    for u in range(1, args.u_max + 1):
        # largest m with u^2 + m^2 + 1 < (u+1)^2 = u^2+2u+1
        # m^2 < 2u, m <= floor(sqrt(2u-1))
        mmax = isqrt(2 * u - 1)
        for m in range(1, mmax + 1):
            n_top = u * u + m * m + 1
            h_top = 2 * m
            h2_top = 2 * u - m * m  # (u+1)^2 - n_top
            # walk the ladder while we could still fail
            t = 0
            while True:
                n = n_top + t
                if n >= (u + 1) * (u + 1):
                    break
                h = h_top - t
                h2 = h2_top - t
                if h < 0 or h2 < 0:
                    break
                if not two_point_fails(h, h2, n):
                    # further rungs are easier
                    break
                W = thresh_int_window(n)
                rec = {
                    "n": n,
                    "u": u,
                    "m": m,
                    "t": t,
                    "h": h,
                    "h2": h2,
                    "W": W,
                }
                window = W + 1  # leftover in 0..W
                if window < 1:
                    window = 1
                hit = any_hit(n, window)
                if hit is None:
                    rec["saved"] = False
                    unsaved.append(rec)
                else:
                    rec["saved"] = True
                    rec["witness"] = [hit[0], hit[1], hit[2]]
                    rec["actual_gap"] = hit[2] - n
                fails.append(rec)
                t += 1

    summary = {
        "u_max": args.u_max,
        "n_max": (args.u_max + 1) ** 2 - 1,
        "n_two_point_fail": len(fails),
        "n_unsaved": len(unsaved),
        "unsaved": unsaved,
        "fails_head": fails[:20],
        "fails_tail": fails[-10:] if fails else [],
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "u_max": args.u_max,
                "n_max": summary["n_max"],
                "n_two_point_fail": len(fails),
                "n_unsaved": len(unsaved),
                "unsaved_n": [r["n"] for r in unsaved],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
