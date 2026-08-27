#!/usr/bin/env python3
"""Type-A extras with a small missed-union.

Type A is (4,2,2,2,2): 160 points, one per four-seed.  A clique C of
type-A extras plus D5 \\ U is a 41-set iff |C| >= |U| + 1.  This file
hunts |C| >= 20 with |U| <= |C| - 1, i.e. 20 extras with |U| <= 19 or
a larger clique that still pays for its union.

The graph is vertex-transitive under signed coordinate permutations,
so the search fixes extra 0 and branches on Stab(0)-orbit
representatives of its neighbours.  Coloured B&B tracks
U = union of missed 4-sets and prunes when
|U| > |stack| + remaining - 1.  node_limit 3e6 (light).  Incomplete
is residue.  Does not claim tau_5 = 40.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import d5_pts, extras_and_groups, ip  # noqa: E402

NODE_LIMIT = 3_000_000
TARGET = 20


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def missed_mask(p, D, thresh):
    m = 0
    for j, r in enumerate(D):
        if ip(p, r) > thresh:
            m |= 1 << j
    return m


def signed_perm_orbit(v):
    out = set()
    for perm in permutations(range(5)):
        w = [v[perm[i]] for i in range(5)]
        for signs in product((-1, 1), repeat=5):
            out.add(tuple(signs[i] * w[i] for i in range(5)))
    return out


def stab_other_axes(p0):
    ax = [i for i in range(5) if abs(p0[i]) == 4]
    assert len(ax) == 1
    a4 = ax[0]
    others = [i for i in range(5) if i != a4]

    def apply(p, perm):
        q = list(p)
        vals = [p[i] for i in others]
        for i, src in enumerate(perm):
            q[others[i]] = vals[src]
        return tuple(q)

    return apply, list(permutations(range(4)))


def neighbour_orbit_reps(type_A, adj, p0_index=0):
    n = len(type_A)
    idx = {p: i for i, p in enumerate(type_A)}
    apply, perms = stab_other_axes(type_A[p0_index])
    nbrs = [i for i in range(n) if i != p0_index and (adj[p0_index] >> i) & 1]
    nbr_set = set(nbrs)
    reps = []
    seen = set()
    for i in nbrs:
        if i in seen:
            continue
        orb = []
        for perm in perms:
            q = apply(type_A[i], perm)
            j = idx[q]
            if j in nbr_set and j not in seen:
                seen.add(j)
                orb.append(j)
        reps.append(min(orb))
    return sorted(set(reps))


def write_code41(type_A, D, clique, Umask):
    """Unit-sphere points: integer model / 4, as Fraction strings."""
    (HERE / "certs").mkdir(exist_ok=True)
    pts = []
    for i in clique:
        pts.append([str(Fraction(x, 4)) for x in type_A[i]])
    for r, p in enumerate(D):
        if not ((Umask >> r) & 1):
            pts.append([str(Fraction(x, 4)) for x in p])
    rec = {
        "n": len(pts),
        "source": "q5 type_a_small_U.py type-A clique plus D5\\\\U",
        "n_extras": len(clique),
        "n1": 40 - Umask.bit_count(),
        "U": Umask.bit_count(),
        "points": pts,
    }
    path = HERE / "certs" / "code41.json"
    path.write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def small_U_search(adj, miss, n, starts, target=TARGET, node_limit=NODE_LIMIT):
    """Coloured B&B tracking U.  Return (found, best_ex, best_U, clique, Umask, nodes, complete)."""
    best_ex = 0
    best_U = None
    best_clique = None
    best_Umask = 0
    found = None
    found_Umask = 0
    nodes = 0

    def record(stack, U):
        nonlocal best_ex, best_U, best_clique, best_Umask, found, found_Umask
        rsz = len(stack)
        uk = U.bit_count()
        if rsz > best_ex or (rsz == best_ex and (best_U is None or uk < best_U)):
            best_ex = rsz
            best_U = uk
            best_clique = list(stack)
            best_Umask = U
        if rsz >= target and uk <= rsz - 1 and found is None:
            found = list(stack)
            found_Umask = U
            best_ex = rsz
            best_U = uk
            best_clique = list(stack)
            best_Umask = U

    def expand(P, stack, U):
        nonlocal nodes
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            return
        rsz = len(stack)
        uk = U.bit_count()
        record(stack, U)
        if found is not None:
            return
        while True:
            psz = P.bit_count()
            if rsz + psz < target:
                return
            if uk > rsz + psz - 1:
                return
            cap = rsz + psz - 1
            P2 = 0
            x = P
            while x:
                v = (x & -x).bit_length() - 1
                x &= x - 1
                if (U | miss[v]).bit_count() <= cap:
                    P2 |= 1 << v
            if P2 == P:
                break
            P = P2
        if P == 0:
            return

        rem = P
        ord_v, col = [], []
        c = 0
        while rem:
            c += 1
            avail = rem
            while avail:
                v = (avail & -avail).bit_length() - 1
                # colour small-new-U vertices first so high-new-U
                # vertices get high colours and are branched first
                pick = v
                pick_new = (miss[v] & ~U).bit_count()
                y = avail & ~(1 << v)
                while y:
                    w = (y & -y).bit_length() - 1
                    y &= y - 1
                    nw = (miss[w] & ~U).bit_count()
                    if nw < pick_new:
                        pick, pick_new = w, nw
                v = pick
                ord_v.append(v)
                col.append(c)
                avail &= ~adj[v]
                avail &= ~(1 << v)
                rem &= ~(1 << v)

        Q = P
        for i in range(len(ord_v) - 1, -1, -1):
            if found is not None or nodes > node_limit:
                return
            if rsz + col[i] < target:
                return
            if uk > rsz + col[i] - 1:
                return
            v = ord_v[i]
            stack.append(v)
            expand(Q & adj[v], stack, U | miss[v])
            stack.pop()
            Q &= ~(1 << v)

    for stack0, U0, P0 in starts:
        if found is not None or nodes > node_limit:
            break
        record(stack0, U0)
        if found is not None:
            break
        expand(P0, list(stack0), U0)

    complete = found is not None or nodes <= node_limit
    return found, best_ex, best_U, best_clique, best_Umask, nodes, complete


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    thresh = G["thresh"]
    type_A = [p for p in extras if type_key(p) == (2, 2, 2, 2, 4)]
    n = len(type_A)
    assert n == 160
    assert signed_perm_orbit((4, 2, 2, 2, 2)) == set(type_A)
    Dlist = d5_pts(4)
    assert Dlist == list(D)

    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(type_A[i], type_A[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    miss = [missed_mask(p, D, thresh) for p in type_A]
    assert all(m.bit_count() == 4 for m in miss)
    assert len(set(miss)) == 160

    # sample 20-clique (unconstrained) so the report records that
    # omega >= 20 with a typically large union
    sample, sample_best, sample_nodes, sample_complete = clique_search(
        adj, n, target=TARGET, node_limit=200_000, seed_best=19
    )
    sample_U = None
    if sample:
        um = 0
        for i in sample:
            um |= miss[i]
        sample_U = um.bit_count()

    reps = neighbour_orbit_reps(type_A, adj, 0)
    starts = []
    for r in reps:
        stack = [0, r]
        U = miss[0] | miss[r]
        P = adj[0] & adj[r]
        starts.append((stack, U, P))

    found, best_ex, best_U, clique, Umask, nodes, complete = small_U_search(
        adj, miss, n, starts, target=TARGET, node_limit=NODE_LIMIT
    )

    uk = None if clique is None else Umask.bit_count()
    n1 = None if uk is None else 40 - uk
    total = None if clique is None else len(clique) + n1
    found_41 = bool(found) or (
        clique is not None and len(clique) >= TARGET and uk <= len(clique) - 1
    )
    write_cert = bool(
        clique is not None and len(clique) >= TARGET and uk is not None and uk <= 19
    )
    if write_cert:
        write_code41(type_A, D, clique, Umask)

    report = {
        "n": n,
        "edges": edges,
        "target": TARGET,
        "node_limit": NODE_LIMIT,
        "nodes": nodes,
        "n_start_orbits": len(reps),
        "fixed_vertex": 0,
        "found_41": found_41,
        "best_extras": best_ex,
        "best_U": best_U,
        "n1": n1,
        "total": total,
        "gives_41": found_41,
        "complete": complete,
        "residue": not complete and not found_41,
        "clique": clique,
        "U_mask_pop": uk,
        "sample_20": {
            "found": bool(sample),
            "best": sample_best,
            "U": sample_U,
            "nodes": sample_nodes,
            "complete": sample_complete,
            "clique": sample,
        },
        "comment": (
            "Coloured B&B on the 160 type-A extras, tracking the missed "
            "4-set union U and pruning when |U| > |stack|+remaining-1.  "
            "Vertex-transitive: cliques are represented with extra 0.  "
            "A hit is a 41-set with D5\\\\U.  Incomplete is residue.  "
            "Did not claim tau_5=40."
        ),
    }
    (HERE / "type_a_small_U.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        k: report[k] for k in (
            "found_41", "best_extras", "best_U", "total",
            "complete", "residue", "nodes", "n_start_orbits",
        )
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
