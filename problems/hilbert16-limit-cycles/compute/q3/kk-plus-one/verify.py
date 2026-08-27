#!/usr/bin/env python3
"""Exact algebra for Gasull–Santana +1 on the radial cubic.

Imagined: an explicit degree-4 field with two hyperbolic isolated
periodic orbits, hence H(4) >= 2. Not produced. The Hopf half of
Theorem 1 (arXiv:2407.13465v2) is not written term-by-term.

Kept: translate p = (2, 0), expand P_t and Q_t over Q with
rho^2 = 1/4, multiply by the line L = 4x - 15y, prove the line
misses the translated circle, and read det = trace = 0 at the
origin. The n+2 field (x^2+y^2)X on the untranslated cubic is
degree 5 and has the same unique circle. Not a bound on H(n).

A second, independent check is verify.rs (cleared Z[x, y] plus
integer-box evaluation of the residuals).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
CORE_PATH = CERTS / "core.json"
IDENT_PATH = CERTS / "identities.json"

XY = ("x", "y")


class QPoly:
    """Sparse bivariate polynomial over Q, variables (x, y)."""

    def __init__(self, terms: dict[tuple[int, int], Fraction] | None = None):
        self.terms: dict[tuple[int, int], Fraction] = defaultdict(lambda: Fraction(0))
        if terms:
            for exp, coeff in terms.items():
                if coeff:
                    self.terms[exp] += Fraction(coeff)
            self._prune()

    def _prune(self) -> None:
        for exp in [e for e, c in self.terms.items() if c == 0]:
            del self.terms[exp]

    def copy(self) -> "QPoly":
        return QPoly(dict(self.terms))

    @classmethod
    def zero(cls) -> "QPoly":
        return cls()

    @classmethod
    def const(cls, value: Fraction | int) -> "QPoly":
        out = cls()
        v = Fraction(value)
        if v:
            out.terms[(0, 0)] = v
        return out

    @classmethod
    def var(cls, name: str) -> "QPoly":
        out = cls()
        if name == "x":
            out.terms[(1, 0)] = Fraction(1)
        elif name == "y":
            out.terms[(0, 1)] = Fraction(1)
        else:
            raise ValueError(name)
        return out

    def __neg__(self) -> "QPoly":
        return QPoly({e: -c for e, c in self.terms.items()})

    def __add__(self, other: "QPoly") -> "QPoly":
        out = self.copy()
        for exp, coeff in other.terms.items():
            out.terms[exp] += coeff
        out._prune()
        return out

    def __sub__(self, other: "QPoly") -> "QPoly":
        return self + (-other)

    def __mul__(self, other: "QPoly") -> "QPoly":
        out = QPoly.zero()
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                out.terms[(e1[0] + e2[0], e1[1] + e2[1])] += c1 * c2
        out._prune()
        return out

    def scale(self, k: Fraction | int) -> "QPoly":
        k = Fraction(k)
        if k == 0:
            return QPoly.zero()
        return QPoly({e: c * k for e, c in self.terms.items()})

    def __pow__(self, n: int) -> "QPoly":
        if n < 0:
            raise ValueError("negative power")
        out = QPoly.const(1)
        base = self
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def dvar(self, name: str) -> "QPoly":
        idx = 0 if name == "x" else 1
        out = QPoly.zero()
        for exp, coeff in self.terms.items():
            power = exp[idx]
            if power == 0:
                continue
            new_exp = list(exp)
            new_exp[idx] = power - 1
            out.terms[tuple(new_exp)] += coeff * power
        out._prune()
        return out

    def subst_x(self, xnew: "QPoly") -> "QPoly":
        out = QPoly.zero()
        y = QPoly.var("y")
        for (i, j), coeff in self.terms.items():
            out = out + (xnew**i) * (y**j) * QPoly.const(coeff)
        return out

    def eval(self, x: Fraction | int, y: Fraction | int) -> Fraction:
        total = Fraction(0)
        xv, yv = Fraction(x), Fraction(y)
        for (i, j), coeff in self.terms.items():
            total += coeff * (xv**i) * (yv**j)
        return total

    def coeff(self, i: int, j: int) -> Fraction:
        return Fraction(self.terms.get((i, j), 0))

    def degree(self) -> int:
        if not self.terms:
            return -1
        return max(i + j for i, j in self.terms)

    def nterms(self) -> int:
        return len(self.terms)

    def is_zero(self) -> bool:
        return not self.terms

    def equals(self, other: "QPoly") -> bool:
        keys = set(self.terms) | set(other.terms)
        return all(self.terms.get(k, 0) == other.terms.get(k, 0) for k in keys)

    def sorted_mons(self) -> list[tuple[int, int, int, int]]:
        items = []
        for (i, j), c in self.terms.items():
            items.append((i + j, i, j, c.numerator, c.denominator))
        items.sort()
        return [(i, j, n, d) for _, i, j, n, d in items]

    def to_terms(self) -> list[dict[str, int | str]]:
        out: list[dict[str, int | str]] = []
        for i, j, n, d in self.sorted_mons():
            item: dict[str, int | str] = {"coeff": _frac_str(n, d)}
            if i:
                item["x"] = i
            if j:
                item["y"] = j
            out.append(item)
        return out

    @classmethod
    def from_terms(cls, terms: Iterable[dict]) -> "QPoly":
        out = cls.zero()
        for item in terms:
            i = int(item.get("x", 0))
            j = int(item.get("y", 0))
            out.terms[(i, j)] += Fraction(item["coeff"])
        out._prune()
        return out

    def times_int(self, k: int) -> dict[tuple[int, int], int]:
        out: dict[tuple[int, int], int] = {}
        for (i, j), c in self.terms.items():
            v = c * k
            if v.denominator != 1:
                raise AssertionError(f"times_int({k}) left a denominator: {c}")
            if v.numerator:
                out[(i, j)] = v.numerator
        return out


def _frac_str(n: int, d: int) -> str:
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _require_zero(poly: QPoly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: QPoly, right: QPoly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}")


def _require_match(terms: list, poly: QPoly, label: str) -> None:
    _require_equal(QPoly.from_terms(terms), poly, label)


def radial_cubic() -> tuple[QPoly, QPoly]:
    x, y = QPoly.var("x"), QPoly.var("y")
    r2 = x**2 + y**2
    rho2 = QPoly.const(Fraction(1, 4))
    p = y - x * (r2 - rho2)
    q = -x - y * (r2 - rho2)
    return p, q


def translate(poly: QPoly) -> QPoly:
    return poly.subst_x(QPoly.var("x") + QPoly.const(2))


def claimed_pt() -> QPoly:
    x, y = QPoly.var("x"), QPoly.var("y")
    return (
        -(x**3)
        - x * (y**2)
        - (x**2).scale(6)
        - (y**2).scale(2)
        + y
        - x.scale(Fraction(47, 4))
        - QPoly.const(Fraction(15, 2))
    )


def claimed_qt() -> QPoly:
    x, y = QPoly.var("x"), QPoly.var("y")
    return (
        -(x**2) * y
        - (y**3)
        - (x * y).scale(4)
        - x
        - y.scale(Fraction(15, 4))
        - QPoly.const(2)
    )


def check_all() -> dict:
    p, q = radial_cubic()
    if p.eval(0, 0) != 0 or q.eval(0, 0) != 0:
        raise AssertionError("untranslated origin is not an equilibrium")
    if p.eval(2, 0) != Fraction(-15, 2):
        raise AssertionError(f"P(2,0) = {p.eval(2, 0)}")
    if q.eval(2, 0) != Fraction(-2):
        raise AssertionError(f"Q(2,0) = {q.eval(2, 0)}")

    x, y = QPoly.var("x"), QPoly.var("y")
    r2 = x**2 + y**2
    rho2 = QPoly.const(Fraction(1, 4))
    polar_r = x * p + y * q
    polar_r_rhs = r2 * (rho2 - r2)
    _require_zero(polar_r - polar_r_rhs, "original polar radial")
    polar_a = x * q - y * p
    _require_zero(polar_a + r2, "original polar angular")

    pt = translate(p)
    qt = translate(q)
    _require_equal(pt, claimed_pt(), "P_t expansion")
    _require_equal(qt, claimed_qt(), "Q_t expansion")
    if pt.eval(0, 0) != Fraction(-15, 2) or qt.eval(0, 0) != Fraction(-2):
        raise AssertionError("translated origin values")
    if pt.degree() != 3 or qt.degree() != 3:
        raise AssertionError("translated degree")

    xi = x + QPoly.const(2)
    rt2 = xi**2 + y**2
    _require_zero(xi * pt + y * qt - rt2 * (rho2 - rt2), "translated polar radial")
    _require_zero(xi * qt - y * pt + rt2, "translated polar angular")

    circle = rt2 - rho2
    dc_dt = circle.dvar("x") * pt + circle.dvar("y") * qt
    # dC/dt = 2((x+2) P_t + y Q_t) = -2 r_t^2 C
    _require_zero(dc_dt + (rt2 * circle).scale(2), "circle orbital derivative")

    a = -qt.eval(0, 0)
    b = pt.eval(0, 0)
    if a != 2 or b != Fraction(-15, 2):
        raise AssertionError(f"GS (a,b) = ({a}, {b})")
    line_gs = x.scale(a) + y.scale(b)
    ell = x.scale(4) + y.scale(-15)
    _require_zero(ell - line_gs.scale(2), "L = 2(ax+by)")

    r = ell * pt
    s = ell * qt
    if r.degree() != 4 or s.degree() != 4:
        raise AssertionError(f"product degrees {r.degree()} {s.degree()}")
    if r.nterms() != 13 or s.nterms() != 10:
        raise AssertionError(f"product term counts {r.nterms()} {s.nterms()}")
    if r.coeff(4, 0) != Fraction(-4):
        raise AssertionError("leading R")
    _require_zero(r - ell * pt, "R definition")
    _require_zero(s - ell * qt, "S definition")
    # line of singularities: R and S are multiples of L
    if r.eval(0, 0) != 0 or s.eval(0, 0) != 0:
        raise AssertionError("origin of the product is not an equilibrium")
    if r.eval(15, 4) != 0 or s.eval(15, 4) != 0:
        raise AssertionError("sample point on L is not an equilibrium")

    dc_prod = circle.dvar("x") * r + circle.dvar("y") * s
    _require_zero(dc_prod - ell * dc_dt, "product orbital derivative factors L")

    # Jacobian of (R, S) at the origin, two ways.
    drdx, drdy = r.dvar("x"), r.dvar("y")
    dsdx, dsdy = s.dvar("x"), s.dvar("y")
    jac = {
        "dRdx": drdx.eval(0, 0),
        "dRdy": drdy.eval(0, 0),
        "dSdx": dsdx.eval(0, 0),
        "dSdy": dsdy.eval(0, 0),
    }
    if jac["dRdx"] != Fraction(-30):
        raise AssertionError(f"dR/dx(0,0) = {jac['dRdx']}")
    if jac["dRdy"] != Fraction(225, 2):
        raise AssertionError(f"dR/dy(0,0) = {jac['dRdy']}")
    if jac["dSdx"] != Fraction(-8):
        raise AssertionError(f"dS/dx(0,0) = {jac['dSdx']}")
    if jac["dSdy"] != Fraction(30):
        raise AssertionError(f"dS/dy(0,0) = {jac['dSdy']}")
    det = jac["dRdx"] * jac["dSdy"] - jac["dRdy"] * jac["dSdx"]
    tr = jac["dRdx"] + jac["dSdy"]
    if det != 0 or tr != 0:
        raise AssertionError(f"Jacobian det={det} trace={tr}")
    # product rule at 0: L=0 so DX = [[Lx Pt, Ly Pt], [Lx Qt, Ly Qt]]
    if Fraction(4) * pt.eval(0, 0) != jac["dRdx"]:
        raise AssertionError("product-rule dR/dx")
    if Fraction(-15) * pt.eval(0, 0) != jac["dRdy"]:
        raise AssertionError("product-rule dR/dy")
    if Fraction(4) * qt.eval(0, 0) != jac["dSdx"]:
        raise AssertionError("product-rule dS/dx")
    if Fraction(-15) * qt.eval(0, 0) != jac["dSdy"]:
        raise AssertionError("product-rule dS/dy")

    gs_ab = a * b
    gs_b2 = b * b
    gs_ma2 = -(a * a)
    gs_mab = -(a * b)
    if gs_ab != Fraction(-15) or gs_b2 != Fraction(225, 4):
        raise AssertionError("GS display ab, b^2")
    if gs_ma2 != Fraction(-4) or gs_mab != Fraction(15):
        raise AssertionError("GS display -a^2, -ab")
    if gs_ab * gs_mab - gs_b2 * gs_ma2 != 0:
        raise AssertionError("GS display det")
    if gs_ab + gs_mab != 0:
        raise AssertionError("GS display trace")

    # Distance from (-2, 0) to 4x-15y=0 versus radius 1/2.
    dist_num = abs(4 * (-2) - 15 * 0)
    dist_den_sq = 4 * 4 + 15 * 15
    if dist_num != 8 or dist_den_sq != 241:
        raise AssertionError("distance integers")
    miss_cleared = 4 * dist_num * dist_num - dist_den_sq
    if miss_cleared != 15:
        raise AssertionError(f"miss_cleared {miss_cleared}")
    if miss_cleared <= 0:
        raise AssertionError("line meets the circle")

    # Intersection quadratic: 900(x+2)^2 + 64 x^2 - 225.
    inter = (x + QPoly.const(2)).scale(1)
    inter_q = (inter**2).scale(900) + (x**2).scale(64) - QPoly.const(225)
    qa = inter_q.coeff(2, 0)
    qb = inter_q.coeff(1, 0)
    qc = inter_q.coeff(0, 0)
    if (qa, qb, qc) != (Fraction(964), Fraction(3600), Fraction(3375)):
        raise AssertionError(f"intersection quadratic {qa} {qb} {qc}")
    disc = qb * qb - Fraction(4) * qa * qc
    if disc != Fraction(-54000):
        raise AssertionError(f"discriminant {disc}")
    if inter_q.coeff(0, 1) != 0 or inter_q.degree() != 2:
        raise AssertionError("intersection quadratic is not univariate")

    if ell.eval(-2, 0) != Fraction(-8):
        raise AssertionError("L at centre")
    if ell.eval(Fraction(-3, 2), 0) != Fraction(-6):
        raise AssertionError("L at rightmost point of the circle")
    # rightmost point is on the circle
    if circle.eval(Fraction(-3, 2), 0) != 0:
        raise AssertionError("(-3/2, 0) is not on the translated circle")

    # Untranslated line through the origin always hits the circle.
    # Distance from (0,0) to any ax+by=0 is 0 < 1/2.
    # Concrete: x=0 meets the circle at (0, ±1/2).
    if r2.eval(0, Fraction(1, 2)) - rho2.eval(0, 0) != 0:
        raise AssertionError("x=0 should meet the untranslated circle")
    if (x * p).eval(0, Fraction(1, 2)) != 0:
        raise AssertionError("untranslated xP vanishes on the circle")

    # n+2 on the untranslated field.
    n2f = r2 * p
    n2g = r2 * q
    if n2f.degree() != 5 or n2g.degree() != 5:
        raise AssertionError("n+2 degree")
    if n2f.nterms() != 7 or n2g.nterms() != 7:
        raise AssertionError("n+2 term counts")
    _require_zero(x * n2f + y * n2g - (r2**2) * (rho2 - r2), "n+2 polar radial")
    _require_zero(x * n2g - y * n2f + (r2**2), "n+2 polar angular")

    # Cleared integer copies of 4 P_t, 4 Q_t.
    p4t = pt.times_int(4)
    q4t = qt.times_int(4)
    if p4t.get((0, 0)) != -30 or q4t.get((0, 0)) != -8:
        raise AssertionError("cleared origin")

    # Negative: a wrong translation does not reproduce P_t.
    wrong = p.subst_x(QPoly.var("x") + QPoly.const(1))
    if wrong.equals(pt):
        raise AssertionError("translation by 1 unexpectedly equals P_t")

    return {
        "P": p,
        "Q": q,
        "Pt": pt,
        "Qt": qt,
        "L": ell,
        "R": r,
        "S": s,
        "n2F": n2f,
        "n2G": n2g,
        "jac": jac,
        "a": a,
        "b": b,
        "gs_ab": gs_ab,
        "gs_b2": gs_b2,
        "gs_ma2": gs_ma2,
        "gs_mab": gs_mab,
        "dist_num": dist_num,
        "dist_den_sq": dist_den_sq,
        "miss_cleared": miss_cleared,
        "qa": int(qa),
        "qb": int(qb),
        "qc": int(qc),
        "disc": int(disc),
        "p4t": p4t,
        "q4t": q4t,
        "P20": p.eval(2, 0),
        "Q20": q.eval(2, 0),
        "L_center": ell.eval(-2, 0),
        "L_right": ell.eval(Fraction(-3, 2), 0),
    }


def _qstr(val: Fraction) -> str:
    return _frac_str(val.numerator, val.denominator)


def dump_mons(prefix: str, poly: QPoly) -> list[str]:
    return [f"{prefix} {i} {j} {n} {d}" for i, j, n, d in poly.sorted_mons()]


def dump_int_mons(prefix: str, terms: dict[tuple[int, int], int]) -> list[str]:
    items = [(i + j, i, j, c) for (i, j), c in terms.items()]
    items.sort()
    return [f"{prefix} {i} {j} {c}" for _, i, j, c in items]


def dump_lines(data: dict) -> list[str]:
    return [
        "imagined_two_hyperbolic_cycles DROP",
        "H4_ge_2 DROP",
        "H4_ge_28_via_plus_one DROP",
        "translated_Pt_Qt KEEP",
        "degree4_field KEEP",
        "line_misses_circle KEEP",
        "translated_circle_orbit KEEP",
        "origin_jacobian KEEP",
        "n_plus_2_same_circle KEEP",
        "hn_moved 0",
        "cycles_proved 1",
        "hopf_cycles_written 0",
        "degree 4",
        "rho2 1/4",
        "translate_p 2 0",
        f"Pt00 {_qstr(data['Pt'].eval(0, 0))}",
        f"Qt00 {_qstr(data['Qt'].eval(0, 0))}",
        "a 2",
        "b -15/2",
        "line 4x-15y",
        "L_coeffs 4 -15",
        f"P20 {_qstr(data['P20'])}",
        f"Q20 {_qstr(data['Q20'])}",
        "regular_p 1",
        f"dist_num {data['dist_num']}",
        f"dist_den_sq {data['dist_den_sq']}",
        "radius 1/2",
        f"miss_cleared {data['miss_cleared']}",
        "miss 1",
        f"circle_line_a {data['qa']}",
        f"circle_line_b {data['qb']}",
        f"circle_line_c {data['qc']}",
        f"circle_line_disc {data['disc']}",
        "jac_det 0",
        "jac_trace 0",
        f"L_jac_dRdx {_qstr(data['jac']['dRdx'])}",
        f"L_jac_dRdy {_qstr(data['jac']['dRdy'])}",
        f"L_jac_dSdx {_qstr(data['jac']['dSdx'])}",
        f"L_jac_dSdy {_qstr(data['jac']['dSdy'])}",
        f"gs_jac_ab {_qstr(data['gs_ab'])}",
        f"gs_jac_b2 {_qstr(data['gs_b2'])}",
        f"gs_jac_ma2 {_qstr(data['gs_ma2'])}",
        f"gs_jac_mab {_qstr(data['gs_mab'])}",
        f"L_at_center {_qstr(data['L_center'])}",
        f"L_at_rightmost {_qstr(data['L_right'])}",
        "L_sign_on_circle -1",
        "n_plus_2_degree 5",
        "n_plus_2_rdot r^3*(rho^2-r^2)",
        "untranslated_origin_eq 1",
        "untranslated_line_through_origin_hits_circle 1",
        "gs_ab_at_untranslated_origin 0 0",
        f"Pt_nterms {data['Pt'].nterms()}",
        f"Qt_nterms {data['Qt'].nterms()}",
        f"R_nterms {data['R'].nterms()}",
        f"S_nterms {data['S'].nterms()}",
        f"n2F_nterms {data['n2F'].nterms()}",
        f"n2G_nterms {data['n2G'].nterms()}",
        *dump_mons("Pt", data["Pt"]),
        *dump_mons("Qt", data["Qt"]),
        *dump_mons("R", data["R"]),
        *dump_mons("S", data["S"]),
        *dump_int_mons("P4t", data["p4t"]),
        *dump_int_mons("Q4t", data["q4t"]),
        *dump_mons("n2F", data["n2F"]),
        *dump_mons("n2G", data["n2G"]),
    ]


def build_core(data: dict) -> dict:
    return {
        "schema": "hilbert16-kk-plus-one-core/v1",
        "claim": (
            "Translate the radial cubic at p=(2,0), multiply by the line "
            "4x-15y, and prove that line misses the translated circle. "
            "The translated circle remains a periodic orbit of the "
            "degree-4 product. Not two hyperbolic cycles and not a "
            "bound on H(n)."
        ),
        "hn_moved": False,
        "imagined_two_cycles": False,
        "hopf_cycles_written": False,
        "cycles_proved": 1,
        "degree": 4,
        "rho2": "1/4",
        "translate_p": [2, 0],
        "Pt00": "-15/2",
        "Qt00": "-2",
        "a": "2",
        "b": "-15/2",
        "line": "4x-15y",
        "line_misses_circle": True,
        "miss_inequality": "8/sqrt(241) > 1/2",
        "miss_cleared": "4*8^2-241=15",
        "circle_line_disc": "-54000",
        "jac_det": "0",
        "jac_trace": "0",
        "n_plus_2_degree": 5,
        "what_this_is_not": [
            "not a dent of H(n)",
            "not two hyperbolic cycles",
            "not an explicit Hopf perturbation",
            "not H(4) >= 2 as a published improvement",
        ],
    }


def build_identities(data: dict) -> dict:
    return {
        "schema": "hilbert16-kk-plus-one-identities/v1",
        "variables": list(XY),
        "P": data["P"].to_terms(),
        "Q": data["Q"].to_terms(),
        "Pt": data["Pt"].to_terms(),
        "Qt": data["Qt"].to_terms(),
        "L": data["L"].to_terms(),
        "R": data["R"].to_terms(),
        "S": data["S"].to_terms(),
        "n2F": data["n2F"].to_terms(),
        "n2G": data["n2G"].to_terms(),
        "P4t": [
            {"coeff": str(c), **({"x": i} if i else {}), **({"y": j} if j else {})}
            for _, i, j, c in sorted((i + j, i, j, c) for (i, j), c in data["p4t"].items())
        ],
        "Q4t": [
            {"coeff": str(c), **({"x": i} if i else {}), **({"y": j} if j else {})}
            for _, i, j, c in sorted((i + j, i, j, c) for (i, j), c in data["q4t"].items())
        ],
        "jacobian_L": {
            "dRdx": _qstr(data["jac"]["dRdx"]),
            "dRdy": _qstr(data["jac"]["dRdy"]),
            "dSdx": _qstr(data["jac"]["dSdx"]),
            "dSdy": _qstr(data["jac"]["dSdy"]),
            "det": "0",
            "trace": "0",
        },
        "gs_display": {
            "ab": _qstr(data["gs_ab"]),
            "b2": _qstr(data["gs_b2"]),
            "minus_a2": _qstr(data["gs_ma2"]),
            "minus_ab": _qstr(data["gs_mab"]),
        },
        "miss": {
            "dist_num": data["dist_num"],
            "dist_den_sq": data["dist_den_sq"],
            "miss_cleared": data["miss_cleared"],
            "circle_line_a": data["qa"],
            "circle_line_b": data["qb"],
            "circle_line_c": data["qc"],
            "circle_line_disc": data["disc"],
        },
    }


def check_core(payload: dict) -> None:
    if payload.get("hn_moved") is not False:
        raise AssertionError("core must not claim that H(n) moved")
    if payload.get("imagined_two_cycles") is not False:
        raise AssertionError("must not claim two cycles")
    if payload.get("hopf_cycles_written") is not False:
        raise AssertionError("must not claim a written Hopf cycle")
    if payload.get("cycles_proved") != 1:
        raise AssertionError("exactly one periodic orbit is proved")
    if payload.get("degree") != 4:
        raise AssertionError("degree")
    if payload.get("line") != "4x-15y":
        raise AssertionError("line")
    if payload.get("line_misses_circle") is not True:
        raise AssertionError("miss")
    if payload.get("Pt00") != "-15/2" or payload.get("Qt00") != "-2":
        raise AssertionError("translated origin")


def check_identities(payload: dict, data: dict) -> None:
    _require_match(payload["Pt"], data["Pt"], "cert Pt")
    _require_match(payload["Qt"], data["Qt"], "cert Qt")
    _require_match(payload["R"], data["R"], "cert R")
    _require_match(payload["S"], data["S"], "cert S")
    _require_match(payload["L"], data["L"], "cert L")
    _require_match(payload["n2F"], data["n2F"], "cert n2F")
    if payload["jacobian_L"]["det"] != "0" or payload["jacobian_L"]["trace"] != "0":
        raise AssertionError("cert jac")
    if payload["miss"]["miss_cleared"] != 15:
        raise AssertionError("cert miss")
    if payload["miss"]["circle_line_disc"] != -54000:
        raise AssertionError("cert disc")


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
    print("VALID kk-plus-one replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
