"""Self-similar lifts of the high end-score seeds.

If min(end_L,end_R)/(n-1) -> 1 along a family, endpoint induction
cannot move the constant 1/2.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import interval_t, t_count  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_endpoints import both_ends  # noqa: E402


def scale_union(seed: list[int], scales: list[int]) -> list[int]:
    s = set()
    for a in seed:
        for lam in scales:
            s.add(a * lam)
    return sorted(s)


def nest3(seed: list[int], depth: int) -> list[int]:
    s = set(seed)
    for _ in range(depth):
        nxt = set()
        for x in s:
            for a in seed:
                nxt.add(3 * x + a)
        s = nxt
    return sorted(s)


def add_point_scan(base: list[int], extra_range: int) -> tuple[float, list[int]]:
    best_r, best_s = 0.0, base
    present = set(base)
    lo, hi = min(base) - extra_range, max(base) + extra_range
    for p in range(lo, hi + 1):
        if p in present:
            continue
        s = sorted(present | {p})
        _, _, mn = both_ends(s)
        r = mn / (len(s) - 1)
        if r > best_r:
            best_r = r
            best_s = s
    return best_r, best_s


def main() -> None:
    seeds = {
        "n5": [0, 2, 3, 4, 6],
        "n9": [0, 2, 3, 4, 6, 8, 9, 10, 12],
        "n10": [0, 6, 9, 12, 18, 20, 24, 27, 30, 36],
        "n7": [0, 3, 4, 6, 8, 9, 12],
    }
    rows = []

    print("=== scale unions {1,3,...,3^k} ===")
    for name, seed in seeds.items():
        for k in range(0, 5):
            scales = [3**i for i in range(k + 1)]
            s = scale_union(seed, scales)
            n = len(s)
            L, R, mn = both_ends(s)
            r = mn / (n - 1) if n > 1 else 0
            rec = {
                "kind": "scale_union",
                "seed": name,
                "k": k,
                "n": n,
                "L": L,
                "R": R,
                "ratio": r,
                "T": t_count(s),
                "I": interval_t(n),
                "T_over_n2": t_count(s) / (n * n),
            }
            rows.append(rec)
            print(
                f"  {name} k={k} n={n} L={L} R={R} ratio={r:.4f} "
                f"T/n2={rec['T_over_n2']:.4f}"
            )

    print("=== IFS nest x |-> 3x+a ===")
    for name, seed in (("n5", [0, 2, 3, 4, 6]), ("n3", [0, 1, 3])):
        for d in range(0, 4):
            s = nest3(seed, d)
            n = len(s)
            L, R, mn = both_ends(s)
            r = mn / (n - 1) if n > 1 else 0
            rec = {
                "kind": "nest3",
                "seed": name,
                "depth": d,
                "n": n,
                "ratio": r,
                "T_over_n2": t_count(s) / (n * n),
            }
            rows.append(rec)
            print(f"  {name} d={d} n={n} ratio={r:.4f} T/n2={rec['T_over_n2']:.4f}")

    print("=== 3*set plus best extra point ===")
    for name, seed in seeds.items():
        scaled = [3 * x for x in seed]
        r, s = add_point_scan(scaled, max(scaled) // 2 + 6)
        n = len(s)
        L, R, mn = both_ends(s)
        print(
            f"  3*{name}+pt n={n} L={L} R={R} ratio={r:.4f} "
            f"T={t_count(s)} S={s}"
        )
        rows.append(
            {
                "kind": "triple_plus",
                "seed": name,
                "n": n,
                "ratio": r,
                "S": s,
                "T": t_count(s),
            }
        )

    print("=== divisor-rich [0, M] cap ===")
    for M in (12, 24, 36, 48, 60, 84, 120, 180, 240):
        # all integers in [0,M] that have a small prime factor from {2,3,4,5}
        s = [x for x in range(M + 1) if x == 0 or x == M or any(x % d == 0 for d in (2, 3, 4, 5))]
        n = len(s)
        L, R, mn = both_ends(s)
        r = mn / (n - 1)
        print(
            f"  M={M} n={n} L={L} R={R} ratio={r:.4f} T/n2={t_count(s)/(n*n):.4f}"
        )
        rows.append({"kind": "divrich", "M": M, "n": n, "ratio": r})

    best = max(r["ratio"] for r in rows)
    print("best ratio", best)
    Path(__file__).resolve().parent.joinpath("certs/selfsimilar.json").write_text(
        json.dumps({"rows": rows, "best": best}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
