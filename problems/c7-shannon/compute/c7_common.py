"""Shared predicates for C7^{⊠5}.

Vertices are 5-tuples over Z/7Z, stored as ints in base 7 in 0..7^5-1.
Distinct x,y are adjacent iff circular distance ≤ 1 in every coordinate.
An independent set therefore needs, for every pair, some coordinate with
circular distance > 1 (difference in {2,3,4,5} mod 7).
"""

from __future__ import annotations

N = 7
DIM = 5
NVERTS = N**DIM  # 16807

# Closed neighborhood size including the vertex itself: 3^5 = 243.
NEIGH_CLOSED = 3**DIM


def encode(coords) -> int:
    v = 0
    for c in coords:
        v = v * N + (c % N)
    return v


def decode(v: int) -> tuple[int, ...]:
    out = [0] * DIM
    for i in range(DIM - 1, -1, -1):
        out[i] = v % N
        v //= N
    return tuple(out)


def circ_dist(a: int, b: int, mod: int = N) -> int:
    d = (a - b) % mod
    return d if d <= mod - d else mod - d


def adjacent(u: int, v: int) -> bool:
    """True iff distinct and circular distance ≤ 1 in every coordinate."""
    if u == v:
        return False
    for _ in range(DIM):
        if circ_dist(u % N, v % N) > 1:
            return False
        u //= N
        v //= N
    return True


def closed_neighbors(v: int) -> list[int]:
    """All 243 points at circular distance ≤ 1 in every coordinate, including v."""
    coords = decode(v)
    out = []
    # offsets in {-1,0,1}^5
    for mask in range(NEIGH_CLOSED):
        w = 0
        m = mask
        ok = True
        for i in range(DIM):
            delta = (m % 3) - 1
            m //= 3
            w = w * N + (coords[i] + delta) % N
        out.append(w)
    return out


def parse_word(s: str) -> int:
    s = s.strip()
    if len(s) != DIM or any(ch not in "0123456" for ch in s):
        raise ValueError(f"bad word {s!r}")
    return encode(int(ch) for ch in s)


def format_word(v: int) -> str:
    return "".join(str(c) for c in decode(v))


def blocked_mask(selected) -> list[bool]:
    """True at every vertex in the closed neighborhood of the set."""
    blocked = [False] * NVERTS
    for v in selected:
        for u in closed_neighbors(v):
            blocked[u] = True
    return blocked


def residual_of(selected) -> list[int]:
    blocked = blocked_mask(selected)
    return [x for x in range(NVERTS) if not blocked[x]]


def greedy_mis_fast(verts) -> list[int]:
    """Greedy MIS using closed neighborhoods; linear in |verts| * 243."""
    vset = set(verts)
    banned: set[int] = set()
    taken: list[int] = []
    for v in verts:
        if v in banned:
            continue
        taken.append(v)
        for u in closed_neighbors(v):
            if u in vset:
                banned.add(u)
    return taken
