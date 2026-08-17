"""Gegenbauer polynomials of dimension 5, and the exact Delsarte LP.

Normalized so P_k(1) = 1, recurrence from Boyvalenkov–Dodunekov–Musin
arXiv:1507.03631 §2.2:

    P_0 = 1, P_1 = t,
    (k + n - 2) P_{k+1}(t) = (2k + n - 2) t P_k(t) - k P_{k-1}(t).

For n = 5 this is (k+3) P_{k+1} = (2k+3) t P_k - k P_{k-1}.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

F = Fraction


def gegenbauer_dim5(max_deg: int) -> List[List[F]]:
    """Return coefficient lists of P_0, ..., P_{max_deg} in the monomial basis.

    coeffs[k][i] is the coefficient of t^i in P_k.
    """
    if max_deg < 0:
        return []
    polys: List[List[F]] = []
    polys.append([F(1)])  # P0
    if max_deg == 0:
        return polys
    polys.append([F(0), F(1)])  # P1
    for k in range(1, max_deg):
        # (k+3) P_{k+1} = (2k+3) t P_k - k P_{k-1}
        pk = polys[k]
        pkm = polys[k - 1]
        deg = k + 1
        acc = [F(0)] * (deg + 1)
        scale = F(2 * k + 3)
        for i, c in enumerate(pk):
            acc[i + 1] += scale * c
        scale_m = F(k)
        for i, c in enumerate(pkm):
            acc[i] -= scale_m * c
        den = F(k + 3)
        polys.append([c / den for c in acc])
    return polys


def eval_poly(coeffs: Sequence[F], t: F) -> F:
    s = F(0)
    pw = F(1)
    for c in coeffs:
        s += c * pw
        pw *= t
    return s


def levenshtein_n5_s_half() -> F:
    """L_5(5, 1/2) via the explicit odd-bound formula.

    For s in I_{2k-1} the bound is
        L_{2k-1}(n,s) = C(k+n-3, k-1)
            * [ (2k+n-3)/(n-1)
                - (P_{k-1}(s) - P_k(s)) / ((1-s) P_k(s)) ].
    For n=5, s=1/2 the relevant bound quoted in the survey is L_5(5,1/2)=48,
    i.e. 2k-1=5 so k=3.
    """
    n = 5
    k = 3
    s = F(1, 2)
    polys = gegenbauer_dim5(k)
    pk = eval_poly(polys[k], s)
    pkm = eval_poly(polys[k - 1], s)
    binom = F(1)
    # C(k+n-3, k-1) = C(5, 2) = 10
    N, K = k + n - 3, k - 1
    for i in range(K):
        binom *= F(N - i, i + 1)
    inner = F(2 * k + n - 3, n - 1) - (pkm - pk) / ((1 - s) * pk)
    return binom * inner


def delsarte_eval(a_t: Dict[F, F], deg: int) -> List[F]:
    """Return (P_k(1) + sum_t A_t P_k(t)) for k=0..deg.

    A_t is the average number of neighbors at inner product t
    (so sum_t A_t = N-1 and the k=0 identity is N).
    """
    polys = gegenbauer_dim5(deg)
    out: List[F] = []
    for k, pk in enumerate(polys):
        s = eval_poly(pk, F(1))  # = 1
        for t, at in a_t.items():
            s += at * eval_poly(pk, t)
        out.append(s)
    return out


def delsarte_feasible(N: int, a_t: Dict[F, F], deg: int) -> Tuple[bool, List[F]]:
    vals = delsarte_eval(a_t, deg)
    # k=0 should equal N (because P0=1 and 1 + (N-1) = N)
    ok = all(v >= 0 for v in vals)
    return ok, vals
