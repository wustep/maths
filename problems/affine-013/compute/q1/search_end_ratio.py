"""Local and seeded search for large min(end_L, end_R)/(n-1)."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import t_count  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_endpoints import both_ends  # noqa: E402


def ratio_of(s: list[int]) -> float:
    n = len(s)
    _, _, mn = both_ends(s)
    return mn / (n - 1)


def hill(n: int, dmax: int, steps: int, rng: random.Random) -> tuple[float, list[int]]:
    s = sorted(rng.sample(range(dmax), n))
    best_r = ratio_of(s)
    best_s = s[:]
    cur = set(s)
    for _ in range(steps):
        # swap one point
        out = rng.choice(s)
        candidates = [x for x in range(dmax) if x not in cur]
        if not candidates:
            break
        inn = rng.choice(candidates)
        cur.remove(out)
        cur.add(inn)
        nxt = sorted(cur)
        r = ratio_of(nxt)
        if r >= best_r - 0.02 or r >= ratio_of(s):
            s = nxt
            if r > best_r:
                best_r = r
                best_s = s[:]
        else:
            cur.remove(inn)
            cur.add(out)
    return best_r, best_s


def periodize(seed: list[int], periods: int, modulus: int | None = None) -> list[int]:
    m = modulus if modulus is not None else (max(seed) + 1)
    s = []
    for k in range(periods):
        s.extend(x + k * m for x in seed)
    return sorted(set(s))


def main() -> None:
    seeds = {
        "n5": [0, 2, 3, 4, 6],
        "n6": [0, 2, 3, 6, 7, 9],
        "n7": [0, 3, 4, 6, 8, 9, 12],
        "n9": [0, 2, 3, 4, 6, 8, 9, 10, 12],
        "n8": [0, 1, 2, 3, 5, 6, 7, 9],
    }
    print("=== periodized seeds ===")
    per_rows = []
    for name, seed in seeds.items():
        mod = max(seed) + 0  # use diameter as period? try max+1 and max
        for m in (max(seed), max(seed) + 1, max(seed) + 2):
            for k in range(1, 6):
                s = periodize(seed, k, m)
                n = len(s)
                L, R, mn = both_ends(s)
                r = mn / (n - 1)
                rec = {
                    "seed": name,
                    "mod": m,
                    "k": k,
                    "n": n,
                    "L": L,
                    "R": R,
                    "ratio": r,
                    "T": t_count(s),
                    "T_over_n2": t_count(s) / (n * n),
                }
                per_rows.append(rec)
                if k == 1 or r >= 0.8:
                    print(
                        f"  {name} mod={m} k={k} n={n} L={L} R={R} "
                        f"ratio={r:.4f} T/n2={rec['T_over_n2']:.4f}"
                    )

    print("=== hill climb ===")
    rng = random.Random(20260827)
    hill_rows = []
    for n in (9, 10, 11, 12, 13, 15, 16, 18, 21):
        best_r, best_s = 0.0, []
        dmax = min(4 * n + 8, 80)
        for _ in range(25):
            r, s = hill(n, dmax, 200, rng)
            if r > best_r:
                best_r = r
                best_s = s
        L, R, mn = both_ends(best_s)
        rec = {
            "n": n,
            "ratio": best_r,
            "L": L,
            "R": R,
            "S": best_s,
            "T": t_count(best_s),
        }
        hill_rows.append(rec)
        print(f"  n={n} ratio={best_r:.4f} L={L} R={R} T={rec['T']} S={best_s}")

    best_overall = max(
        [p["ratio"] for p in per_rows] + [h["ratio"] for h in hill_rows]
    )
    print("best_overall_ratio", best_overall)
    Path(__file__).resolve().parent.joinpath("certs/end_ratio_search.json").write_text(
        json.dumps(
            {
                "periodized": per_rows,
                "hill": hill_rows,
                "best_ratio": best_overall,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
