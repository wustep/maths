#!/usr/bin/env python3
"""Fast T-curve evaluator: precomputed complex + integer union-find.

Same mathematics as tcurve.TCurve, restructured for speed so the
annealing search can evaluate thousands of sign distributions per
second on a fixed triangulation.  Every witness the search reports is
re-verified afterwards with the slow exact path (tcurve.py), so this
module is an accelerator, not the verifier of record.
"""


class IUF:
    __slots__ = ("p",)

    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


class Complex:
    """Rhombus complex of a primitive triangulation of T_d, with the
    antipodal boundary gluing, prepared for fast repeated evaluation."""

    def __init__(self, d, tris):
        self.d = d
        base_pts = sorted({v for t in tris for v in t})
        self.base_pts = base_pts
        bidx = {p: k for k, p in enumerate(base_pts)}

        vco = {}     # coord -> vid
        vbase = []   # vid -> base point index
        vflip = []   # vid -> +-1 sign factor for the reflection rule

        def vid(x, y):
            if (x, y) in vco:
                return vco[(x, y)]
            i, j = abs(x), abs(y)
            f = 1
            if x < 0 and i % 2 == 1:
                f = -f
            if y < 0 and j % 2 == 1:
                f = -f
            v = len(vbase)
            vco[(x, y)] = v
            vbase.append(bidx[(i, j)])
            vflip.append(f)
            return v

        rtris = []
        rtco = []
        for t in tris:
            for a in (1, -1):
                for b in (1, -1):
                    co = tuple((a * x, b * y) for (x, y) in t)
                    rtris.append(tuple(vid(*p) for p in co))
                    rtco.append(co)
        self.rtris = rtris
        self.nv = len(vbase)
        self.vbase = vbase
        self.vflip = vflip
        F = len(rtris)
        self.F = F

        # edges keyed by coordinate pairs
        etris = {}
        for ti, co in enumerate(rtco):
            for k in range(3):
                e = frozenset((co[k], co[(k + 1) % 3]))
                etris.setdefault(e, []).append(ti)
        edges = []   # (t1, t2, cross, u1, u2, w1, w2) vids, u1<->u2, w1<->w2
        seen = set()
        for e, ts in etris.items():
            if len(ts) == 2:
                p, q = tuple(e)
                edges.append((ts[0], ts[1], 0,
                              vco[p], vco[p], vco[q], vco[q]))
            elif len(ts) == 1:
                if e in seen:
                    continue
                p, q = tuple(e)
                e2 = frozenset(((-p[0], -p[1]), (-q[0], -q[1])))
                if e2 not in etris or len(etris[e2]) != 1:
                    raise ValueError("bad boundary gluing")
                seen.add(e)
                seen.add(e2)
                edges.append((ts[0], etris[e2][0], 1,
                              vco[p], vco[(-p[0], -p[1])],
                              vco[q], vco[(-q[0], -q[1])]))
            else:
                raise ValueError("edge in >2 triangles")
        self.edges = edges
        # corner slot lookup: corner id = 3*ti + slot
        self.slot = [{rtris[ti][s]: s for s in range(3)} for ti in range(F)]

    # ------------------------------------------------------------------
    def eval(self, signs, want_scheme=True):
        """signs: list of +-1 indexed like self.base_pts.

        Returns (ncomp, scheme or None).  scheme is the canonical
        bracket string; ncomp the number of components in RP^2.
        """
        vbase, vflip = self.vbase, self.vflip
        sigma = [signs[vbase[v]] * vflip[v] for v in range(self.nv)]
        rtris, F = self.rtris, self.F

        # per-triangle: odd slot (-1 if uncut)
        odd = [-1] * F
        cut = []
        for ti in range(F):
            a, b, c = rtris[ti]
            sa, sb, sc = sigma[a], sigma[b], sigma[c]
            if sa == sb:
                if sa != sc:
                    odd[ti] = 2
                    cut.append(ti)
            elif sa == sc:
                odd[ti] = 1
                cut.append(ti)
            else:
                odd[ti] = 0
                cut.append(ti)

        # curve UF on 2F (sheet, tri); regions UF on 6F corners
        ufc = IUF(2 * F)
        ufr = IUF(6 * F)
        for ti in range(F):
            o = odd[ti]
            base = 3 * ti
            if o < 0:
                for sh in (0, 3 * F):
                    ufr.union(sh + base, sh + base + 1)
                    ufr.union(sh + base, sh + base + 2)
            else:
                s1, s2 = (o + 1) % 3, (o + 2) % 3
                for sh in (0, 3 * F):
                    ufr.union(sh + base + s1, sh + base + s2)
        for (t1, t2, cross, u1, u2, w1, w2) in self.edges:
            cutedge = sigma[u1] != sigma[w1]
            s1t1 = 3 * t1 + self.slot[t1][u1]
            s1t2 = 3 * t2 + self.slot[t2][u2]
            s2t1 = 3 * t1 + self.slot[t1][w1]
            s2t2 = 3 * t2 + self.slot[t2][w2]
            H = 3 * F
            if cross:
                ufr.union(s1t1, H + s1t2)
                ufr.union(H + s1t1, s1t2)
                ufr.union(s2t1, H + s2t2)
                ufr.union(H + s2t1, s2t2)
                if cutedge:
                    ufc.union(t1, F + t2)
                    ufc.union(F + t1, t2)
            else:
                ufr.union(s1t1, s1t2)
                ufr.union(H + s1t1, H + s1t2)
                ufr.union(s2t1, s2t2)
                ufr.union(H + s2t1, H + s2t2)
                if cutedge:
                    ufc.union(t1, t2)
                    ufc.union(F + t1, F + t2)

        # project S^2 classes to RP^2 by identifying deck partners
        crep = {}

        def croot(x):
            crep.setdefault(x, x)
            while crep[x] != crep.setdefault(crep[x], crep[x]):
                crep[x] = crep[crep[x]]
            return crep[x]

        for ti in cut:
            a = croot(ufc.find(ti))
            b = croot(ufc.find(F + ti))
            if a != b:
                crep[b] = a
        comp_of = {ti: croot(ufc.find(ti)) for ti in cut}
        # a component is two-sided iff its two sheet classes differ
        comp_lifts = {}
        for ti in cut:
            c = comp_of[ti]
            if c not in comp_lifts:
                comp_lifts[c] = 2 if ufc.find(ti) != ufc.find(F + ti) else 1
        ncomp = len(set(comp_of.values()))
        if not want_scheme:
            return ncomp, None

        # regions in RP^2
        H = 3 * F
        rrep = {}

        def rroot(x):
            while rrep[x] != rrep.get(rrep[x], rrep[x]):
                rrep[x] = rrep[rrep[x]]
            return rrep[x]

        for cid in range(3 * F):
            r0, r1 = ufr.find(cid), ufr.find(H + cid)
            a = rrep.setdefault(r0, r0)
            a = rroot(r0)
            b = rrep.setdefault(r1, r1)
            b = rroot(r1)
            if a != b:
                rrep[b] = a
        region_of = [rroot(ufr.find(cid)) for cid in range(3 * F)]
        region_lifts = {}
        for cid in range(3 * F):
            r = region_of[cid]
            if r not in region_lifts:
                region_lifts[r] = (2 if ufr.find(cid) != ufr.find(H + cid)
                                   else 1)

        # adjacency
        adj = {}
        for ti in cut:
            o = odd[ti]
            c = comp_of[ti]
            s = adj.setdefault(c, set())
            s.add(region_of[3 * ti + o])
            s.add(region_of[3 * ti + (o + 1) % 3])

        return ncomp, _scheme(self.d, comp_of, comp_lifts,
                              region_of, region_lifts, adj)


def _scheme(d, comp_of, comp_lifts, region_of, region_lifts, adj):
    comps = sorted(set(comp_of.values()))
    regions = sorted(set(region_of))
    ovals, pseudo = [], []
    for c in comps:
        if comp_lifts[c] == 2:
            if len(adj[c]) != 2:
                return None
            ovals.append(c)
        else:
            if len(adj[c]) != 1:
                return None
            pseudo.append(c)
    if len(regions) != len(ovals) + 1:
        return None
    if d % 2 == 0 and pseudo:
        return None
    if d % 2 == 1 and len(pseudo) != 1:
        return None
    if pseudo:
        root = next(iter(adj[pseudo[0]]))
    else:
        nonor = [r for r in regions if region_lifts[r] == 1]
        if len(nonor) != 1:
            return None
        root = nonor[0]
    region_children = {r: [] for r in regions}
    for c in ovals:
        for r in adj[c]:
            region_children[r].append(c)
    seen_r, seen_c = {root}, set()
    frontier = [root]
    parent_region = {}
    while frontier:
        nxt = []
        for r in frontier:
            for c in region_children[r]:
                if c in seen_c:
                    continue
                seen_c.add(c)
                other = [x for x in adj[c] if x != r]
                if len(other) != 1:
                    return None
                r2 = other[0]
                if r2 in seen_r:
                    return None
                seen_r.add(r2)
                parent_region[c] = r
                nxt.append(r2)
        frontier = nxt
    if len(seen_c) != len(ovals) or len(seen_r) != len(regions):
        return None
    tree = {}
    for c in ovals:
        r = parent_region[c]
        other = [x for x in adj[c] if x != r][0]
        tree[c] = [x for x in region_children[other]
                   if parent_region.get(x) == other]
    roots = [c for c in ovals if parent_region[c] == root]

    def enc(c):
        return tuple(sorted(enc(k) for k in tree[c]))

    def render(forest):
        groups = []
        i = 0
        forest = sorted(forest)
        while i < len(forest):
            j = i
            while j < len(forest) and forest[j] == forest[i]:
                j += 1
            mult = j - i
            if forest[i] == ():
                groups.append(str(mult))
            else:
                groups.append(f"{mult}<{render(list(forest[i]))}>")
            i = j
        return " u ".join(groups) if groups else "0"

    body = render(sorted(enc(c) for c in roots))
    if pseudo:
        body = f"J u {body}" if body != "0" else "J"
    return f"<{body}>"
