"""Exact linear-extension counts and pair probabilities.

Two independent counters:

* ``count_le_ideals`` / ``pair_counts_fb`` — De Loof–De Meyer–De Baets
  forward–backward pass on the lattice of order ideals (bitmask DP).
* ``count_le_mins`` — recursion on the remaining ground set, branching
  on current minima, with memoisation.

A poset is an integer ``n`` together with a strict down-set family
``down[i]``: a Python int whose bit ``j`` is set iff ``j < i`` in P.
The identity on ``{0,...,n-1}`` need not be a linear extension.
"""

from __future__ import annotations

from functools import lru_cache
from math import comb, factorial
from typing import Iterable


def transitive_closure(n: int, rel: list[int]) -> list[int]:
    """Warshall on bitmasks. ``rel[i]`` has bit ``j`` set if i < j is given."""
    leq_from = [rel[i] | (1 << i) for i in range(n)]  # i ≤ j
    # we store "i < j" in rel; build succ[i] = {j : i < j}
    succ = list(rel)
    for k in range(n):
        for i in range(n):
            if succ[i] & (1 << k):
                succ[i] |= succ[k]
    return succ


def downsets_from_succ(n: int, succ: list[int]) -> list[int]:
    """down[j] = bitmask of i with i < j (strict)."""
    down = [0] * n
    for i in range(n):
        s = succ[i]
        while s:
            lsb = s & -s
            j = lsb.bit_length() - 1
            down[j] |= 1 << i
            s ^= lsb
    return down


def succ_from_covers(n: int, covers: Iterable[tuple[int, int]]) -> list[int]:
    """covers are pairs (a, b) meaning a is covered by b (a < b)."""
    rel = [0] * n
    for a, b in covers:
        rel[a] |= 1 << b
    return transitive_closure(n, rel)


class Poset:
    def __init__(self, n: int, down: list[int]):
        if n > 62:
            raise ValueError("bitmask implementation is for n <= 62")
        self.n = n
        self.down = list(down)
        self.full = (1 << n) - 1
        # succ[i] = {j : i < j}
        self.succ = [0] * n
        for j in range(n):
            d = down[j]
            while d:
                lsb = d & -d
                i = lsb.bit_length() - 1
                self.succ[i] |= 1 << j
                d ^= lsb
        # comparable (strict) mask
        self.comp = [self.down[i] | self.succ[i] for i in range(n)]
        self.incomp = [self.full ^ self.comp[i] ^ (1 << i) for i in range(n)]

    @classmethod
    def from_covers(cls, n: int, covers: Iterable[tuple[int, int]]) -> "Poset":
        succ = succ_from_covers(n, covers)
        return cls(n, downsets_from_succ(n, succ))

    @classmethod
    def from_relations(cls, n: int, pairs: Iterable[tuple[int, int]]) -> "Poset":
        rel = [0] * n
        for a, b in pairs:
            rel[a] |= 1 << b
        succ = transitive_closure(n, rel)
        return cls(n, downsets_from_succ(n, succ))

    def is_ideal(self, mask: int) -> bool:
        m = mask
        while m:
            lsb = m & -m
            i = lsb.bit_length() - 1
            if self.down[i] & ~mask:
                return False
            m ^= lsb
        return True

    def maxima(self, mask: int) -> int:
        """Bitmask of maximal elements of the induced subposet on ``mask``."""
        out = 0
        m = mask
        while m:
            lsb = m & -m
            i = lsb.bit_length() - 1
            if (self.succ[i] & mask) == 0:
                out |= lsb
            m ^= lsb
        return out

    def minima(self, mask: int) -> int:
        out = 0
        m = mask
        while m:
            lsb = m & -m
            i = lsb.bit_length() - 1
            if (self.down[i] & mask) == 0:
                out |= lsb
            m ^= lsb
        return out

    def width_lower(self) -> int:
        """Size of a largest antichain among subsets we bother to check.

        Exact for n <= 20 via DP (Dilworth / max antichain = max independent
        set of the comparability graph, here just 2^n scan of antichains).
        """
        n = self.n
        best = 1 if n else 0
        # meet-in-the-middle free scan: every subset that is an antichain
        full = 1 << n
        for mask in range(1, full):
            ok = True
            m = mask
            while m:
                lsb = m & -m
                i = lsb.bit_length() - 1
                if self.comp[i] & mask:
                    ok = False
                    break
                m ^= lsb
            if ok:
                c = mask.bit_count()
                if c > best:
                    best = c
        return best


def count_le_ideals(P: Poset) -> int:
    """e(P) by DP over all order ideals, iterating masks in order."""
    n = P.n
    F = [0] * (1 << n)
    F[0] = 1
    for mask in range(1, 1 << n):
        if not P.is_ideal(mask):
            continue
        tot = 0
        mx = P.maxima(mask)
        m = mx
        while m:
            lsb = m & -m
            tot += F[mask ^ lsb]
            m ^= lsb
        F[mask] = tot
    return F[(1 << n) - 1]


def count_le_mins(P: Poset) -> int:
    """e(P) by recursion on remaining elements, branching at minima."""
    n = P.n
    full = (1 << n) - 1

    @lru_cache(maxsize=None)
    def rec(mask: int) -> int:
        if mask == 0:
            return 1
        tot = 0
        m = P.minima(mask)
        while m:
            lsb = m & -m
            tot += rec(mask ^ lsb)
            m ^= lsb
        return tot

    return rec(full)


def list_ideals(P: Poset) -> list[int]:
    """All order ideals, generated by adding a minimum of the complement."""
    n = P.n
    if n > 24:
        raise ValueError("list_ideals flag array is for n<=24")
    full = (1 << n) - 1
    seen = bytearray(1 << n)
    seen[0] = 1
    q = [0]
    for I in q:
        mins = P.minima(full ^ I)
        m = mins
        while m:
            lsb = m & -m
            nxt = I | lsb
            if not seen[nxt]:
                seen[nxt] = 1
                q.append(nxt)
            m ^= lsb
    return q


def all_ideals_F(P: Poset) -> list[int]:
    """F[I] = # linear extensions of the induced poset on ideal I."""
    n = P.n
    F = [0] * (1 << n)
    F[0] = 1
    ideals = list_ideals(P)
    # process in order of increasing size so F[I-x] is ready
    ideals.sort(key=int.bit_count)
    for mask in ideals:
        if mask == 0:
            continue
        tot = 0
        mx = P.maxima(mask)
        m = mx
        while m:
            lsb = m & -m
            tot += F[mask ^ lsb]
            m ^= lsb
        F[mask] = tot
    return F


def pair_counts_fb(P: Poset) -> tuple[int, list[list[int]]]:
    """All-pairs e(P + x<y) via one forward and one backward pass.

    Returns (e(P), C) with C[x][y] = e(P+xy) (0 if y < x already).
    Formula (De Loof–De Meyer–De Baets):
        e(P+xy) = sum_{I ni x, not y, I∪{y} ideal} F[I] B[I∪{y}].
    """
    n = P.n
    full = (1 << n) - 1
    F = all_ideals_F(P)
    e = F[full]
    ideals = list_ideals(P)
    # B[I] = # ways to complete a linear extension after occupying I
    B = [0] * (1 << n)
    B[full] = 1
    for mask in sorted(ideals, key=int.bit_count, reverse=True):
        rem = full ^ mask
        if rem == 0:
            continue
        mins = P.minima(rem)
        m = mins
        while m:
            lsb = m & -m
            B[mask] += B[mask | lsb]
            m ^= lsb
    C = [[0] * n for _ in range(n)]
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            if (P.succ[x] >> y) & 1:
                C[x][y] = e
    for I in ideals:
        fI = F[I]
        for x in range(n):
            if (I >> x) & 1 == 0:
                continue
            inc = P.incomp[x]
            ys = inc & ~I
            while ys:
                lsb = ys & -ys
                y = lsb.bit_length() - 1
                Iy = I | lsb
                if (P.down[y] & ~I) == 0:
                    C[x][y] += fI * B[Iy]
                ys ^= lsb
    return e, C


def pair_counts_by_adding(P: Poset) -> tuple[int, list[list[int]]]:
    """Independent pair counts: e(P+xy) by counting LEs of the enlarged poset."""
    n = P.n
    e = count_le_mins(P)
    C = [[0] * n for _ in range(n)]
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            if (P.succ[x] >> y) & 1:
                C[x][y] = e
                continue
            if (P.succ[y] >> x) & 1:
                C[x][y] = 0
                continue
            # add x < y
            rel = [P.succ[i] for i in range(n)]
            rel[x] |= 1 << y
            succ = transitive_closure(n, rel)
            Q = Poset(n, downsets_from_succ(n, succ))
            C[x][y] = count_le_mins(Q)
    return e, C


def balance(P: Poset, C: list[list[int]] | None = None, e: int | None = None):
    """Return (delta_num, delta_den, e, best_pair, all incomparable fractions)."""
    if C is None or e is None:
        e, C = pair_counts_fb(P)
    n = P.n
    best_n, best_d = 0, 1
    best_pair = None
    pairs = []
    for x in range(n):
        ys = P.incomp[x]
        while ys:
            lsb = ys & -ys
            y = lsb.bit_length() - 1
            if x < y:
                a, b = C[x][y], C[y][x]
                if a + b != e:
                    raise AssertionError(
                        f"pair ({x},{y}): {a}+{b} != e={e}"
                    )
                mn = a if a < b else b
                # mn/e vs best
                if mn * best_d > best_n * e:
                    best_n, best_d = mn, e
                    best_pair = (x, y, a, b)
                pairs.append((x, y, a, b, mn, e))
            ys ^= lsb
    return best_n, best_d, e, best_pair, pairs


def delta_frac(P: Poset) -> tuple[int, int]:
    num, den, *_ = balance(P)
    g = _gcd(num, den)
    return num // g, den // g


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


# ---------------------------------------------------------------------------
# Standard examples
# ---------------------------------------------------------------------------

def chain(n: int) -> Poset:
    covers = [(i, i + 1) for i in range(n - 1)]
    return Poset.from_covers(n, covers)


def antichain(n: int) -> Poset:
    return Poset(n, [0] * n)


def T_poset() -> Poset:
    """3-element extremal: a < b, c incomparable. δ = 1/3."""
    return Poset.from_covers(3, [(0, 1)])


def linear_sum(P: Poset, Q: Poset) -> Poset:
    """P ⊕ Q: every element of P below every element of Q."""
    n, m = P.n, Q.n
    down = [0] * (n + m)
    for i in range(n):
        down[i] = P.down[i]
    Pall = (1 << n) - 1
    for j in range(m):
        down[n + j] = Pall | (Q.down[j] << n)
    return Poset(n + m, down)


def disjoint_sum(P: Poset, Q: Poset) -> Poset:
    n, m = P.n, Q.n
    down = [P.down[i] for i in range(n)]
    for j in range(m):
        down.append(Q.down[j] << n)
    return Poset(n + m, down)


def product_of_chains(dims: tuple[int, ...]) -> Poset:
    """C_{d0} × C_{d1} × ... with cells in row-major order.

    Index of (i0, i1, ..., ik) with 0 <= it < dt is
    ((i0 * d1 + i1) * d2 + ...) .
    (i) ≤ (j) iff it ≤ jt for all t.
    """
    dims = tuple(dims)
    # number of cells
    n = 1
    for d in dims:
        n *= d

    def unravel(idx: int) -> tuple[int, ...]:
        coords = [0] * len(dims)
        for t in range(len(dims) - 1, -1, -1):
            coords[t] = idx % dims[t]
            idx //= dims[t]
        return tuple(coords)

    down = [0] * n
    coords = [unravel(i) for i in range(n)]
    for i in range(n):
        ci = coords[i]
        mask = 0
        for j in range(n):
            if i == j:
                continue
            cj = coords[j]
            if all(aj <= bi for aj, bi in zip(cj, ci)) and any(
                aj < bi for aj, bi in zip(cj, ci)
            ):
                mask |= 1 << j
        down[i] = mask
    return Poset(n, down)


def young_diagram(rows: list[int]) -> Poset:
    """English Young diagram as a poset of cells, componentwise."""
    cells = []
    for r, L in enumerate(rows):
        for c in range(L):
            cells.append((r, c))
    n = len(cells)
    down = [0] * n
    for i, (r, c) in enumerate(cells):
        mask = 0
        for j, (r2, c2) in enumerate(cells):
            if (r2 <= r and c2 <= c) and (r2, c2) != (r, c):
                mask |= 1 << j
        down[i] = mask
    return Poset(n, down)


def chen_poset(m: int, n: int) -> Poset:
    """Chen 2018 P(m,n): two chains a1<...<am, b1<...<bn plus the 5-periodic covers.

    ai ≤ b_{i+1} when i ≡ 1,2,3,4 (mod 5)   (1-based i)
    bj ≤ a_{j+2} when j ≡ 0,2,4 (mod 5)
    """
    # elements: 0..m-1 are a1..am, m..m+n-1 are b1..bn
    rel = []
    for i in range(m - 1):
        rel.append((i, i + 1))
    for j in range(n - 1):
        rel.append((m + j, m + j + 1))
    for i1 in range(1, m + 1):  # 1-based
        if i1 % 5 in (1, 2, 3, 4):
            j = i1 + 1  # 1-based b index
            if 1 <= j <= n:
                rel.append((i1 - 1, m + j - 1))
    for j1 in range(1, n + 1):
        if j1 % 5 in (0, 2, 4):
            i = j1 + 2
            if 1 <= i <= m:
                rel.append((m + j1 - 1, i - 1))
    return Poset.from_covers(m + n, rel)


def W10() -> Poset:
    """The unique 10-element width-3 poset with δ = 6/17 < 14/39."""
    return Poset(10, [0, 0, 1, 1, 7, 11, 23, 87, 95, 255])


def saks_M7() -> Poset:
    """Saks' 7-element width-3 example with published δ = 14/39.

    Reconstructed from Peczarski's M_7 drawing and Olson–Sagan Fig. 12
    (right): a 3-crown / chevron with an extra bottom and a crossing.

    Labelling used here (verified in verify_known.py against 14/39):

        6
       / \\
      4   5
      | X |
      2   3
       \\ /
        1
        |
        0

    Covers: 0<1, 1<2, 1<3, 2<4, 2<5, 3<4, 3<5, 4<6, 5<6.
    That would be a product-like diamond stack (width 2). The published
    M_7 is width 3, so one of the crossing relations is *missing* and an
    extra side element is present. See ``guess_M7`` in verify_known.py;
    the certified cover list is stored as SAKS_M7_COVERS once found.
    """
    return Poset.from_covers(7, SAKS_M7_COVERS)


# Saks M7, naturally labelled so id is a linear extension.
# down-sets [0,0,1,1,7,7,31], independently δ = 14/39, e = 39, width 3.
SAKS_M7_COVERS = [
    (0, 2),
    (0, 3),
    (1, 4),
    (1, 5),
    (2, 4),
    (2, 5),
    (3, 6),
    (4, 6),
]


def olson_C() -> Poset:
    """Olson–Sagan Fig. 13 C, published δ = 37/106. Width 2.

    Two chains with a broken-ladder pattern. Labelling (left chain 0-4,
    right chain 5-8), covers read off the figure:

        L: 0 < 1 < 2 < 3 < 4
        R: 5 < 6 < 7 < 8
        crosses: 0<6, 1<5? , 2<8, 3<7, 5<3, 6<4
    The certified cover list is OLSON_C_COVERS, confirmed by 37/106.
    """
    return Poset.from_covers(9, OLSON_C_COVERS)


# Width-2 poset on 9 elements; filled after search if the hand reading is off.
OLSON_C_COVERS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 6),
    (2, 8),
    (5, 3),
    (6, 4),
    (1, 7),
]


def hook_rectangle(m: int, n: int) -> int:
    """e(C_m × C_n) by the 2-dimensional hook-length formula."""
    num = factorial(m * n)
    den = 1
    for i in range(m):
        for j in range(n):
            den *= (m - i) + (n - j) - 1
    return num // den
