#!/usr/bin/env python3
"""Find empty open BC-ladders: no two-square strictly between
u^2+m^2 and u^2+(m+1)^2.

Such an empty interval is a genuine consecutive gap of length 2m+1.
If it occurs with m ~ sqrt(2u), the ratio is close to 2*sqrt(2).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import isqrt  # noqa: E402


def interior_hit(u: int, m: int):
    """Two-square in (u^2+m^2, u^2+(m+1)^2)."""
    lo_s = u * u + m * m + 1
    hi_s = u * u + (m + 1) * (m + 1)  # exclusive
    window = hi_s - lo_s
    if window <= 0:
        return None
    umax = isqrt(hi_s - 1)
    for uu in range(umax, -1, -1):
        a = lo_s - uu * uu
        b = hi_s - 1 - uu * uu
        if b < 0:
            continue
        if a < 0:
            a = 0
        s = isqrt(a)
        if s * s < a:
            s += 1
        if s * s <= b:
            return (uu, s, uu * uu + s * s)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--u-max", type=int, default=2000)
    ap.add_argument("--min-m", type=int, default=1)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    empties = []
    checked = 0
    for u in range(1, args.u_max + 1):
        mmax = isqrt(2 * u)
        # only ladders that can be long: m >= min_m
        for m in range(args.min_m, mmax + 1):
            # stay inside I_u: u^2+m^2+1 < (u+1)^2
            if m * m >= 2 * u:
                continue
            checked += 1
            if interior_hit(u, m) is None:
                prev_s = u * u + m * m
                next_s = u * u + (m + 1) * (m + 1)
                gap = next_s - prev_s
                ratio = gap / (next_s ** 0.25)
                empties.append(
                    {
                        "u": u,
                        "m": m,
                        "prev": prev_s,
                        "next": next_s,
                        "gap": gap,
                        "ratio": ratio,
                    }
                )

    empties.sort(key=lambda r: -r["ratio"])
    summary = {
        "u_max": args.u_max,
        "checked": checked,
        "n_empty": len(empties),
        "max_ratio_empty": empties[0] if empties else None,
        "top15": empties[:15],
        "largest_m_empty": max((e["m"] for e in empties), default=None),
        "empties": empties,
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(
        json.dumps(
            {
                "u_max": args.u_max,
                "checked": checked,
                "n_empty": len(empties),
                "max_ratio": summary["max_ratio_empty"],
                "largest_m_empty": summary["largest_m_empty"],
                "top8": empties[:8],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
