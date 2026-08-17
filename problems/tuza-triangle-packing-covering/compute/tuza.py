"""Exact nu / tau / WKE helpers. Standard library + optional pulp."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable


def edge(a, b):
    return (a, b) if a < b else (b, a)


def complete_edges(vertices):
    return {edge(a, b) for a, b in combinations(sorted(vertices), 2)}


def triangles_of(edges, vertices=None):
    if vertices is None:
        vertices = sorted({x for e in edges for x in e})
    E = set(edges)
    out = []
    for a, b, c in combinations(vertices, 3):
        ea, eb, ec = edge(a, b), edge(b, c), edge(a, c)
        if ea in E and eb in E and ec in E:
            out.append((a, b, c))
    return out


def triangle_edge_set(t):
    a, b, c = t
    return frozenset((edge(a, b), edge(b, c), edge(a, c)))


def packing_number(edges, vertices=None):
    """Maximum number of pairwise edge-disjoint triangles."""
    tris = triangles_of(edges, vertices)
    sets = [triangle_edge_set(t) for t in tris]
    best = 0

    def search(index, used, size):
        nonlocal best
        if size + (len(sets) - index) <= best:
            return
        if index == len(sets):
            if size > best:
                best = size
            return
        if not (used & sets[index]):
            search(index + 1, used | sets[index], size + 1)
        search(index + 1, used, size)

    search(0, frozenset(), 0)
    return best


def cover_number(edges, vertices=None):
    """Minimum number of edges meeting every triangle."""
    tris = triangles_of(edges, vertices)
    if not tris:
        return 0
    sets = [triangle_edge_set(t) for t in tris]

    def feasible(budget):
        def rec(deleted, left):
            remaining = [s for s in sets if not (s & deleted)]
            if not remaining:
                return True
            if left == 0:
                return False
            # branch on an unused triangle of minimum leftover edges
            t = min(remaining, key=len)
            for e in t:
                if rec(deleted | {e}, left - 1):
                    return True
            return False

        return rec(frozenset(), budget)

    lo, hi = 0, min(len(edges), 3 * packing_number(edges, vertices))
    # hi is a valid cover (all edges of a max packing)
    # but we may not want to recompute packing; use |edges|
    hi = min(len(edges), sum(1 for _ in tris))
    # binary search
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def nu_tau(edges, vertices=None):
    return packing_number(edges, vertices), cover_number(edges, vertices)


def nu_tau_ilp(edges, vertices=None):
    """Exact nu, tau via CBC. Falls back to search if pulp is missing."""
    try:
        import pulp
    except ImportError:
        return nu_tau(edges, vertices)
    if vertices is None:
        vertices = sorted({x for e in edges for x in e})
    tris = triangles_of(edges, vertices)
    if not tris:
        return 0, 0
    elist = [tuple(sorted(e)) for e in edges]
    tsets = [triangle_edge_set(t) for t in tris]

    p = pulp.LpProblem("nu", pulp.LpMaximize)
    s = [pulp.LpVariable(f"s{i}", cat="Binary") for i in range(len(tris))]
    p += pulp.lpSum(s)
    for e in elist:
        p += pulp.lpSum(s[i] for i, ts in enumerate(tsets) if e in ts) <= 1
    st = p.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))
    if pulp.LpStatus[st] != "Optimal":
        return nu_tau(edges, vertices)
    nu = int(round(pulp.value(p.objective)))

    q = pulp.LpProblem("tau", pulp.LpMinimize)
    x = {e: pulp.LpVariable(f"x{i}", cat="Binary") for i, e in enumerate(elist)}
    q += pulp.lpSum(x[e] for e in elist)
    for ts in tsets:
        q += pulp.lpSum(x[e] for e in ts if e in x) >= 1
    st = q.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))
    if pulp.LpStatus[st] != "Optimal":
        return nu, cover_number(edges, vertices)
    tau = int(round(pulp.value(q.objective)))
    return nu, tau


# ---------------------------------------------------------------------------
# Weak König–Egerváry
# ---------------------------------------------------------------------------

def all_matchings(n):
    """All matchings on K_n as lists of edges (pairs)."""
    pairs = list(combinations(range(n), 2))
    out = [[]]
    def rec(start, used, cur):
        out.append(list(cur))
        for i in range(start, len(pairs)):
            a, b = pairs[i]
            if (used >> a) & 1 or (used >> b) & 1:
                continue
            cur.append((a, b))
            rec(i + 1, used | (1 << a) | (1 << b), cur)
            cur.pop()
    rec(0, 0, [])
    # rec appended empty at the start of every call; unique-ify
    uniq = {frozenset(m) for m in out}
    return [list(m) for m in uniq]


def is_wke(n, edges):
    """True iff the n-vertex graph with the given edges is weak KE."""
    E = set(edge(a, b) for a, b in edges)
    # precompute incident edges per vertex
    inc = [set() for _ in range(n)]
    for a, b in E:
        inc[a].add(edge(a, b))
        inc[b].add(edge(a, b))
    pairs = list(combinations(range(n), 2))

    # enumerate matchings contained in E
    def matchings():
        yield []
        def rec(start, used, cur):
            for i in range(start, len(pairs)):
                a, b = pairs[i]
                if edge(a, b) not in E:
                    continue
                if (used >> a) & 1 or (used >> b) & 1:
                    continue
                nxt = cur + [(a, b)]
                yield nxt
                yield from rec(i + 1, used | (1 << a) | (1 << b), nxt)
        yield from rec(0, 0, [])

    for M in matchings():
        rem = E - {edge(a, b) for a, b in M}
        k = len(M)
        # does rem have a vertex cover of size <= k?
        # enumerate subsets of V of size <= k
        vs = list(range(n))
        found = False
        for r in range(k + 1):
            for Q in combinations(vs, r):
                covered = set()
                for v in Q:
                    covered |= inc[v]
                if rem <= covered:
                    found = True
                    break
            if found:
                break
        if found:
            return True
    return False


def is_connected(n, edges):
    if n == 0:
        return True
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


def degrees(n, edges):
    d = [0] * n
    for a, b in edges:
        d[a] += 1
        d[b] += 1
    return d
