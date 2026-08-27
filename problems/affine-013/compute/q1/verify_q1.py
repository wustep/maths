"""q1 checks: second T-count, almost-interval identity, named residue.

Does not claim a constant below 1/2. Writes certs/q1.json.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(HERE))

from count import interval_t, t_count  # noqa: E402
from ends import end_scores, n1_n2, t_from_hooks  # noqa: E402


def ceil_n2_half(n: int) -> int:
    return (n * n + 1) // 2


def almost_interval(n: int) -> list[int]:
    return list(range(n - 1)) + [n]


def almost_t_formula(n: int) -> int:
    """T({0,...,n-2,n}). For n=3m this is n^2/3 + 1."""
    if n % 3 == 0:
        m = n // 3
        return 3 * m * m + 1
    return t_count(almost_interval(n))


def hole_pairs(n: int) -> list[tuple[int, int]]:
    """Pairs (x,y) in S^2 with (x+2y)/3 equal to the hole n-1."""
    s = set(almost_interval(n))
    hole = n - 1
    hits = []
    for x in s:
        for y in s:
            tot = x + 2 * y
            if tot % 3 == 0 and tot // 3 == hole:
                hits.append((x, y))
    return hits


def main() -> None:
    rng = random.Random(20260827)
    ok = True

    # 1. T = n + sum (N1+N2), a different loop from count.t_count
    identity_sets = [
        list(range(n))
        for n in range(1, 25)
    ] + [
        [0, 1, 3],
        [0, 1, 2, 3, 4, 6],
        [0, 3, 6, 8, 9, 12, 18],
        [0, 2, 3, 4, 6],
        [0, 2, 3, 4, 6, 8, 9, 10, 12],
        [0, 6, 9, 12, 18, 20, 24, 27, 30, 36],
        [0, 18, 27, 36, 48, 54, 60, 72, 81, 90, 108],
        almost_interval(36),
    ]
    for n in range(3, 16):
        dmax = n + 8
        for _ in range(8):
            identity_sets.append(sorted(rng.sample(range(dmax), n)))

    n_id = 0
    for s in identity_sets:
        t0 = t_count(s)
        t1 = t_from_hooks(s)
        n = len(s)
        if t0 != t1 or t0 > ceil_n2_half(n):
            print("FAIL identity", s, t0, t1)
            ok = False
            break
        n_id += 1
    print(f"hook identity sets={n_id} ok={ok}")

    # 2. almost-interval closed form, n=3m, unique hole pair
    almost_rows = []
    almost_ok = True
    for m in range(1, 41):
        n = 3 * m
        s = almost_interval(n)
        t = t_count(s)
        formula = 3 * m * m + 1
        if t != formula or t != t_from_hooks(s):
            print("FAIL almost formula", n, t, formula)
            almost_ok = False
            break
        hits = hole_pairs(n)
        if hits != [(n - 3, n)]:
            print("FAIL unique hole pair", n, hits)
            almost_ok = False
            break
        # residue sizes on [0,n]\\{n-1}
        a = [0, 0, 0]
        for x in s:
            a[x % 3] += 1
        if a != [m + 1, m, m - 1]:
            print("FAIL residues", n, a)
            almost_ok = False
            break
        # A0^2+A1^2+A2^2 = 3m^2+2, one pair dies in the hole
        res_bound = a[0] ** 2 + a[1] ** 2 + a[2] ** 2
        if res_bound != 3 * m * m + 2 or t != res_bound - 1:
            print("FAIL residue vs T", n, res_bound, t)
            almost_ok = False
            break
        almost_rows.append({"n": n, "T": t, "formula": formula, "hole_pair": hits[0]})
    print(f"almost-interval n=3m through {3*40} ok={almost_ok}")
    ok = ok and almost_ok

    # 3. 2/3 endpoint budget fails; those sets do not beat the interval
    over_budget = [
        [0, 2, 3, 4, 6],
        [0, 2, 3, 6, 7, 9],
        [0, 3, 4, 6, 8, 9, 12],
        [0, 2, 3, 4, 6, 8, 9, 10, 12],
    ]
    over_rows = []
    over_ok = True
    for s in over_budget:
        n = len(s)
        L, R = end_scores(s)
        cap = 2 * (n - 1) / 3
        t = t_count(s)
        row = {
            "S": s,
            "n": n,
            "end_L": L,
            "end_R": R,
            "min_end": min(L, R),
            "two_thirds_budget": cap,
            "over": min(L, R) > cap,
            "T": t,
            "T_interval": interval_t(n),
            "ratio": t / (n * n),
        }
        over_rows.append(row)
        if not row["over"] or t > interval_t(n) or t > ceil_n2_half(n):
            print("FAIL over-budget row", row)
            over_ok = False
        print(
            f"over n={n} L={L} R={R} cap={cap:.4f} T={t} I={interval_t(n)}"
        )
    ok = ok and over_ok

    # 4. high both-end ratios; T still <= interval; not an infinite-family seed
    high = [
        ("n9_7/8", [0, 2, 3, 4, 6, 8, 9, 10, 12]),
        ("n10_8/9", [0, 6, 9, 12, 18, 20, 24, 27, 30, 36]),
        ("n11_9/10", [0, 18, 27, 36, 48, 54, 60, 72, 81, 90, 108]),
    ]
    high_rows = []
    high_ok = True
    for name, s in high:
        n = len(s)
        L, R = end_scores(s)
        t = t_count(s)
        row = {
            "name": name,
            "S": s,
            "n": n,
            "end_L": L,
            "end_R": R,
            "min_end_ratio": min(L, R) / (n - 1),
            "T": t,
            "T_interval": interval_t(n),
            "ratio": t / (n * n),
        }
        high_rows.append(row)
        if t > interval_t(n) or min(L, R) / (n - 1) < 0.87:
            print("FAIL high-end row", row)
            high_ok = False
        print(
            f"high {name} L={L} R={R} ratio={row['min_end_ratio']:.4f} "
            f"T={t} I={interval_t(n)}"
        )
    ok = ok and high_ok

    # 5. families: ratio heads toward 1/3, none above 1/3 + 2/n at large n
    fam_ok = True
    fam_rows = []
    for m in (5, 10, 20, 40):
        n = 3 * m
        s = almost_interval(n)
        t = t_count(s)
        fam_rows.append(
            {
                "fam": "almost",
                "n": n,
                "T": t,
                "I": interval_t(n),
                "ratio": t / (n * n),
            }
        )
        if t != interval_t(n) + 1:
            fam_ok = False
    # periodized n=9 seed
    seed = [0, 2, 3, 4, 6, 8, 9, 10, 12]
    for k in (1, 3, 5, 7):
        s = sorted({x + 12 * i for i in range(k) for x in seed})
        n = len(s)
        t = t_count(s)
        fam_rows.append(
            {
                "fam": f"period12_k{k}",
                "n": n,
                "T": t,
                "I": interval_t(n),
                "ratio": t / (n * n),
            }
        )
        if t > interval_t(n) and k > 1:
            # k=1 matches the interval; larger k is below
            print("unexpected period beat", k, t, interval_t(n))
            fam_ok = False
        if k >= 5 and t / (n * n) > 1 / 3 + 2 / n:
            print("period ratio too high", k, t / (n * n))
            fam_ok = False
    print(f"families ok={fam_ok}")
    ok = ok and fam_ok

    # 6. exhaustive: 2/3 budget can fail, max T still the known small-n picture
    exh = []
    exh_ok = True
    for n, dmax in [(5, 12), (6, 14), (7, 16)]:
        n_over = 0
        tmax = 0
        for comb in itertools.combinations(range(1, dmax + 1), n - 1):
            s = [0] + list(comb)
            L, R = end_scores(s)
            if min(L, R) > 2 * (n - 1) / 3:
                n_over += 1
            tmax = max(tmax, t_from_hooks(s))
        exh.append(
            {
                "n": n,
                "dmax": dmax,
                "n_over_two_thirds": n_over,
                "T_max": tmax,
                "T_interval": interval_t(n),
                "half": ceil_n2_half(n),
            }
        )
        if tmax > ceil_n2_half(n):
            exh_ok = False
        print(
            f"exh n={n} dmax={dmax} over={n_over} Tmax={tmax} "
            f"I={interval_t(n)} half={ceil_n2_half(n)}"
        )
    ok = ok and exh_ok

    out = {
        "claim": "no new constant; gamma still <= 1/2, conjecture 1/3 open",
        "ok": ok,
        "hook_identity_sets": n_id,
        "almost_interval": {
            "formula": "n=3m => T({0..n-2,n}) = n^2/3 + 1",
            "checked_m_max": 40,
            "unique_hole_pair": "(n-3, n)",
            "ok": almost_ok,
        },
        "two_thirds_budget_fails": over_rows,
        "high_end_ratio": high_rows,
        "families": fam_rows,
        "exhaustive_over_budget": exh,
        "constant_moved": False,
    }
    HERE.joinpath("certs/q1.json").write_text(json.dumps(out, indent=2) + "\n")
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
