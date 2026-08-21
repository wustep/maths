#!/usr/bin/env python3
"""Combinatorial patchworking (T-curve) verifier, written from scratch.

Given
  * a primitive triangulation of T_d = conv{(0,0),(d,0),(0,d)} using all
    lattice points of T_d as vertices,
  * a rational lifting (heights) certifying the triangulation is convex
    (= regular: it is exactly the projection of the lower hull of the
    lifted points), and
  * a sign distribution eps: lattice points -> {+1,-1},
this module builds the T-curve in RP^2 (rhombus |x|+|y| <= d with
antipodal boundary gluing, signs replicated by
eps((-1)^a i, (-1)^b j) = eps(i,j) * (-1)^(a*i + b*j)),
computes its connected components, decides oval vs one-sided component
via the S^2 double cover, and extracts the real scheme (nesting forest)
in standard bracket notation.

By Viro's patchworking theorem the T-curve is isotopic in RP^2 to a
nonsingular real algebraic curve of degree d, so a verified certificate
here is a certified algebraic realization of the printed scheme.

Everything is exact: convexity checks use Fractions, topology is
combinatorial union-find.  No third-party libraries.

CLI:
  python3 tcurve.py verify cert.json      # full certificate check
"""

from fractions import Fraction
import json
import sys


# ---------------------------------------------------------------------------
# small union-find

class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        if x not in p:
            p[x] = x
            return x
        r = x
        while p[r] != r:
            r = p[r]
        while p[x] != r:
            p[x], x = r, p[x]
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb

    def classes(self):
        out = {}
        for x in self.p:
            out.setdefault(self.find(x), []).append(x)
        return out


# ---------------------------------------------------------------------------
# lattice / triangulation basics

def lattice_points(d):
    return [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]


def tri_area2(t):
    (x1, y1), (x2, y2), (x3, y3) = t
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))


def validate_triangulation(d, triangles):
    """Primitive triangulation of T_d using all lattice points.

    Checks: d^2 triangles, each of lattice area 1/2 (area2 == 1), all
    vertices lattice points of T_d, every lattice point used, and the
    edge-manifold condition: every edge lies in exactly 2 triangles
    except edges on the boundary of T_d, which lie in exactly 1.
    Together with the area count 4 * d^2 * (1/2)... more precisely
    sum of areas = area(T_d) and interiors are disjoint by the exact
    convexity certificate checked separately; here we do the purely
    combinatorial part.
    """
    pts = set(lattice_points(d))
    errs = []
    if len(triangles) != d * d:
        errs.append(f"expected {d*d} triangles, got {len(triangles)}")
    used = set()
    edge_count = {}
    for t in triangles:
        if len(t) != 3:
            errs.append(f"non-triangle cell {t}")
            continue
        for v in t:
            if tuple(v) not in pts:
                errs.append(f"vertex {v} outside T_{d}")
        if tri_area2([tuple(v) for v in t]) != 1:
            errs.append(f"non-primitive triangle {t}")
        vs = [tuple(v) for v in t]
        used.update(vs)
        for k in range(3):
            e = frozenset((vs[k], vs[(k + 1) % 3]))
            edge_count[e] = edge_count.get(e, 0) + 1
    missing = pts - used
    if missing:
        errs.append(f"unused lattice points {sorted(missing)}")

    def on_boundary(e):
        (x1, y1), (x2, y2) = sorted(e)
        if x1 == x2 == 0 or y1 == y2 == 0:
            return True
        return x1 + y1 == d and x2 + y2 == d

    for e, c in edge_count.items():
        want = 1 if on_boundary(e) else 2
        if c != want:
            errs.append(f"edge {sorted(e)} in {c} triangles, want {want}")
    return errs


def check_convexity(d, triangles, heights):
    """Exact certificate that `triangles` is the regular subdivision
    induced by `heights` (a dict point -> Fraction).

    For each triangle, the affine function through its three lifted
    vertices must lie strictly below every other lifted lattice point.
    That makes each triangle a face of the lower hull, and since the
    triangles tile T_d, the regular subdivision is exactly this
    triangulation.  Returns list of error strings (empty = certified).
    """
    errs = []
    pts = lattice_points(d)
    for t in triangles:
        (x1, y1), (x2, y2), (x3, y3) = [tuple(v) for v in t]
        h1, h2, h3 = heights[(x1, y1)], heights[(x2, y2)], heights[(x3, y3)]
        # affine A(x,y) = a x + b y + c through the three lifted points
        det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        if det == 0:
            errs.append(f"degenerate triangle {t}")
            continue
        a = Fraction((h2 - h1) * (y3 - y1) - (h3 - h1) * (y2 - y1), det)
        b = Fraction((x2 - x1) * (h3 - h1) - (x3 - x1) * (h2 - h1), det)
        c = h1 - a * x1 - b * y1
        tv = {(x1, y1), (x2, y2), (x3, y3)}
        for p in pts:
            if p in tv:
                continue
            if heights[p] <= a * p[0] + b * p[1] + c:
                errs.append(
                    f"height at {p} not above plane of {t}: "
                    f"{heights[p]} <= {a * p[0] + b * p[1] + c}")
    return errs


# ---------------------------------------------------------------------------
# the T-curve in RP^2

def _sign_at(signs, x, y):
    i, j = abs(x), abs(y)
    s = signs[(i, j)]
    if x < 0 and i % 2 == 1:
        s = -s
    if y < 0 and j % 2 == 1:
        s = -s
    return s


def _antipode(p):
    return (-p[0], -p[1])


class TCurve:
    """Combinatorial T-curve in RP^2 for even or odd degree d."""

    def __init__(self, d, triangles, signs):
        self.d = d
        self.signs = signs
        # rhombus triangles: reflect each triangle into the 4 quadrants
        rtris = []
        for t in triangles:
            vs = [tuple(v) for v in t]
            for a in (1, -1):
                for b in (1, -1):
                    rtris.append(tuple((a * x, b * y) for (x, y) in vs))
        self.rtris = rtris
        self.sigma = {}
        for t in rtris:
            for (x, y) in t:
                if (x, y) not in self.sigma:
                    self.sigma[(x, y)] = _sign_at(signs, x, y)
        # sanity: sign rule is consistent on the axes by construction;
        # antipodal boundary consistency holds up to (-1)^d and both
        # endpoints of an edge flip together, so cut-ness is well defined.
        self._build()

    # -- construction -----------------------------------------------------
    def _build(self):
        d = self.d
        edge_tris = {}
        for ti, t in enumerate(self.rtris):
            for k in range(3):
                e = frozenset((t[k], t[(k + 1) % 3]))
                edge_tris.setdefault(e, []).append(ti)

        def on_rhombus_boundary(e):
            return all(abs(x) + abs(y) == d for (x, y) in e)

        # glue rhombus boundary edges antipodally
        glue = {}
        for e, ts in edge_tris.items():
            if len(ts) == 1:
                if not on_rhombus_boundary(e):
                    raise ValueError(f"dangling interior edge {sorted(e)}")
                e2 = frozenset(_antipode(p) for p in e)
                if e2 not in edge_tris or len(edge_tris[e2]) != 1:
                    raise ValueError(f"boundary edge {sorted(e)} has no "
                                     "antipodal partner")
                glue[e] = e2
            elif len(ts) != 2:
                raise ValueError(f"edge {sorted(e)} in {len(ts)} triangles")

        self.edge_tris = edge_tris
        self.glue = glue

        def cut(e):
            p, q = tuple(e)
            return self.sigma[p] != self.sigma[q]

        # --- curve components: union-find over triangles with a segment
        ufc = UF()
        cut_tris = set()
        for ti, t in enumerate(self.rtris):
            ss = {self.sigma[v] for v in t}
            if len(ss) == 2:
                cut_tris.add(ti)
                ufc.find(ti)
        for e, ts in edge_tris.items():
            if not cut(e):
                continue
            if len(ts) == 2:
                ufc.union(ts[0], ts[1])
            else:
                e2 = glue[e]
                ufc.union(ts[0], edge_tris[e2][0])
        self.comp_of = {ti: ufc.find(ti) for ti in cut_tris}
        self.components = sorted(set(self.comp_of.values()))

        # --- regions: union-find over corners (triangle, vertex)
        ufr = UF()
        for ti, t in enumerate(self.rtris):
            svals = [self.sigma[v] for v in t]
            if len(set(svals)) == 1:
                ufr.union((ti, t[0]), (ti, t[1]))
                ufr.union((ti, t[0]), (ti, t[2]))
            else:
                # the two same-sign corners connect
                maj = 1 if svals.count(1) == 2 else -1
                same = [v for v in t if self.sigma[v] == maj]
                ufr.union((ti, same[0]), (ti, same[1]))
        for e, ts in edge_tris.items():
            if len(ts) == 2:
                t1, t2 = ts
                for p in e:
                    ufr.union((t1, p), (t2, p))
            else:
                e2 = glue[e]
                t1, t2 = ts[0], edge_tris[e2][0]
                for p in e:
                    ufr.union((t1, p), (t2, _antipode(p)))
        self.region_of = {}
        for ti, t in enumerate(self.rtris):
            for v in t:
                self.region_of[(ti, v)] = ufr.find((ti, v))
        self.regions = sorted(set(self.region_of.values()))

        # --- double cover (S^2): same complex, two sheets, boundary
        # gluing crosses sheets.  Detects one-sided components and
        # non-orientable regions.
        ufc2, ufr2 = UF(), UF()
        for sheet in (0, 1):
            for ti, t in enumerate(self.rtris):
                svals = [self.sigma[v] for v in t]
                if len(set(svals)) == 1:
                    ufr2.union((sheet, ti, t[0]), (sheet, ti, t[1]))
                    ufr2.union((sheet, ti, t[0]), (sheet, ti, t[2]))
                else:
                    maj = 1 if svals.count(1) == 2 else -1
                    same = [v for v in t if self.sigma[v] == maj]
                    ufr2.union((sheet, ti, same[0]), (sheet, ti, same[1]))
                if ti in cut_tris:
                    ufc2.find((sheet, ti))
        for e, ts in edge_tris.items():
            if len(ts) == 2:
                t1, t2 = ts
                for sheet in (0, 1):
                    if cut(e):
                        ufc2.union((sheet, t1), (sheet, t2))
                    for p in e:
                        ufr2.union((sheet, t1, p), (sheet, t2, p))
            else:
                e2 = glue[e]
                t1, t2 = ts[0], edge_tris[e2][0]
                for sheet in (0, 1):
                    if cut(e):
                        ufc2.union((sheet, t1), (1 - sheet, t2))
                    for p in e:
                        ufr2.union((sheet, t1, p),
                                   (1 - sheet, t2, _antipode(p)))
        lifts_c = {}
        for ti in cut_tris:
            for sheet in (0, 1):
                lifts_c.setdefault(self.comp_of[ti], set()).add(
                    ufc2.find((sheet, ti)))
        self.comp_lifts = {c: len(s) for c, s in lifts_c.items()}
        lifts_r = {}
        for (ti, v), r in self.region_of.items():
            for sheet in (0, 1):
                lifts_r.setdefault(r, set()).add(ufr2.find((sheet, ti, v)))
        self.region_lifts = {r: len(s) for r, s in lifts_r.items()}

        # --- component <-> region adjacency
        adj = {}
        for ti in cut_tris:
            t = self.rtris[ti]
            svals = [self.sigma[v] for v in t]
            maj = 1 if svals.count(1) == 2 else -1
            odd = [v for v in t if self.sigma[v] != maj][0]
            same = [v for v in t if self.sigma[v] == maj][0]
            c = self.comp_of[ti]
            adj.setdefault(c, set()).add(self.region_of[(ti, odd)])
            adj.setdefault(c, set()).add(self.region_of[(ti, same)])
        self.adj = adj

        # Euler characteristic of the glued complex must be chi(RP^2)=1
        verts = set()
        for t in self.rtris:
            verts.update(t)
        boundary_verts = {v for v in verts
                          if abs(v[0]) + abs(v[1]) == self.d}
        nv = (len(verts) - len(boundary_verts)) + len(boundary_verts) // 2
        ne_int = sum(1 for e, ts in edge_tris.items() if len(ts) == 2)
        ne_bnd = len(glue) // 2
        nf = len(self.rtris)
        self.euler = nv - (ne_int + ne_bnd) + nf
        if self.euler != 1:
            raise ValueError(f"glued complex has chi={self.euler}, not 1")

    # -- topology ---------------------------------------------------------
    def structure(self):
        """Validate global structure, return (ovals, pseudolines, tree).

        ovals: components with 2 lifts; pseudolines: 1 lift.
        Checks each oval touches exactly 2 regions, each pseudoline 1,
        #regions == #ovals + 1, region graph over ovals is a tree.
        """
        errs = []
        ovals, pseudo = [], []
        for c in self.components:
            nl = self.comp_lifts[c]
            na = len(self.adj[c])
            if nl == 2:
                ovals.append(c)
                if na != 2:
                    errs.append(f"oval {c} adjacent to {na} regions")
            elif nl == 1:
                pseudo.append(c)
                if na != 1:
                    errs.append(f"one-sided comp {c} adjacent to "
                                f"{na} regions")
            else:
                errs.append(f"component {c} has {nl} lifts")
        if len(self.regions) != len(ovals) + 1:
            errs.append(f"{len(self.regions)} regions vs "
                        f"{len(ovals)} ovals + 1")
        if self.d % 2 == 0 and pseudo:
            errs.append("one-sided component in even degree")
        if self.d % 2 == 1 and len(pseudo) != 1:
            errs.append(f"{len(pseudo)} one-sided components, want 1")
        nonor = [r for r in self.regions if self.region_lifts[r] == 1]
        if errs:
            return errs, None, None, None
        # root: the region 'outside' every oval
        if pseudo:
            root = next(iter(self.adj[pseudo[0]]))
        else:
            if len(nonor) != 1:
                return ([f"{len(nonor)} non-orientable regions, want 1"],
                        None, None, None)
            root = nonor[0]
        # build tree by BFS from root over oval edges
        tree = {}   # oval -> list of child ovals
        region_children = {r: [] for r in self.regions}
        for c in ovals:
            for r in self.adj[c]:
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
                    other = [x for x in self.adj[c] if x != r]
                    if len(other) != 1:
                        return ([f"oval {c} bad adjacency"], None, None,
                                None)
                    r2 = other[0]
                    if r2 in seen_r:
                        return ([f"region graph has a cycle at {r2}"],
                                None, None, None)
                    seen_r.add(r2)
                    parent_region[c] = r
                    tree[c] = []
                    nxt.append(r2)
            frontier = nxt
        if len(seen_c) != len(ovals) or len(seen_r) != len(self.regions):
            return (["region graph disconnected"], None, None, None)
        for c in ovals:
            r = parent_region[c]
            other = [x for x in self.adj[c] if x != r][0]
            tree[c] = list(region_children[other])
            tree[c] = [x for x in tree[c] if parent_region.get(x) == other]
        roots = [c for c in ovals if parent_region[c] == root]
        return [], roots, tree, bool(pseudo)

    def scheme(self):
        """Canonical bracket notation of the real scheme."""
        errs, roots, tree, has_j = self.structure()
        if errs:
            raise ValueError("; ".join(errs))

        def enc(c):
            kids = sorted(enc(k) for k in tree[c])
            return tuple(kids)

        def render(forest):
            # forest: sorted list of encodings
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
                    inner = render(list(forest[i]))
                    groups.append(f"{mult}<{inner}>")
                i = j
            return " u ".join(groups) if groups else "0"

        forest = sorted(enc(c) for c in roots)
        body = render(forest)
        if has_j:
            body = f"J u {body}" if body != "0" else "J"
        return f"<{body}>"

    def counts(self):
        errs, roots, tree, has_j = self.structure()
        if errs:
            raise ValueError("; ".join(errs))
        n_ovals = len(tree)
        return {"components": len(self.components), "ovals": n_ovals,
                "pseudolines": 1 if has_j else 0}


# ---------------------------------------------------------------------------
# certificates

def parse_heights(d, hdict):
    out = {}
    for k, v in hdict.items():
        i, j = (int(x) for x in k.split(","))
        out[(i, j)] = Fraction(v)
    return out


def parse_signs(d, sdict):
    out = {}
    for k, v in sdict.items():
        i, j = (int(x) for x in k.split(","))
        if v not in (1, -1):
            raise ValueError(f"sign at ({i},{j}) is {v}")
        out[(i, j)] = v
    return out


def verify_certificate(cert, quiet=False):
    d = cert["d"]
    triangles = [tuple(tuple(v) for v in t) for t in cert["triangles"]]
    heights = parse_heights(d, cert["heights"])
    signs = parse_signs(d, cert["signs"])
    for p in lattice_points(d):
        if p not in heights:
            raise ValueError(f"missing height at {p}")
        if p not in signs:
            raise ValueError(f"missing sign at {p}")
    errs = validate_triangulation(d, triangles)
    if errs:
        return False, "triangulation: " + "; ".join(errs[:5]), None
    errs = check_convexity(d, triangles, heights)
    if errs:
        return False, "convexity: " + "; ".join(errs[:5]), None
    tc = TCurve(d, triangles, signs)
    scheme = tc.scheme()
    counts = tc.counts()
    if "claimed_scheme" in cert and cert["claimed_scheme"] != scheme:
        return (False, f"claimed {cert['claimed_scheme']} but computed "
                f"{scheme}", scheme)
    if not quiet:
        print(f"degree {d}: {counts['components']} components "
              f"({counts['ovals']} ovals"
              + (", 1 pseudoline" if counts["pseudolines"] else "")
              + f"), scheme {scheme}")
        print("triangulation: primitive, convex (exact rational "
              "certificate) -- Viro: realized by a nonsingular real "
              f"algebraic curve of degree {d}")
    return True, "ok", scheme


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "verify":
        ok_all = True
        for path in sys.argv[2:]:
            with open(path) as f:
                cert = json.load(f)
            ok, msg, scheme = verify_certificate(cert)
            print(f"{path}: {'PASS' if ok else 'FAIL'} ({msg})")
            ok_all = ok_all and ok
        sys.exit(0 if ok_all else 1)
    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
