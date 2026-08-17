#!/usr/bin/env python3
"""Two-point a=3 failures at large m, via the (m,k) ladder tops.

A two-point failure must sit on a Shiu ladder. The integer test
    (min(2m, k)+3)^4 >= 64 n
with n = u^2+m^2+1, 2u = m^2+k, forces k into a short interval
around 2m. We walk that interval, plus a few rungs down, and try
to save each failure with any_hit.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt  # noqa: E402


def _try_u(n: int, window: int, u: int):
    lo = n - u * u
    hi = n + window - 1 - u * u
    if hi < 0:
        return None
    if lo < 0:
        lo = 0
    s = isqrt(lo)
    if s * s < lo:
        s += 1
    vs = s * s
    if vs <= hi:
        return (u, s, u * u + vs)
    return None


def any_hit(n: int, window: int):
    if window <= 0:
        r = isqrt(n)
        return (r, 0, n) if r * r == n else None
    umax = isqrt(n + window - 1)
    # Near-circle first (almost all hits live here).
    near = 4000
    lo_u = umax - near if umax > near else 0
    for u in range(umax, lo_u - 1, -1):
        hit = _try_u(n, window, u)
        if hit is not None:
            return hit
    if lo_u == 0:
        return None
    for u in range(lo_u - 1, -1, -1):
        hit = _try_u(n, window, u)
        if hit is not None:
            return hit
    return None


def window_for(n: int) -> int:
    target = 64 * n
    phi = 2.0 * math.sqrt(2.0) * n ** 0.25
    w = math.floor(phi - 3.0)
    while w + 3 > 0 and (w + 3) ** 4 >= target:
        w -= 1
    while w + 4 > 0 and (w + 4) ** 4 < target:
        w += 1
    return w  # max leftover strictly below Phi-3


def two_point_fails(h: int, h2: int, n: int) -> bool:
    m = min(h, h2)
    if m + 3 <= 0:
        return True
    return (m + 3) ** 4 >= 64 * n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-max", type=int, default=4000)
    ap.add_argument("--m-min", type=int, default=1)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    unsaved = []
    n_fail = 0
    n_saved = 0
    k_span_max = 0

    for m in range(args.m_min, args.m_max + 1):
        # k must make m^2+k even so u is an integer
        # search a generous interval around 2m
        k_lo = max(1, 2 * m - 8)
        k_hi = 3 * m + 6
        if k_hi - k_lo > k_span_max:
            k_span_max = k_hi - k_lo
        for k in range(k_lo, k_hi + 1):
            if (m * m + k) % 2:
                continue
            u = (m * m + k) // 2
            if u < 1:
                continue
            n_top = u * u + m * m + 1
            h_top = 2 * m
            h2_top = k
            t = 0
            while t <= 6:
                n = n_top + t
                h = h_top - t
                h2 = h2_top - t
                if h < 0 or h2 < 0:
                    break
                if n >= (u + 1) * (u + 1):
                    break
                if not two_point_fails(h, h2, n):
                    break
                n_fail += 1
                W = window_for(n)
                win = W + 1
                if win < 1:
                    win = 1
                hit = any_hit(n, win)
                if hit is None:
                    unsaved.append({"n": n, "u": u, "m": m, "k": k, "t": t, "W": W})
                else:
                    n_saved += 1
                t += 1

    summary = {
        "m_min": args.m_min,
        "m_max": args.m_max,
        "n_two_point_fail": n_fail,
        "n_saved": n_saved,
        "n_unsaved": len(unsaved),
        "unsaved": unsaved,
        "k_span_max": k_span_max,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "m_min": args.m_min,
                "m_max": args.m_max,
                "n_fail": n_fail,
                "n_saved": n_saved,
                "n_unsaved": len(unsaved),
                "unsaved_n": [r["n"] for r in unsaved],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
