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
part-count).  A solver cutoff is not a proof of the maximum and is
not a proof of emptiness.  A feasible U with verified_ns >= k+1 shows
the slice is not empty by part-count.  Star-free emptiness is not an
unrestricted bound.  This does not claim tau5 = 40.
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


def count_contained(seeds, U_mask):
    return sum(1 for s in seeds if (s & ~U_mask) == 0)


def mask_of(idxs):
    m = 0
    for i in idxs:
        m |= 1 << i
    return m


def star_meets(U_mask, stars):
    return [(U_mask & mask_of(S)).bit_count() for S in stars]


def verify_U(seeds, stars, idxs, k, star_free):
    if len(idxs) != k or len(set(idxs)) != k:
        return None
    if any(j < 0 or j >= 40 for j in idxs):
        return None
    U = mask_of(idxs)
    meets = star_meets(U, stars)
    if star_free and any(t > 6 for t in meets):
        return None
    return {
        "U": sorted(idxs),
        "verified_ns": count_contained(seeds, U),
        "star_meets": meets,
    }


def extract_U(x, n=40):
    return [j for j in range(n) if x[j] >= 0.5]


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
    witness = None
    if res.x is not None:
        witness = verify_U(seeds, stars, extract_U(res.x), k, star_free)
    incumbent = witness["verified_ns"] if witness else None
    code = int(res.status)
    if code == 0 and incumbent is not None:
        return incumbent, "ok", elapsed, witness
    if code == 1:
        return incumbent, "cutoff", elapsed, witness
    if code == 2:
        return None, "infeasible", elapsed, witness
    msg = str(res.message).strip() or f"status={code}"
    return incumbent, f"other:{msg}", elapsed, witness


def rec_of(k, ns, status, elapsed, witness, star_free):
    verified = witness["verified_ns"] if witness else None
    # Proven empty only when the solver certifies an optimum below k+1
    # (or the family is infeasible).  Cutoff is not a proof of emptiness.
    # A verified witness with ns >= k+1 shows the slice is not empty
    # by part-count; that is a lower-bound fact, not a maximum.
    empty = False
    if status == "ok" and ns is not None and ns < k + 1:
        empty = True
    if status == "infeasible":
        empty = True
    rec = {
        "k": k,
        "n1": 40 - k,
        "need": k + 1,
        "star_free": star_free,
        "max_ns": ns if status == "ok" else None,
        "incumbent": verified,
        "status": status,
        "empty_by_part_count": empty,
        "seconds": round(elapsed, 3),
    }
    if witness:
        rec["U"] = witness["U"]
        rec["verified_ns"] = witness["verified_ns"]
        rec["star_meets"] = witness["star_meets"]
        rec["promising_witness"] = witness["verified_ns"] >= k + 1
    return rec


def greedy_unrestricted(seeds, stars, k):
    """Opposite coordinate-stars (16 roots, 32 four-seeds), then greedy."""
    U = mask_of(stars[0]) | mask_of(stars[1])
    used = {i for i in range(40) if (U >> i) & 1}
    while len(used) < k:
        best, bestc = None, -1
        for i in range(40):
            if i in used:
                continue
            c = count_contained(seeds, U | (1 << i))
            if c > bestc:
                bestc, best = c, i
        used.add(best)
        U |= 1 << best
    return sorted(used)


def greedy_star_free(seeds, stars, k):
    star_of = [[] for _ in range(40)]
    for t, S in enumerate(stars):
        for j in S:
            star_of[j].append(t)
    U = 0
    used = set()
    meets = [0] * 10
    while len(used) < k:
        best, bestc = None, -1
        for i in range(40):
            if i in used:
                continue
            if any(meets[t] >= 6 for t in star_of[i]):
                continue
            c = count_contained(seeds, U | (1 << i))
            if c > bestc:
                bestc, best = c, i
        if best is None:
            break
        used.add(best)
        U |= 1 << best
        for t in star_of[best]:
            meets[t] += 1
    return sorted(used)


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
            "HiGHS MILP, leftover |U|=k in {19,20,21}; 22..24 only if "
            "cheap.  max_ns is the proven maximum (null on cutoff).  "
            "incumbent / verified_ns is an independently recounted "
            "contained-seed count for the solver's U.  "
            "empty_by_part_count is true only on a proven max_ns < k+1 "
            "or an infeasible family.  Cutoff is not a proof of the "
            "maximum and not a proof of emptiness.  A promising_witness "
            "(verified_ns >= k+1) shows the slice is not empty by "
            "part-count.  Star-free facts are not an unrestricted bound "
            "and do not move 40 <= tau5 <= 44."
        ),
    }

    for k in (4, 7):
        ns, status, elapsed, witness = max_ns(
            seeds, stars, k, True, TIME_LIMIT, four_hosted
        )
        rec = rec_of(k, ns, status, elapsed, witness, True)
        report["replay_star_free_small"][str(k)] = rec
        print(
            f"replay k={k} star_free max_ns={rec['max_ns']} "
            f"status={status} empty={rec['empty_by_part_count']} "
            f"{elapsed:.2f}s",
            flush=True,
        )

    leftover = [19, 20, 21]
    extra = [22, 23, 24]
    cheap = True

    def run_k(k, milp_solve=True):
        nonlocal cheap
        slice_rec = {"k": k, "n1": 40 - k, "need": k + 1}
        for name, star_free, ctor in (
            ("unrestricted", False, greedy_unrestricted),
            ("star_free", True, greedy_star_free),
        ):
            ctor_idxs = ctor(seeds, stars, k)
            ctor_w = verify_U(seeds, stars, ctor_idxs, k, star_free)
            slice_rec[f"{name}_construction"] = {
                "verified_ns": ctor_w["verified_ns"] if ctor_w else None,
                "promising_witness": bool(
                    ctor_w and ctor_w["verified_ns"] >= k + 1
                ),
                "U": ctor_w["U"] if ctor_w else ctor_idxs,
            }
            if not milp_solve:
                slice_rec[name] = {
                    "k": k,
                    "n1": 40 - k,
                    "need": k + 1,
                    "star_free": star_free,
                    "max_ns": None,
                    "incumbent": None,
                    "status": "skipped",
                    "empty_by_part_count": False,
                }
                print(
                    f"k={k} {name} skipped construction_ns="
                    f"{slice_rec[f'{name}_construction']['verified_ns']}",
                    flush=True,
                )
                continue
            ns, status, elapsed, witness = max_ns(
                seeds, stars, k, star_free, TIME_LIMIT,
                four_hosted if star_free else None,
            )
            rec = rec_of(k, ns, status, elapsed, witness, star_free)
            slice_rec[name] = rec
            if status == "cutoff" or elapsed >= 0.8 * TIME_LIMIT:
                cheap = False
            print(
                f"k={k} {name} max_ns={rec['max_ns']} "
                f"incumbent={rec.get('incumbent')} status={status} "
                f"empty={rec['empty_by_part_count']} "
                f"promising={rec.get('promising_witness')} "
                f"{elapsed:.2f}s",
                flush=True,
            )
        report["slices"][str(k)] = slice_rec

    for k in leftover:
        run_k(k, milp_solve=True)
    if cheap:
        for k in extra:
            run_k(k, milp_solve=True)
    else:
        report["skipped_22_24_milp"] = (
            "not cheap: a leftover solve hit cutoff or used most of "
            "the 30s budget; 22..24 recorded by greedy construction only"
        )
        print(report["skipped_22_24_milp"], flush=True)
        for k in extra:
            run_k(k, milp_solve=False)

    path = HERE / "n1_partcount.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
