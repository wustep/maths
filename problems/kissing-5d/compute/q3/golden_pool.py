#!/usr/bin/env python3
"""Exact kissing graph on D5 plus Q(√5) orbits of equal squared-norm 2.

The 600-cell uses even permutations of (±φ, ±1, ±1/φ, 0) in four
dimensions.  The same three-value pattern, with two zeros, sits in R^5.
Scaled to squared-norm 2 the coordinates live in Q(√5).  Inner products
are exact.  A 41-clique would be a new kissing code.

Also includes the 10 axes of squared-norm 2 and the 32 points
(±1,±1,±1,±1,±1)/√(5/2), rewritten over Q(√5) only when the scale is
in the field — the cube is kept as a separate Q(√10) family and checked
by clearing denominators (integer model below).

Integer model for the golden family: multiply by 2 so
    φ = (1+√5)/2  becomes  (1+√5),   1/φ = (√5-1)/2  becomes (√5-1).
A vector is stored as a 5-tuple of pairs (a, b) meaning (a + b√5)/2,
and squared-norm 2 means Σ (a + b√5)^2 / 4 = 2, i.e.
Σ (a^2 + 5 b^2 + 2ab √5) = 8, so Σ(a^2+5b^2)=8 and Σ ab = 0.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q2"))

from configs import d5, l5, _dot, _norm2
from graphio import write_adj

# Coordinate (a, b) means (a + b√5)/2.  Inner product of u, v is
#   Σ (a_i + b_i √5)(c_i + d_i √5) / 4
# = (Σ(ac+5bd) + Σ(ad+bc)√5) / 4.
# Kissing of squared-norm-2 vectors: <u,v> <= 1 iff
#   Σ(ac+5bd) + Σ(ad+bc)√5  <= 4.


def ip_pair(u, v):
    """Return (p, q) so <u,v> = (p + q √5)/4."""
    p = 0
    q = 0
    for (a, b), (c, d) in zip(u, v):
        p += a * c + 5 * b * d
        q += a * d + b * c
    return p, q


def le1(u, v):
    """Exact <u,v> <= 1, i.e. (p - 4) + q √5 <= 0."""
    p, q = ip_pair(u, v)
    # (p-4) + q√5 <= 0.
    # If q=0, p<=4.  If q>0, compare to -q√5, i.e. isolate and square
    # only when the rational part has the sign that makes it necessary.
    r = p - 4
    if q == 0:
        return r <= 0
    if q > 0:
        # r <= -q√5 < 0, so r must be negative, and r^2 >= 5 q^2
        return r < 0 and r * r >= 5 * q * q
    # q < 0: r <= |q|√5.  True if r<=0, or if r>0 and r^2 <= 5 q^2
    if r <= 0:
        return True
    return r * r <= 5 * q * q


def norm2_is_2(u):
    p, q = ip_pair(u, u)
    # (p + q√5)/4 = 2 iff p=8 and q=0
    return p == 8 and q == 0


def golden_orbit():
    """Signed-permutation orbit of (±φ, ±1, ±1/φ, 0, 0) / √2.

    Unscaled, that 600-cell pattern has squared-norm 4.  Scaling by
    1/√2 puts it on |x|^2 = 2, in the field Q(√2, √5).  We store the
    unscaled (a,b) pairs (meaning (a+b√5)/2) and compare inner products
    after the 1/√2 scale: old <u,v> / 2 <= 1 iff old <u,v> <= 2 iff
    (p - 8) + q√5 <= 0 in the (p,q) model.
    """
    seen = set()
    out = []
    for pos in permutations(range(5), 3):
        for signs in product((-1, 1), repeat=3):
            v = [(0, 0)] * 5
            raw = ((1, 1), (2, 0), (-1, 1))
            for k, (s, (a, b)) in enumerate(zip(signs, raw)):
                v[pos[k]] = (s * a, s * b)
            key = tuple(v)
            if key in seen:
                continue
            p, q = ip_pair(key, key)
            if p == 16 and q == 0:  # unscaled |x|^2 = 4
                seen.add(key)
                out.append(key)
    return out


def le1_scaled_golden(u, v):
    """Both golden, each already scaled by 1/√2 in the comparison."""
    p, q = ip_pair(u, v)
    r = p - 8
    if q == 0:
        return r <= 0
    if q > 0:
        return r < 0 and r * r >= 5 * q * q
    if r <= 0:
        return True
    return r * r <= 5 * q * q


def le1_d5_golden(d5v, g):
    """D5 (unscaled, |x|^2=2) against golden/√2.

    D5 coords are (2,0) meaning 1.  The raw inner product against the
    unscaled golden is (p+q√5)/4; after 1/√2 on golden only,
    <d,g> = (p+q√5)/(4√2).  Need (p+q√5)/(4√2) <= 1, i.e.
    p + q√5 <= 4√2.  Square when the left side is nonnegative:
    (p + q√5)^2 <= 32.
    """
    p, q = ip_pair(d5v, g)
    # left = p + q√5.  If left <= 0, inequality holds.
    if q == 0:
        if p <= 0:
            return True
        return p * p <= 32
    # sign of p + q√5
    if q > 0:
        pos = p > 0 or p * p < 5 * q * q
    else:
        pos = p > 0 and p * p > 5 * q * q
    if not pos:
        return True
    # (p^2 + 5q^2 - 32) + 2pq √5 <= 0
    r = p * p + 5 * q * q - 32
    s = 2 * p * q
    if s == 0:
        return r <= 0
    if s > 0:
        return r < 0 and r * r >= 5 * s * s
    if r <= 0:
        return True
    return r * r <= 5 * s * s


def d5_as_pairs():
    """D5 roots (±1,±1,0,0,0) as (a,b) with (2,0) standing for 1 = 2/2."""
    out = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [(0, 0)] * 5
            v[i] = (2 * si, 0)
            v[j] = (2 * sj, 0)
            out.append(tuple(v))
    return out


def axes_as_pairs():
    """(±√2, 0,0,0,0) is not in Q(√5).  Skip."""
    return []


def l5_half_as_pairs():
    """L5 half-spinor layer: (±1/2)^4 × {1} with odd number of minuses.

    1/2 = (1,0) in the /2 model; last coord 1 = (2,0).
    |x|^2 = 4*(1/4) + 1 = 2.  Yes.
    """
    out = []
    for signs in product((-1, 1), repeat=4):
        if sum(1 for s in signs if s < 0) % 2 != 1:
            continue
        v = [(s, 0) for s in signs] + [(2, 0)]
        out.append(tuple(v))
    # also the even-sign half-spinor at last = 1, and both at last = -1
    for odd in (True, False):
        for last in (1, -1):
            for signs in product((-1, 1), repeat=4):
                nneg = sum(1 for s in signs if s < 0)
                if (nneg % 2 == 1) != odd:
                    continue
                v = [(s, 0) for s in signs] + [(2 * last, 0)]
                out.append(tuple(v))
    # unique
    seen = set()
    uniq = []
    for v in out:
        if v not in seen and norm2_is_2(v):
            seen.add(v)
            uniq.append(v)
    return uniq


def unique(pts):
    seen = set()
    out = []
    for p in pts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def max_clique_seeded(adj, n, seeds, target=41, node_limit=2_000_000):
    """Bitset B&B.  seeds are known cliques used as lower bounds."""
    best = 0
    best_cl = []
    for s in seeds:
        if len(s) > best:
            best = len(s)
            best_cl = list(s)
    found = None
    nodes = 0

    def expand(P, stack):
        nonlocal best, best_cl, found, nodes
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            return
        rsz = len(stack)
        if rsz + P.bit_count() <= best:
            return
        if P == 0:
            if rsz > best:
                best = rsz
                best_cl = list(stack)
            return
        # colour
        rem = P
        ord_v, col = [], []
        c = 0
        while rem:
            c += 1
            avail = rem
            while avail:
                v = (avail & -avail).bit_length() - 1
                ord_v.append(v)
                col.append(c)
                avail &= ~adj[v]
                avail &= ~(1 << v)
                rem &= ~(1 << v)
        Q = P
        for i in range(len(ord_v) - 1, -1, -1):
            if found is not None or nodes > node_limit:
                return
            if rsz + col[i] <= best:
                return
            v = ord_v[i]
            stack.append(v)
            if rsz + 1 >= target:
                found = list(stack)
                best = rsz + 1
                best_cl = found
                return
            expand(Q & adj[v], stack)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [])
    return found, best, best_cl, nodes


def _kiss(kind_i, pi, kind_j, pj):
    if kind_i == "gold" and kind_j == "gold":
        return le1_scaled_golden(pi, pj)
    if kind_i == "gold" and kind_j != "gold":
        return le1_d5_golden(pj, pi)
    if kind_j == "gold" and kind_i != "gold":
        return le1_d5_golden(pi, pj)
    return le1(pi, pj)


def main() -> int:
    gold = golden_orbit()
    D = d5_as_pairs()
    H = l5_half_as_pairs()
    tagged = [("d5", p) for p in D] + [("gold", p) for p in gold] + [("half", p) for p in H]
    seen = set()
    pool = []
    kinds = []
    for kind, p in tagged:
        if p in seen:
            continue
        seen.add(p)
        pool.append(p)
        kinds.append(kind)
    n = len(pool)
    print(f"golden orbit {len(gold)}; D5 {len(D)}; half-spinors {len(H)}; "
          f"unique pool {n}", flush=True)
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if _kiss(kinds[i], pool[i], kinds[j], pool[j]):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    # seeds: D5 indices, L5-like (D5 minus last=+1 plus odd half-spinors)
    d5_idx = list(range(len(D)))
    # L5 in the pair model: keep D5 with last coord != +1, plus odd half at +1
    # Last coord of D5-as-pairs is (2,0) or (0,0) or (-2,0).
    l5_idx = []
    d5_set = set(D)
    for i, p in enumerate(pool):
        if p in d5_set and p[4] != (2, 0):
            l5_idx.append(i)
    # odd half-spinors at last = +1
    for i, p in enumerate(pool):
        if p[4] == (2, 0) and all(b == 0 for _, b in p):
            # coords are ±1/2 or ±1
            avals = [a for a, b in p]
            if avals[4] == 2 and all(abs(a) == 1 for a in avals[:4]):
                nneg = sum(1 for a in avals[:4] if a < 0)
                if nneg % 2 == 1:
                    l5_idx.append(i)
    l5_idx = sorted(set(l5_idx))
    print(f"edges={edges} D5_seed={len(d5_idx)} L5_seed={len(l5_idx)}", flush=True)

    found, best, cl, nodes = max_clique_seeded(
        adj, n, [d5_idx, l5_idx], target=41, node_limit=3_000_000
    )
    clique41 = None
    if found is not None and len(found) >= 41:
        pts = [pool[i] for i in found[:41]]
        ok = all(_kiss(kinds[found[a]], pts[a], kinds[found[b]], pts[b])
                 for a in range(41) for b in range(a + 1, 41))
        clique41 = {
            "ok": ok,
            "indices": found[:41],
            "points_ab": [list(p) for p in pts],
        }
        if ok:
            (HERE / "certs" / "code41_golden.json").write_text(
                json.dumps(clique41, indent=2) + "\n"
            )
    report = {
        "n_golden": len(gold),
        "n_d5": len(D),
        "n_half": len(H),
        "n": n,
        "n_edges": edges,
        "best": best,
        "nodes": nodes,
        "found_41": bool(clique41 and clique41["ok"]),
        "complete": found is not None or nodes <= 3_000_000,
        "clique41": clique41,
        "comment": (
            "Exact kissing graph on D5 plus the signed-permutation orbit of "
            "(φ, 1, 1/φ, 0, 0)/√2 (field Q(√2,√5)) and the half-spinor "
            "layers.  A 41-clique would be a new code.  Incomplete search "
            "is residue."
        ),
    }
    (HERE / "golden_pool.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("n", "n_edges", "best", "found_41", "complete", "nodes")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
