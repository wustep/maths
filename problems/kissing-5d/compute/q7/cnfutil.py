#!/usr/bin/env python3
"""Leftover SAT CNFs for the 1480-point (1/4)Z^5 graph.

A leftover 41-set is extras E plus D5 roots outside U = union miss(E),
with |U| >= 19 and |E| >= |U| + 1.  q4 emptied |U| <= 18.  q6 emptied
every leftover host whose U sits in four D5 coordinate-stars.

UNSAT without a stored native CaDiCaL DRAT is residue.
"""

from __future__ import annotations

import hashlib
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent / "q5"))
sys.path.insert(0, str(HERE.parent))

from sphere import extras_and_groups, ip  # noqa: E402


def stars_of(D):
    out = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            assert bits.bit_count() == 8
            out.append(bits)
    return out


def star_type(comb):
    """(n_full_axes, n_half_axes) for a 5-star combination."""
    axes = [0] * 5
    for s in comb:
        axes[s // 2] += 1
    n2 = sum(1 for a in axes if a == 2)
    n1 = sum(1 for a in axes if a == 1)
    return n2, n1


def load_graph():
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    masks = G["masks"]
    thresh = G["thresh"]
    seeds = list(groups)
    seed_index = {m: i for i, m in enumerate(seeds)}
    return {
        "extras": extras,
        "D": D,
        "groups": groups,
        "masks": masks,
        "thresh": thresh,
        "seeds": seeds,
        "seed_index": seed_index,
        "stars": stars_of(D),
    }


def pool_for_stars(G, comb):
    stars = G["stars"]
    U = 0
    for s in comb:
        U |= stars[s]
    local, local_g, local_miss = [], [], []
    for i, m in enumerate(G["masks"]):
        if m & ~U == 0:
            local.append(i)
            local_g.append(G["seed_index"][m])
            local_miss.append(m)
    return U, local, local_g, local_miss


def leftover_tight_cnf(G, local, local_g, local_miss, Uhost,
                       need=20, umin=19):
    """Leftover-tight extras clique inside a host union."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF

    extras = G["extras"]
    thresh = G["thresh"]
    nL = len(local)
    roots = [r for r in range(40) if (Uhost >> r) & 1]

    def vx(i):
        return i + 1

    def vy(t):
        return nL + t + 1

    cnf = CNF()
    by_g = {}
    for i, g in enumerate(local_g):
        by_g.setdefault(g, []).append(i)
    for vs in by_g.values():
        for a, b in combinations(vs, 2):
            cnf.append([-vx(a), -vx(b)])

    for i in range(nL):
        for j in range(i + 1, nL):
            if ip(extras[local[i]], extras[local[j]]) > thresh:
                cnf.append([-vx(i), -vx(j)])

    support = [[] for _ in roots]
    rpos = {r: t for t, r in enumerate(roots)}
    for i, m in enumerate(local_miss):
        mm = m
        while mm:
            r = (mm & -mm).bit_length() - 1
            mm &= mm - 1
            if r in rpos:
                cnf.append([-vx(i), vy(rpos[r])])
                support[rpos[r]].append(i)
    for t, vs in enumerate(support):
        cnf.append([-vy(t)] + [vx(i) for i in vs])

    nY = len(roots)
    top = nL + nY
    card_y = CardEnc.atleast(
        lits=[vy(t) for t in range(nY)], bound=umin,
        top_id=top, encoding=EncType.seqcounter,
    )
    cnf.extend(card_y.clauses)
    card_x = CardEnc.atleast(
        lits=[vx(i) for i in range(nL)], bound=need,
        top_id=card_y.nv, encoding=EncType.seqcounter,
    )
    cnf.extend(card_x.clauses)
    # |E| - |U| >= 1  <=>  |X| + (nY - |Y|) >= nY + 1
    card_diff = CardEnc.atleast(
        lits=[vx(i) for i in range(nL)] + [-vy(t) for t in range(nY)],
        bound=nY + 1,
        top_id=card_x.nv, encoding=EncType.seqcounter,
    )
    cnf.extend(card_diff.clauses)
    return cnf, nL, nY


def global_leftover_cnf(G, k=19, min_star_cover=5):
    """|U| = k, |E| >= k+1, U not contained in any (min_star_cover-1)-star."""
    from n1_leftover_sat import build_instance

    cover_in_build = 4 if min_star_cover >= 4 else min_star_cover
    inst = build_instance(k, min_star_cover=cover_in_build)
    cnf = inst["cnf"]
    if min_star_cover >= 5:
        stars = G["stars"]
        nE, nD = inst["nE"], inst["nD"]

        def vy(r):
            return nE + r + 1

        for comb in combinations(range(10), min_star_cover - 1):
            W = 0
            for s in comb:
                W |= stars[s]
            outside = [vy(r) for r in range(nD) if ((W >> r) & 1) == 0]
            if outside:
                cnf.append(outside)
    inst["min_star_cover"] = min_star_cover
    inst["cnf"] = cnf
    return inst


def cnf_sha256(cnf) -> str:
    h = hashlib.sha256()
    h.update(f"p cnf {cnf.nv} {len(cnf.clauses)}\n".encode())
    for cl in cnf.clauses:
        h.update((" ".join(str(x) for x in cl) + " 0\n").encode())
    return h.hexdigest()


def write_dimacs(cnf, path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    cnf.to_file(str(path))
    return {
        "path": str(path),
        "vars": cnf.nv,
        "clauses": len(cnf.clauses),
        "sha256": cnf_sha256(cnf),
        "bytes": path.stat().st_size,
    }
