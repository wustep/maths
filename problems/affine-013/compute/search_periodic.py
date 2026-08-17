"""Periodic lifts: S = {x in [0, L*m) : x mod m in P}.

As L -> infinity this is an infinite family. If any seed P gives
T / n^2 -> c > 1/3, that is a dent.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t, t_count  # noqa: E402


def lift(p: set[int], m: int, L: int) -> list[int]:
    return [q * m + r for q in range(L) for r in sorted(p)]


def ratio_for(p: set[int], m: int, L: int) -> tuple[int, int, float]:
    s = lift(p, m, L)
    n = len(s)
    t = t_count(s)
    return t, n, t / (n * n) if n else 0.0


def scan_m(m: int, L: int) -> list[dict]:
    rows = []
    # skip empty and full (full = interval)
    for bits in range(1, (1 << m) - 1):
        p = {i for i in range(m) if bits >> i & 1}
        # translation-normalise P so min = 0
        if 0 not in p:
            continue
        t, n, r = ratio_for(p, m, L)
        it = interval_t(n)
        rows.append(
            {
                "m": m,
                "L": L,
                "P": sorted(p),
                "n": n,
                "T": t,
                "T_interval": it,
                "ratio": r,
                "delta": t - it,
            }
        )
    rows.sort(key=lambda d: -d["ratio"])
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mmin", type=int, default=2)
    ap.add_argument("--mmax", type=int, default=8)
    ap.add_argument("--L", type=int, default=12)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    best = None
    all_best = []
    for m in range(args.mmin, args.mmax + 1):
        rows = scan_m(m, args.L)
        if not rows:
            continue
        top = rows[0]
        all_best.append(top)
        print(
            f"m={m} L={args.L} best P={top['P']} n={top['n']} "
            f"T={top['T']} I={top['T_interval']} ratio={top['ratio']:.6f} "
            f"delta={top['delta']}",
            flush=True,
        )
        if best is None or top["ratio"] > best["ratio"]:
            best = top
        # also report anything strictly above interval
        above = [r for r in rows if r["delta"] > 0][:5]
        for r in above:
            print(
                f"  ABOVE I: P={r['P']} T={r['T']} I={r['T_interval']} "
                f"ratio={r['ratio']:.6f}",
                flush=True,
            )

    print("GLOBAL BEST periodic:", best)
    if args.out:
        Path(args.out).write_text(
            json.dumps({"L": args.L, "best": best, "per_m": all_best}, indent=2)
            + "\n"
        )


if __name__ == "__main__":
    main()
