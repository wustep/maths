"""Unions of 2 or 3 integer intervals, and {0,1,3}-placed blocks.

These are infinite families once the length ratios and gaps are fixed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t, t_count  # noqa: E402


def two_intervals(n: int) -> dict:
    """S = [0, a) ∪ [g, g+n-a), a=1..n-1, g>=a, gcd-free not required."""
    best = {"T": interval_t(n), "S": list(range(n)), "kind": "interval"}
    hits = []
    for a in range(1, n):
        b = n - a
        for g in range(a, 3 * n + 1):
            s = list(range(a)) + list(range(g, g + b))
            t = t_count(s)
            if t > best["T"]:
                best = {"T": t, "S": s, "kind": f"two a={a} g={g}"}
                hits.append(best)
    return {"n": n, "best": best, "n_improvements": len(hits)}


def three_blocks_013(m: int, d: int) -> list[int]:
    """Three length-m blocks at 0, d, 3d (the {0,1,3} configuration)."""
    s = set(range(m))
    s.update(range(d, d + m))
    s.update(range(3 * d, 3 * d + m))
    return sorted(s)


def scan_013_blocks(mmax: int) -> list[dict]:
    rows = []
    for m in range(1, mmax + 1):
        local = None
        for d in range(1, 4 * m + 1):
            s = three_blocks_013(m, d)
            n = len(s)
            t = t_count(s)
            rec = {
                "m": m,
                "d": d,
                "n": n,
                "T": t,
                "T_interval": interval_t(n),
                "ratio": t / (n * n),
                "overlap": 3 * m - n,
            }
            if local is None or rec["ratio"] > local["ratio"]:
                local = rec
        rows.append(local)
        print(
            f"013-blocks m={m} best d={local['d']} n={local['n']} "
            f"T={local['T']} I={local['T_interval']} "
            f"ratio={local['ratio']:.6f} ov={local['overlap']}",
            flush=True,
        )
    return rows


def residue_restricted_interval(n_ambient: int) -> list[dict]:
    """Interval minus one residue class, and other 2-class windows."""
    rows = []
    for N in range(3, n_ambient + 1):
        for drop in (0, 1, 2):
            s = [x for x in range(N) if x % 3 != drop]
            n = len(s)
            t = t_count(s)
            rows.append(
                {
                    "N": N,
                    "drop": drop,
                    "n": n,
                    "T": t,
                    "T_interval": interval_t(n),
                    "ratio": t / (n * n),
                }
            )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=18)
    ap.add_argument("--mmax", type=int, default=12)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    two = []
    for n in range(3, args.nmax + 1):
        rec = two_intervals(n)
        two.append(rec)
        b = rec["best"]
        it = interval_t(n)
        print(
            f"two-int n={n} T={b['T']} I={it} kind={b['kind']} "
            f"ratio={b['T']/(n*n):.6f}",
            flush=True,
        )

    print("--- 013 blocks ---", flush=True)
    blocks = scan_013_blocks(args.mmax)

    print("--- residue-restricted ---", flush=True)
    res = residue_restricted_interval(max(30, args.nmax * 2))
    res_best = max(res, key=lambda d: d["ratio"])
    print("best residue-restricted:", res_best, flush=True)
    above = [r for r in res if r["T"] > r["T_interval"]]
    print(f"residue-restricted above interval: {len(above)}", flush=True)
    for r in above[:8]:
        print(" ", r, flush=True)

    if args.out:
        Path(args.out).write_text(
            json.dumps(
                {
                    "two_intervals": two,
                    "blocks_013": blocks,
                    "residue_best": res_best,
                    "residue_above": above[:20],
                },
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    main()
