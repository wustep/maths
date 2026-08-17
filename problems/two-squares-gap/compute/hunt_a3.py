#!/usr/bin/env python3
"""Classify n where the two obvious points fail Jameson-a=3, and hunt
a third lattice point.

Two-point failure:
    min( BC leftover, (u+1)^2 - n ) >= 2*sqrt(2)*n^{1/4} - 3

Shiu's family is the infinite subset of these. We record every failure
up to N and, for each, the first two-square in [n, n + floor(Phi-3)+1).
If that search succeeds for every two-point failure, a=3 holds up to N
from an independently checkable witness list.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import bc_point, isqrt  # noqa: E402


TWO_SQRT2 = 2.0 * math.sqrt(2.0)


def first_hit(n: int, window: int):
    if window <= 0:
        # need s=n itself
        u = isqrt(n)
        if u * u == n:
            return (u, 0, n)
        window = 1
    umax = isqrt(n + window - 1)
    best = None
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
            val = u * u + vs
            if best is None or val < best[2]:
                best = (u, s, val)
            # once we have s=n we are done
            if val == n:
                return best
    return best


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=200_000)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    fails = []
    unsaved = []
    saved = []

    for n in range(1, args.N + 1):
        u, v, s = bc_point(n)
        h = s - n
        h2 = (u + 1) * (u + 1) - n
        phi = TWO_SQRT2 * n ** 0.25
        thresh = phi - 3.0
        if min(h, h2) < thresh:
            continue
        # two-point a=3 failure
        # window: we need s < phi-3, i.e. leftover <= floor(thresh-eps) = ceil(thresh)-1
        # leftover <= T  with T = max(0, ceil(thresh) - 1)  if thresh is not integer
        # We need leftover < thresh. Integer leftover <= floor(thresh-eps) = ceil(thresh)-1
        max_leftover = math.ceil(thresh) - 1
        if max_leftover < 0:
            max_leftover = 0
        rec = {
            "n": n,
            "u": u,
            "v": v,
            "h_bc": h,
            "h_nextsq": h2,
            "phi": phi,
            "thresh": thresh,
            "max_leftover": max_leftover,
        }
        # detect Shiu top-of-ladder: n = u^2 + m^2 + 1 for some m, h_bc = 2m
        rem = n - u * u
        # rem = m^2 + 1, v = m+1, h = 2m - 0 = 2m if rem = m^2+1
        rec["shiu_shape"] = (v * v - rem == 2 * v - 2) and (h == 2 * (v - 1))
        hit = first_hit(n, max_leftover + 1)
        if hit is None:
            rec["saved"] = False
            unsaved.append(rec)
        else:
            rec["saved"] = True
            rec["witness"] = [hit[0], hit[1], hit[2]]
            rec["actual_gap"] = hit[2] - n
            saved.append(rec)
        fails.append(rec)

    summary = {
        "N": args.N,
        "n_two_point_fail": len(fails),
        "n_saved": len(saved),
        "n_unsaved": len(unsaved),
        "unsaved": unsaved,
        "n_shiu_shape": sum(1 for r in fails if r.get("shiu_shape")),
        "fails": fails,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "N": args.N,
                "n_two_point_fail": len(fails),
                "n_saved": len(saved),
                "n_unsaved": len(unsaved),
                "unsaved_n": [r["n"] for r in unsaved],
                "n_shiu_shape": summary["n_shiu_shape"],
                "first_fails": [
                    {k: r[k] for k in ("n", "h_bc", "h_nextsq", "thresh", "saved", "shiu_shape") if k in r}
                    for r in fails[:15]
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
