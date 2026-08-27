#!/usr/bin/env python3
"""Part-count on leftover |U| = k (n1 = 40-k, k >= 19).

240 seeds on the 40 D5 roots (160 four-sets, 80 six-sets).  A k-set U
is promising for a 41-set only if it contains at least k+1 seeds
(enough groups to hope for an extras-clique of size k+1).

This maximises the contained-seed count among k-sets via SciPy HiGHS,
with an optional star-free cut: each of the 10 coordinate-stars
(axis i, sign s; the 8 roots with x_i = s*4) meets U in at most 6
points.  Time limit 30s per solve.

If the proven maximum is < k+1 the slice has no 41-set (empty by
part-count).  A solver cutoff is not a proof.  Star-free emptiness is
not an unrestricted bound.  This does not claim tau5 = 40.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from sphere import extras_and_groups  # noqa: E402

TIME_LIMIT = 30.0


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = [j for j, r in enumerate(D) if r[i] == s * 4]
            assert len(bits) == 8
            out.append(bits)
    return out


def four_seeds_by_star(seeds, stars):
    """Four-seeds hosted by each star (each four-seed lives in one star)."""
    hosted = [[] for _ in stars]
    star_masks = []
    for S in stars:
        m = 0
        for j in S:
            m |= 1 << j
        star_masks.append(m)
    for g, seed in enumerate(seeds):
        if seed.bit_count() != 4:
            continue
        hits = [t for t, S in enumerate(star_masks) if (seed & S) == seed]
        assert len(hits) == 1
        hosted[hits[0]].append(g)
    assert all(len(h) == 16 for h in hosted)
    return hosted


def max_ns(seeds, stars, k, star_free, time_limit, four_hosted=None):
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

    if star_free:
        for S in stars:
            row = np.zeros(width)
            for j in S:
                row[j] = 1
            rows.append(row)
            lb.append(0)
            ub.append(6)
        # Valid: a 6-subset of a star holds at most 4 of its 16 four-seeds
        # (one from each opposite pair; max product 2*2*1*1 = 4).
        if four_hosted is not None:
            for hosted in four_hosted:
                row = np.zeros(width)
                for g in hosted:
                    row[n + g] = 1
                rows.append(row)
                lb.append(0)
                ub.append(4)

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
    t0 = time.perf_counter()
    res = milp(
        c,
        integrality=np.ones(width, dtype=int),
        bounds=Bounds(0, 1),
        constraints=cons,
        options={"disp": False, "time_limit": time_limit},
    )
    elapsed = time.perf_counter() - t0
    incumbent = None
    if res.x is not None and res.fun is not None and np.isfinite(res.fun):
        incumbent = int(round(-res.fun))
    code = int(res.status)
    if code == 0 and incumbent is not None:
        return incumbent, "ok", elapsed, incumbent
    if code == 1:
        return incumbent, "cutoff", elapsed, incumbent
    if code == 2:
        return None, "infeasible", elapsed, incumbent
    msg = str(res.message).strip() or f"status={code}"
    return incumbent, f"other:{msg}", elapsed, incumbent


def rec_of(k, ns, status, elapsed, incumbent, star_free):
    empty = False
    if status == "ok" and ns is not None and ns < k + 1:
        empty = True
    if status == "infeasible":
        # No k-set exists in this family, so no promising U either.
        empty = True
    return {
        "k": k,
        "n1": 40 - k,
        "need": k + 1,
        "star_free": star_free,
        "max_ns": ns,
        "incumbent": incumbent,
        "status": status,
        "empty_by_part_count": empty,
        "seconds": round(elapsed, 3),
    }


def main() -> int:
    G = extras_and_groups(4)
    seeds = list(G["groups"])
    stars = stars_of(G["D"])
    four = [m for m in seeds if m.bit_count() == 4]
    six = [m for m in seeds if m.bit_count() == 6]
    assert len(seeds) == 240
    assert len(four) == 160 and len(six) == 80
    assert len(stars) == 10
    four_hosted = four_seeds_by_star(seeds, stars)

    report = {
        "n_groups": len(seeds),
        "n_four": len(four),
        "n_six": len(six),
        "n_stars": len(stars),
        "time_limit_s": TIME_LIMIT,
        "solver": "scipy.optimize.milp / HiGHS",
        "replay_star_free_small": {},
        "slices": {},
        "comment": (
            "HiGHS MILP, leftover |U|=k in {19,20,21} and cheap "
            "{22,23,24}.  max_ns is the proven maximum contained-seed "
            "count, or the incumbent on cutoff (then not proven).  "
            "empty_by_part_count is true only on a proven max_ns < k+1 "
            "or an infeasible family.  Cutoff is not a proof.  "
            "Star-free emptiness is not an unrestricted bound and does "
            "not move 40 <= tau5 <= 44."
        ),
    }

    # Replay the q4 star-free optima that finished (k=4..7).
    for k in (4, 7):
        ns, status, elapsed, inc = max_ns(
            seeds, stars, k, True, TIME_LIMIT, four_hosted
        )
        rec = rec_of(k, ns, status, elapsed, inc, True)
        report["replay_star_free_small"][str(k)] = rec
        print(
            f"replay k={k} star_free max_ns={ns} status={status} "
            f"empty={rec['empty_by_part_count']} {elapsed:.2f}s",
            flush=True,
        )

    leftover = [19, 20, 21]
    extra = [22, 23, 24]
    cheap = True

    def run_k(k):
        nonlocal cheap
        slice_rec = {"k": k, "n1": 40 - k, "need": k + 1}
        for name, star_free in (("unrestricted", False), ("star_free", True)):
            ns, status, elapsed, inc = max_ns(
                seeds, stars, k, star_free, TIME_LIMIT,
                four_hosted if star_free else None,
            )
            rec = rec_of(k, ns, status, elapsed, inc, star_free)
            slice_rec[name] = rec
            if status == "cutoff" or elapsed >= 0.8 * TIME_LIMIT:
                cheap = False
            print(
                f"k={k} {name} max_ns={ns} status={status} "
                f"empty={rec['empty_by_part_count']} {elapsed:.2f}s",
                flush=True,
            )
        report["slices"][str(k)] = slice_rec

    for k in leftover:
        run_k(k)
    if cheap:
        for k in extra:
            run_k(k)
    else:
        report["skipped_22_24"] = (
            "not cheap: a leftover solve hit cutoff or used most of "
            "the 30s budget"
        )
        print(report["skipped_22_24"], flush=True)

    path = HERE / "n1_partcount.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
