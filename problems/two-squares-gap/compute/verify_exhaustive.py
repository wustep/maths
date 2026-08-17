#!/usr/bin/env python3
"""Exhaustive a=3 check on [1, N] from a generated two-square table.

For every n in 1..N, G(n) = next two-square minus n. Compare to
2*sqrt(2)*n^{1/4}-3 by the integer test (G+3)^4 < 64 n.
Reports every failure. Independent of certify_a3.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_squares import generate_two_squares_upto  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2_000_000)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    ss = generate_two_squares_upto(args.N + 1000)  # pad so G(N) exists
    # next_ge[n] = least two-square >= n
    nxt = [0] * (args.N + 1)
    j = 0
    for n in range(1, args.N + 1):
        while ss[j] < n:
            j += 1
        nxt[n] = ss[j]

    fails_a3 = []
    fails_a2 = []
    for n in range(1, args.N + 1):
        g = nxt[n] - n
        if (g + 3) ** 4 >= 64 * n:
            fails_a3.append({"n": n, "G": g, "next": nxt[n]})
        if (g + 2) ** 4 >= 64 * n:
            fails_a2.append({"n": n, "G": g, "next": nxt[n]})

    summary = {
        "N": args.N,
        "fails_a3": fails_a3,
        "fails_a2": fails_a2,
        "a3_exception_set": [r["n"] for r in fails_a3],
        "a2_exception_set": [r["n"] for r in fails_a2],
    }
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
