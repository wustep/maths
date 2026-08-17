"""Core predicates for Seymour's second-neighborhood conjecture.

An oriented graph on n vertices is stored as a pair of bitmasks
``out[v]``, ``inn[v]`` (n <= 32).  Pair {i,j} is either i->j, j->i, or missing.
"""

from __future__ import annotations

from collections import deque
from typing import Iterable


def n2_mask(out: list[int], v: int) -> int:
    first = out[v]
    second = 0
    m = first
    while m:
        u = (m & -m).bit_length() - 1
        second |= out[u]
        m &= m - 1
    second &= ~first
    second &= ~(1 << v)
    return second


def margin(out: list[int], v: int) -> int:
    first = out[v]
    return n2_mask(out, v).bit_count() - first.bit_count()


def all_margins(out: list[int]) -> list[int]:
    return [margin(out, v) for v in range(len(out))]


def delta(out: list[int]) -> int:
    return max(all_margins(out))


def is_seymour_vertex(out: list[int], v: int) -> bool:
    return margin(out, v) >= 0


def has_seymour_vertex(out: list[int]) -> bool:
    return any(is_seymour_vertex(out, v) for v in range(len(out)))


def outdegrees(out: list[int]) -> list[int]:
    return [x.bit_count() for x in out]


def is_oriented(out: list[int]) -> bool:
    n = len(out)
    for v in range(n):
        if out[v] & (1 << v):
            return False
        for w in range(v + 1, n):
            a = (out[v] >> w) & 1
            b = (out[w] >> v) & 1
            if a and b:
                return False
    return True


def is_strongly_connected(out: list[int]) -> bool:
    n = len(out)
    if n == 0:
        return True
    inn = [0] * n
    for v in range(n):
        m = out[v]
        while m:
            w = (m & -m).bit_length() - 1
            inn[w] |= 1 << v
            m &= m - 1

    def reach(adj: list[int], src: int) -> int:
        seen = 1 << src
        q = deque([src])
        while q:
            v = q.popleft()
            nxt = adj[v] & ~seen
            while nxt:
                w = (nxt & -nxt).bit_length() - 1
                seen |= 1 << w
                q.append(w)
                nxt &= nxt - 1
        return seen

    full = (1 << n) - 1
    return reach(out, 0) == full and reach(inn, 0) == full


def is_pisa(out: list[int]) -> bool:
    return is_oriented(out) and is_strongly_connected(out) and delta(out) == 0


def is_seymour_tight(out: list[int]) -> bool:
    return is_oriented(out) and all(m == 0 for m in all_margins(out))


def missing_mask(out: list[int]) -> list[int]:
    """Undirected missing-neighbour bitmask (no self)."""
    n = len(out)
    full = (1 << n) - 1
    miss = [0] * n
    for v in range(n):
        present = out[v]
        for w in range(n):
            if w != v and ((out[w] >> v) & 1):
                present |= 1 << w
        miss[v] = full ^ (1 << v) ^ present
    return miss


def missing_degree_sequence(out: list[int]) -> tuple[int, ...]:
    return tuple(sorted(m.bit_count() for m in missing_mask(out)))


def underlying_degree_sequence(out: list[int]) -> tuple[int, ...]:
    n = len(out)
    miss = missing_degree_sequence(out)
    return tuple(sorted((n - 1 - d) for d in reversed(miss)))


def is_matching_missing(out: list[int]) -> bool:
    return all(d <= 1 for d in missing_degree_sequence(out))


def is_cycle_underlying(out: list[int]) -> bool:
    n = len(out)
    deg = underlying_degree_sequence(out)
    return deg == tuple([2] * n) and is_strongly_connected(out)


def empty_graph(n: int) -> list[int]:
    return [0] * n


def directed_cycle(n: int) -> list[int]:
    out = [0] * n
    for i in range(n):
        out[i] = 1 << ((i + 1) % n)
    return out


def cycle_power(n: int, k: int) -> list[int]:
    """Directed k-th power of C_n: i -> i+1,...,i+k (mod n)."""
    out = [0] * n
    for i in range(n):
        mask = 0
        for t in range(1, k + 1):
            mask |= 1 << ((i + t) % n)
        out[i] = mask
    return out


def regular_tournament(n: int) -> list[int]:
    """Quadratic residue / cyclic regular tournament; n must be odd."""
    if n % 2 == 0:
        raise ValueError("regular tournament needs odd n")
    k = n // 2
    return cycle_power(n, k)


def lex_product(D: list[int], G: list[int]) -> list[int]:
    """Lexicographic product D[G] on V(D) x V(G), row-major (v, i) -> v*|G|+i."""
    nD, nG = len(D), len(G)
    n = nD * nG
    out = [0] * n
    for v in range(nD):
        for i in range(nG):
            src = v * nG + i
            mask = 0
            # edges copied from G inside the fibre
            m = G[i]
            while m:
                j = (m & -m).bit_length() - 1
                mask |= 1 << (v * nG + j)
                m &= m - 1
            # complete bipartite to out-neighbours of v
            m = D[v]
            while m:
                w = (m & -m).bit_length() - 1
                for j in range(nG):
                    mask |= 1 << (w * nG + j)
                m &= m - 1
            out[src] = mask
    return out


def from_arcs(n: int, arcs: Iterable[tuple[int, int]]) -> list[int]:
    out = [0] * n
    for u, v in arcs:
        if u == v:
            raise ValueError("loop")
        out[u] |= 1 << v
    if not is_oriented(out):
        raise ValueError("not oriented")
    return out


def to_arcs(out: list[int]) -> list[tuple[int, int]]:
    arcs = []
    for v, mask in enumerate(out):
        m = mask
        while m:
            w = (m & -m).bit_length() - 1
            arcs.append((v, w))
            m &= m - 1
    return arcs


def complement_edges(out: list[int]) -> list[tuple[int, int]]:
    n = len(out)
    miss = []
    for i in range(n):
        for j in range(i + 1, n):
            if not ((out[i] >> j) & 1) and not ((out[j] >> i) & 1):
                miss.append((i, j))
    return miss


def encode_ternary(out: list[int]) -> int:
    """Pack pair orientations: 0 = i->j, 1 = j->i, 2 = missing, pairs in lex order."""
    n = len(out)
    code = 0
    mult = 1
    for i in range(n):
        for j in range(i + 1, n):
            if (out[i] >> j) & 1:
                digit = 0
            elif (out[j] >> i) & 1:
                digit = 1
            else:
                digit = 2
            code += digit * mult
            mult *= 3
    return code


def decode_ternary(n: int, code: int) -> list[int]:
    out = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            digit = code % 3
            code //= 3
            if digit == 0:
                out[i] |= 1 << j
            elif digit == 1:
                out[j] |= 1 << i
    return out


def graph_signature(out: list[int]) -> dict:
    n = len(out)
    margins = all_margins(out)
    return {
        "n": n,
        "arcs": to_arcs(out),
        "missing": complement_edges(out),
        "outdegrees": outdegrees(out),
        "margins": margins,
        "delta": max(margins) if margins else 0,
        "strong": is_strongly_connected(out),
        "pisa": is_pisa(out),
        "tight": is_seymour_tight(out),
        "missing_deg": list(missing_degree_sequence(out)),
        "underlying_deg": list(underlying_degree_sequence(out)),
        "matching_missing": is_matching_missing(out),
        "code": encode_ternary(out),
    }
