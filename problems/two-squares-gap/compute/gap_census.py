#!/usr/bin/env python3
"""Census of consecutive two-square gaps up to N.

Records:
- max G(s_k) / s_k^{1/4}
- max G(s_k) / (2 sqrt(2) s_k^{1/4})
- whether any backward gap from X exceeds (1/10) X^{1/4}
- top gaps

This is a table. By the house rule it is residue unless it produces an
infinite-family bound. We keep it because it is the only way to see
whether 1/10 already fails at accessible X, and whether the Shiu
family is close to the observed extrema.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import generate_two_squares_upto, isqrt  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2_000_000)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    ss = generate_two_squares_upto(args.N)
    two_sqrt2 = 2.0 * math.sqrt(2.0)
    tenth = 0.1

    records = []
    max_ratio = 0.0
    max_rec = None
    exceeds_tenth = []
    max_gap = 0
    max_gap_rec = None

    for a, b in zip(ss, ss[1:]):
        gap = b - a
        # Backward gap at X = b is gap; at X = b-1 it is gap-1.
        # Forward gap at X = a+1 is gap-1.
        # The consecutive difference is the quantity BC bounds.
        n4 = b ** 0.25
        ratio = gap / n4
        if ratio > max_ratio:
            max_ratio = ratio
            max_rec = {
                "prev": a,
                "next": b,
                "gap": gap,
                "ratio": ratio,
                "ratio_over_2sqrt2": ratio / two_sqrt2,
            }
        if gap > max_gap:
            max_gap = gap
            max_gap_rec = {"prev": a, "next": b, "gap": gap, "ratio": ratio}
        # Green interval at X=b: [b - (1/10) b^{1/4}, b]. The previous
        # two-square is a. It lies in the interval iff b-a <= (1/10) b^{1/4}.
        if gap > tenth * n4:
            exceeds_tenth.append(
                {"X": b, "prev": a, "gap": gap, "tenth_X14": tenth * n4, "ratio": ratio}
            )
        records.append((ratio, a, b, gap))

    records.sort(reverse=True)
    top = [
        {
            "prev": a,
            "next": b,
            "gap": g,
            "ratio": r,
            "ratio_over_2sqrt2": r / two_sqrt2,
        }
        for r, a, b, g in records[: args.top]
    ]

    # Largest X that exceeds 1/10, if any.
    last_tenth = exceeds_tenth[-1] if exceeds_tenth else None

    summary = {
        "N": args.N,
        "count_two_squares": len(ss),
        "max_ratio": max_rec,
        "max_raw_gap": max_gap_rec,
        "n_exceeds_tenth": len(exceeds_tenth),
        "last_exceeds_tenth": last_tenth,
        "first_10_exceeds_tenth": exceeds_tenth[:10],
        "top": top,
    }
    text = json.dumps(summary, indent=2)
    if args.out:
        Path(args.out).write_text(text)
    print(
        json.dumps(
            {
                "N": args.N,
                "count": len(ss),
                "max_ratio": max_rec,
                "max_raw_gap": max_gap_rec,
                "n_exceeds_tenth": len(exceeds_tenth),
                "last_exceeds_tenth": last_tenth,
                "top5": top[:5],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
