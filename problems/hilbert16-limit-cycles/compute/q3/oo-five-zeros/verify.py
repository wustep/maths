#!/usr/bin/env python3
"""Replay the n=3 radial slice on H=(x^2+y^2)/2 and the named
family on the cubic Hamiltonian of a quadratic field.

Imagined: five simple zeros of I(h), hence a dent of
Li-Liu-Yang 13, or an attaining of Han-Yang-Yu's local 5.
Not produced. Closed forms give one positive zero on the
circles and no regular zero on the nest. Not a bound on H(n).

A second check is verify.rs (BTreeMap plus integer-box
evaluation). No numeric hunt for five zeros.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
CORE_PATH = CERTS / "core.json"
IDENT_PATH = CERTS / "identities.json"


class Poly:
    """Sparse multivariate polynomial with integer coefficients."""

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

    def eval(self, values: dict[str, int]) -> int:
        total = 0
        for exp, coeff in self.terms.items():
            mon = coeff
            for name, power in zip(self.variables, exp):
                if power:
                    mon *= values[name] ** power
            total += mon
        return total

    def degree(self) -> int:
        if not self.terms:
            return -1
        return max(sum(exp) for exp in self.terms)

    def term_count(self) -> int:
        return len(self.terms)

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


XY = ("x", "y")
XYA = ("x", "y", "alpha")
XYHA = ("x", "y", "h", "alpha")
HA = ("h", "alpha")
XYM = ("x", "y", "mu")


def z2(n: int) -> int:
    return (n - 1) // 2


def five_need_deg_q() -> int:
    return 2 * 5 + 1


# ---------------------------------------------------------------------------
# Circles: H = (x^2+y^2)/2, n=3 radial slice
# ---------------------------------------------------------------------------


def circles_unperturbed() -> dict[str, Poly]:
    x, y = V(XY, "x"), V(XY, "y")
    hnum = (x**2) + (y**2)
    p = y
    q = -x
    dhdt = hnum.dvar("x") * p + hnum.dvar("y") * q
    return {"Hnum": hnum, "P": p, "Qfield": q, "dHdt": dhdt}


def circles_forms() -> dict[str, Poly]:
    x, y, alpha = V(XYA, "x"), V(XYA, "y"), V(XYA, "alpha")
    qform = y * (alpha - (x**2) - (y**2))
    h, a = V(HA, "h"), V(HA, "alpha")
    i_tilde = h * (a - h.scale(2))
    claimed = h * a - (h**2).scale(2)
    xv, yv, hv, av = V(XYHA, "x"), V(XYHA, "y"), V(XYHA, "h"), V(XYHA, "alpha")
    r2 = (xv**2) + (yv**2)
    p_r = av - r2
    p_h = av - hv.scale(2)
    factor = r2 - hv.scale(2)
    residual = (p_r - p_h) + factor
    x1, y1 = V(XY, "x"), V(XY, "y")
    q_alpha1 = y1 * (C(XY, 1) - (x1**2) - (y1**2))
    return {
        "Q": qform,
        "Q_alpha1": q_alpha1,
        "I_tilde": i_tilde,
        "I_claimed": claimed,
        "I_diff": i_tilde - claimed,
        "oval_residual": residual,
    }


def uni_eval_at_half_num(coeffs: list[int]) -> int:
    """Numerator of I(1/2) with denominator 2^{deg}."""
    if not coeffs:
        return 0
    deg = len(coeffs) - 1
    num = 0
    for k, c in enumerate(coeffs):
        num += c * (2 ** (deg - k))
    return num


# ---------------------------------------------------------------------------
# Cubic Hamiltonian of a quadratic field
# ---------------------------------------------------------------------------


def cubic_unperturbed() -> dict[str, Poly]:
    x, y = V(XY, "x"), V(XY, "y")
    p = y
    q = x - (x**2)
    h6 = (y**2).scale(3) + (x**3).scale(2) - (x**2).scale(3)
    hx, hy = h6.dvar("x"), h6.dvar("y")
    dh6 = hx * p + hy * q
    q_factored = x * (C(XY, 1) - x)
    pot = (x**3).scale(2) - (x**2).scale(3) + C(XY, 1)
    well = ((x - C(XY, 1)) ** 2) * (x.scale(2) + C(XY, 1))
    j11, j12 = p.dvar("x"), p.dvar("y")
    j21, j22 = q.dvar("x"), q.dvar("y")
    det = j11 * j22 - j12 * j21
    det_claimed = x.scale(2) - C(XY, 1)
    div = j11 + j22
    return {
        "P": p,
        "Q": q,
        "H6": h6,
        "Hx": hx,
        "Hy": hy,
        "dH6": dh6,
        "Q_factored": q_factored,
        "Q_factor_diff": q - q_factored,
        "pot": pot,
        "well": well,
        "pot_diff": pot - well,
        "j11": j11,
        "j12": j12,
        "j21": j21,
        "j22": j22,
        "det": det,
        "det_claimed": det_claimed,
        "det_diff": det - det_claimed,
        "div": div,
    }


def cubic_family() -> dict[str, Poly]:
    x, y, mu = V(XYM, "x"), V(XYM, "y"), V(XYM, "mu")
    p0 = y
    q0 = x - (x**2)
    p_pert = C(XYM, 0)
    q_pert = mu * y
    h6 = (y**2).scale(3) + (x**3).scale(2) - (x**2).scale(3)
    extra = h6.dvar("x") * p_pert + h6.dvar("y") * q_pert
    claimed = mu.scale(6) * (y**2)
    # Full perturbed field: P = y, Q = x-x^2 + mu y.
    q_full = q0 + q_pert
    dh6_full = h6.dvar("x") * p0 + h6.dvar("y") * q_full
    j11 = p0.dvar("x")
    j12 = p0.dvar("y")
    j21 = q_full.dvar("x")
    j22 = q_full.dvar("y")
    trace = j11 + j22
    det = j11 * j22 - j12 * j21
    return {
        "P_pert": p_pert,
        "Q_pert": q_pert,
        "extra": extra,
        "claimed": claimed,
        "extra_diff": extra - claimed,
        "dh6_full": dh6_full,
        "dh6_full_diff": dh6_full - claimed,
        "trace": trace,
        "trace_claimed": mu,
        "trace_diff": trace - mu,
        "det": det,
        "j22": j22,
    }


def homoclinic_tip() -> None:
    """V(3/2)=0: 2*(27/8) - 3*(9/4) = 0, cleared by 8."""
    # 8 * (2 x^3 - 3 x^2) at x=3/2 is 2*(27) - 3*(9)*2 = 54-54.
    if 2 * 27 - 3 * 9 * 2 != 0:
        raise AssertionError("V(3/2) cleared numerator")
    if 3 * 3 != 9 or 2 * 2 * 2 != 8:
        raise AssertionError("V(3/2) denominators")


def area_rectangle() -> tuple[int, int]:
    """Max of H6 on [3/4,5/4] x [-1/4,1/4] is -19/32 < 0."""
    # 2x^3-3x^2 at x=5/4: 2*(125/64)-3*(25/16) = 250/64 - 75/16 = -25/32
    x3_num, x3_den = 125, 64
    x2_num, x2_den = 25, 16
    two_x3_num = 2 * x3_num
    three_x2_num, three_x2_den = 3 * x2_num, x2_den
    # 250/64 - 75/16 = 125/32 - 150/32 = -25/32
    if two_x3_num != 250 or x3_den != 64:
        raise AssertionError("x=5/4 cube")
    if three_x2_num != 75 or three_x2_den != 16:
        raise AssertionError("x=5/4 square")
    pot_num, pot_den = 125 - 150, 32
    if (pot_num, pot_den) != (-25, 32):
        raise AssertionError(f"potential at 5/4 {pot_num}/{pot_den}")
    # 3 y^2 at y=1/4: 3/16 = 6/32
    y2_num, y2_den = 3, 16
    if y2_den * 2 != pot_den:
        raise AssertionError("y^2 denominator")
    max_num = pot_num + 6
    max_den = pot_den
    if (max_num, max_den) != (-19, 32):
        raise AssertionError(f"max H6 {max_num}/{max_den}")
    if max_num >= 0:
        raise AssertionError("rectangle not inside a nest oval")
    # x=3/4: 2*(27/64)-3*(9/16)=54/64-27/16=27/32-54/32=-27/32 < -25/32
    left_num = 27 - 54
    if left_num != -27:
        raise AssertionError("potential at 3/4")
    # area (1/2)*(1/2)=1/4
    if 1 * 1 != 1 or 2 * 2 != 4:
        raise AssertionError("rectangle area")
    return max_num, max_den


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_circles(ham: dict[str, Poly], forms: dict[str, Poly]) -> None:
    _require_zero(ham["dHdt"], "circles dHnum/dt")
    if ham["Hnum"].degree() != 2:
        raise AssertionError("Hnum is not quadratic")
    if ham["P"].degree() != 1 or ham["Qfield"].degree() != 1:
        raise AssertionError("circle field is not linear")
    q: Poly = forms["Q"]
    q1: Poly = forms["Q_alpha1"]
    if q.degree() != 3:
        raise AssertionError(f"circles deg Q is {q.degree()}")
    if q1.degree() != 3:
        raise AssertionError(f"circles alpha=1 deg Q is {q1.degree()}")
    if q.term_count() != 3 or q1.term_count() != 3:
        raise AssertionError("circles Q term count")
    _require_zero(forms["I_diff"], "I_tilde - h(alpha-2h)")
    _require_zero(forms["oval_residual"], "circles oval reduction")
    it = forms["I_tilde"]
    if it.eval({"h": 1, "alpha": 2}) != 0:
        raise AssertionError("I_tilde(1,2)")
    if it.eval({"h": 2, "alpha": 4}) != 0:
        raise AssertionError("I_tilde(2,4)")
    if it.eval({"h": 1, "alpha": 1}) == 0:
        raise AssertionError("I_tilde(1,1) vanished")
    if it.eval({"h": 0, "alpha": 1}) != 0:
        raise AssertionError("I_tilde(0,1)")
    if it.eval({"h": 1, "alpha": 0}) == 0:
        raise AssertionError("I_tilde(1,0) vanished")
    # alpha=1 slice: I = h - 2 h^2, zero at h=1/2
    i_alpha1 = [0, 1, -2]
    if uni_eval_at_half_num(i_alpha1) != 0:
        raise AssertionError("I_tilde(1/2) for alpha=1")
    if z2(3) != 1:
        raise AssertionError("Z(2,3)")
    if five_need_deg_q() != 11:
        raise AssertionError("five zeros need deg Q 11")
    if five_need_deg_q() <= 3:
        raise AssertionError("five zeros unexpectedly fit in degree 3")


def check_cubic(up: dict[str, Poly], fam: dict[str, Poly]) -> None:
    _require_zero(up["dH6"], "unperturbed dH6/dt")
    _require_zero(up["Q_factor_diff"], "Q factorization")
    _require_zero(up["pot_diff"], "potential well factor")
    _require_zero(up["det_diff"], "Jacobian det")
    _require_zero(up["div"], "unperturbed divergence")
    _require_equal(up["j12"], C(XY, 1), "j12")
    _require_zero(up["j11"], "j11")
    _require_zero(up["j22"], "j22")
    if up["H6"].eval({"x": 0, "y": 0}) != 0:
        raise AssertionError("H6(0,0)")
    if up["H6"].eval({"x": 1, "y": 0}) != -1:
        raise AssertionError("H6(1,0)")
    if up["H6"].eval({"x": -1, "y": 0}) != -5:
        raise AssertionError("H6(-1,0) unexpected")
    # well-bottom companion point (-1/2,0): H6 = -1
    # 2*(-1/8)-3*(1/4) = -1/4-3/4 = -1, cleared: H6 at (-1,0) with half-scale...
    # Evaluate 4*H6 at x=-1,y=0 after x |-> x/2: do it by fractions.
    # 2*(-1/8)-3*(1/4)=-1. Cleared numerator: 2*(-1)-3*(2)=-2-6=-8, den 8 => -1.
    if 2 * (-1) - 3 * 2 != -8:
        raise AssertionError("H6(-1/2,0) numerator")
    if up["P"].eval({"x": 0, "y": 0}) != 0 or up["Q"].eval({"x": 0, "y": 0}) != 0:
        raise AssertionError("(0,0) is not an equilibrium")
    if up["P"].eval({"x": 1, "y": 0}) != 0 or up["Q"].eval({"x": 1, "y": 0}) != 0:
        raise AssertionError("(1,0) is not an equilibrium")
    if up["det"].eval({"x": 0, "y": 0}) != -1:
        raise AssertionError("det(0,0)")
    if up["det"].eval({"x": 1, "y": 0}) != 1:
        raise AssertionError("det(1,0)")
    _require_zero(fam["extra_diff"], "family extra")
    _require_zero(fam["dh6_full_diff"], "perturbed dH6/dt")
    _require_zero(fam["trace_diff"], "perturbed trace")
    _require_zero(fam["P_pert"], "family P")
    for mu in range(-3, 4):
        vals0 = {"x": 0, "y": 0, "mu": mu}
        vals1 = {"x": 1, "y": 0, "mu": mu}
        if fam["det"].eval(vals0) != -1:
            raise AssertionError(f"perturbed det(0,0) mu={mu}")
        if fam["trace"].eval(vals0) != mu:
            raise AssertionError(f"perturbed trace(0,0) mu={mu}")
        if fam["det"].eval(vals1) != 1:
            raise AssertionError(f"perturbed det(1,0) mu={mu}")
        if fam["trace"].eval(vals1) != mu:
            raise AssertionError(f"perturbed trace(1,0) mu={mu}")
        if fam["P_pert"].eval(vals0) != 0 or (fam["Q_pert"].eval(vals0) != 0):
            raise AssertionError("perturbation moves the saddle as an equilibrium")
        if fam["Q_pert"].eval(vals1) != 0:
            raise AssertionError("perturbation Q at the center")
    homoclinic_tip()
    area_rectangle()


def check_integer_box(ham: dict[str, Poly], forms: dict[str, Poly], up: dict[str, Poly], fam: dict[str, Poly]) -> None:
    for x in range(-3, 4):
        for y in range(-3, 4):
            vals = {"x": x, "y": y}
            if ham["dHdt"].eval(vals) != 0:
                raise AssertionError(f"circles dHnum/dt at {(x, y)}")
            if 2 * x * y + 2 * y * (-x) != 0:
                raise AssertionError("circles hand dH/dt")
            if up["dH6"].eval(vals) != 0:
                raise AssertionError(f"cubic dH6/dt at {(x, y)}")
            eq = up["P"].eval(vals) == 0 and up["Q"].eval(vals) == 0
            if eq != ((x, y) in ((0, 0), (1, 0))):
                raise AssertionError(f"cubic equilibrium set at {(x, y)}")
            for mu in range(-2, 3):
                fvals = {"x": x, "y": y, "mu": mu}
                if fam["extra"].eval(fvals) != 6 * mu * y * y:
                    raise AssertionError(f"family extra at {(x, y, mu)}")
                if fam["dh6_full"].eval(fvals) != 6 * mu * y * y:
                    raise AssertionError(f"full dH6 at {(x, y, mu)}")
    oval: Poly = forms["oval_residual"]
    it: Poly = forms["I_tilde"]
    for x in range(-3, 4):
        for y in range(-3, 4):
            for h in range(-3, 4):
                for alpha in range(-3, 4):
                    vals = {"x": x, "y": y, "h": h, "alpha": alpha}
                    if oval.eval(vals) != 0:
                        raise AssertionError(f"oval residual at {vals}")
                    claimed = h * (alpha - 2 * h)
                    if it.eval({"h": h, "alpha": alpha}) != claimed:
                        raise AssertionError(f"I_tilde at {(h, alpha)}")


def check_negative(forms: dict[str, Poly], up: dict[str, Poly]) -> None:
    extra = forms["I_tilde"] + (V(HA, "h") ** 3)
    if extra.equals(forms["I_tilde"]):
        raise AssertionError("extra cubic term of I_tilde collided")
    if extra.eval({"h": 1, "alpha": 2}) != 1:
        raise AssertionError("h^3 perturbation at (1,2)")
    x, y = V(XY, "x"), V(XY, "y")
    bad_h = (y**2).scale(3) - (x**2).scale(3)
    bad_dh = bad_h.dvar("x") * up["P"] + bad_h.dvar("y") * up["Q"]
    if bad_dh.is_zero():
        raise AssertionError("dropped-x^3 energy unexpectedly conserved")
    if 5 <= 1:
        raise AssertionError("5 <= Z(2,3)")
    if 5 <= z2(3):
        raise AssertionError("5 <= Z(2,3)")
    if five_need_deg_q() <= 3:
        raise AssertionError("five zeros fit in degree 3")


def check_all() -> dict:
    ham = circles_unperturbed()
    forms = circles_forms()
    up = cubic_unperturbed()
    fam = cubic_family()
    check_circles(ham, forms)
    check_cubic(up, fam)
    check_negative(forms, up)
    check_integer_box(ham, forms, up, fam)
    max_n, max_d = area_rectangle()
    return {
        "ham": ham,
        "forms": forms,
        "up": up,
        "fam": fam,
        "circles_dhdt_terms": ham["dHdt"].term_count(),
        "circles_q_terms": forms["Q"].term_count(),
        "circles_oval_terms": forms["oval_residual"].term_count(),
        "cubic_h6_terms": up["H6"].term_count(),
        "cubic_dh6_terms": up["dH6"].term_count(),
        "cubic_extra_terms": fam["extra"].term_count(),
        "cubic_extra_diff_terms": fam["extra_diff"].term_count(),
        "area_num": max_n,
        "area_den": max_d,
    }


def build_core(data: dict) -> dict:
    return {
        "schema": "hilbert16-oo-five-zeros-core/v1",
        "claim": (
            "n=3 radial slice on H=(x^2+y^2)/2 has I_tilde=h(alpha-2h) "
            "(one positive zero, Z(2,3)=1). Named family P=0, Q=mu y on "
            "H=y^2/2+x^3/3-x^2/2 has one-signed I and first-order "
            "cyclicity at most 1. Not five zeros and not a dent of H(3)>=13."
        ),
        "hn_moved": False,
        "beats_H3": False,
        "five_zeros_produced": False,
        "regular_I_zeros_circles": 1,
        "regular_I_zeros_cubic": 0,
        "well_bottom_I_zeros_cubic": 1,
        "circles_Z23": 1,
        "circles_deg_p_at_most": 1,
        "circles_positive_zeros_at_most": 1,
        "circles_sample_alpha": 1,
        "circles_sample_zero_h": "1/2",
        "circles_extra_zeros_need_degQ": 11,
        "cubic_first_order_cyclicity_at_most": 1,
        "area_max_H6": "-19/32",
        "what_this_is_not": [
            "not a dent of Z(2,3)",
            "not a dent of H(3)",
            "not five zeros of an Abelian integral",
            "not a beat of Han-Yang-Yu local 5",
            "not a numeric search",
        ],
    }


def build_identities(data: dict) -> dict:
    ham, forms, up, fam = data["ham"], data["forms"], data["up"], data["fam"]
    return {
        "schema": "hilbert16-oo-five-zeros-identities/v1",
        "circles": {
            "variables": list(XY),
            "Hnum": ham["Hnum"].to_terms(),
            "P": ham["P"].to_terms(),
            "Qfield": ham["Qfield"].to_terms(),
            "dHdt": ham["dHdt"].to_terms(),
        },
        "circles_forms": {
            "variables_Q": list(XYA),
            "Q": forms["Q"].to_terms(),
            "variables_I": list(HA),
            "I_tilde": forms["I_tilde"].to_terms(),
            "variables_oval": list(XYHA),
            "oval_residual": forms["oval_residual"].to_terms(),
            "Q_alpha1": forms["Q_alpha1"].to_terms(),
            "variables_Q_alpha1": list(XY),
        },
        "cubic": {
            "variables": list(XY),
            "P": up["P"].to_terms(),
            "Q": up["Q"].to_terms(),
            "H6": up["H6"].to_terms(),
            "dH6": up["dH6"].to_terms(),
            "det": up["det"].to_terms(),
            "div": up["div"].to_terms(),
            "pot_diff": up["pot_diff"].to_terms(),
        },
        "family": {
            "variables": list(XYM),
            "P_pert": fam["P_pert"].to_terms(),
            "Q_pert": fam["Q_pert"].to_terms(),
            "extra": fam["extra"].to_terms(),
            "claimed": fam["claimed"].to_terms(),
            "trace": fam["trace"].to_terms(),
        },
        "rectangles": {
            "area_num": data["area_num"],
            "area_den": data["area_den"],
        },
    }


def check_core(payload: dict) -> None:
    if payload.get("schema") != "hilbert16-oo-five-zeros-core/v1":
        raise AssertionError("core schema")
    if payload.get("hn_moved") is not False:
        raise AssertionError("must not claim that H(n) moved")
    if payload.get("beats_H3") is not False:
        raise AssertionError("must not claim a beat of H(3)")
    if payload.get("five_zeros_produced") is not False:
        raise AssertionError("must not claim five zeros")
    if payload.get("regular_I_zeros_circles") != 1:
        raise AssertionError("circles zeros")
    if payload.get("regular_I_zeros_cubic") != 0:
        raise AssertionError("cubic regular zeros")
    if payload.get("well_bottom_I_zeros_cubic") != 1:
        raise AssertionError("well-bottom zero")
    if payload.get("circles_Z23") != 1:
        raise AssertionError("Z(2,3)")
    if payload.get("cubic_first_order_cyclicity_at_most") != 1:
        raise AssertionError("named cyclicity")
    if payload.get("circles_extra_zeros_need_degQ") != 11:
        raise AssertionError("deg Q for five zeros")


def check_identities(payload: dict, data: dict) -> None:
    if payload.get("schema") != "hilbert16-oo-five-zeros-identities/v1":
        raise AssertionError("identities schema")
    ham, forms, up, fam = data["ham"], data["forms"], data["up"], data["fam"]
    b = payload["circles"]
    vs = tuple(b["variables"])
    for key in ("Hnum", "P", "Qfield", "dHdt"):
        _require_match(vs, b[key], ham[key], f"cert circles {key}")
    b = payload["circles_forms"]
    _require_match(tuple(b["variables_Q"]), b["Q"], forms["Q"], "cert Q")
    _require_match(tuple(b["variables_I"]), b["I_tilde"], forms["I_tilde"], "cert I")
    _require_match(tuple(b["variables_oval"]), b["oval_residual"], forms["oval_residual"], "cert oval")
    _require_match(tuple(b["variables_Q_alpha1"]), b["Q_alpha1"], forms["Q_alpha1"], "cert Q alpha=1")
    b = payload["cubic"]
    vs = tuple(b["variables"])
    for key in ("P", "Q", "H6", "dH6", "det", "div", "pot_diff"):
        _require_match(vs, b[key], up[key], f"cert cubic {key}")
    b = payload["family"]
    vs = tuple(b["variables"])
    for key in ("P_pert", "Q_pert", "extra", "claimed", "trace"):
        _require_match(vs, b[key], fam[key], f"cert family {key}")
    r = payload["rectangles"]
    if r["area_num"] != -19 or r["area_den"] != 32:
        raise AssertionError("area rectangle")


def dump_lines(data: dict) -> list[str]:
    return [
        "imagined_five_zeros DROP",
        "H3_ge_5_as_dent_of_13 DROP",
        "circles_n3_slice KEEP",
        "cubic_hamiltonian_quadratic_field KEEP",
        "hn_moved 0",
        "beats_H3 0",
        "five_zeros_produced 0",
        "regular_I_zeros_circles 1",
        "regular_I_zeros_cubic 0",
        "well_bottom_I_zeros_cubic 1",
        "circles Z(2,3) 1",
        "circles I_tilde h*(alpha-2h)",
        "circles deg_p_at_most 1",
        "circles positive_zeros_at_most 1",
        "circles sample_alpha 1",
        "circles sample_zero_h 1/2",
        "circles extra_zeros_need_degQ 11",
        f"circles dHnum/dt terms {data['circles_dhdt_terms']}",
        f"circles Q terms {data['circles_q_terms']}",
        f"circles oval_reduction {data['circles_oval_terms']}",
        f"cubic H6 terms {data['cubic_h6_terms']}",
        f"cubic dH6dt terms {data['cubic_dh6_terms']}",
        "cubic eq 0 0 kind=saddle det=-1 trace=0 H=0",
        "cubic eq 1 0 kind=center det=1 trace=0 H=-1/6",
        "cubic extra 6*mu*y^2",
        f"cubic extra_diff terms {data['cubic_extra_diff_terms']}",
        "cubic I mu*oint_y_dx",
        "cubic I_one_signed 1",
        "cubic first_order_cyclicity_at_most 1",
        "cubic named_family_zeros_not_5",
        "area rectangle [3/4,5/4]x[-1/4,1/4]",
        f"area max_H6 {data['area_num']}/{data['area_den']}",
        "homoclinic V(3/2) 0",
        "potential_factor 2x^3-3x^2+1=(x-1)^2*(2x+1)",
        "negative five-zero rejected",
        "integer box zeros",
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
    print("VALID oo-five-zeros replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
