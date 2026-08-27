"""Hunt whether min(end_L, end_R) <= 2(n-1)/3 always.

end_L counts triples that use min(S) as x or y:
  N2 = #{d>0: min+d in S, min+3d in S}
  N1 = #{d>0: min+2d in S, min+3d in S}
end_R is the same on -S.

If min(end_L, end_R) <= 2(n-1)/3 for every S, induction gives
T(n) <= T(n-1) + 1 + 2(n-1)/3, hence gamma <= 1/3.

This script searches for a counterexample (both ends strictly above
the 2/3 budget) and records the max of min(end_L, end_R)/(n-1).
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import interval_t, t_count  # noqa: E402


def end_score(pts: list[int]) -> int:
    """N1 + N2 at the leftmost point."""
    a = min(pts)
    present = set(pts)
    shifted = {p - a for p in present if p != a}
    n1 = n2 = 0
    # d such that 3d is in shifted
    for p in shifted:
        if p % 3:
            continue
        d = p // 3
        if d in shifted:
            n2 += 1
        if 2 * d in shifted:
            n1 += 1
    return n1 + n2


def both_ends(pts: list[int]) -> tuple[int, int, int]:
    left = end_score(pts)
    right = end_score([-p for p in pts])
    return left, right, min(left, right)


def budget(n: int) -> float:
    return 2 * (n - 1) / 3


def scan_exhaustive(n: int, dmax: int) -> dict:
    cap = budget(n)
    worst = -1.0
    worst_s: list[int] = []
    n_over = 0
    n_sets = 0
    best_t = interval_t(n)
    best_t_s: list[int] = list(range(n))
    for comb in itertools.combinations(range(1, dmax + 1), n - 1):
        s = [0] + list(comb)
        n_sets += 1
        L, R, m = both_ends(s)
        ratio = m / (n - 1) if n > 1 else 0.0
        if ratio > worst:
            worst = ratio
            worst_s = s
        if m > cap + 1e-12:
            n_over += 1
            if n_over <= 5:
                print(f"  OVER n={n} {s} L={L} R={R} cap={cap:.4f} T={t_count(s)}")
        t = t_count(s)
        if t > best_t:
            best_t = t
            best_t_s = s
    return {
        "n": n,
        "dmax": dmax,
        "n_sets": n_sets,
        "n_over_budget": n_over,
        "worst_min_ratio": worst,
        "worst_set": worst_s,
        "T_max": best_t,
        "T_max_set": best_t_s,
        "T_interval": interval_t(n),
        "budget": cap,
    }


def named_sets() -> list[tuple[str, list[int]]]:
    rows = [
        ("interval_9", list(range(9))),
        ("almost_9", list(range(8)) + [9]),
        ("n3_013", [0, 1, 3]),
        ("n6_hole", [0, 1, 2, 3, 4, 6]),
        ("n7_sparse", [0, 3, 6, 8, 9, 12, 18]),
        ("plus1_n12", list(range(11)) + [12]),
        ("two_int", list(range(6)) + list(range(12, 18))),
        ("gp2", [0, 1, 2, 4, 8, 16, 32]),
        ("E_2_2", [-2 - 4, -2 - 2, -2, -1, 0, 1, 2, 4, 6]),
    ]
    # interval plus 3-tail
    m = 6
    tail = list(range(m + 1)) + [3 * k for k in range(1, m + 1)]
    rows.append(("int_3tail", sorted(set(tail))))
    return rows


def random_scan(n: int, trials: int, dmax: int, rng: random.Random) -> dict:
    cap = budget(n)
    n_over = 0
    worst = -1.0
    worst_s: list[int] = []
    for _ in range(trials):
        s = sorted(rng.sample(range(dmax), n))
        L, R, m = both_ends(s)
        ratio = m / (n - 1)
        if ratio > worst:
            worst = ratio
            worst_s = s
        if m > cap + 1e-12:
            n_over += 1
    return {
        "n": n,
        "trials": trials,
        "dmax": dmax,
        "n_over_budget": n_over,
        "worst_min_ratio": worst,
        "worst_set": worst_s,
    }


def main() -> None:
    print("=== named ===")
    named_rows = []
    for name, s in named_sets():
        n = len(s)
        L, R, m = both_ends(s)
        cap = budget(n)
        t = t_count(s)
        row = {
            "name": name,
            "n": n,
            "L": L,
            "R": R,
            "min": m,
            "budget": cap,
            "over": m > cap + 1e-12,
            "T": t,
            "T_I": interval_t(n),
            "S": s,
        }
        named_rows.append(row)
        print(
            f"{name:12s} n={n:2d} L={L:2d} R={R:2d} min={m:2d} "
            f"cap={cap:.3f} over={row['over']} T={t} I={interval_t(n)}"
        )

    print("=== exhaustive small n ===")
    exh = []
    for n, dmax in [(3, 18), (4, 16), (5, 16), (6, 16), (7, 18), (8, 16), (9, 14)]:
        rec = scan_exhaustive(n, dmax)
        exh.append(rec)
        print(
            f"exh n={n} dmax={dmax} sets={rec['n_sets']} over={rec['n_over_budget']} "
            f"worst_ratio={rec['worst_min_ratio']:.4f} set={rec['worst_set']} "
            f"Tmax={rec['T_max']} I={rec['T_interval']}",
            flush=True,
        )

    print("=== random ===")
    rng = random.Random(20260827)
    rnd = []
    for n in (10, 12, 15, 18, 24, 30):
        rec = random_scan(n, 4000, max(6 * n, 40), rng)
        rnd.append(rec)
        print(
            f"rand n={n} over={rec['n_over_budget']} "
            f"worst_ratio={rec['worst_min_ratio']:.4f} set={rec['worst_set']}",
            flush=True,
        )

    out = {
        "named": named_rows,
        "exhaustive": exh,
        "random": rnd,
        "any_over": any(r["n_over_budget"] for r in exh + rnd)
        or any(r["over"] for r in named_rows),
    }
    Path(__file__).resolve().parent.joinpath("certs/endpoint_scan.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print("any_over", out["any_over"])


if __name__ == "__main__":
    main()
