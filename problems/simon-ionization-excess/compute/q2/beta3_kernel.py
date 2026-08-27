#!/usr/bin/env python3
"""Shared kernel / error / tail-lemma arithmetic for β_3^{rad}.

HPS arXiv:2504.18487v1, s=3 radial Newton form.
"""

from __future__ import annotations

import math
from typing import Sequence

from mpmath import iv, mp, mpf, nstr, power, sqrt

mp.dps = 80
iv.dps = 60

# Closed forms, HPS Prop. 4.5 / (2.9)
T0_MP = (1 + sqrt(2)) ** (mpf(1) / 3) - (1 + sqrt(2)) ** (mpf(-1) / 3)
B3_MP = (mpf(2) / 3) * (1 + sqrt(2)) ** (mpf(1) / 3) / (
    (1 + sqrt(2)) ** (mpf(2) / 3) - 1
)
FMIN_MP = 1 / B3_MP


def S(x, d: int = 40) -> str:
    return nstr(x, d, strip_zeros=False)


def iv_bounds(x) -> tuple[str, str]:
    return S(mpf(x.a)), S(mpf(x.b))


def f_mp(t):
    t = mpf(t)
    if t <= 0:
        return mpf(1)
    return (1 + t**3) / (1 + t**2)


def f_iv(t):
    """Interval image of f on a positive interval t."""
    return (1 + t**3) / (1 + t**2)


def t0_iv():
    u = iv.exp(iv.log(1 + iv.sqrt(2)) / 3)
    return u - 1 / u


def fmin_iv():
    return (iv.mpf(3) / 2) * t0_iv()


def b3_iv():
    return 1 / fmin_iv()


def geometric_edges(R, n):
    """Edges  R^{i/n} for i=0..n, as mpfs."""
    R = mpf(R)
    n = int(n)
    return [power(R, mpf(i) / n) for i in range(n + 1)]


def t_range_bins(a1, b1, a2, b2):
    """Exact t=min/max range on [a1,b1]×[a2,b2], as mpf pair."""
    corners = []
    for r in (a1, b1):
        for u in (a2, b2):
            mn, mx = (r, u) if r <= u else (u, r)
            corners.append(mn / mx)
    tlo = min(corners)
    thi = max(corners)
    # intervals overlap ⇒ t=1 is attained
    if a1 <= b2 and a2 <= b1:
        thi = mpf(1)
    return tlo, thi


def Fmin_on_trange(tlo, thi, t0, fmin):
    """min f on [tlo,thi] ⊂ [0,1]. f ↓ on [0,t0], ↑ on [t0,1]."""
    if thi <= t0:
        return f_mp(thi)
    if tlo >= t0:
        return f_mp(tlo)
    return fmin


def Fmin_on_trange_iv(tlo, thi):
    """Interval lower/upper enclosure of min f on the t-range."""
    t0 = t0_iv()
    fmin = fmin_iv()
    tlo_i = iv.mpf(str(tlo)) if not isinstance(tlo, type(iv.mpf(1))) else tlo
    thi_i = iv.mpf(str(thi)) if not isinstance(thi, type(iv.mpf(1))) else thi
    # Conservative: if t0 might lie in [tlo,thi], use fmin; else endpoint
    # Using real comparisons on the interval endpoints.
    t0_lo, t0_hi = mpf(t0.a), mpf(t0.b)
    thi_hi = mpf(thi_i.b)
    tlo_lo = mpf(tlo_i.a)
    if thi_hi <= t0_lo:
        return f_iv(thi_i)
    if tlo_lo >= t0_hi:
        return f_iv(tlo_i)
    return fmin


def assemble_mid(R: float, n: int):
    """Build F (lower), rmid2, A_mid (lower), q, theta with intervals.

    Returns dict of mp/iv objects and float arrays for the C verifier.
    """
    edges = geometric_edges(R, n)
    a = edges[:-1]
    b = edges[1:]
    t0 = T0_MP
    fmin = FMIN_MP
    F_lo = [[None] * n for _ in range(n)]
    F_hi = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            tlo, thi = t_range_bins(a[i], b[i], a[j], b[j])
            Fi = Fmin_on_trange_iv(tlo, thi)
            F_lo[i][j] = mpf(Fi.a)
            F_hi[i][j] = mpf(Fi.b)

    # r^{*2} = a_i b_i = R^{(2i+1)/n}
    rmid2 = [a[i] * b[i] for i in range(n)]
    # A_ij = F_ij (c_i + c_j)/2  — use F_lo for a valid lower quadratic
    A_lo = [
        [F_lo[i][j] * (rmid2[i] + rmid2[j]) / 2 for j in range(n)] for i in range(n)
    ]

    q_iv = iv.exp(iv.log(iv.mpf(str(R))) / n)
    theta_iv = q_iv - 1
    fmin_i = fmin_iv()
    # error upper: θ/(1-θ) * (1-fmin). Need upper on θ and on (1-fmin).
    one_m_fmin = 1 - fmin_i
    err_iv = theta_iv / (1 - theta_iv) * one_m_fmin

    return {
        "n": n,
        "R": R,
        "edges": edges,
        "rmid2": rmid2,
        "F_lo": F_lo,
        "F_hi": F_hi,
        "A_lo": A_lo,
        "q_iv": q_iv,
        "theta_iv": theta_iv,
        "err_iv": err_iv,
        "fmin_iv": fmin_i,
        "b3_iv": b3_iv(),
        "t0_iv": t0_iv(),
    }


def tail_h(x, y, a, beta, fmin):
    """Lower bound of I (D=1) in the tail lemma. x=D_L, y=D_R."""
    Dc = 1 - x - y
    if Dc < 0:
        return mpf("1e9")
    return (
        beta * Dc
        + (x / a) * (1 - beta) * Dc
        + y * (1 - a * (1 - fmin) - a * beta * Dc)
    )


def tail_lemma_min(a, beta, fmin, n_grid: int = 400):
    """Grid min of h on {x∈[0,a], y≥0, x+y≤1} plus corners."""
    a = mpf(a)
    beta = mpf(beta)
    fmin = mpf(fmin)
    best = tail_h(mpf(0), mpf(0), a, beta, fmin)
    at = (mpf(0), mpf(0))
    for i in range(n_grid + 1):
        x = a * i / n_grid
        y_max = 1 - x
        for j in range(n_grid + 1):
            y = y_max * j / n_grid
            v = tail_h(x, y, a, beta, fmin)
            if v < best:
                best = v
                at = (x, y)
    return best, at


def b_of_s(s):
    """b(s) = (s-1)/(s t0), t0^s + s t0 + 1-s = 0."""
    s = mpf(s)

    def fn(t):
        return t**s + s * t + 1 - s

    lo, hi = mpf("1e-30"), mpf(1)
    for _ in range(220):
        mid = (lo + hi) / 2
        if fn(mid) < 0:
            lo = mid
        else:
            hi = mid
    t0 = (lo + hi) / 2
    b = (s - 1) / (s * t0)
    return b, t0
