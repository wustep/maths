#!/usr/bin/env python3
"""Szöllősi-style compatible-vector graph on the known 40-point angle set.

Fix a 5-point basis B of pairwise kissing vectors of squared-norm 2.  A
candidate extra vector is determined by its inner-product vector t ∈ T^5
via v = G^{-1} t, and lies on the sphere iff t^T G^{-1} t = 2.  The finite
set of such v, together with B, is a compatibility graph.  A clique of
size 41 would be a new exact kissing code whose inner products with the
basis lie in T.

T is the union of the four published 40-point angle sets, all rational.
G is rational for every published basis, so the search is exact.  A max
clique of size 40 is residue for this ansatz, not a lower bound of 40
(that bound is already realised).
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import CONFIGS, _dot, _norm2
from exact_duals import ge_q

F = Fraction

T_ALL = [
    F(-1), F(-4, 5), F(-3, 4), F(-1, 2), F(-3, 10), F(-1, 4),
    F(0), F(1, 5), F(1, 2),
]


def gram(B):
    n = len(B)
    return [[_dot(B[i], B[j]) for j in range(n)] for i in range(n)]


def solve_basis(B, t):
    """Solve G x = t over Q and return the combination Σ x_i B_i."""
    G = gram(B)
    try:
        x = ge_q(G, list(t))
    except ValueError:
        return None
    v = [F(0)] * 5
    for xi, b in zip(x, B):
        for k in range(5):
            v[k] += xi * b[k]
    return tuple(v)


def first_basis(pts):
    """First 5 linearly independent points."""
    chosen = []
    rows = []
    for p in pts:
        trial = rows + [p]
        # rank test:  try to find a 5×5 or k×k minor
        if _rank_q(trial) == len(trial):
            chosen.append(p)
            rows.append(p)
            if len(chosen) == 5:
                return chosen
    return None


def _rank_q(rows):
    """Row rank over Q by Gaussian elimination."""
    M = [list(r) for r in rows]
    m, n = len(M), 5
    r = 0
    for c in range(n):
        pivot = None
        for i in range(r, m):
            if M[i][c] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        piv = M[r][c]
        M[r] = [v / piv for v in M[r]]
        for i in range(m):
            if i == r:
                continue
            fac = M[i][c]
            if fac:
                M[i] = [M[i][k] - fac * M[r][k] for k in range(n)]
        r += 1
        if r == m:
            break
    return r


def candidates_from_basis(B, T):
    found = []
    # Inner products against basis points of squared-norm 2: <v, b> ∈ {2} ∪ 2T
    # because published T is *normalised* (<u,w>/2).  We work unnormalised:
    # kissing means <v,w> ≤ 1, and T_unnorm = 2T.
    Tun = [2 * t for t in T]
    for t in product(Tun, repeat=5):
        v = solve_basis(B, t)
        if v is None:
            continue
        if _norm2(v) != F(2):
            continue
        if any(_dot(v, b) > 1 for b in B):
            continue
        found.append(v)
    # unique
    seen = set()
    uniq = []
    for v in found:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def max_clique(pts, seed_idx):
    n = len(pts)
    ok = [0] * n
    for i, j in combinations(range(n), 2):
        if _dot(pts[i], pts[j]) <= 1:
            ok[i] |= 1 << j
            ok[j] |= 1 << i
    seed = 0
    for i in seed_idx:
        seed |= 1 << i
    best = seed.bit_count()
    best_mask = seed

    def rec(used, start, sz):
        nonlocal best, best_mask
        rem = 0
        for v in range(start, n):
            # v adjacent to all used?
            if (ok[v] & used) == used:
                rem += 1
        if sz + rem <= best:
            return
        if sz > best:
            best, best_mask = sz, used
        for v in range(start, n):
            if (ok[v] & used) != used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(seed, 0, seed.bit_count())
    rec(0, 0, 0)
    return best, best_mask


def run_config(name, builder, T):
    pts = builder()
    B = first_basis(pts)
    if B is None:
        return {"name": name, "error": "no basis"}
    # Restrict T slightly for the product: the full 9^5 = 59049 is fine.
    cands = candidates_from_basis(B, T)
    # Include the original 40 points that kiss the basis (they should).
    pool = []
    seen = set()
    for v in list(B) + cands + pts:
        if v not in seen and _norm2(v) == F(2):
            if all(_dot(v, b) <= 1 for b in B):
                seen.add(v)
                pool.append(v)
    # Clique search only if the pool is modest.
    rec = {
        "name": name,
        "basis_size": len(B),
        "n_T5_on_sphere": len(cands),
        "pool": len(pool),
    }
    if len(pool) <= 56:
        seed = [pool.index(p) for p in pts if p in seen][:40]
        # map original points that survived
        seed_idx = []
        sset = set(pts)
        for i, v in enumerate(pool):
            if v in sset:
                seed_idx.append(i)
        best, mask = max_clique(pool, seed_idx)
        rec["max_clique"] = best
        rec["beats_40"] = best > 40
    else:
        rec["max_clique"] = None
        rec["beats_40"] = False
        rec["note"] = f"pool {len(pool)} too large for exact clique; no 41 claimed"
    return rec


def main() -> int:
    report = {}
    for name, builder in CONFIGS.items():
        print(f"{name}: generating T^5 candidates ...", flush=True)
        rec = run_config(name, builder, T_ALL)
        report[name] = rec
        print(f"  {rec}", flush=True)
    out = Path(__file__).resolve().parent / "szollosi_candidates.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
