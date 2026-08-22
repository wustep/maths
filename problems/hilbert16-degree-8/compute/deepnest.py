#!/usr/bin/env python3
"""Search in Haas-collection space for the two open deep nests.

Background.  Haas' theorem (arXiv:2602.06888 v3 Thm 13, and haas.py in
this folder) says every MAXIMAL degree-8 T-curve is C(S) for a
compatible collection S of Harnack splits, that its sign distribution
is eta + sum_{S in S} delta_S, and -- Section 3.5 -- that the resulting
real scheme does NOT depend on which unimodular triangulation refining
S is used.  So the maximal T-curve schemes are a function of the
collection alone:

        S  (compatible collection of Harnack splits)  |-->  scheme C(S)

Every previous pass in this folder searched *sign space on a fixed
triangulation*.  This module searches the collection space instead:
the triangulation is a by-product (any unimodular refinement will do),
so "designing a triangulation" becomes "choosing a set of pairwise
non-crossing split paths", which is the level at which the nesting of
the curve is visible.

Structural fact used for the design: pairwise non-crossing chords of
the triangle have nested-or-disjoint zones, so the Z+ zones of a
compatible collection form a LAMINAR family, and the depth of that
family bounds the depth of the oval nesting of C(S).

Regularity is NOT assumed here (Haas needs none).  A hit has to be
regularized afterwards -- haas.regularize + tcurve.check_convexity --
before it is a T-curve in Viro's sense.

Public API:
  splits()                       the 1254 Harnack splits (cached)
  cross_masks()                  bitmask crossing table on haas.PAIRS
  fast_refine(coll, rng)         unimodular triangulation containing
                                 every split edge of coll
  evaluate(coll, rng)            (ncomp, scheme, tris)
  zone_tree(coll)                laminar forest of the Z+ zones
"""

import random
from functools import lru_cache

import haas
from fastcx import Complex

D8 = 8


@lru_cache(maxsize=1)
def splits():
    return haas.all_splits()


@lru_cache(maxsize=1)
def _pairs_index():
    pairs = haas.PAIRS
    idx = {frozenset(p): k for k, p in enumerate(pairs)}
    return pairs, idx


@lru_cache(maxsize=1)
def cross_masks():
    """cross[k] = bitmask of the primitive pairs whose relative interior
    meets that of pair k (haas.seg_cross), so a crossing-free set is an
    independent set for these masks."""
    pairs, _ = _pairs_index()
    n = len(pairs)
    cross = [0] * n
    for i in range(n):
        a, b = pairs[i]
        for j in range(i + 1, n):
            c, d = pairs[j]
            if haas.seg_cross(a, b, c, d):
                cross[i] |= 1 << j
                cross[j] |= 1 << i
    return cross


def _edge_indices(coll):
    _, idx = _pairs_index()
    out = []
    for s in coll:
        for e in s.edges:
            out.append(idx[e])
    return out


def fast_refine(coll, rng=None, order=None):
    """Unimodular triangulation of T_8 containing every edge of coll.

    Same greedy maximal crossing-free completion as haas.refine, but the
    crossing tests are precomputed bitmasks, which is ~20x faster.
    Raises ValueError if coll is not compatible.
    """
    pairs, _ = _pairs_index()
    n = len(pairs)
    cross = cross_masks()
    allowed = (1 << n) - 1
    chosen = []
    for k in _edge_indices(coll):
        if not (allowed >> k) & 1:
            if k in chosen:
                continue
            raise ValueError("incompatible collection")
        chosen.append(k)
        allowed &= ~cross[k]
        allowed &= ~(1 << k)
    if order is None:
        order = list(range(n))
        if rng is not None:
            rng.shuffle(order)
    for k in order:
        if (allowed >> k) & 1:
            chosen.append(k)
            allowed &= ~cross[k]
            allowed &= ~(1 << k)
    eset = {frozenset(pairs[k]) for k in chosen}
    return tris_from_edges(eset)


def tris_from_edges(eset):
    pts = haas.PTS
    nbr = {p: set() for p in pts}
    for e in eset:
        a, b = tuple(e)
        nbr[a].add(b)
        nbr[b].add(a)
    tris = []
    for i, u in enumerate(pts):
        for v in nbr[u]:
            if v <= u:
                continue
            for w in nbr[u] & nbr[v]:
                if w <= v:
                    continue
                if abs(haas.cross(u, v, w)) == 1:
                    tris.append((u, v, w))
    return tris


def signs_of(coll):
    return haas.signs_of(coll)


def evaluate(coll, rng=None, order=None):
    """(ncomp, scheme, tris) for the maximal T-curve C(coll)."""
    tris = fast_refine(coll, rng, order)
    if len(tris) != 64:
        raise ValueError(f"refinement has {len(tris)} triangles")
    tris = [tuple(tuple(v) for v in t) for t in tris]
    cx = Complex(D8, tris)
    sg = haas.signs_of(coll)
    nc, sch = cx.eval([sg[p] for p in cx.base_pts])
    return nc, sch, tris


# ------------------------------------------------------------ zone tree

def zone_tree(coll):
    """Laminar forest of the Z+ zones of coll: list of (split, children).

    Non-crossing chords => zones nested or (interior-)disjoint.
    Depth of this forest is the structural handle on nesting depth.
    """
    items = sorted(coll, key=lambda s: -len(s.zplus))
    parent = {}
    for i, s in enumerate(items):
        for t in items[:i]:
            if s.zplus <= t.zplus:
                parent[i] = t
        # nearest enclosing = smallest such
    par = {}
    for i, s in enumerate(items):
        best = None
        for j, t in enumerate(items):
            if j == i:
                continue
            if s.zplus < t.zplus or (s.zplus <= t.zplus and j < i):
                if best is None or len(t.zplus) < len(items[best].zplus):
                    best = j
        par[i] = best
    kids = {i: [] for i in range(len(items))}
    roots = []
    for i in range(len(items)):
        if par[i] is None:
            roots.append(i)
        else:
            kids[par[i]].append(i)

    def depth(i):
        return 1 + max((depth(k) for k in kids[i]), default=0)

    return items, par, kids, roots, max((depth(r) for r in roots), default=0)


def compat_matrix():
    """adjacency bitmasks over splits() (compatibility graph)."""
    import pickle
    import os
    if os.path.exists("haas_adj.pkl"):
        d = pickle.load(open("haas_adj.pkl", "rb"))
        return d["adj"]
    sp = splits()
    n = len(sp)
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if haas.compatible(sp[i], sp[j]):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


if __name__ == "__main__":
    import time
    rng = random.Random(0)
    sp = splits()
    t0 = time.time()
    cross_masks()
    print(f"crossing table {time.time()-t0:.1f}s, {len(haas.PAIRS)} pairs")
    t0 = time.time()
    for k in range(50):
        evaluate([sp[k]], rng)
    print(f"{(time.time()-t0)/50*1000:.1f} ms / collection")
