"""Exact Cohn–Elkies Laguerre–Gaussian auxiliaries in dimension 2.

Radial Fourier eigenfunctions (Cohn–Elkies 2003, §7; Lebedev 4.20.3):

    g_k(x) = L_k(2π |x|²) exp(-π |x|²),    hat g_k = (-1)^k g_k.

Work in the coordinate t = 2π |x|². Sign of a radial eigenfunction combination
is the sign of a polynomial in t. Theorem 3.2 then gives the center-density
bound R/(8π) for a last sign-change at t = R.

This module is the exact-arithmetic core. Search scripts call it; verify.py
re-checks a saved certificate without trusting the search.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Sequence

import sympy as sp

T = sp.symbols("t")


@lru_cache(maxsize=None)
def laguerre_Q(n: int) -> sp.Poly:
    """Monomial Laguerre L_n in Q[t], via the three-term recurrence."""
    if n < 0:
        raise ValueError(n)
    if n == 0:
        return sp.Poly(1, T, domain=sp.QQ)
    if n == 1:
        return sp.Poly(1 - T, T, domain=sp.QQ)
    Lm2 = sp.Poly(1, T, domain=sp.QQ)
    Lm1 = sp.Poly(1 - T, T, domain=sp.QQ)
    for k in range(1, n):
        # (k+1) L_{k+1} = (2k+1 - t) L_k - k L_{k-1}
        num = sp.Poly(2 * k + 1 - T, T, domain=sp.QQ) * Lm1 - k * Lm2
        Lk = sp.Poly(num, T, domain=sp.QQ) / (k + 1)
        Lm2, Lm1 = Lm1, sp.Poly(Lk, T, domain=sp.QQ)
    return sp.Poly(Lm1, T, domain=sp.QQ)


def _odd_indices(m: int) -> list[int]:
    # L_1, L_3, ..., L_{4m+3}: 2m+2 functions
    return list(range(1, 4 * m + 4, 2))


def _even_indices(m: int) -> list[int]:
    # L_0, L_2, ..., L_{4m+2}: 2m+2 functions
    return list(range(0, 4 * m + 3, 2))


def _as_qq(val) -> sp.Rational:
    if hasattr(val, "as_expr"):
        val = val.as_expr()
    val = sp.together(sp.sympify(val))
    num, den = sp.fraction(val)
    return sp.QQ(int(num), int(den))


def _eval_basis(indices: Sequence[int], t0: sp.Rational) -> list[sp.Rational]:
    return [_as_qq(laguerre_Q(k).eval(t0)) for k in indices]


def _eval_basis_deriv(indices: Sequence[int], t0: sp.Rational) -> list[sp.Rational]:
    return [_as_qq(sp.Poly(laguerre_Q(k).diff(T), T, domain=sp.QQ).eval(t0)) for k in indices]


def _nullspace_1d(rows: list[list[sp.Rational]]) -> list[sp.Rational] | None:
    """Return a primitive Q-null vector of a (n-1) x n matrix, or None."""
    M = sp.Matrix(rows)
    ker = M.nullspace()
    if not ker:
        return None
    v = ker[0]
    # Clear denominators
    dens = [sp.fraction(sp.together(c))[1] for c in v]
    lcm = sp.ilcm(*[int(d) for d in dens]) if dens else 1
    ints = [sp.Integer(sp.together(c) * lcm) for c in v]
    g = sp.igcd(*[int(a) for a in ints]) or 1
    ints = [_as_qq(int(a) // g) for a in ints]
    # Canonical sign: first nonzero positive
    for a in ints:
        if a != 0:
            if a < 0:
                ints = [-a for a in ints]
            break
    return ints


def _solve_square(A: list[list[sp.Rational]], b: list[sp.Rational]) -> list[sp.Rational] | None:
    M = sp.Matrix(A)
    rhs = sp.Matrix(b)
    try:
        sol = M.solve(rhs)
    except Exception:
        return None
    return [_as_qq(c) for c in sol]


def build_G(m: int, t_roots: Sequence[sp.Rational]) -> tuple[sp.Poly, list[sp.Rational]] | None:
    """Odd combination with G(0)=0 and double roots at each t_i.

    Returns (G, coefficients on the odd Laguerre basis) or None if the
    constraint matrix has no 1-dimensional kernel.
    """
    if len(t_roots) != m:
        raise ValueError(f"expected {m} forced roots, got {len(t_roots)}")
    odds = _odd_indices(m)
    n = len(odds)
    rows: list[list[sp.Rational]] = []
    # G(0) = sum a_j, since L_k(0) = 1
    rows.append([sp.QQ(1)] * n)
    for ti in t_roots:
        rows.append(_eval_basis(odds, ti))
        rows.append(_eval_basis_deriv(odds, ti))
    if len(rows) != n - 1:
        raise RuntimeError(f"row count {len(rows)} != {n - 1}")
    coeffs = _nullspace_1d(rows)
    if coeffs is None:
        return None
    G = sum((cj * laguerre_Q(k) for cj, k in zip(coeffs, odds)), sp.Poly(0, T, domain=sp.QQ))
    return sp.Poly(G, T, domain=sp.QQ), coeffs


def build_H(
    m: int,
    t_roots: Sequence[sp.Rational],
    R: sp.Rational,
    G: sp.Poly,
) -> tuple[sp.Poly, list[sp.Rational]] | None:
    """Even combination with double roots at t_i and G+H double at R."""
    evens = _even_indices(m)
    n = len(evens)
    A: list[list[sp.Rational]] = []
    b: list[sp.Rational] = []
    for ti in t_roots:
        A.append(_eval_basis(evens, ti))
        b.append(sp.QQ(0))
        A.append(_eval_basis_deriv(evens, ti))
        b.append(sp.QQ(0))
    A.append(_eval_basis(evens, R))
    b.append(-_as_qq(G.eval(R)))
    A.append(_eval_basis_deriv(evens, R))
    b.append(-_as_qq(G.diff(T).eval(R)))
    if len(A) != n:
        raise RuntimeError(f"H system {len(A)} x {n}")
    coeffs = _solve_square(A, b)
    if coeffs is None:
        return None
    H = sum((cj * laguerre_Q(k) for cj, k in zip(coeffs, evens)), sp.Poly(0, T, domain=sp.QQ))
    return sp.Poly(H, T, domain=sp.QQ), coeffs


def sturm_sign_changes(values: Sequence[sp.Expr]) -> int:
    seq = [_as_qq(v) for v in values if v != 0]
    changes = 0
    for a, b in zip(seq, seq[1:]):
        if a * b < 0:
            changes += 1
    return changes


def sturm_chain(p: sp.Poly) -> list[sp.Poly]:
    """Classical Sturm sequence over Q."""
    p = sp.Poly(p, T, domain=sp.QQ)
    if p.degree() < 0:
        return [p]
    chain = [p, sp.Poly(p.diff(T), T, domain=sp.QQ)]
    while chain[-1].degree() > 0:
        _, rem = sp.div(chain[-2], chain[-1], domain=sp.QQ)
        chain.append(sp.Poly(-rem, T, domain=sp.QQ))
        if chain[-1].degree() < 0:
            chain.pop()
            break
    return chain


def sturm_eval(chain: Sequence[sp.Poly], x) -> int:
    if x == sp.oo:
        vals = [c.LC() if c.degree() % 2 == 0 else -c.LC() for c in chain]
        # p(∞) has sign of LC; for odd degree, t^deg → +∞ so sign(LC),
        # wait: if deg odd, t→+∞ gives sign(LC); t→-∞ gives -sign(LC).
        # Here x = +∞: sign is sign(LC) regardless of degree.
        vals = [c.LC() for c in chain]
    elif x == -sp.oo:
        vals = [c.LC() * ((-1) ** c.degree()) for c in chain]
    else:
        vals = [c.eval(x) for c in chain]
    return sturm_sign_changes(vals)


def count_real_roots_open(p: sp.Poly, a, b) -> int:
    """Distinct real roots of p in (a, b). a,b may be ±oo."""
    p = sp.Poly(p, T, domain=sp.QQ).as_poly().to_exact()
    # Work with the square-free part so multiple roots are counted once
    sf = sp.Poly(sp.sqf_part(p.as_expr()), T, domain=sp.QQ)
    if sf.degree() <= 0:
        return 0
    chain = sturm_chain(sf)
    return sturm_eval(chain, a) - sturm_eval(chain, b)


def positive_roots_squarefree(p: sp.Poly) -> int:
    return count_real_roots_open(p, 0, sp.oo)


def last_odd_positive_root_numeric(p: sp.Poly) -> float | None:
    """Largest positive root of odd multiplicity (a genuine sign change)."""
    p = sp.Poly(p, T, domain=sp.QQ)
    if p.degree() <= 0:
        return None
    best = None
    _cont, facs = p.sqf_list()
    for fac, mult in facs:
        if int(mult) % 2 == 0:
            continue
        q = sp.Poly(fac, T, domain=sp.QQ)
        for r in sp.real_roots(q):
            try:
                val = float(r)
            except Exception:
                val = float(r.evalf(40))
            if val > 1e-15 and (best is None or val > best):
                best = val
    return best


def last_positive_root_numeric(p: sp.Poly, bits: int = 80) -> float | None:
    """Largest positive real root as a float, or None."""
    p = sp.Poly(p, T, domain=sp.QQ)
    pos_f: list[float] = []
    for r in sp.real_roots(p):
        try:
            val = float(r)
        except Exception:
            try:
                val = float(r.evalf(bits))
            except Exception:
                continue
        if val > 1e-15:
            pos_f.append(val)
    if not pos_f:
        return None
    return max(pos_f)


def last_positive_root_isolated(p: sp.Poly) -> tuple[sp.Rational, sp.Rational] | None:
    """Isolating interval (a,b) for the largest positive real root, or None."""
    p = sp.Poly(p, T, domain=sp.QQ)
    roots = sp.real_roots(p)
    best = None
    best_mid = None
    for r in roots:
        if not r.is_real:
            continue
        # Get a rational isolating interval
        try:
            a, b = r.interval().as_tuple() if hasattr(r, "interval") else (None, None)
        except Exception:
            a, b = None, None
        try:
            mid = sp.QQ(r.eval_rational(n=10**8))
        except Exception:
            continue
        if mid <= 0:
            continue
        if best_mid is None or mid > best_mid:
            best_mid = mid
            if a is not None:
                best = (sp.QQ(a), sp.QQ(b))
            else:
                # Fallback: tiny interval around the approximation
                best = (mid - sp.QQ(1, 10**6), mid + sp.QQ(1, 10**6))
    return best


def poly_sign_at(p: sp.Poly, x) -> int:
    v = _as_qq(p.eval(x))
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def analyze_signs(G: sp.Poly, H: sp.Poly, R: sp.Rational) -> dict:
    """Independent sign report for f = -G+H and hat f = G+H on [0,∞)."""
    F = sp.Poly(-G + H, T, domain=sp.QQ)
    hatF = sp.Poly(G + H, T, domain=sp.QQ)
    # hatF should have a double root at R by construction
    hatF_at_R = _as_qq(hatF.eval(R))
    hatF_d_at_R = _as_qq(hatF.diff(T).eval(R))
    # Divide out (t-R)^2 exactly if possible
    linear = sp.Poly(T - R, T, domain=sp.QQ)
    q, rem = sp.div(hatF, linear**2, domain=sp.QQ)
    hatF_reduced = q if rem == 0 else hatF
    pos_hat_extra = positive_roots_squarefree(hatF_reduced)
    # F on (R, ∞): we want no sign change, F(R) ≤ 0, F(+∞) ≤ 0
    pos_F_after_R = count_real_roots_open(F, R, sp.oo)
    report = {
        "F0": str(_as_qq(F.eval(0))),
        "hatF0": str(_as_qq(hatF.eval(0))),
        "F_at_R": str(_as_qq(F.eval(R))),
        "hatF_at_R": str(hatF_at_R),
        "hatF_deriv_at_R": str(hatF_d_at_R),
        "hatF_divides_tR2": bool(rem == 0),
        "hatF_extra_positive_roots": int(pos_hat_extra),
        "F_roots_after_R": int(pos_F_after_R),
        "F_sign_plus_inf": int(1 if F.LC() > 0 else -1),
        "hatF_sign_plus_inf": int(1 if hatF.LC() > 0 else -1),
        "hatF_sign_at_0": poly_sign_at(hatF, 0),
        "F_sign_at_R": poly_sign_at(F, R),
        "deg_F": int(F.degree()),
        "deg_hatF": int(hatF.degree()),
    }
    # Admissible for Theorem 3.2:
    #   F(0) = hatF(0) > 0  (true if G(0)=0 and H(0)>0)
    #   hatF ≥ 0 on [0,∞): no extra positive roots of odd multiplicity,
    #                      hatF(0)>0, hatF(+∞)>0 (or identically zero, rejected)
    #   F ≤ 0 on [R,∞): F(R)≤0, no roots in (R,∞) of odd mult, F(+∞)≤0
    hat_ok = (
        report["hatF_sign_at_0"] > 0
        and report["hatF_extra_positive_roots"] == 0
        and report["hatF_sign_plus_inf"] > 0
        and rem == 0
    )
    F_ok = report["F_sign_at_R"] <= 0 and report["F_roots_after_R"] == 0 and report["F_sign_plus_inf"] < 0
    # Also F(0)>0 is required by Theorem 3.2 together with F(0)=hatF(0)
    eq0 = _as_qq(F.eval(0)) == _as_qq(hatF.eval(0))
    report["F0_eq_hatF0"] = bool(eq0)
    report["hatF_nonnegative"] = bool(hat_ok)
    report["F_nonpositive_past_R"] = bool(F_ok)
    report["theorem32_ok"] = bool(hat_ok and F_ok and eq0 and _as_qq(F.eval(0)) > 0)
    return report


def hex_R() -> float:
    # 4π/√3
    return float(4 * sp.pi / sp.sqrt(3))


def center_density(R) -> float:
    return float(sp.QQ(R) / (8 * sp.pi))


def ratio_vs_hex(R) -> float:
    # (R/(8π)) / (√3/6) = R * √3 / (4π)
    return float(sp.QQ(R) * sp.sqrt(3) / (4 * sp.pi))


def qq(x) -> sp.Rational:
    if isinstance(x, Fraction):
        return sp.QQ(x.numerator, x.denominator)
    if isinstance(x, int):
        return sp.QQ(x)
    if isinstance(x, str):
        return sp.QQ(x)
    # sympy Rational / MPQ / Integer
    try:
        return sp.QQ(x)
    except Exception:
        pass
    ns = sp.nsimplify(x, rational=True)
    return sp.QQ(ns)


def build_certificate(m: int, t_roots: Iterable, R) -> dict | None:
    ts = [qq(t) for t in t_roots]
    Rv = qq(R)
    built = build_G(m, ts)
    if built is None:
        return None
    G, a_odd = built
    builtH = build_H(m, ts, Rv, G)
    if builtH is None:
        return None
    H, b_even = builtH
    signs = analyze_signs(G, H, Rv)
    F = sp.Poly(-G + H, T, domain=sp.QQ)
    hatF = sp.Poly(G + H, T, domain=sp.QQ)
    return {
        "m": m,
        "t_roots": [str(t) for t in ts],
        "R": str(Rv),
        "odd_indices": _odd_indices(m),
        "even_indices": _even_indices(m),
        "a_odd": [str(c) for c in a_odd],
        "b_even": [str(c) for c in b_even],
        "G_coeffs_monomial": [str(c) for c in G.all_coeffs()],
        "H_coeffs_monomial": [str(c) for c in H.all_coeffs()],
        "F_coeffs_monomial": [str(c) for c in F.all_coeffs()],
        "hatF_coeffs_monomial": [str(c) for c in hatF.all_coeffs()],
        "signs": signs,
        "center_density_float": center_density(Rv),
        "ratio_vs_hex_float": ratio_vs_hex(Rv),
        "hex_R_float": hex_R(),
    }
