#!/usr/bin/env python3
"""Verify a 2-coloring has no monochromatic 7-AP.

Accepts a compact 01/ab string or whitespace-separated bits. Reports length,
whether every 7-AP was checked, and the first obstruction if any.
A coloring of length <= 3703 is recorded as 'not a dent'.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vdw import first_mono_ap, load_coloring


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coloring", type=Path)
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    colors = load_coloring(str(args.coloring))
    hit = first_mono_ap(colors, k=args.k, cyclic=False)
    n = len(colors)
    payload = {
        "path": str(args.coloring),
        "length": n,
        "k": args.k,
        "mono_ap": None if hit is None else {"start_0based": hit[0], "diff": hit[1]},
        "ok": hit is None,
        "dent": hit is None and n >= 3704,
        "note": (
            "verified, length is a dent"
            if hit is None and n >= 3704
            else "verified, but length <= 3703 is not a dent"
            if hit is None
            else "monochromatic 7-AP present"
        ),
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"length {n}")
        if hit is None:
            print(f"no monochromatic {args.k}-AP")
            if n >= 3704:
                print("dent: W(2,7) >", n)
            else:
                print("not a dent (need length >= 3704)")
        else:
            a, d = hit
            pts = [a + i * d + 1 for i in range(args.k)]
            print(f"mono {args.k}-AP start={a + 1} diff={d} points={pts}")
    return 0 if hit is None else 1


if __name__ == "__main__":
    sys.exit(main())
