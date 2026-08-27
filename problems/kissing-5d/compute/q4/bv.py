#!/usr/bin/env python3
"""Exact Bachoc–Vallentin matrices S_k^5 over Q.

Follows Bachoc–Vallentin, JAMS 21 (2008), Theorem 3.2 and Remark 3.4,
and the computational form in Mittelmann–Vallentin, arXiv:0902.1105v3 §2.

Y_k^n is taken in the monomial basis
    (Y_k)_{i,j}(u,v,t) = u^i v^j Q_k^{n-1}(u,v,t),
which is congruent to the Gegenbauer form and is enough for the dual
(Remark 3.4).  Q_k^{n-1} is the polynomial
    ((1-u^2)(1-v^2))^{k/2} P_k^{n-1}((t-uv)/sqrt((1-u^2)(1-v^2))).
S_k is the average of Y_k over the six permutations of (u,v,t).

All arithmetic is rational.  A numerical SDP that does not become an
exact Putinar / principal-minor certificate is residue, not a bound.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

F = Fraction
Mono = Tuple[int, int, int]  # u^i v^j t^k
N_BV = 5  # kissing in R^5; sphere S^4


# ---------------------------------------------------------------------------
# Gegenbauer P_k^n, P_k^n(1) = 1
# (k + n - 2) P_{k+1} = (2k + n - 2) t P_k - k P_{k-1}
# ---------------------------------------------------------------------------

def gegenbauer(n: int, max_deg: int) -> List[List[F]]:
    if max_deg < 0:
        return []
    polys: List[List[F]] = [[F(1)]]
    if max_deg == 0:
        return polys
    polys.append([F(0), F(1)])
    for k in range(1, max_deg):
        pk, pkm = polys[k], polys[k - 1]
        acc = [F(0)] * (k + 2)
        scale = F(2 * k + n - 2)
        for i, c in enumerate(pk):
            acc[i + 1] += scale * c
        scale_m = F(k)
        for i, c in enumerate(pkm):
            acc[i] -= scale_m * c
        den = F(k + n - 2)
        polys.append([c / den for c in acc])
    return polys


def eval_univariate(coeffs: Sequence[F], t: F) -> F:
    s, pw = F(0), F(1)
    for c in coeffs:
        s += c * pw
        pw *= t
    return s


# ---------------------------------------------------------------------------
# Sparse polynomials in (u, v, t)
# ---------------------------------------------------------------------------

class Poly3:
    __slots__ = ("c",)

    def __init__(self, coeffs: Dict[Mono, F] | None = None):
        self.c: Dict[Mono, F] = {}
        if coeffs:
            for m, a in coeffs.items():
                if a != 0:
                    self.c[m] = F(a)

    @staticmethod
    def const(a: F) -> "Poly3":
        return Poly3({(0, 0, 0): F(a)}) if a != 0 else Poly3()

    @staticmethod
    def var(which: int) -> "Poly3":
        e = [0, 0, 0]
        e[which] = 1
        return Poly3({(e[0], e[1], e[2]): F(1)})

    def __bool__(self) -> bool:
        return bool(self.c)

    def copy(self) -> "Poly3":
        return Poly3(dict(self.c))

    def __add__(self, other: "Poly3") -> "Poly3":
        out = dict(self.c)
        for m, a in other.c.items():
            s = out.get(m, F(0)) + a
            if s == 0:
                out.pop(m, None)
            else:
                out[m] = s
        return Poly3(out)

    def __sub__(self, other: "Poly3") -> "Poly3":
        return self + other.scale(F(-1))

    def scale(self, s: F) -> "Poly3":
        if s == 0:
            return Poly3()
        return Poly3({m: s * a for m, a in self.c.items()})

    def __mul__(self, other: "Poly3") -> "Poly3":
        out: Dict[Mono, F] = {}
        for (i1, j1, k1), a in self.c.items():
            for (i2, j2, k2), b in other.c.items():
                m = (i1 + i2, j1 + j2, k1 + k2)
                s = out.get(m, F(0)) + a * b
                if s == 0:
                    out.pop(m, None)
                else:
                    out[m] = s
        return Poly3(out)

    def pow(self, n: int) -> "Poly3":
        out = Poly3.const(F(1))
        base = self
        e = n
        while e:
            if e & 1:
                out = out * base
            base = base * base
            e >>= 1
        return out

    def eval(self, u: F, v: F, t: F) -> F:
        s = F(0)
        for (i, j, k), a in self.c.items():
            s += a * (u ** i) * (v ** j) * (t ** k)
        return s

    def permute(self, p: Tuple[int, int, int]) -> "Poly3":
        """Substitute (u,v,t) -> (vars[p0], vars[p1], vars[p2])."""
        out: Dict[Mono, F] = {}
        for (e0, e1, e2), a in self.c.items():
            ne = [0, 0, 0]
            old = (e0, e1, e2)
            for i, exp in enumerate(old):
                ne[p[i]] += exp
            m = (ne[0], ne[1], ne[2])
            s = out.get(m, F(0)) + a
            if s == 0:
                out.pop(m, None)
            else:
                out[m] = s
        return Poly3(out)

    def restrict_uu1(self) -> List[F]:
        """f(u,u,1) as a univariate polynomial in u, low degree first."""
        acc: Dict[int, F] = {}
        for (i, j, k), a in self.c.items():
            deg = i + j
            acc[deg] = acc.get(deg, F(0)) + a
        if not acc:
            return [F(0)]
        m = max(acc)
        return [acc.get(d, F(0)) for d in range(m + 1)]

    def degree(self) -> int:
        if not self.c:
            return -1
        return max(i + j + k for (i, j, k) in self.c)

    def items(self):
        return self.c.items()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Poly3):
            return NotImplemented
        return self.c == other.c


U, V, T = Poly3.var(0), Poly3.var(1), Poly3.var(2)
ONE = Poly3.const(F(1))

PERMS: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (1, 0, 2),
    (2, 1, 0),
    (0, 2, 1),
    (1, 2, 0),
    (2, 0, 1),
)


def p_interval() -> Poly3:
    """p(u) = (u+1)(1/2-u) ≥ 0 on [-1, 1/2]."""
    # (u+1)(1/2-u) = 1/2 + u/2 - u^2
    return Poly3({(0, 0, 0): F(1, 2), (1, 0, 0): F(1, 2), (2, 0, 0): F(-1)})


def p4_gram() -> Poly3:
    """1 + 2uvt - u^2 - v^2 - t^2."""
    return Poly3({
        (0, 0, 0): F(1),
        (1, 1, 1): F(2),
        (2, 0, 0): F(-1),
        (0, 2, 0): F(-1),
        (0, 0, 2): F(-1),
    })


# ---------------------------------------------------------------------------
# Q_k^{n-1} and the matrices Y_k, S_k
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _Q_poly_cached(n_minus_1: int, k: int) -> Poly3:
    if k == 0:
        return ONE.copy()
    Pk = gegenbauer(n_minus_1, k)[k]
    tuv = T - (U * V)                       # t - uv
    one_uu = ONE - (U * U)                  # 1 - u^2
    one_vv = ONE - (V * V)                  # 1 - v^2
    uv_sq = one_uu * one_vv                 # (1-u^2)(1-v^2)
    acc = Poly3()
    for a, ca in enumerate(Pk):
        if ca == 0:
            continue
        rest = k - a
        if rest % 2:
            # P_k is even or odd with k, so this term is identically zero
            # after clearing the square root.  Skip.
            continue
        m = rest // 2
        term = tuv.pow(a)
        if m:
            term = term * uv_sq.pow(m)
        acc = acc + term.scale(ca)
    return acc


def Q_poly(n_minus_1: int, k: int) -> Poly3:
    """Q_k^{n-1}(u,v,t) as a polynomial."""
    return _Q_poly_cached(n_minus_1, k).copy()


def Y_entry(k: int, i: int, j: int, n: int = N_BV) -> Poly3:
    """(Y_k^n)_{i,j} = u^i v^j Q_k^{n-1}."""
    q = Q_poly(n - 1, k)
    mon = Poly3({(i, j, 0): F(1)})
    return mon * q


def S_entry(k: int, i: int, j: int, n: int = N_BV) -> Poly3:
    y = Y_entry(k, i, j, n)
    acc = Poly3()
    for p in PERMS:
        acc = acc + y.permute(p)
    return acc.scale(F(1, 6))


def S_matrix(k: int, d: int, n: int = N_BV) -> List[List[Poly3]]:
    """(d-k+1) × (d-k+1) matrix of polynomials."""
    m = d - k + 1
    return [[S_entry(k, i, j, n) for j in range(m)] for i in range(m)]


def frobenius(Fmat: Sequence[Sequence[F]], S: Sequence[Sequence[Poly3]]) -> Poly3:
    """⟨F, S⟩ = sum_{i,j} F_{ij} S_{ij}."""
    acc = Poly3()
    m = len(Fmat)
    for i in range(m):
        for j in range(m):
            if Fmat[i][j] != 0:
                acc = acc + S[i][j].scale(Fmat[i][j])
    return acc


# ---------------------------------------------------------------------------
# Exact linear algebra / PSD
# ---------------------------------------------------------------------------

def det_exact(A: Sequence[Sequence[F]]) -> F:
    n = len(A)
    if n == 0:
        return F(1)
    M = [[F(A[i][j]) for j in range(n)] for i in range(n)]
    det = F(1)
    for i in range(n):
        pivot = None
        for r in range(i, n):
            if M[r][i] != 0:
                pivot = r
                break
        if pivot is None:
            return F(0)
        if pivot != i:
            M[i], M[pivot] = M[pivot], M[i]
            det = -det
        piv = M[i][i]
        det *= piv
        for r in range(i + 1, n):
            if M[r][i] == 0:
                continue
            fac = M[r][i] / piv
            for c in range(i, n):
                M[r][c] -= fac * M[i][c]
    return det


def principal_minors_nonneg(A: Sequence[Sequence[F]]) -> bool:
    """A ≽ 0 over R iff every principal minor is ≥ 0 (Sylvester)."""
    n = len(A)
    for r in range(1, n + 1):
        for idx in combinations(range(n), r):
            M = [[A[i][j] for j in idx] for i in idx]
            if det_exact(M) < 0:
                return False
    return True


def is_symmetric(A: Sequence[Sequence[F]]) -> bool:
    n = len(A)
    return all(A[i][j] == A[j][i] for i in range(n) for j in range(n))


def is_psd_exact(A: Sequence[Sequence[F]]) -> bool:
    if not is_symmetric(A):
        return False
    if not A:
        return True
    # cheap diagonal filter
    if any(A[i][i] < 0 for i in range(len(A))):
        return False
    return principal_minors_nonneg(A)


def parse_matrix(rows: Sequence[Sequence[str]]) -> List[List[F]]:
    return [[F(x) for x in row] for row in rows]


def matrix_to_str(A: Sequence[Sequence[F]]) -> List[List[str]]:
    return [[str(x) for x in row] for row in A]


# ---------------------------------------------------------------------------
# SOS / Putinar
# ---------------------------------------------------------------------------

def monomials_3(max_deg: int) -> List[Mono]:
    out = []
    for d in range(max_deg + 1):
        for i in range(d + 1):
            for j in range(d - i + 1):
                k = d - i - j
                out.append((i, j, k))
    return out


def sos_from_gram(G: Sequence[Sequence[F]], mons: Sequence[Mono]) -> Poly3:
    acc = Poly3()
    m = len(mons)
    for a in range(m):
        for b in range(m):
            gab = G[a][b]
            if gab == 0:
                continue
            i1, j1, k1 = mons[a]
            i2, j2, k2 = mons[b]
            mon = (i1 + i2, j1 + j2, k1 + k2)
            acc.c[mon] = acc.c.get(mon, F(0)) + gab
    # drop zeros
    acc.c = {m: c for m, c in acc.c.items() if c != 0}
    return acc


def univariate_sos(G: Sequence[Sequence[F]]) -> List[F]:
    """z^T G z for z = (1, u, u^2, ..., u^{m-1})."""
    m = len(G)
    acc = [F(0)] * (2 * m - 1)
    for i in range(m):
        for j in range(m):
            acc[i + j] += G[i][j]
    while len(acc) > 1 and acc[-1] == 0:
        acc.pop()
    return acc


def putinar_combine(
    r: Poly3,
    r_i: Sequence[Poly3],
) -> Poly3:
    """r + p(u) r1 + p(v) r2 + p(t) r3 + p4 r4."""
    pu = p_interval()
    pv = pu.permute((1, 0, 2))  # p(v)
    pt = pu.permute((2, 1, 0))  # p(t)
    gens = [pu, pv, pt, p4_gram()]
    acc = r
    for g, ri in zip(gens, r_i):
        acc = acc + g * ri
    return acc


# ---------------------------------------------------------------------------
# Self-tests (identities from the paper, not a dual search)
# ---------------------------------------------------------------------------

def self_tests() -> List[Tuple[str, bool]]:
    tests: List[Tuple[str, bool]] = []

    # P_k^5 matches delsarte.py for a few degrees
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from delsarte import gegenbauer_dim5
    p5 = gegenbauer(5, 8)
    q5 = gegenbauer_dim5(8)
    tests.append(("gegenbauer_n5_matches_delsarte", p5 == q5))

    # P_k^n(1) = 1
    ok1 = True
    for n in (3, 4, 5, 7):
        for k, pk in enumerate(gegenbauer(n, 6)):
            if eval_univariate(pk, F(1)) != 1:
                ok1 = False
    tests.append(("P_k_n_at_1", ok1))

    # n=4: P2 = (4t^2-1)/3
    p4 = gegenbauer(4, 2)
    tests.append(("P2_n4", p4[2] == [F(-1, 3), F(0), F(4, 3)]))

    # Q0 = 1, Q1 = t-uv
    tests.append(("Q0", Q_poly(4, 0) == ONE))
    tests.append(("Q1", Q_poly(4, 1) == (T - U * V)))

    # Q_k(u,u,1) = (1-u^2)^k  as a polynomial identity
    okQ = True
    for k in range(0, 5):
        q = Q_poly(4, k)
        uni = q.restrict_uu1()
        # (1-u^2)^k
        one_m = [F(1), F(0), F(-1)]  # 1 - u^2
        want = [F(1)]
        for _ in range(k):
            nxt = [F(0)] * (len(want) + 2)
            for i, a in enumerate(want):
                nxt[i] += a
                nxt[i + 2] -= a
            want = nxt
        # pad
        L = max(len(uni), len(want))
        uni += [F(0)] * (L - len(uni))
        want += [F(0)] * (L - len(want))
        if uni != want:
            okQ = False
    tests.append(("Q_k(u,u,1)=(1-u^2)^k", okQ))

    # S_k(1,1,1) = 0 for k≥1; S_0 entries are 1
    s0 = S_matrix(0, 2)
    okS0 = all(s0[i][j].eval(F(1), F(1), F(1)) == 1
               for i in range(3) for j in range(3))
    tests.append(("S0(1,1,1)=J", okS0))
    okSk = True
    for k in (1, 2, 3):
        sk = S_matrix(k, k)  # 1×1
        if sk[0][0].eval(F(1), F(1), F(1)) != 0:
            okSk = False
    tests.append(("Sk(1,1,1)=0 for k>=1", okSk))

    # S is symmetric as a matrix of polynomials, and each entry is
    # symmetric in (u,v,t)
    s1 = S_matrix(0, 1)
    ok_sym = (s1[0][1] == s1[1][0])
    # S_{00} is constant 1
    ok_sym = ok_sym and (s1[0][0] == ONE)
    # S_{11} = (uv+ut+vt)/3
    want11 = Poly3({(1, 1, 0): F(1, 3), (1, 0, 1): F(1, 3), (0, 1, 1): F(1, 3)})
    tests.append(("S0_d1_entries", ok_sym and s1[1][1] == want11))

    # Gram det ≥ 0 is necessary for three unit vectors
    p4 = p4_gram()
    # (0,0,0): three orthogonal — wait 1≥0.  (1/2,1/2,1/2): 1+2/8-3/4=1+1/4-3/4=1/2≥0
    tests.append(("p4_half", p4.eval(F(1, 2), F(1, 2), F(1, 2)) == F(1, 2)))

    # PSD: all-ones 2×2 is PSD; [[0,1],[1,0]] is not
    tests.append(("psd_J", is_psd_exact([[F(1), F(1)], [F(1), F(1)]])))
    tests.append(("psd_off", not is_psd_exact([[F(0), F(1)], [F(1), F(0)]])))
    tests.append(("psd_diag", is_psd_exact([[F(2), F(0)], [F(0), F(3)]])))

    return tests


def main() -> int:
    bad = []
    for name, ok in self_tests():
        print(f"{'OK' if ok else 'FAIL'}  {name}")
        if not ok:
            bad.append(name)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
