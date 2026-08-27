"""Census of middle points with fibre ratio >= 1.6.

If that count stays O(1), a split of the 1/2 fibre sum gives
gamma <= 4/9.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count import t_count  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explore_families import almost_interval, double_gp, e_km, f_km  # noqa: E402


def rich_middle(pts: list[int], tau: float = 1.6) -> dict:
    a = sorted(pts)
    n = len(a)
    present = set(a)
    rich = []
    t = 0
    for j, z in enumerate(a):
        L = j
        R = n - 1 - j
        m = min(L, R)
        lam = mu = 0
        for y in a:
            x = 3 * z - 2 * y
            if x in present:
                t += 1
                if y < z:
                    lam += 1
                elif y > z:
                    mu += 1
        ratio = (lam + mu) / m if m else 0.0
        if m >= n / 3 and ratio + 1e-15 >= tau:
            rich.append(
                {
                    "j": j,
                    "z": z,
                    "L": L,
                    "R": R,
                    "lam": lam,
                    "mu": mu,
                    "ratio": ratio,
                }
            )
    return {"n": n, "T": t, "n_rich": len(rich), "rich": rich}


def main() -> None:
    tau = 1.6
    rows = []
    print("=== named / families ===")
    named = {
        "I30": list(range(30)),
        "I90": list(range(90)),
        "almost30": almost_interval(30),
        "almost90": almost_interval(90),
        "n7": [0, 3, 6, 8, 9, 12, 18],
        "n9": [0, 2, 3, 4, 6, 8, 9, 10, 12],
        "n10": [0, 6, 9, 12, 18, 20, 24, 27, 30, 36],
        "n11": [0, 18, 27, 36, 48, 54, 60, 72, 81, 90, 108],
        "gp8": double_gp(8),
        "E44": e_km(8, 8),
        "F44": f_km(8, 8),
        "two": list(range(20)) + list(range(40, 60)),
    }
    max_k = 0
    for name, s in named.items():
        rec = rich_middle(s, tau)
        rec["name"] = name
        rows.append(rec)
        max_k = max(max_k, rec["n_rich"])
        print(f"  {name:10s} n={rec['n']:3d} T={rec['T']:5d} rich={rec['n_rich']}")

    print("=== exhaustive n=6..8 ===")
    for n, dmax in [(6, 16), (7, 16), (8, 15)]:
        worst = 0
        worst_s = []
        for comb in itertools.combinations(range(1, dmax + 1), n - 1):
            s = [0] + list(comb)
            rec = rich_middle(s, tau)
            if rec["n_rich"] > worst:
                worst = rec["n_rich"]
                worst_s = s
        print(f"  n={n} dmax={dmax} max_rich={worst} ex={worst_s}")
        max_k = max(max_k, worst)

    print("=== random ===")
    rng = random.Random(1)
    rand_max = 0
    for n in (12, 18, 24, 36, 48):
        local = 0
        for _ in range(300):
            s = sorted(rng.sample(range(6 * n), n))
            rec = rich_middle(s, tau)
            local = max(local, rec["n_rich"])
        print(f"  rand n={n} max_rich={local}")
        rand_max = max(rand_max, local)
    max_k = max(max_k, rand_max)

    print("max_K_seen", max_k)
    Path(__file__).resolve().parent.joinpath("certs/rich_middle.json").write_text(
        json.dumps({"tau": tau, "max_K_seen": max_k, "named": rows}, indent=2)
        + "\n"
    )


if __name__ == "__main__":
    main()
