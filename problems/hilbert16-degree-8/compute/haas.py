#!/usr/bin/env python3
"""Haas zone decompositions for degree-8 T-curves.

Implements the combinatorial objects of Geiselmann-Joswig-Kastner-
Mundinger-Pokutta-Spiegel-Wack-Zimmer, arXiv:2602.06888 v3, Section 3
(their reading of Haas, "Real algebraic curves", Habilitationsschrift):

  * Harnack splits of d*Delta_2 (simple: one primitive edge between two
    boundary points with distinct parities; double: two primitive edges
    through an interior apex, base points of equal parity),
  * the two zones Z^+ (surrounded) / Z^- (root) of a split,
  * compatibility (pairwise non-crossing edges, no shared edge),
  * the surgical twist sigma -> sigma + eps + i*x + j*y on Z^+,
  * the maximal T-curve C(S) of a compatible collection S: apply every
    twist to the Harnack sign distribution eta(x,y) = (x+1)(y+1).

Theorem 13 (Haas): a T-curve is maximal iff some compatible collection
of Harnack splits is valid for it.  Section 3.5: C(S) does not depend
on which unimodular triangulation refining S is used.  So the set of
maximal degree-8 T-curve schemes is exactly {scheme C(S) : S compatible},
a FINITE enumeration -- that is what this module makes computable.

Regularity is a separate matter and is NOT assumed here; Haas' theorem
holds for unimodular triangulations, regular or not.  `refine` builds a
unimodular triangulation containing all split edges, and `regularize`
searches for an exact convexity certificate for one; only certificates
that pass tcurve.check_convexity are ever claimed.
"""

from math import gcd

D = 8
CORNERS = [(0, 0), (D, 0), (0, D)]


def lattice_points(d=D):
    return [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]


PTS = lattice_points()


def on_boundary(p, d=D):
    i, j = p
    return i == 0 or j == 0 or i + j == d


BD = [p for p in PTS if on_boundary(p)]
INT = [p for p in PTS if not on_boundary(p)]


def sides(p, d=D):
    i, j = p
    s = set()
    if i == 0:
        s.add("i")
    if j == 0:
        s.add("j")
    if i + j == d:
        s.add("h")
    return s


def parity(p):
    return (p[0] % 2, p[1] % 2)


def primitive(u, v):
    return gcd(abs(u[0] - v[0]), abs(u[1] - v[1])) == 1


def bd_cycle(d=D):
    """Boundary lattice points counterclockwise from (0,0)."""
    c = [(i, 0) for i in range(d)]
    c += [(d - i, i) for i in range(d)]
    c += [(0, d - i) for i in range(d)]
    return c


BDC = bd_cycle()
BDPOS = {p: k for k, p in enumerate(BDC)}


# ---------------------------------------------------------------- geometry

def cross(o, a, b):
    return ((a[0] - o[0]) * (b[1] - o[1])
            - (a[1] - o[1]) * (b[0] - o[0]))


def on_seg(p, a, b):
    if cross(a, b, p) != 0:
        return False
    return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def seg_cross(a, b, c, d):
    """True if the relative interiors of [a,b] and [c,d] meet."""
    if len({a, b, c, d}) < 4:
        # sharing an endpoint: only a problem if collinear and overlapping
        if cross(a, b, c) == 0 and cross(a, b, d) == 0:
            # collinear; overlap beyond the shared point?
            pts = sorted([a, b, c, d])
            return len(set([a, b]) & set([c, d])) == 1 and (
                on_seg(c, a, b) and c not in (a, b)
                or on_seg(d, a, b) and d not in (a, b)
                or on_seg(a, c, d) and a not in (c, d)
                or on_seg(b, c, d) and b not in (c, d))
        return False
    d1, d2 = cross(c, d, a), cross(c, d, b)
    d3, d4 = cross(a, b, c), cross(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) \
            and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0:
        return True
    # touching / collinear cases
    for p, (x, y) in ((c, (a, b)), (d, (a, b)), (a, (c, d)), (b, (c, d))):
        if on_seg(p, x, y) and p != x and p != y:
            return True
    return False


def in_polygon(p, poly):
    """Point in closed simple lattice polygon, exact integer arithmetic."""
    n = len(poly)
    for k in range(n):
        if on_seg(p, poly[k], poly[(k + 1) % n]):
            return True
    inside = False
    x, y = p
    for k in range(n):
        ax, ay = poly[k]
        bx, by = poly[(k + 1) % n]
        if (ay > y) != (by > y):
            # x of the intersection of the edge with the horizontal ray
            t = (y - ay) * (bx - ax)
            xi = ax * (by - ay) + t
            if (by - ay) > 0:
                if xi > x * (by - ay):
                    inside = not inside
            else:
                if xi < x * (by - ay):
                    inside = not inside
    return inside


# ------------------------------------------------------------------ splits

class Split:
    __slots__ = ("path", "edges", "kind", "alpha", "beta", "zplus",
                 "zminus", "even", "eps", "ti", "tj", "key")

    def __init__(self, path):
        self.path = tuple(path)
        self.edges = frozenset(frozenset(e) for e in
                               zip(path, path[1:]))
        self.kind = "simple" if len(path) == 2 else "double"
        ps = {parity(p) for p in path}
        assert len(ps) == 2, path
        self.alpha, self.beta = sorted(ps)
        a, b = self.alpha, self.beta
        self.even = (0, 0) in ps
        self.eps = (a[0] * b[1] + a[1] * b[0]) % 2
        self.ti = (a[1] + b[1]) % 2
        self.tj = (a[0] + b[0]) % 2
        self.key = self.path if self.path[0] < self.path[-1] \
            else self.path[::-1]
        self._zones()

    def _zones(self):
        u, v = self.path[0], self.path[-1]
        mid = list(self.path[1:-1])
        ku, kv = BDPOS[u], BDPOS[v]
        n = len(BDC)
        arc1 = []                       # v -> u counterclockwise, exclusive
        k = (kv + 1) % n
        while k != ku:
            arc1.append(BDC[k])
            k = (k + 1) % n
        arc2 = []                       # u -> v counterclockwise, exclusive
        k = (ku + 1) % n
        while k != kv:
            arc2.append(BDC[k])
            k = (k + 1) % n
        polyA = [u] + mid + [v] + arc1
        polyB = [v] + mid[::-1] + [u] + arc2
        za = frozenset(p for p in PTS if in_polygon(p, polyA))
        zb = frozenset(p for p in PTS if in_polygon(p, polyB))
        onpath = frozenset(p for p in PTS
                           if any(on_seg(p, e[0], e[1])
                                  for e in zip(self.path, self.path[1:])))
        ca = sum(1 for c in CORNERS if c in za and c not in onpath)
        cb = sum(1 for c in CORNERS if c in zb and c not in onpath)
        if ca <= cb:
            self.zplus, self.zminus = za, zb
        else:
            self.zplus, self.zminus = zb, za

    def twist(self, sigma):
        for p in self.zplus:
            sigma[p] = (sigma[p] + self.eps + self.ti * p[0]
                        + self.tj * p[1]) % 2

    def __repr__(self):
        return f"Split{self.path}"


def all_splits(d=D):
    out = {}
    # simple
    for a in range(len(BD)):
        for b in range(a + 1, len(BD)):
            u, v = BD[a], BD[b]
            if sides(u) & sides(v):
                continue
            if parity(u) == parity(v):
                continue
            if not primitive(u, v):
                continue
            s = Split((u, v))
            out[s.key] = s
    # double
    for w in INT:
        pw = parity(w)
        cand = {}
        for u in BD:
            if parity(u) == pw:
                continue
            if not primitive(u, w):
                continue
            cand.setdefault(parity(u), []).append(u)
        for al, lst in cand.items():
            for a in range(len(lst)):
                for b in range(a + 1, len(lst)):
                    u, v = lst[a], lst[b]
                    if on_seg(w, u, v):
                        pass          # collinear through the apex: allowed
                    s = Split((u, w, v))
                    out[s.key] = s
    return list(out.values())


def compatible(s, t):
    if s.edges & t.edges:
        return False
    for e in s.edges:
        a, b = tuple(e)
        for f in t.edges:
            c, dd = tuple(f)
            if seg_cross(a, b, c, dd):
                return False
    return True


def eta(d=D):
    return {(i, j): 1 if (i % 2 == 0 and j % 2 == 0) else 0
            for (i, j) in lattice_points(d)}


def signs_of(coll, d=D):
    sigma = eta(d)
    for s in coll:
        s.twist(sigma)
    return {p: (-1 if sigma[p] else 1) for p in sigma}


if __name__ == "__main__":
    sp = all_splits()
    ns = sum(1 for s in sp if s.kind == "simple")
    nd = len(sp) - ns
    print(f"{len(sp)} Harnack splits: {ns} simple, {nd} double")
    print(f"  odd: {sum(1 for s in sp if not s.even)},"
          f"  even: {sum(1 for s in sp if s.even)}")
    from collections import Counter
    print(Counter((s.kind, s.even) for s in sp))
    s0 = sp[0]
    print("example", s0, "Z+ size", len(s0.zplus), "eps,i,j",
          s0.eps, s0.ti, s0.tj)


# ------------------------------------------------------- refinement to a T

def primitive_pairs(d=D):
    out = []
    for a in range(len(PTS)):
        for b in range(a + 1, len(PTS)):
            u, v = PTS[a], PTS[b]
            if primitive(u, v):
                out.append((u, v))
    return out


PAIRS = primitive_pairs()


def refine(coll, rng=None):
    """A unimodular triangulation of T_D containing every split edge.

    Greedy maximal crossing-free set of primitive segments: maximality
    forces every lattice point to be a vertex and every face to be an
    empty triangle, i.e. the result is unimodular.
    """
    forced = [tuple(e) for s in coll for e in
              (tuple(x) for x in s.edges)]
    acc = []
    for e in forced:
        a, b = e
        for c, dd in acc:
            if seg_cross(a, b, c, dd):
                raise ValueError("incompatible collection")
        acc.append((a, b))
    cand = list(PAIRS)
    if rng is not None:
        rng.shuffle(cand)
    for a, b in cand:
        if any((a, b) == e or (b, a) == e for e in acc):
            continue
        if any(seg_cross(a, b, c, dd) for c, dd in acc):
            continue
        acc.append((a, b))
    eset = {frozenset(e) for e in acc}
    tris = []
    for a in range(len(PTS)):
        for b in range(a + 1, len(PTS)):
            u, v = PTS[a], PTS[b]
            if frozenset((u, v)) not in eset:
                continue
            for c in range(b + 1, len(PTS)):
                w = PTS[c]
                if abs(cross(u, v, w)) != 1:
                    continue
                if frozenset((u, w)) in eset and frozenset((v, w)) in eset:
                    tris.append((u, v, w))
    return tris


# ------------------------------------------------------------ regularity

def _bary(a, b, c, p):
    """Integer barycentric coords of p w.r.t. the unimodular triangle abc."""
    det = cross(a, b, c)
    al = cross(p, b, c)
    be = cross(a, p, c)
    ga = cross(a, b, p)
    assert abs(det) == 1
    return al * det, be * det, ga * det      # det = +-1, so /det == *det


def convexity_rows(tris):
    """Local-convexity constraints r.h >= 1, one per interior edge.

    For a triangulation of a convex polygon, local convexity across
    every interior edge is equivalent to the triangulation being the
    regular one induced by h.
    """
    idx = {p: k for k, p in enumerate(PTS)}
    by_edge = {}
    for t in tris:
        for k in range(3):
            e = frozenset((t[k], t[(k + 1) % 3]))
            by_edge.setdefault(e, []).append(t[(k + 2) % 3])
    rows = []
    for e, opp in by_edge.items():
        if len(opp) != 2:
            continue
        a, b = tuple(e)
        c, dd = opp
        al, be, ga = _bary(a, b, c, dd)
        r = [0] * len(PTS)
        r[idx[dd]] += 1
        r[idx[a]] -= al
        r[idx[b]] -= be
        r[idx[c]] -= ga
        rows.append(r)
    return rows


def regularize(tris, iters=200000, seed=0):
    """Agmon-Motzkin-Schoenberg relaxation for r.h >= 1; returns integer
    heights that make `tris` the lower-hull triangulation, or None.

    A returned vector is only a *candidate*: callers must re-certify it
    exactly with tcurve.check_convexity.
    """
    import numpy as np
    R = np.array(convexity_rows(tris), dtype=float)
    if len(R) == 0:
        return None
    nrm = (R * R).sum(1)
    h = np.zeros(R.shape[1])
    rs = np.random.RandomState(seed)
    for it in range(iters):
        v = 1.0 - R @ h
        k = int(np.argmax(v))
        if v[k] <= 0:
            break
        h += 1.7 * v[k] / nrm[k] * R[k]
        if it % 5000 == 4999:
            h += 1e-9 * rs.randn(len(h))
    if (R @ h < 1.0 - 1e-9).any():
        return None
    for scale in (1, 2, 4, 8, 16, 64, 256, 1024, 4096, 1 << 16):
        hi = np.rint(h * scale).astype(object)
        if all(sum(r[k] * hi[k] for k in range(len(hi))) > 0
               for r in convexity_rows(tris)):
            return {PTS[k]: int(hi[k]) for k in range(len(PTS))}
    return None
