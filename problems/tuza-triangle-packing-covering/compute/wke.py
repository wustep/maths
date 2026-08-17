"""Bitset WKE / graph6 helpers. Standard library only."""

from __future__ import annotations

from itertools import combinations
from functools import lru_cache


def parse_g6(line: str):
    s = line.strip()
    if not s or s[0] == ">":
        return None
    n = ord(s[0]) - 63
    bits = []
    for c in s[1:]:
        v = ord(c) - 63
        for b in range(5, -1, -1):
            bits.append((v >> b) & 1)
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges


def edge_index_table(n):
    pairs = list(combinations(range(n), 2))
    idx = {e: i for i, e in enumerate(pairs)}
    return pairs, idx


@lru_cache(maxsize=None)
def _wke_tables(n):
    pairs = list(combinations(range(n), 2))
    inc = [0] * n
    for i, (a, b) in enumerate(pairs):
        inc[a] |= 1 << i
        inc[b] |= 1 << i
    # all matchings as (edge_mask, size)
    matchings = []

    def rec(start, used_v, emask, sz):
        matchings.append((emask, sz))
        for i in range(start, len(pairs)):
            a, b = pairs[i]
            if (used_v >> a) & 1 or (used_v >> b) & 1:
                continue
            rec(i + 1, used_v | (1 << a) | (1 << b), emask | (1 << i), sz + 1)

    rec(0, 0, 0, 0)
    # covers: for each vertex-set mask, edges incident to it
    covers = [0] * (1 << n)
    for q in range(1 << n):
        m = 0
        t = q
        while t:
            v = (t & -t).bit_length() - 1
            m |= inc[v]
            t &= t - 1
        covers[q] = m
    # q-masks by size
    by_size = [[] for _ in range(n + 1)]
    for q in range(1 << n):
        by_size[q.bit_count()].append(q)
    return tuple(matchings), tuple(covers), tuple(tuple(s) for s in by_size), tuple(inc)


def edges_to_mask(n, edges):
    pairs, idx = edge_index_table(n)
    m = 0
    for a, b in edges:
        if a > b:
            a, b = b, a
        m |= 1 << idx[(a, b)]
    return m


def is_wke_mask(n, gmask):
    matchings, covers, by_size, _inc = _wke_tables(n)
    for emask, sz in matchings:
        if emask & ~gmask:
            continue
        rem = gmask & ~emask
        if rem == 0:
            return True
        for r in range(sz + 1):
            for q in by_size[r]:
                if rem & ~covers[q] == 0:
                    return True
    return False


def is_connected_mask(n, gmask, inc=None):
    if n <= 1:
        return True
    if inc is None:
        *_, inc = _wke_tables(n)
        inc = list(inc)
    adj = [0] * n
    # rebuild adj from mask
    pairs = list(combinations(range(n), 2))
    for i, (a, b) in enumerate(pairs):
        if (gmask >> i) & 1:
            adj[a] |= 1 << b
            adj[b] |= 1 << a
    seen = 1
    stack = [0]
    while stack:
        v = stack.pop()
        nbrs = adj[v]
        while nbrs:
            w = (nbrs & -nbrs).bit_length() - 1
            nbrs &= nbrs - 1
            if not ((seen >> w) & 1):
                seen |= 1 << w
                stack.append(w)
    return seen == (1 << n) - 1


def degrees_from_mask(n, gmask):
    pairs = list(combinations(range(n), 2))
    d = [0] * n
    for i, (a, b) in enumerate(pairs):
        if (gmask >> i) & 1:
            d[a] += 1
            d[b] += 1
    return d
