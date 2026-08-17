"""Independent check of T(S) <= ceil(n^2 / 2).

For A = {a_1 < ... < a_n} and z = a_j, the map
    y |-> 3z - 2y
sends {y in A : y < z} into {x : x > z} and
      {y in A : y > z} into {x : x < z},
each injectively. Hence the fibre at z has size at most
    1 + 2 min(j-1, n-j).
Summing over j recovers ceil(n^2/2).

This script does not assume that identity: it recomputes both the
fibre sizes and the closed form from scratch.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count import interval_t, t_count  # noqa: E402


def ceil_n2_half(n: int) -> int:
    return (n * n + 1) // 2


def sum_min_formula(n: int) -> int:
    """n + 2 * sum_j min(j-1, n-j), computed by a loop (not the closed form)."""
    s = n
    for j in range(1, n + 1):
        s += 2 * min(j - 1, n - j)
    return s


def fibre_bound_and_actual(pts: list[int]) -> tuple[int, int, bool]:
    """Return (T_actual, sum of per-z bounds, all fibres obey the injection)."""
    a = sorted(pts)
    n = len(a)
    present = set(a)
    t = 0
    bound_sum = 0
    ok = True
    for j, z in enumerate(a):
        left = a[:j]
        right = a[j + 1 :]
        n_left = 0
        n_right = 0
        for y in a:
            x = 3 * z - 2 * y
            if x in present:
                t += 1
                if y < z:
                    n_left += 1
                    if not (x > z):
                        ok = False
                    if x in left:
                        ok = False
                elif y > z:
                    n_right += 1
                    if not (x < z):
                        ok = False
                    if x in right:
                        ok = False
        cap = 1 + 2 * min(len(left), len(right))
        if n_left + n_right + 1 > cap:
            ok = False
        if n_left > min(len(left), len(right)):
            ok = False
        if n_right > min(len(left), len(right)):
            ok = False
        bound_sum += cap
    if t != t_count(a):
        ok = False
    return t, bound_sum, ok


def main() -> None:
    # 1. numerical identity
    identity_ok = all(
        sum_min_formula(n) == ceil_n2_half(n) for n in range(0, 400)
    )
    print("sum identity n<=399:", identity_ok)

    # 2. interval never exceeds
    interval_ok = all(interval_t(n) <= ceil_n2_half(n) for n in range(0, 500))
    print("interval <= bound n<=499:", interval_ok)

    # 3. exhaustive n-subsets of {0..dmax} for small n
    exhaustive = []
    exh_ok = True
    for n, dmax in [(3, 12), (4, 12), (5, 12), (6, 12), (7, 14)]:
        worst = 0
        nsets = 0
        for comb in itertools.combinations(range(1, dmax + 1), n - 1):
            s = [0] + list(comb)
            t, bsum, ok = fibre_bound_and_actual(s)
            nsets += 1
            if t > worst:
                worst = t
            if (not ok) or t > ceil_n2_half(n) or bsum != ceil_n2_half(n):
                exh_ok = False
                print("FAIL exhaustive", s, t, bsum, ok)
                break
        exhaustive.append(
            {
                "n": n,
                "dmax": dmax,
                "n_sets": nsets,
                "T_max_observed": worst,
                "bound": ceil_n2_half(n),
                "T_interval": interval_t(n),
            }
        )
        print(
            f"exhaustive n={n} dmax={dmax} sets={nsets} "
            f"Tmax={worst} bound={ceil_n2_half(n)} I={interval_t(n)}"
        )
        if not exh_ok:
            break

    # 4. random larger sets
    rng = random.Random(20260817)
    rand_ok = True
    nrand = 0
    for n in range(2, 61):
        dmax = max(n * 6, n + 10)
        for _ in range(40):
            s = sorted(rng.sample(range(dmax), n))
            t, bsum, ok = fibre_bound_and_actual(s)
            nrand += 1
            if (not ok) or t > ceil_n2_half(n) or bsum != ceil_n2_half(n):
                rand_ok = False
                print("FAIL random", s, t, bsum, ok)
                break
        if not rand_ok:
            break
    print(f"random sets checked: {nrand} ok={rand_ok}")

    # 5. named witnesses
    witnesses = {
        "interval_30": list(range(30)),
        "n3_013": [0, 1, 3],
        "n6_hole": [0, 1, 2, 3, 4, 6],
        "n7_sparse": [0, 3, 6, 8, 9, 12, 18],
        "n9_hole": [0, 1, 2, 3, 4, 5, 6, 7, 9],
        "plus1_n36": list(range(35)) + [36],
    }
    wit_rows = []
    wit_ok = True
    for name, s in witnesses.items():
        t, bsum, ok = fibre_bound_and_actual(s)
        n = len(s)
        row = {
            "name": name,
            "n": n,
            "T": t,
            "bound": ceil_n2_half(n),
            "T_interval": interval_t(n),
            "fibre_ok": ok,
            "bound_sum": bsum,
        }
        wit_rows.append(row)
        if (not ok) or t > ceil_n2_half(n):
            wit_ok = False
            print("FAIL witness", row)
        print(
            f"witness {name} n={n} T={t} I={interval_t(n)} bound={ceil_n2_half(n)}"
        )

    all_ok = identity_ok and interval_ok and exh_ok and rand_ok and wit_ok
    out = {
        "bound": "T(S) <= ceil(n^2 / 2)",
        "implies": "gamma_{1,2,-3} <= 1/2",
        "beats": "Hardy-Littlewood / Aaronson 3/4",
        "ok": all_ok,
        "identity_ok": identity_ok,
        "interval_ok": interval_ok,
        "exhaustive": exhaustive,
        "n_random": nrand,
        "random_ok": rand_ok,
        "witnesses": wit_rows,
    }
    Path(__file__).resolve().parent.joinpath("certs/half_bound.json").write_text(
        json.dumps(out, indent=2) + "\n"
    )
    print("ALL OK" if all_ok else "FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
