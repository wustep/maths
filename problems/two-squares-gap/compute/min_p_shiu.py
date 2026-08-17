#!/usr/bin/env python3
"""For each even m, the least p>=0 such that some q makes
    n <= (u-p)^2 + (m+1+q)^2 < n+2m
on the Shiu family. p=0 is the BC point at leftover 2m, which is
NOT in [n, n+2m). We want p>=1 or q != 0 with leftover in [0, 2m).

Also try all first-coordinates, but record the p = u - u_hit of the
first success with small p.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt, shiu_family_n  # noqa: E402


def least_p(m: int, p_max: int):
    u, n, gap = shiu_family_n(m)
    # leftover (u-p)^2 + v^2 - n in [0, gap)
    # v^2 in [n-(u-p)^2, n+gap-1-(u-p)^2]
    for p in range(0, p_max + 1):
        uu = u - p
        if uu < 0:
            break
        lo = n - uu * uu
        hi = n + gap - 1 - uu * uu
        if hi < 0:
            continue
        if lo < 0:
            lo = 0
        s = isqrt(lo)
        if s * s < lo:
            s += 1
        if s * s <= hi:
            return p, uu, s, uu * uu + s * s
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-max", type=int, default=2000)
    ap.add_argument("--p-max", type=int, default=500)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    worst = []
    fails = []
    hist = {}
    for m in range(2, args.m_max + 1, 2):
        got = least_p(m, args.p_max)
        if got is None:
            fails.append(m)
            continue
        p, uu, vv, s = got
        hist[p] = hist.get(p, 0) + 1
        worst.append((p, m, uu, vv, s - shiu_family_n(m)[1]))

    worst.sort(reverse=True)
    summary = {
        "m_max": args.m_max,
        "p_max": args.p_max,
        "fails": fails,
        "max_p": worst[0][0] if worst else None,
        "top20_p": [
            {"p": p, "m": m, "uu": uu, "vv": vv, "gap": g}
            for p, m, uu, vv, g in worst[:20]
        ],
        "hist": {str(k): hist[k] for k in sorted(hist)},
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "m_max": args.m_max,
                "fails": fails,
                "max_p": summary["max_p"],
                "top10": summary["top20_p"][:10],
                "n_p0": hist.get(0, 0),
                "n_p1": hist.get(1, 0),
                "n_p_ge_10": sum(c for p, c in hist.items() if p >= 10),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
