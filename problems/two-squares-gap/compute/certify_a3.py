#!/usr/bin/env python3
"""Certificate for Jameson-a=3 except {3,6,21,91}, on every ladder top
in the integer danger zone with 1 <= m <= M.

Classification (proved in RESEARCH.md, integer form):

    A two-point a=3 failure with n >= 92 must be a ladder TOP
        n = u^2 + m^2 + 1,   2u = m^2 + k,   k odd or even with m,
    satisfying
        2*m - 2 <= k <= 3*m + 2
    and
        (min(2*m, k) + 3)^4 >= 64 * n.

For each such top we store a witness (a,b,s) with
    s = a^2 + b^2,   n <= s,   (s - n + 3)^4 < 64 * n
so leftover = s-n < Phi-3.

Replay: python3 compute/verify_a3_cert.py compute/a3_cert.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt  # noqa: E402


def any_hit(n: int, window: int):
    if window <= 0:
        r = isqrt(n)
        return (r, 0, n) if r * r == n else None
    umax = isqrt(n + window - 1)
    near = 8000
    start = umax - near if umax > near else 0
    for u in range(umax, start - 1, -1):
        lo = n - u * u
        hi = n + window - 1 - u * u
        if hi < 0:
            continue
        if lo < 0:
            lo = 0
        s = isqrt(lo)
        if s * s < lo:
            s += 1
        if s * s <= hi:
            return (u, s, u * u + s * s)
    if start == 0:
        return None
    for u in range(start - 1, -1, -1):
        lo = n - u * u
        hi = n + window - 1 - u * u
        if hi < 0:
            continue
        if lo < 0:
            lo = 0
        s = isqrt(lo)
        if s * s < lo:
            s += 1
        if s * s <= hi:
            return (u, s, u * u + s * s)
    return None


def max_leftover(n: int) -> int:
    """Largest w >= 0 with (w+3)^4 < 64 n."""
    # w+3 < (64 n)^{1/4}. Start from integer fourth-root estimate.
    # (64 n)^{1/4} = (2^6 n)^{1/4} = 2^{3/2} n^{1/4} = Phi.
    target = 64 * n
    # binary search for largest t>=1 with t^4 < target, then w = t-3
    lo, hi = 1, 4
    while hi ** 4 < target:
        hi *= 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** 4 < target:
            lo = mid
        else:
            hi = mid - 1
    return lo - 3


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-max", type=int, default=2000)
    ap.add_argument("--out", type=str, default="compute/a3_cert.json")
    ap.add_argument("--store", action="store_true", help="write the witness list")
    args = ap.parse_args()

    known_exceptions = [3, 6, 21, 91]
    witnesses = []
    unsaved = []
    n_tested = 0

    for m in range(1, args.m_max + 1):
        k_lo = 2 * m - 2
        if k_lo < 1:
            k_lo = 1
        k_hi = 3 * m + 2
        for k in range(k_lo, k_hi + 1):
            if (m * m + k) % 2:
                continue
            u = (m * m + k) // 2
            if u < 1:
                continue
            n = u * u + m * m + 1
            if n < 92:
                # small n handled as named exceptions + direct check
                continue
            mn = min(2 * m, k)
            if (mn + 3) ** 4 < 64 * n:
                continue
            n_tested += 1
            W = max_leftover(n)
            hit = any_hit(n, W + 1)
            if hit is None:
                unsaved.append({"m": m, "k": k, "u": u, "n": n, "W": W})
            else:
                a, b, s = hit
                if args.store:
                    witnesses.append([n, a, b, s])

    n_max_bound = (args.m_max * args.m_max) // 2
    n_max_bound = n_max_bound * n_max_bound + args.m_max * args.m_max + 1
    cert = {
        "m_max": args.m_max,
        "n_max_bound": n_max_bound,
        "known_exceptions": known_exceptions,
        "n_danger_tops": n_tested,
        "n_witnesses": len(witnesses),
        "n_unsaved": len(unsaved),
        "unsaved": unsaved,
    }
    if args.store:
        cert["witnesses"] = witnesses
        Path(args.out).write_text(json.dumps(cert, separators=(",", ":")))
    else:
        Path(args.out).write_text(json.dumps(cert, indent=2))
    print(
        json.dumps(
            {
                "m_max": args.m_max,
                "n_danger_tops": n_tested,
                "n_witnesses": len(witnesses),
                "n_unsaved": len(unsaved),
                "unsaved_n": [r["n"] for r in unsaved],
                "out": args.out,
                "bytes": Path(args.out).stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
