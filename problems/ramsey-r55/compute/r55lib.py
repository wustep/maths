"""Bitset tools for (5,5)-Ramsey graphs on n <= 64 vertices.

A (s,t,n)-Ramsey graph is an n-vertex graph with omega < s and alpha < t.
"""

from __future__ import annotations

import json
from typing import Iterable


def parse_graph6(line: str) -> tuple[int, list[int]]:
    """Return (n, nbr) where nbr[i] is a uint64 neighbourhood bitset."""
    s = line.strip()
    if not s or s[0] == ">":
        raise ValueError(f"unsupported graph6: {s[:20]!r}")
    n = ord(s[0]) - 63
    if n < 0 or n > 62:
        raise ValueError(f"graph6 order {n} out of range")
    need = (n * (n - 1) // 2 + 5) // 6
    data = s[1:]
    if len(data) < need:
        raise ValueError(f"short graph6 n={n}: got {len(data)} need {need}")
    bits = []
    for c in data[:need]:
        v = ord(c) - 63
        for i in range(5, -1, -1):
            bits.append((v >> i) & 1)
    nbr = [0] * n
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                nbr[i] |= 1 << j
                nbr[j] |= 1 << i
            k += 1
    return n, nbr


def to_graph6(nbr: list[int]) -> str:
    n = len(nbr)
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (nbr[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for i in range(0, len(bits), 6):
        v = 0
        for b in bits[i : i + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return "".join(out)


def complement(nbr: list[int]) -> list[int]:
    n = len(nbr)
    full = ((1 << n) - 1)
    return [((full ^ (1 << i)) ^ nbr[i]) for i in range(n)]


def degrees(nbr: list[int]) -> list[int]:
    return [x.bit_count() for x in nbr]


def n_edges(nbr: list[int]) -> int:
    return sum(degrees(nbr)) // 2


def triangles(nbr: list[int]) -> int:
    t = 0
    n = len(nbr)
    for i in range(n):
        ni = nbr[i]
        jmask = ni
        while jmask:
            jbit = jmask & -jmask
            j = jbit.bit_length() - 1
            if j > i:
                t += (ni & nbr[j]).bit_count()
            jmask ^= jbit
    return t // 3


def _has_clique(nbr: list[int], k: int) -> bool:
    """True iff some clique of size k exists. Tomita-style BK with early abort."""
    n = len(nbr)
    found = False

    def rec(r_size: int, p: int) -> None:
        nonlocal found
        if found:
            return
        if r_size == k:
            found = True
            return
        if r_size + p.bit_count() < k:
            return
        # pivot: vertex of P with most neighbours in P
        pm = p
        best_u = -1
        best_d = -1
        while pm:
            ubit = pm & -pm
            u = ubit.bit_length() - 1
            d = (p & nbr[u]).bit_count()
            if d > best_d:
                best_d = d
                best_u = u
            pm ^= ubit
        cand = p if best_u < 0 else (p & ~nbr[best_u])
        while cand and not found:
            vbit = cand & -cand
            v = vbit.bit_length() - 1
            rec(r_size + 1, p & nbr[v])
            cand ^= vbit
            p ^= vbit

    rec(0, (1 << n) - 1)
    return found


def omega_at_least(nbr: list[int], k: int) -> bool:
    return _has_clique(nbr, k)


def alpha_at_least(nbr: list[int], k: int) -> bool:
    return _has_clique(complement(nbr), k)


def clique_number(nbr: list[int], cap: int = 8) -> int:
    w = 0
    while w < cap and omega_at_least(nbr, w + 1):
        w += 1
    return w


def independence_number(nbr: list[int], cap: int = 8) -> int:
    return clique_number(complement(nbr), cap=cap)


def is_ramsey(nbr: list[int], s: int = 5, t: int = 5) -> bool:
    return (not omega_at_least(nbr, s)) and (not alpha_at_least(nbr, t))


def list_k_cliques(nbr: list[int], k: int) -> list[int]:
    """All k-cliques as bitmasks."""
    n = len(nbr)
    out: list[int] = []

    def rec(start: int, r: int, r_size: int, p: int) -> None:
        if r_size == k:
            out.append(r)
            return
        for v in range(start, n):
            vbit = 1 << v
            if p & vbit:
                rec(v + 1, r | vbit, r_size + 1, p & nbr[v])

    rec(0, 0, 0, (1 << n) - 1)
    return out


def legal_degree_range(n: int, s: int = 5, t: int = 5) -> tuple[int, int]:
    """R(4,5)=25, so deg <= 24 and n-1-deg <= 24."""
    # Neighbourhood is a (s-1, t)-graph, dual neighbourhood a (s, t-1)-graph.
    # Using the known values R(4,5)=R(5,4)=25.
    lo = max(0, n - 25)
    hi = min(n - 1, 24)
    return lo, hi


def circulant_nbr(n: int, distances: Iterable[int]) -> list[int]:
    S = set()
    for d in distances:
        d = d % n
        if d == 0:
            continue
        S.add(d)
        S.add((-d) % n)
    nbr = [0] * n
    for i in range(n):
        m = 0
        for d in S:
            m |= 1 << ((i + d) % n)
        nbr[i] = m
    return nbr


def fingerprint(nbr: list[int]) -> dict:
    degs = degrees(nbr)
    return {
        "n": len(nbr),
        "edges": n_edges(nbr),
        "min_deg": min(degs) if degs else 0,
        "max_deg": max(degs) if degs else 0,
        "deg_hist": {str(d): degs.count(d) for d in sorted(set(degs))},
        "triangles": triangles(nbr),
        "omega_ge5": omega_at_least(nbr, 5),
        "alpha_ge5": alpha_at_least(nbr, 5),
    }


def dump_json(path: str, obj) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
