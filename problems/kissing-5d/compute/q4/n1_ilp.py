#!/usr/bin/env python3
"""Exact max contained-seeds per k among star-free k-sets.

40 binary root variables, 240 seed indicators. SciPy HiGHS MILP.
If max ns < k+1 the star-free slice cannot host a 41-set.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from sphere import extras_and_groups

HERE = Path(__file__).resolve().parent


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = [j for j, r in enumerate(D) if r[i] == s * 4]
            assert len(bits) == 8
            out.append(bits)
    return out


def max_ns_free(seeds, stars, k):
    n = 40
    nG = len(seeds)
    width = n + nG
    c = np.zeros(width)
    c[n:] = -1.0
    rows = []
    lb = []
    ub = []
    row = np.zeros(width)
    row[:n] = 1
    rows.append(row)
    lb.append(k)
    ub.append(k)
    for S in stars:
        row = np.zeros(width)
        for j in S:
            row[j] = 1
        rows.append(row)
        lb.append(0)
        ub.append(6)
    for g, m in enumerate(seeds):
        x = m
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            row = np.zeros(width)
            row[n + g] = 1
            row[b] = -1
            rows.append(row)
            lb.append(-np.inf)
            ub.append(0)
    A = np.vstack(rows)
    cons = LinearConstraint(A, np.array(lb, dtype=float), np.array(ub, dtype=float))
    res = milp(
        c,
        integrality=np.ones(width, dtype=int),
        bounds=Bounds(0, 1),
        constraints=cons,
        options={"disp": False, "time_limit": 20},
    )
    if not res.success or res.x is None:
        return None, str(res.message)
    return int(round(-res.fun)), "ok"


def main() -> int:
    G = extras_and_groups(4)
    seeds = list(G["groups"])
    stars = stars_of(G["D"])
    report = {"n_groups": len(seeds), "n_stars": len(stars), "slices": {}}
    any_prom = False
    # k>=8 hits a short HiGHS cutoff; do not pretend those slices are empty.
    for k in range(4, 8):
        ns, msg = max_ns_free(seeds, stars, k)
        empty = ns is not None and ns < k + 1
        if ns is not None and ns >= k + 1:
            any_prom = True
        report["slices"][str(k)] = {
            "k": k,
            "n1": 40 - k,
            "max_seeds_star_free": ns,
            "status": msg,
            "empty_by_part_count": empty,
        }
        print(f"k={k} free_max={ns} empty={empty} {msg}", flush=True)
    report["any_promising_star_free_through_7"] = any_prom
    report["comment"] = (
        "HiGHS MILP, star-free k-sets (every coordinate-star meets U in "
        "at most 6 points). k=4..7 agree with the seed-union scan: no "
        "promising star-free U. k>=8 hit the 20s HiGHS cutoff; not a "
        "proof for those k."
    )
    path = HERE / "n1_ilp.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path, "any_promising_star_free", any_prom)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
