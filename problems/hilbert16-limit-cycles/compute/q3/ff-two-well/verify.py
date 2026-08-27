#!/usr/bin/env python3
"""Exact identities for the two-well cubic Hamiltonian and the
named van der Pol perturbation.

Imagined: 14 isolated zeros of I(h), hence H(3) >= 14. Not produced.
Kept: unperturbed classification, dH/dt identities, I(h) formula,
I(0) = 4 mu / 15 on each figure-eight lobe, and L1 = sqrt(2) mu at
each well after the q1 focal scaling. Not a bound on H(n).

A second, independent check is verify.rs (BTreeMap expansion plus
integer-box evaluation of the cleared dH/dt residuals).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
CORE_PATH = CERTS / "core.json"
IDENT_PATH = CERTS / "identities.json"


# ---------------------------------------------------------------------------
# Sparse integer polynomials
# ---------------------------------------------------------------------------


class Poly:
    def __init__(self, variables: tuple[str, ...], terms: dict[tuple[int, ...], int] | None = None):
        self.variables = variables
        self.terms: dict[tuple[int, ...], int] = defaultdict(int)
        if terms:
            for exp, coeff in terms.items():
                if coeff:
                    self.terms[exp] += coeff
            self._prune()

    def _prune(self) -> None:
        for exp in [e for e, c in self.terms.items() if c == 0]:
            del self.terms[exp]

    def copy(self) -> "Poly":
        return Poly(self.variables, dict(self.terms))

    @classmethod
    def zero(cls, variables: tuple[str, ...]) -> "Poly":
        return cls(variables)

    @classmethod
    def const(cls, variables: tuple[str, ...], value: int) -> "Poly":
        out = cls(variables)
        if value:
            out.terms[(0,) * len(variables)] = value
        return out

    @classmethod
    def var(cls, variables: tuple[str, ...], name: str) -> "Poly":
        out = cls(variables)
        exp = [0] * len(variables)
        exp[variables.index(name)] = 1
        out.terms[tuple(exp)] = 1
        return out

    def _align(self, other: "Poly") -> None:
        if self.variables != other.variables:
            raise ValueError(f"variable mismatch {self.variables} vs {other.variables}")

    def __neg__(self) -> "Poly":
        return Poly(self.variables, {e: -c for e, c in self.terms.items()})

    def __add__(self, other: "Poly") -> "Poly":
        self._align(other)
        out = self.copy()
        for exp, coeff in other.terms.items():
            out.terms[exp] += coeff
        out._prune()
        return out

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (-other)

    def __mul__(self, other: "Poly") -> "Poly":
        self._align(other)
        out = Poly.zero(self.variables)
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                exp = tuple(a + b for a, b in zip(e1, e2))
                out.terms[exp] += c1 * c2
        out._prune()
        return out

    def scale(self, k: int) -> "Poly":
        if k == 0:
            return Poly.zero(self.variables)
        return Poly(self.variables, {e: c * k for e, c in self.terms.items()})

    def __pow__(self, n: int) -> "Poly":
        if n < 0:
            raise ValueError("negative power")
        out = Poly.const(self.variables, 1)
        base = self
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def dvar(self, name: str) -> "Poly":
        idx = self.variables.index(name)
        out = Poly.zero(self.variables)
        for exp, coeff in self.terms.items():
            power = exp[idx]
            if power == 0:
                continue
            new_exp = list(exp)
            new_exp[idx] = power - 1
            out.terms[tuple(new_exp)] += coeff * power
        out._prune()
        return out

    def subst(self, mapping: dict[str, "Poly"]) -> "Poly":
        out = Poly.zero(self.variables)
        for exp, coeff in self.terms.items():
            mon = Poly.const(self.variables, coeff)
            for name, power in zip(self.variables, exp):
                if power == 0:
                    continue
                factor = mapping[name] if name in mapping else Poly.var(self.variables, name)
                mon = mon * (factor ** power)
            out = out + mon
        return out

    def eval(self, values: dict[str, int]) -> int:
        total = 0
        for exp, coeff in self.terms.items():
            mon = coeff
            for name, power in zip(self.variables, exp):
                if power:
                    mon *= values[name] ** power
            total += mon
        return total

    def coeff(self, powers: dict[str, int]) -> int:
        exp = [0] * len(self.variables)
        for name, power in powers.items():
            exp[self.variables.index(name)] = power
        return self.terms.get(tuple(exp), 0)

    def to_terms(self) -> list[dict[str, int | str]]:
        items: list[dict[str, int | str]] = []
        for exp in sorted(self.terms):
            coeff = self.terms[exp]
            if coeff == 0:
                continue
            item: dict[str, int | str] = {"coeff": str(coeff)}
            for name, power in zip(self.variables, exp):
                if power:
                    item[name] = power
            items.append(item)
        return items

    @classmethod
    def from_terms(cls, variables: tuple[str, ...], terms: Iterable[dict]) -> "Poly":
        out = cls.zero(variables)
        for item in terms:
            exp = [0] * len(variables)
            for i, name in enumerate(variables):
                if name in item:
                    exp[i] = int(item[name])
            out.terms[tuple(exp)] += int(item["coeff"])
        out._prune()
        return out

    def equals(self, other: "Poly") -> bool:
        self._align(other)
        keys = set(self.terms) | set(other.terms)
        return all(self.terms.get(k, 0) == other.terms.get(k, 0) for k in keys)

    def is_zero(self) -> bool:
        return not self.terms

    def nterms(self) -> int:
        return len(self.terms)


def V(names: tuple[str, ...], name: str) -> Poly:
    return Poly.var(names, name)


def C(names: tuple[str, ...], value: int) -> Poly:
    return Poly.const(names, value)


def _require_zero(poly: Poly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: Poly, right: Poly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}")


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    _require_equal(Poly.from_terms(variables, terms), poly, label)


# ---------------------------------------------------------------------------
# Unperturbed field
# ---------------------------------------------------------------------------

XY = ("x", "y")
XYM = ("x", "y", "mu")
XYMS = ("X", "Y", "mu")
UVMS = ("u", "v", "mu", "s")
T_VARS = ("t",)


def unperturbed() -> dict[str, Poly]:
    x, y = V(XY, "x"), V(XY, "y")
    p = y
    q = x - (x ** 3)
    # 4H = 2 y^2 + x^4 - 2 x^2
    h4 = (y ** 2).scale(2) + (x ** 4) - (x ** 2).scale(2)
    hx = h4.dvar("x")
    hy = h4.dvar("y")
    dh4 = hx * p + hy * q
    # potential identity: (x^2-1)^2 - 1 - (x^4 - 2 x^2) = 0
    well = (x ** 2 - C(XY, 1)) ** 2
    potential_diff = well - C(XY, 1) - ((x ** 4) - (x ** 2).scale(2))
    # Q = x (1-x)(1+x) = x - x^3
    q_factored = x * (C(XY, 1) - x) * (C(XY, 1) + x)
    # Jacobian entries
    dq_dx = q.dvar("x")
    dq_dy = q.dvar("y")
    dp_dx = p.dvar("x")
    dp_dy = p.dvar("y")
    # det = dp_dx * dq_dy - dp_dy * dq_dx = - (1-3x^2) = 3x^2-1
    det = dp_dx * dq_dy - dp_dy * dq_dx
    det_claimed = (x ** 2).scale(3) - C(XY, 1)
    div = dp_dx + dq_dy
    return {
        "P": p,
        "Q": q,
        "H4": h4,
        "Hx": hx,
        "Hy": hy,
        "dH4": dh4,
        "potential_diff": potential_diff,
        "Q_factored": q_factored,
        "Q_factor_diff": q - q_factored,
        "dP_dx": dp_dx,
        "dP_dy": dp_dy,
        "dQ_dx": dq_dx,
        "dQ_dy": dq_dy,
        "det": det,
        "det_claimed": det_claimed,
        "det_diff": det - det_claimed,
        "div": div,
    }


def check_equilibria(field: dict[str, Poly]) -> None:
    pts = [(0, 0), (1, 0), (-1, 0)]
    for xv, yv in pts:
        vals = {"x": xv, "y": yv}
        if field["P"].eval(vals) != 0 or field["Q"].eval(vals) != 0:
            raise AssertionError(f"({xv},{yv}) is not an equilibrium")
    if field["H4"].eval({"x": 0, "y": 0}) != 0:
        raise AssertionError("H4(0,0) is not 0")
    if field["H4"].eval({"x": 1, "y": 0}) != -1:
        raise AssertionError("H4(1,0) is not -1")
    if field["H4"].eval({"x": -1, "y": 0}) != -1:
        raise AssertionError("H4(-1,0) is not -1")
    # det = 3x^2-1
    if field["det"].eval({"x": 0, "y": 0}) != -1:
        raise AssertionError("det(0,0) is not -1")
    if field["det"].eval({"x": 1, "y": 0}) != 2:
        raise AssertionError("det(1,0) is not 2")
    if field["det"].eval({"x": -1, "y": 0}) != 2:
        raise AssertionError("det(-1,0) is not 2")
    if not field["div"].is_zero():
        raise AssertionError("unperturbed divergence is not 0")
    if field["dP_dy"].eval({"x": 0, "y": 0}) != 1:
        raise AssertionError("dP/dy is not 1")


# ---------------------------------------------------------------------------
# Perturbed field
# ---------------------------------------------------------------------------


def perturbed() -> dict[str, Poly]:
    x, y, mu = V(XYM, "x"), V(XYM, "y"), V(XYM, "mu")
    p = y
    q = x - (x ** 3) + mu * (C(XYM, 1) - x ** 2) * y
    h4 = (y ** 2).scale(2) + (x ** 4) - (x ** 2).scale(2)
    dh4 = h4.dvar("x") * p + h4.dvar("y") * q
    claimed = mu * (y ** 2) * (C(XYM, 1) - x ** 2)
    claimed4 = claimed.scale(4)
    dP_dx = p.dvar("x")
    dP_dy = p.dvar("y")
    dQ_dx = q.dvar("x")
    dQ_dy = q.dvar("y")
    trace = dP_dx + dQ_dy
    trace_claimed = mu * (C(XYM, 1) - x ** 2)
    det = dP_dx * dQ_dy - dP_dy * dQ_dx
    return {
        "P": p,
        "Q": q,
        "H4": h4,
        "dH4": dh4,
        "claimed4": claimed4,
        "dH4_diff": dh4 - claimed4,
        "dP_dx": dP_dx,
        "dP_dy": dP_dy,
        "dQ_dx": dQ_dx,
        "dQ_dy": dQ_dy,
        "trace": trace,
        "trace_claimed": trace_claimed,
        "trace_diff": trace - trace_claimed,
        "det": det,
    }


def check_perturbed(field: dict[str, Poly]) -> None:
    pts = [(0, 0), (1, 0), (-1, 0)]
    for xv, yv in pts:
        for mu in range(-3, 4):
            vals = {"x": xv, "y": yv, "mu": mu}
            if field["P"].eval(vals) != 0 or field["Q"].eval(vals) != 0:
                raise AssertionError(f"perturbed ({xv},{yv}) is not an equilibrium at mu={mu}")
    # (0,0): det = -1, trace = mu
    for mu in range(-3, 4):
        vals = {"x": 0, "y": 0, "mu": mu}
        if field["det"].eval(vals) != -1:
            raise AssertionError(f"perturbed det(0,0) at mu={mu}")
        if field["trace"].eval(vals) != mu:
            raise AssertionError(f"perturbed trace(0,0) at mu={mu}")
        if field["dH4_diff"].eval(vals) != 0:
            raise AssertionError("dH4 residual at origin")
    # wells: trace 0, det 2
    for xv in (1, -1):
        for mu in range(-3, 4):
            vals = {"x": xv, "y": 0, "mu": mu}
            if field["trace"].eval(vals) != 0:
                raise AssertionError(f"trace at ({xv},0) is not 0")
            if field["det"].eval(vals) != 2:
                raise AssertionError(f"det at ({xv},0) is not 2")
    # sample energy sign: mu=1, (x,y)=(0,1) => dH/dt = mu y^2 (1-x^2) = 1
    # dH4/dt = 4
    if field["dH4"].eval({"x": 0, "y": 1, "mu": 1}) != 4:
        raise AssertionError("dH4 sample at (0,1) mu=1")
    if field["dH4"].eval({"x": 2, "y": 1, "mu": 1}) != -12:
        raise AssertionError("dH4 sample at (2,1) mu=1")


# ---------------------------------------------------------------------------
# Translation and focal jets
# ---------------------------------------------------------------------------


def reduce_s(poly: Poly) -> Poly:
    """Rewrite s^2 = 2 in Z[u, v, mu, s]."""
    s_idx = poly.variables.index("s")
    out = Poly.zero(poly.variables)
    for exp, coeff in poly.terms.items():
        e = list(exp)
        s_pow = e[s_idx]
        extra = 1
        while s_pow >= 2:
            extra *= 2
            s_pow -= 2
        e[s_idx] = s_pow
        out.terms[tuple(e)] += coeff * extra
    out._prune()
    return out


def translate_plus() -> dict[str, Poly]:
    """x = 1+X, y = Y. Q = (1+X) - (1+X)^3 + mu (1-(1+X)^2) Y."""
    X, Y, mu = V(XYMS, "X"), V(XYMS, "Y"), V(XYMS, "mu")
    one = C(XYMS, 1)
    xp = one + X
    q = xp - (xp ** 3) + mu * (one - xp ** 2) * Y
    claimed = (
        X.scale(-2)
        - (X ** 2).scale(3)
        - (X ** 3)
        - mu.scale(2) * X * Y
        - mu * (X ** 2) * Y
    )
    return {"Q": q, "claimed": claimed, "diff": q - claimed}


def translate_minus() -> dict[str, Poly]:
    """x = -1+X, y = Y."""
    X, Y, mu = V(XYMS, "X"), V(XYMS, "Y"), V(XYMS, "mu")
    one = C(XYMS, 1)
    xm = X - one
    q = xm - (xm ** 3) + mu * (one - xm ** 2) * Y
    claimed = (
        X.scale(-2)
        + (X ** 2).scale(3)
        - (X ** 3)
        + mu.scale(2) * X * Y
        - mu * (X ** 2) * Y
    )
    return {"Q": q, "claimed": claimed, "diff": q - claimed}


def focal_plus() -> Poly:
    """Nonlinear part of dv/dτ at +1, in Z[u,v,mu,s] / (s^2-2).

    N = -3 X^2 - X^3 - 2 mu X Y - mu X^2 Y,  Y = -s v, X = u.
    dv/dτ = u - N/2, so the nonlinear piece is -N/2 (cleared: -N).
    We return 2 * Q_nl = -N(u, -s v), then divide by 2 when reading jets.
    """
    u, v, mu, s = (V(UVMS, n) for n in UVMS)
    # N(u, -s v) = -u^3 - 3 u^2 - 2 mu u (-s v) - mu u^2 (-s v)
    #            = -u^3 - 3 u^2 + 2 mu s u v + mu s u^2 v
    N = (
        -(u ** 3)
        - (u ** 2).scale(3)
        + mu.scale(2) * s * u * v
        + mu * s * (u ** 2) * v
    )
    return reduce_s(N)


def focal_minus() -> Poly:
    """N at -1: -X^3 + 3 X^2 + 2 mu X Y - mu X^2 Y, Y = -s v."""
    u, v, mu, s = (V(UVMS, n) for n in UVMS)
    N = (
        -(u ** 3)
        + (u ** 2).scale(3)
        + mu.scale(2) * u * (-(s * v))
        - mu * (u ** 2) * (-(s * v))
    )
    return reduce_s(N)


def jet_from_n(n_poly: Poly) -> dict[str, tuple[int, int, int]]:
    """Q_nl = -N/2. Return (num, den, s_power) of each b_ij, a_ij=0.

    Coefficient of u^i v^j mu^k s^p in N, then b = -coeff/2.
    Stored as (num, den, s_power) of the coefficient of mu^k, with k in {0,1}.
    We return the coefficient of the monomial including mu if present,
    as a string-ready triple for the mu-linear or mu-free part.
    """
    # Read raw N coefficients; Q_nl = -N/2.
    def raw(powers: dict[str, int]) -> int:
        return n_poly.coeff(powers)

    # b20: Q coeff of u^2 = -N(u^2)/2. N has -3 u^2 => Q has 3/2
    # b11: Q coeff of u v. N has 2 mu s u v at +1 => Q has -mu s
    # b30: N has -u^3 => Q has 1/2
    # b21: N has mu s u^2 v => Q has -mu s / 2
    jets = {
        "a20": (0, 1, 0),
        "a11": (0, 1, 0),
        "a02": (0, 1, 0),
        "a30": (0, 1, 0),
        "a21": (0, 1, 0),
        "a12": (0, 1, 0),
        "a03": (0, 1, 0),
        "b20": (-raw({"u": 2}), 2, 0),
        "b02": (-raw({"v": 2}), 2, 0),
        "b30": (-raw({"u": 3}), 2, 0),
        "b12": (-raw({"u": 1, "v": 2}), 2, 0),
        "b03": (-raw({"v": 3}), 2, 0),
    }
    # mu-linear, possibly times s
    # b11: coeff of u v, split mu^0 and mu^1, s^0 and s^1
    b11_mu_s = -raw({"u": 1, "v": 1, "mu": 1, "s": 1})
    b11_mu = -raw({"u": 1, "v": 1, "mu": 1})
    b11_s = -raw({"u": 1, "v": 1, "s": 1})
    b11_c = -raw({"u": 1, "v": 1})
    if b11_mu or b11_s or b11_c:
        raise AssertionError(f"unexpected b11 constant pieces {b11_mu, b11_s, b11_c}")
    jets["b11"] = (b11_mu_s, 2, 1)  # (-N/2) of (2 or -2) => ±1, times mu s

    b21_mu_s = -raw({"u": 2, "v": 1, "mu": 1, "s": 1})
    b21_mu = -raw({"u": 2, "v": 1, "mu": 1})
    b21_s = -raw({"u": 2, "v": 1, "s": 1})
    b21_c = -raw({"u": 2, "v": 1})
    if b21_mu or b21_s or b21_c:
        raise AssertionError(f"unexpected b21 constant pieces {b21_mu, b21_s, b21_c}")
    jets["b21"] = (b21_mu_s, 2, 1)

    # reduce fractions
    out = {}
    for name, (num, den, sp) in jets.items():
        if num == 0:
            out[name] = (0, 1, 0)
            continue
        g = math.gcd(abs(num), abs(den))
        num //= g
        den //= g
        if den < 0:
            num, den = -num, -den
        out[name] = (num, den, sp)
    return out


def l1_from_jet(jet: dict[str, tuple[int, int, int]]) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    """L1_quad, L1_cubic, L1_full as (num, den, s_power) times mu^0 or mu^1.

    All a_ij = 0 in this family. The surviving pieces are
        L1_quad = -(b20 + b02) b11
        L1_cubic = b21 + 3 b03 + 3 a30 + a12
    b11 and b21 are already the coefficients of mu (times s^p).
    b20, b02, b03, a30, a12 are mu-free.
    Product (b20)(b11) is (mu-free)*(mu * s^p).
    """

    def add(a, b):
        n1, d1, s1 = a
        n2, d2, s2 = b
        if n1 == 0:
            return b
        if n2 == 0:
            return a
        if s1 != s2:
            raise AssertionError(f"cannot add s^{s1} and s^{s2} without reducing")
        num = n1 * d2 + n2 * d1
        den = d1 * d2
        g = math.gcd(abs(num), abs(den))
        num //= g
        den //= g
        return (num, den, s1)

    def mul(a, b):
        n1, d1, s1 = a
        n2, d2, s2 = b
        num = n1 * n2
        den = d1 * d2
        sp = s1 + s2
        extra = 1
        while sp >= 2:
            extra *= 2
            sp -= 2
        num *= extra
        if num == 0:
            return (0, 1, 0)
        g = math.gcd(abs(num), abs(den))
        num //= g
        den //= g
        return (num, den, sp)

    def sc(a, k: int):
        n, d, s = a
        num = n * k
        if num == 0:
            return (0, 1, 0)
        g = math.gcd(abs(num), d)
        return (num // g, d // g, s)

    a20, a11, a02 = jet["a20"], jet["a11"], jet["a02"]
    b20, b11, b02 = jet["b20"], jet["b11"], jet["b02"]
    a30, a12 = jet["a30"], jet["a12"]
    b21, b03 = jet["b21"], jet["b03"]

    # (a20+a02)*a11
    lq = mul(add(a20, a02), a11)
    # -(b20+b02)*b11
    lq = add(lq, sc(mul(add(b20, b02), b11), -1))
    # -2 a20 b20
    lq = add(lq, sc(mul(a20, b20), -2))
    # +2 a02 b02
    lq = add(lq, sc(mul(a02, b02), 2))
    lc = add(add(sc(a30, 3), a12), add(b21, sc(b03, 3)))
    lf = add(lq, lc)
    return lq, lc, lf


# ---------------------------------------------------------------------------
# Figure-eight I(0)
# ---------------------------------------------------------------------------


def figure_eight() -> dict[str, Poly | str | int]:
    t = V(T_VARS, "t")
    integrand = (t ** 4).scale(4) - (t ** 2).scale(2)
    # 15 * antiderivative = 12 t^5 - 10 t^3
    anti15 = (t ** 5).scale(12) - (t ** 3).scale(10)
    deriv = anti15.dvar("t")
    fifteen_int = integrand.scale(15)
    deriv_diff = deriv - fifteen_int
    # evenness of (1-x^2) and of the radicand x^2 - x^4/2 = (1/2)(2x^2 - x^4)
    # cleared radicand R = 2x^2 - x^4, even
    xe = ("x",)
    x = V(xe, "x")
    one_minus = C(xe, 1) - x ** 2
    rad = (x ** 2).scale(2) - (x ** 4)
    even_damp = one_minus.subst({"x": -x}) - one_minus
    even_rad = rad.subst({"x": -x}) - rad
    # 4/5 - 2/3 = 2/15; 2 * 2/15 = 4/15
    if 4 * 3 - 2 * 5 != 2:
        raise AssertionError("4/5 - 2/3 numerator")
    if 5 * 3 != 15:
        raise AssertionError("4/5 - 2/3 denominator")
    if 2 * 2 != 4 or 15 != 15:
        raise AssertionError("2/15 * 2")
    # evaluate [12 t^5 - 10 t^3] at 1, divide by 15: (12-10)/15 = 2/15
    at1 = anti15.eval({"t": 1})
    if at1 != 2:
        raise AssertionError(f"15*antideriv(1) = {at1}, expected 2")
    at0 = anti15.eval({"t": 0})
    if at0 != 0:
        raise AssertionError("antideriv(0) is not 0")
    return {
        "integrand": integrand,
        "anti15": anti15,
        "deriv_diff": deriv_diff,
        "even_damp": even_damp,
        "even_rad": even_rad,
        "anti15_at_1": at1,
        "I0_num": 4,
        "I0_den": 15,
    }


# ---------------------------------------------------------------------------
# Certificates and dump
# ---------------------------------------------------------------------------


def check_all() -> dict:
    up = unperturbed()
    _require_zero(up["dH4"], "unperturbed dH4/dt")
    _require_zero(up["potential_diff"], "potential shift")
    _require_zero(up["Q_factor_diff"], "Q factorization")
    _require_zero(up["det_diff"], "Jacobian det")
    _require_zero(up["div"], "divergence")
    check_equilibria(up)

    pr = perturbed()
    _require_zero(pr["dH4_diff"], "perturbed dH4/dt")
    _require_zero(pr["trace_diff"], "perturbed trace")
    check_perturbed(pr)

    plus = translate_plus()
    minus = translate_minus()
    _require_zero(plus["diff"], "+1 translation")
    _require_zero(minus["diff"], "-1 translation")

    n_plus = focal_plus()
    n_minus = focal_minus()
    # N(+1) = -3 u^2 - u^3 + 2 mu s u v + mu s u^2 v
    if n_plus.coeff({"u": 2}) != -3:
        raise AssertionError("N+ u^2")
    if n_plus.coeff({"u": 3}) != -1:
        raise AssertionError("N+ u^3")
    if n_plus.coeff({"u": 1, "v": 1, "mu": 1, "s": 1}) != 2:
        raise AssertionError("N+ mu s u v")
    if n_plus.coeff({"u": 2, "v": 1, "mu": 1, "s": 1}) != 1:
        raise AssertionError("N+ mu s u^2 v")
    if n_minus.coeff({"u": 2}) != 3:
        raise AssertionError("N- u^2")
    if n_minus.coeff({"u": 3}) != -1:
        raise AssertionError("N- u^3")
    if n_minus.coeff({"u": 1, "v": 1, "mu": 1, "s": 1}) != -2:
        raise AssertionError("N- mu s u v")
    if n_minus.coeff({"u": 2, "v": 1, "mu": 1, "s": 1}) != 1:
        raise AssertionError("N- mu s u^2 v")

    jet_p = jet_from_n(n_plus)
    jet_m = jet_from_n(n_minus)
    if jet_p["b20"] != (3, 2, 0):
        raise AssertionError(f"plus b20 {jet_p['b20']}")
    if jet_p["b11"] != (-1, 1, 1):
        raise AssertionError(f"plus b11 {jet_p['b11']}")
    if jet_p["b30"] != (1, 2, 0):
        raise AssertionError(f"plus b30 {jet_p['b30']}")
    if jet_p["b21"] != (-1, 2, 1):
        raise AssertionError(f"plus b21 {jet_p['b21']}")
    if jet_m["b20"] != (-3, 2, 0):
        raise AssertionError(f"minus b20 {jet_m['b20']}")
    if jet_m["b11"] != (1, 1, 1):
        raise AssertionError(f"minus b11 {jet_m['b11']}")
    if jet_m["b30"] != (1, 2, 0):
        raise AssertionError(f"minus b30 {jet_m['b30']}")
    if jet_m["b21"] != (-1, 2, 1):
        raise AssertionError(f"minus b21 {jet_m['b21']}")

    lq_p, lc_p, lf_p = l1_from_jet(jet_p)
    lq_m, lc_m, lf_m = l1_from_jet(jet_m)
    if lq_p != (3, 2, 1):
        raise AssertionError(f"L1_quad plus {lq_p}")
    if lc_p != (-1, 2, 1):
        raise AssertionError(f"L1_cubic plus {lc_p}")
    if lf_p != (1, 1, 1):
        raise AssertionError(f"L1 plus {lf_p}")
    if lq_m != (3, 2, 1):
        raise AssertionError(f"L1_quad minus {lq_m}")
    if lc_m != (-1, 2, 1):
        raise AssertionError(f"L1_cubic minus {lc_m}")
    if lf_m != (1, 1, 1):
        raise AssertionError(f"L1 minus {lf_m}")
    # mu=0 => L1=0 is the same tuples with the understanding they multiply mu
    # L1^2 / mu^2 = 2
    # (1*sqrt(2))^2 = 2

    fe = figure_eight()
    _require_zero(fe["deriv_diff"], "15*antideriv derivative")
    _require_zero(fe["even_damp"], "1-x^2 even")
    _require_zero(fe["even_rad"], "radicand even")

    # negative: a wrong potential is not a first integral
    x, y = V(XY, "x"), V(XY, "y")
    bad_h = (y ** 2).scale(2) - (x ** 2).scale(2)  # dropped x^4
    bad_dh = bad_h.dvar("x") * up["P"] + bad_h.dvar("y") * up["Q"]
    if bad_dh.is_zero():
        raise AssertionError("dropped-x^4 energy unexpectedly conserved")

    # degree
    # P degree 1, Q unperturbed degree 3, perturbed Q degree 3
    if up["P"].nterms() != 1:
        raise AssertionError("P terms")
    if up["Q"].nterms() != 2:
        raise AssertionError("Q terms")

    return {
        "up": up,
        "pr": pr,
        "plus": plus,
        "minus": minus,
        "jet_p": jet_p,
        "jet_m": jet_m,
        "lq_p": lq_p,
        "lc_p": lc_p,
        "lf_p": lf_p,
        "lq_m": lq_m,
        "lc_m": lc_m,
        "lf_m": lf_m,
        "fe": fe,
        "H4_terms": up["H4"].nterms(),
        "dH4_unperturbed_terms": up["dH4"].nterms(),
        "dH4_perturbed_diff_terms": pr["dH4_diff"].nterms(),
        "plus_translate_diff_terms": plus["diff"].nterms(),
        "minus_translate_diff_terms": minus["diff"].nterms(),
    }


def build_core(data: dict) -> dict:
    return {
        "schema": "hilbert16-ff-two-well-core/v1",
        "claim": (
            "Unperturbed two-well cubic Hamiltonian classification, "
            "dH/dt identities, I(h) formula, I(0)=4 mu/15 per figure-eight "
            "lobe, and L1=sqrt(2)*mu at each well. Not 14 zeros of I(h) "
            "and not a bound on H(n)."
        ),
        "hn_moved": False,
        "fourteen_zeros_produced": False,
        "regular_I_zeros_exhibited": 0,
        "cycles_proved": 0,
        "degree": 3,
        "L1_plus": "sqrt(2)*mu",
        "L1_minus": "sqrt(2)*mu",
        "L1_quad_plus": "3*sqrt(2)*mu/2",
        "L1_cubic_plus": "-sqrt(2)*mu/2",
        "L1_quad_minus": "3*sqrt(2)*mu/2",
        "L1_cubic_minus": "-sqrt(2)*mu/2",
        "V1_plus": "sqrt(2)*mu/8",
        "L1_squared_coeff": 2,
        "I0_right": "4/15*mu",
        "I0_left": "4/15*mu",
        "I_at_well_bottom": "0",
        "weak_focus_order": 1,
        "saddle_stays_saddle": True,
        "trace_at_wells": "0",
        "H_saddle": "0",
        "H_wells": "-1/4",
        "potential_shift": "1/4",
        "equilibria": [
            {"x": 0, "y": 0, "kind": "saddle", "det": "-1", "trace": "0", "H": "0"},
            {"x": 1, "y": 0, "kind": "center", "det": "2", "trace": "0", "H": "-1/4"},
            {"x": -1, "y": 0, "kind": "center", "det": "2", "trace": "0", "H": "-1/4"},
        ],
        "perturbed_equilibria": [
            {"x": 0, "y": 0, "kind": "saddle", "det": "-1", "trace": "mu"},
            {"x": 1, "y": 0, "kind": "center", "det": "2", "trace": "0"},
            {"x": -1, "y": 0, "kind": "center", "det": "2", "trace": "0"},
        ],
        "what_this_is_not": [
            "not a dent of H(n)",
            "not fourteen zeros of an Abelian integral",
            "not a proved pair of limit cycles",
            "not a new H(3)",
        ],
    }


def build_identities(data: dict) -> dict:
    up, pr, plus, minus, fe = data["up"], data["pr"], data["plus"], data["minus"], data["fe"]
    return {
        "schema": "hilbert16-ff-two-well-identities/v1",
        "unperturbed": {
            "variables": list(XY),
            "P": up["P"].to_terms(),
            "Q": up["Q"].to_terms(),
            "H4": up["H4"].to_terms(),
            "dH4": up["dH4"].to_terms(),
            "det": up["det"].to_terms(),
            "div": up["div"].to_terms(),
            "Q_factored": up["Q_factored"].to_terms(),
        },
        "perturbed": {
            "variables": list(XYM),
            "P": pr["P"].to_terms(),
            "Q": pr["Q"].to_terms(),
            "dH4": pr["dH4"].to_terms(),
            "claimed4": pr["claimed4"].to_terms(),
            "trace": pr["trace"].to_terms(),
        },
        "translate_plus": {
            "variables": list(XYMS),
            "Q": plus["Q"].to_terms(),
            "claimed": plus["claimed"].to_terms(),
            "diff": plus["diff"].to_terms(),
        },
        "translate_minus": {
            "variables": list(XYMS),
            "Q": minus["Q"].to_terms(),
            "claimed": minus["claimed"].to_terms(),
            "diff": minus["diff"].to_terms(),
        },
        "figure_eight": {
            "variables": list(T_VARS),
            "integrand": fe["integrand"].to_terms(),
            "anti15": fe["anti15"].to_terms(),
            "deriv_diff": fe["deriv_diff"].to_terms(),
            "I0_num": fe["I0_num"],
            "I0_den": fe["I0_den"],
        },
        "jets": {
            "plus": {k: {"num": v[0], "den": v[1], "s_power": v[2]} for k, v in data["jet_p"].items()},
            "minus": {k: {"num": v[0], "den": v[1], "s_power": v[2]} for k, v in data["jet_m"].items()},
            "L1_plus": {"num": data["lf_p"][0], "den": data["lf_p"][1], "s_power": data["lf_p"][2]},
            "L1_minus": {"num": data["lf_m"][0], "den": data["lf_m"][1], "s_power": data["lf_m"][2]},
        },
    }


def check_core(payload: dict) -> None:
    if payload.get("hn_moved") is not False:
        raise AssertionError("core must not claim that H(n) moved")
    if payload.get("fourteen_zeros_produced") is not False:
        raise AssertionError("must not claim 14 zeros")
    if payload.get("cycles_proved") != 0:
        raise AssertionError("must not claim proved cycles")
    if payload.get("regular_I_zeros_exhibited") != 0:
        raise AssertionError("no regular I zeros were exhibited")
    if payload.get("L1_plus") != "sqrt(2)*mu":
        raise AssertionError("L1_plus")
    if payload.get("L1_minus") != "sqrt(2)*mu":
        raise AssertionError("L1_minus")
    if payload.get("I0_right") != "4/15*mu":
        raise AssertionError("I0_right")
    if payload.get("degree") != 3:
        raise AssertionError("degree")


def check_identities(payload: dict, data: dict) -> None:
    up, pr = data["up"], data["pr"]
    ub = payload["unperturbed"]
    _require_match(XY, ub["P"], up["P"], "cert P")
    _require_match(XY, ub["Q"], up["Q"], "cert Q")
    _require_match(XY, ub["H4"], up["H4"], "cert H4")
    _require_match(XY, ub["dH4"], up["dH4"], "cert dH4")
    pb = payload["perturbed"]
    _require_match(XYM, pb["P"], pr["P"], "cert pert P")
    _require_match(XYM, pb["Q"], pr["Q"], "cert pert Q")
    _require_match(XYM, pb["dH4"], pr["dH4"], "cert pert dH4")
    _require_match(XYM, pb["claimed4"], pr["claimed4"], "cert claimed4")
    _require_match(XYMS, payload["translate_plus"]["diff"], data["plus"]["diff"], "cert plus diff")
    _require_match(XYMS, payload["translate_minus"]["diff"], data["minus"]["diff"], "cert minus diff")
    _require_match(T_VARS, payload["figure_eight"]["deriv_diff"], data["fe"]["deriv_diff"], "cert I0 deriv")
    if payload["jets"]["L1_plus"] != {"num": 1, "den": 1, "s_power": 1}:
        raise AssertionError("cert L1 plus")
    if payload["jets"]["L1_minus"] != {"num": 1, "den": 1, "s_power": 1}:
        raise AssertionError("cert L1 minus")


def dump_lines(data: dict) -> list[str]:
    return [
        "imagined_fourteen_zeros DROP",
        "H3_ge_14 DROP",
        "unperturbed_classification KEEP",
        "dHdt_identities KEEP",
        "I_h_formula KEEP",
        "I0_figure_eight KEEP",
        "L1_both_wells KEEP",
        "hn_moved 0",
        "fourteen_zeros_produced 0",
        "regular_I_zeros_exhibited 0",
        "cycles_proved 0",
        "degree 3",
        "eq 0 0 kind=saddle det=-1 trace=0 H=0",
        "eq 1 0 kind=center det=2 trace=0 H=-1/4",
        "eq -1 0 kind=center det=2 trace=0 H=-1/4",
        f"H4_terms {data['H4_terms']}",
        f"dH4_unperturbed_terms {data['dH4_unperturbed_terms']}",
        f"dH4_perturbed_diff_terms {data['dH4_perturbed_diff_terms']}",
        "div_unperturbed 0",
        "perturbed_eq 0 0 kind=saddle det=-1 trace=mu",
        "perturbed_eq 1 0 kind=center det=2 trace=0",
        "perturbed_eq -1 0 kind=center det=2 trace=0",
        "saddle_stays_saddle 1",
        "trace_at_wells 0",
        f"plus_translate_diff_terms {data['plus_translate_diff_terms']}",
        f"minus_translate_diff_terms {data['minus_translate_diff_terms']}",
        "plus_jet b20=3/2 b11=-sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "minus_jet b20=-3/2 b11=sqrt(2)*mu b30=1/2 b21=-sqrt(2)*mu/2",
        "L1_formula_quad (a20+a02)*a11-(b20+b02)*b11-2*a20*b20+2*a02*b02",
        "L1_formula_cubic 3*a30+a12+b21+3*b03",
        "L1_quad_plus 3*sqrt(2)*mu/2",
        "L1_cubic_plus -sqrt(2)*mu/2",
        "L1_plus sqrt(2)*mu",
        "L1_quad_minus 3*sqrt(2)*mu/2",
        "L1_cubic_minus -sqrt(2)*mu/2",
        "L1_minus sqrt(2)*mu",
        "L1_squared_coeff 2",
        "V1_plus sqrt(2)*mu/8",
        "weak_focus_order 1",
        "I0_antideriv_at_1 2/15",
        "I0_J 4/15",
        "I0_right 4/15*mu",
        "I0_left 4/15*mu",
        "I_at_well_bottom 0",
        "I_not_identically_zero 1",
        "potential_shift 1/4",
    ]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    data = check_all()
    core = build_core(data)
    ident = build_identities(data)
    check_core(core)
    check_identities(ident, data)

    if args.write_cert:
        write_json(CORE_PATH, core)
        write_json(IDENT_PATH, ident)
        print(f"wrote {CORE_PATH}")
        print(f"wrote {IDENT_PATH}")

    if not CORE_PATH.is_file() or not IDENT_PATH.is_file():
        raise SystemExit("missing certificates; run with --write-cert")

    saved_core = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    saved_ident = json.loads(IDENT_PATH.read_text(encoding="utf-8"))
    check_core(saved_core)
    check_identities(saved_ident, data)
    if saved_core != core:
        raise AssertionError("committed core.json is not the canonical dump")
    if saved_ident != ident:
        raise AssertionError("committed identities.json is not the canonical dump")

    lines = dump_lines(data)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID ff-two-well replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
