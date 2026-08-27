"""How large can min(end_L, end_R)/(n-1) get?

Endpoint induction gives gamma <= alpha/2 if that ratio is <= alpha
for every n-set. Need alpha < 1 to move 1/2.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import interval_t, t_count  # noqa: E402

# reuse helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_endpoints import both_ends, budget  # noqa: E402
from explore_families import e_km, f_km  # noqa: E402


def drop_mod(N: int, mod: int, drop: int) -> list[int]:
    return [x for x in range(N + 1) if x % mod != drop]


def holes_symmetric(n_int: int, holes: list[int]) -> list[int]:
    s = [x for x in range(n_int + 1) if x not in set(holes)]
    return s


def main() -> None:
    rows = []

    print("=== E(k,m) / F(k,m) end ratios ===")
    best_e = {"ratio": 0.0}
    for k in range(0, 12):
        for m in range(0, 12):
            for name, fn in (("E", e_km), ("F", f_km)):
                s = fn(k, m)
                n = len(s)
                if n < 3:
                    continue
                L, R, mn = both_ends(s)
                ratio = mn / (n - 1)
                rec = {
                    "fam": f"{name}{k}_{m}",
                    "n": n,
                    "L": L,
                    "R": R,
                    "ratio": ratio,
                    "T": t_count(s),
                    "I": interval_t(n),
                }
                rows.append(rec)
                if ratio > best_e["ratio"]:
                    best_e = rec
    print("best E/F", best_e)

    print("=== interval minus one residue class ===")
    best_drop = {"ratio": 0.0}
    for mod in (3, 4, 5, 6):
        for drop in range(mod):
            for N in range(mod, 80, mod):
                s = drop_mod(N, mod, drop)
                n = len(s)
                if n < 3:
                    continue
                L, R, mn = both_ends(s)
                ratio = mn / (n - 1)
                rec = {
                    "fam": f"drop_m{mod}_d{drop}_N{N}",
                    "n": n,
                    "ratio": ratio,
                    "L": L,
                    "R": R,
                    "T": t_count(s),
                    "I": interval_t(n),
                }
                if ratio > best_drop["ratio"]:
                    best_drop = rec
                if n <= 16 or N == 36 or N == 72:
                    rows.append(rec)
    print("best drop-residue", best_drop)

    print("=== two equal intervals with a hole ===")
    best_two = {"ratio": 0.0}
    for a in range(2, 20):
        for gap in range(1, 12):
            s = list(range(a)) + list(range(a + gap, 2 * a + gap))
            n = len(s)
            L, R, mn = both_ends(s)
            ratio = mn / (n - 1)
            rec = {
                "fam": f"twoeq_{a}_{gap}",
                "n": n,
                "ratio": ratio,
                "L": L,
                "R": R,
                "T": t_count(s),
                "I": interval_t(n),
            }
            if ratio > best_two["ratio"]:
                best_two = rec
    print("best two-eq", best_two)

    print("=== the n=9 pattern [0,3k]\\{1 mod 4 odds} ===")
    for k in range(2, 16):
        N = 3 * k
        s = [x for x in range(N + 1) if not (x % 4 == 1)]
        # the n=9 example was [0,12] minus {1,5,7,11}
        n = len(s)
        L, R, mn = both_ends(s)
        ratio = mn / (n - 1)
        print(
            f"  k={k} N={N} n={n} L={L} R={R} ratio={ratio:.4f} "
            f"T={t_count(s)} I={interval_t(n)}"
        )
        rows.append(
            {
                "fam": f"no1mod4_{N}",
                "n": n,
                "ratio": ratio,
                "L": L,
                "R": R,
                "T": t_count(s),
                "I": interval_t(n),
            }
        )

    print("=== [0,12k] minus {1,5,7,11} + 12Z  (period-12 of n=9 seed) ===")
    seed_holes = {1, 5, 7, 11}
    for k in range(1, 8):
        N = 12 * k
        s = [x for x in range(N + 1) if (x % 12) not in seed_holes]
        n = len(s)
        L, R, mn = both_ends(s)
        ratio = mn / (n - 1)
        print(
            f"  k={k} n={n} L={L} R={R} ratio={ratio:.4f} "
            f"T={t_count(s)} I={interval_t(n)} T/n2={t_count(s)/(n*n):.4f}"
        )

    print("=== exhaustive max min-end-ratio n=5..8 wider diameter ===")
    exh_best = []
    for n, dmax in [(5, 20), (6, 18), (7, 20), (8, 18)]:
        worst = 0.0
        worst_s = []
        n_over = 0
        cap = budget(n)
        for comb in itertools.combinations(range(1, dmax + 1), n - 1):
            s = [0] + list(comb)
            L, R, mn = both_ends(s)
            ratio = mn / (n - 1)
            if mn > cap:
                n_over += 1
            if ratio > worst:
                worst = ratio
                worst_s = s
        rec = {
            "n": n,
            "dmax": dmax,
            "worst_ratio": worst,
            "worst_set": worst_s,
            "n_over": n_over,
        }
        exh_best.append(rec)
        print(f"  n={n} worst={worst:.4f} set={worst_s} over={n_over}")

    out = {
        "best_EF": best_e,
        "best_drop": best_drop,
        "best_two": best_two,
        "exhaustive_worst": exh_best,
    }
    Path(__file__).resolve().parent.joinpath("certs/end_ratio.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
