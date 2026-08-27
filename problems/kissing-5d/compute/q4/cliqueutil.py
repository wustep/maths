"""Coloured branch-and-bound for a bitset graph."""

from __future__ import annotations


def clique_search(adj, n, target, node_limit=2_000_000, seed_best=0):
    """Return (found_clique or None, best, nodes, complete)."""
    best = seed_best
    found = None
    nodes = 0

    def expand(P, stack):
        nonlocal best, found, nodes
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
            return
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
                return
            expand(Q & adj[v], stack)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [])
    return found, best, nodes, found is not None or nodes <= node_limit


def graph_from_ok(n, ok):
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ok(i, j):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    return adj, edges
