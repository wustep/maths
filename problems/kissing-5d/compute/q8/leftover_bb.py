#!/usr/bin/env python3
"""Leftover-tight extras B&B (second algorithm, Python).

A leftover 41-set in a pool is a clique E of extras with missed-union U
satisfying |U| >= 19 and |E| >= |U| + 1 (hence |E| >= 20).  This is the
same cut as four_star_extras.c / five_star_extras.c, not a pure ω hunt.
A 20-clique with large U is not a 41-set.
"""

from __future__ import annotations


def leftover_search(adj, n, miss, target=20, node_limit=2_000_000):
    """Return (found_stack or None, best, nodes, complete, found_U)."""
    best = target - 1
    found = None
    found_U = 0
    nodes = 0

    def expand(P, stack, U):
        nonlocal best, found, found_U, nodes
        if found is not None:
            return
        nodes += 1
        if nodes > node_limit:
            return
        rsz = len(stack)
        psz = P.bit_count()
        uk = U.bit_count()
        if rsz + psz <= uk:
            return
        if rsz + psz < target:
            return
        if P == 0:
            if rsz > best:
                best = rsz
            if rsz >= uk + 1 and rsz >= target and uk >= 19:
                found = list(stack)
                found_U = U
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
            if rsz + col[i] < target:
                return
            v = ord_v[i]
            U2 = U | miss[v]
            uk2 = U2.bit_count()
            if rsz + 1 + (psz - 1) <= uk2:
                Q &= ~(1 << v)
                continue
            stack.append(v)
            if rsz + 1 >= target and rsz + 1 >= uk2 + 1 and uk2 >= 19:
                found = list(stack)
                best = rsz + 1
                found_U = U2
                return
            expand(Q & adj[v], stack, U2)
            stack.pop()
            Q &= ~(1 << v)

    expand((1 << n) - 1, [], 0)
    complete = found is not None or nodes <= node_limit
    return found, best, nodes, complete, found_U
