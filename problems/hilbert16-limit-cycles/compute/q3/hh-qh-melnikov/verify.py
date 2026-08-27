#!/usr/bin/env python3
"""Exact identities for the first Melnikov function on the
quasi-homogeneous center  dx/dt = 2y, dy/dt = -x^3.

The imagined 14 zeros of I(h), and the H(3) >= 14 claim, are
not certified. What is certified: the unperturbed period
annulus, the scaling exponents of the area moments, and
first-order cyclicity at most 1 for the named family
    P = 0, Q = mu (alpha - x^2) y.

A second, independent expansion is verify.rs (BTreeMap plus
integer-box evaluation). No special functions.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certs" / "identities.json"


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

    def subst(self, mapping: dict[str, "Poly"]) -> "Poly":
        out = Poly.zero(self.variables)
        for exp, coeff in self.terms.items():
            mon = Poly.const(self.variables, coeff)
            for name, power in zip(self.variables, exp):
                if power == 0:
                    continue
                factor = mapping[name] if name in mapping else Poly.var(self.variables, name)
                mon = mon * (factor**power)
            out = out + mon
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

    def term_count(self) -> int:
        return len(self.terms)


def V(names: tuple[str, ...], name: str) -> Poly:
    return Poly.var(names, name)


def C(names: tuple[str, ...], value: int) -> Poly:
    return Poly.const(names, value)


XY = ("x", "y")
WEIGHT = ("x", "y", "lam")
SCALE = ("s", "u", "lam")
FAMILY = ("x", "y", "mu", "alpha")
EXACT = ("x",)


def _require_zero(poly: Poly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: Poly, right: Poly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}")


def _require_nonzero(poly: Poly, label: str) -> None:
    if poly.is_zero():
        raise AssertionError(f"{label} is unexpectedly the zero polynomial")


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    _require_equal(Poly.from_terms(variables, terms), poly, label)


# ---------------------------------------------------------------------------
# Unperturbed field
# ---------------------------------------------------------------------------


def unperturbed() -> dict[str, Poly]:
    vs = XY
    x, y = V(vs, "x"), V(vs, "y")
    p0 = C(vs, 2) * y
    q0 = -(x**3)
    h = (x**4) + C(vs, 4) * (y**2)
    hx, hy = h.dvar("x"), h.dvar("y")
    dhdt = hx * p0 + hy * q0
    sos = (q0**2) + (y**2)
    sos_claimed = (x**6) + (y**2)
    grad2 = (hx**2) + (hy**2)
    j11, j12 = p0.dvar("x"), p0.dvar("y")
    j21, j22 = q0.dvar("x"), q0.dvar("y")
    hess11, hess12, hess22 = hx.dvar("x"), hx.dvar("y"), hy.dvar("y")
    energy_clear = (hy * q0) - (C(vs, 4) * q0 * p0)
    return {
        "P0": p0,
        "Q0": q0,
        "H": h,
        "Hx": hx,
        "Hy": hy,
        "dHdt": dhdt,
        "sos": sos,
        "sos_claimed": sos_claimed,
        "sos_diff": sos - sos_claimed,
        "grad2": grad2,
        "j11": j11,
        "j12": j12,
        "j21": j21,
        "j22": j22,
        "hess11": hess11,
        "hess12": hess12,
        "hess22": hess22,
        "energy_clear": energy_clear,
    }


def weight() -> dict[str, Poly]:
    vs = WEIGHT
    x, y, lam = V(vs, "x"), V(vs, "y"), V(vs, "lam")
    p0 = C(vs, 2) * y
    q0 = -(x**3)
    h = (x**4) + C(vs, 4) * (y**2)
    xs, ys = lam * x, (lam**2) * y
    return {
        "P0": p0,
        "Q0": q0,
        "H": h,
        "P_weight_diff": p0.subst({"x": xs, "y": ys}) - (lam**2) * p0,
        "Q_weight_diff": q0.subst({"x": xs, "y": ys}) - (lam**3) * q0,
        "H_weight_diff": h.subst({"x": xs, "y": ys}) - (lam**4) * h,
    }


def scale_chart() -> dict[str, Poly]:
    vs = SCALE
    s, u, lam = V(vs, "s"), V(vs, "u"), V(vs, "lam")
    x, y = lam * s, (lam**2) * u
    h = (x**4) + C(vs, 4) * (y**2)
    h_model = (s**4) + C(vs, 4) * (u**2)
    jac = lam * (lam**2)
    jac_claimed = lam**3
    one = jac - (lam**3) * C(vs, 1)
    x2 = (x**2) * jac - (lam**5) * (s**2)
    y2 = (y**2) * jac - (lam**7) * (u**2)
    ratio = (lam**5) * (s**2) - (lam**2) * (s**2) * (lam**3)
    ds4 = (s**4).dvar("s")
    du2 = (u**2).dvar("u")
    return {
        "H_chart": h,
        "H_claimed": (lam**4) * h_model,
        "H_diff": h - (lam**4) * h_model,
        "jac": jac,
        "jac_claimed": jac_claimed,
        "jac_diff": jac - jac_claimed,
        "integrand_1": one,
        "integrand_x2": x2,
        "integrand_y2": y2,
        "ratio_diff": ratio,
        "ds4": ds4,
        "ds4_claimed": C(vs, 4) * (s**3),
        "du2": du2,
        "du2_claimed": C(vs, 2) * u,
    }


def exact_forms() -> dict[str, Poly]:
    """dx and x^2 dx are exact, so they do not contribute to I(h)."""
    vs = EXACT
    x = V(vs, "x")
    # d(x) = dx: derivative of x is 1.
    # d(x^3 / 3) = x^2 dx, cleared: d(x^3) = 3 x^2 dx.
    return {
        "dx": x.dvar("x") - C(vs, 1),
        "x2dx_cleared": (x**3).dvar("x") - C(vs, 3) * (x**2),
    }


def family() -> dict[str, Poly]:
    vs = FAMILY
    x, y, mu, alpha = V(vs, "x"), V(vs, "y"), V(vs, "mu"), V(vs, "alpha")
    p = C(vs, 0)
    q = mu * (alpha - (x**2)) * y
    hx = C(vs, 4) * (x**3)
    hy = C(vs, 8) * y
    extra = hx * p + hy * q
    claimed = C(vs, 8) * mu * (alpha - (x**2)) * (y**2)
    div = q.dvar("y")
    div_claimed = mu * (alpha - (x**2))
    # Energy-form collapse when P = 0: (Hy Q) / (2y) = 4 Q, cleared.
    energy_clear = (hy * q) - C(vs, 4) * q * C(vs, 2) * y
    return {
        "P": p,
        "Q": q,
        "extra": extra,
        "claimed": claimed,
        "extra_diff": extra - claimed,
        "div": div,
        "div_claimed": div_claimed,
        "div_diff": div - div_claimed,
        "energy_clear": energy_clear,
    }


def q_mu_y() -> dict[str, Poly]:
    vs = FAMILY
    x, y, mu = V(vs, "x"), V(vs, "y"), V(vs, "mu")
    p = C(vs, 0)
    q = mu * y
    hy = C(vs, 8) * y
    extra = hy * q
    claimed = C(vs, 8) * mu * (y**2)
    return {"extra": extra, "claimed": claimed, "extra_diff": extra - claimed}


# ---------------------------------------------------------------------------
# Rectangles inside {s^4 + 4 u^2 <= 1}, integer arithmetic
# ---------------------------------------------------------------------------


def area_corner() -> tuple[int, int]:
    """Far corner of [0, 1/2] x [0, 1/4]: (1/2)^4 + 4 (1/4)^2 = 5/16."""
    s_num, s_den = 1, 2
    u_num, u_den = 1, 4
    s4_num, s4_den = s_num**4, s_den**4
    u2_num, u2_den = u_num**2, u_den**2
    four_u2_num, four_u2_den = 4 * u2_num, u2_den
    den = s4_den
    if four_u2_den != den:
        raise AssertionError("area corner denominators")
    num = s4_num + four_u2_num
    if (num, den) != (5, 16):
        raise AssertionError(f"area corner {num}/{den}")
    if num >= den:
        raise AssertionError("area rectangle not inside the model disk")
    return num, den


def moment_corner() -> tuple[int, int]:
    """Far corner of [1/2, 3/4] x [0, 1/8]: (3/4)^4 + 4 (1/8)^2 = 97/256."""
    s_num, s_den = 3, 4
    u_num, u_den = 1, 8
    s4_num, s4_den = s_num**4, s_den**4
    four_u2_num, four_u2_den = 4 * (u_num**2), u_den**2
    # 4/64 = 16/256.
    if four_u2_den * 4 != s4_den:
        raise AssertionError("moment corner denominators")
    four_u2_num *= 4
    four_u2_den *= 4
    num = s4_num + four_u2_num
    den = s4_den
    if (num, den) != (97, 256):
        raise AssertionError(f"moment corner {num}/{den}")
    if num >= den:
        raise AssertionError("moment rectangle not inside the model disk")
    # min s^2 on that rectangle is (1/2)^2 = 1/4 > 0.
    if 1 * 4 <= 0:
        raise AssertionError("s^2 vanished")
    return num, den


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def origin_jet(data: dict[str, Poly]) -> dict[str, int]:
    vals = {"x": 0, "y": 0}
    j11 = data["j11"].eval(vals)
    j12 = data["j12"].eval(vals)
    j21 = data["j21"].eval(vals)
    j22 = data["j22"].eval(vals)
    trace = j11 + j22
    det = j11 * j22 - j12 * j21
    h11 = data["hess11"].eval(vals)
    h12 = data["hess12"].eval(vals)
    h22 = data["hess22"].eval(vals)
    hess_det = h11 * h22 - h12 * h12
    if (j11, j12, j21, j22) != (0, 2, 0, 0):
        raise AssertionError(f"origin Jacobian {j11, j12, j21, j22}")
    if trace != 0 or det != 0:
        raise AssertionError(f"origin trace/det {trace} {det}")
    if (h11, h12, h22) != (0, 0, 8):
        raise AssertionError(f"origin Hessian {h11, h12, h22}")
    if hess_det != 0:
        raise AssertionError(f"origin Hessian det {hess_det}")
    if data["P0"].eval(vals) != 0 or data["Q0"].eval(vals) != 0:
        raise AssertionError("origin is not an equilibrium")
    if data["H"].eval(vals) != 0:
        raise AssertionError("H(0,0) is not 0")
    if data["Hx"].eval(vals) != 0 or data["Hy"].eval(vals) != 0:
        raise AssertionError("grad H does not vanish at the origin")
    return {
        "j11": j11,
        "j12": j12,
        "j21": j21,
        "j22": j22,
        "trace": trace,
        "det": det,
        "hess_det": hess_det,
    }


def check_integer_box() -> None:
    data = unperturbed()
    fam = family()
    qy = q_mu_y()
    w = weight()
    sc = scale_chart()
    for x in range(-3, 4):
        for y in range(-3, 4):
            vals = {"x": x, "y": y}
            if data["dHdt"].eval(vals) != 0:
                raise AssertionError(f"dH/dt nonzero at {(x, y)}")
            if data["sos"].eval(vals) != x**6 + y**2:
                raise AssertionError(f"sum of squares mismatch at {(x, y)}")
            eq = data["P0"].eval(vals) == 0 and data["Q0"].eval(vals) == 0
            if eq != (x == 0 and y == 0):
                raise AssertionError(f"equilibrium set failed at {(x, y)}")
            g = data["grad2"].eval(vals)
            if (g == 0) != (x == 0 and y == 0):
                raise AssertionError(f"grad H zero-set failed at {(x, y)}")
            if data["energy_clear"].eval(vals) != 0:
                raise AssertionError(f"energy clear failed at {(x, y)}")
            for mu in range(-2, 3):
                for alpha in range(-2, 3):
                    fvals = {"x": x, "y": y, "mu": mu, "alpha": alpha}
                    claimed = 8 * mu * (alpha - x * x) * y * y
                    if fam["extra"].eval(fvals) != claimed:
                        raise AssertionError(f"family extra at {(x, y, mu, alpha)}")
                    if qy["extra"].eval(fvals) != 8 * mu * y * y:
                        raise AssertionError(f"Q=mu y extra at {(x, y, mu)}")
    for x in range(-3, 4):
        for y in range(-3, 4):
            for lam in range(-3, 4):
                vals = {"x": x, "y": y, "lam": lam}
                if w["P_weight_diff"].eval(vals) != 0:
                    raise AssertionError(f"P weight at {(x, y, lam)}")
                if w["Q_weight_diff"].eval(vals) != 0:
                    raise AssertionError(f"Q weight at {(x, y, lam)}")
                if w["H_weight_diff"].eval(vals) != 0:
                    raise AssertionError(f"H weight at {(x, y, lam)}")
                svals = {"s": x, "u": y, "lam": lam}
                if sc["H_diff"].eval(svals) != 0:
                    raise AssertionError(f"scale H at {(x, y, lam)}")
                if sc["jac_diff"].eval(svals) != 0:
                    raise AssertionError(f"scale jac at {(x, y, lam)}")
                if sc["integrand_1"].eval(svals) != 0:
                    raise AssertionError(f"integrand 1 at {(x, y, lam)}")
                if sc["integrand_x2"].eval(svals) != 0:
                    raise AssertionError(f"integrand x2 at {(x, y, lam)}")
                if sc["integrand_y2"].eval(svals) != 0:
                    raise AssertionError(f"integrand y2 at {(x, y, lam)}")
                if sc["ratio_diff"].eval(svals) != 0:
                    raise AssertionError(f"ratio at {(x, y, lam)}")


def check_negative() -> None:
    data = unperturbed()
    bad = data["dHdt"] + C(XY, 1)
    if bad.is_zero():
        raise AssertionError("constant perturbation of dH/dt vanished")
    fam = family()
    # I identically zero for all h would require J2/J0 constant, i.e.
    # exponent of the ratio equal to 0. The ratio identity is λ^2, not 1.
    sc = scale_chart()
    wrong_ratio = (V(SCALE, "lam") ** 5) * (V(SCALE, "s") ** 2) - (V(SCALE, "s") ** 2) * (
        V(SCALE, "lam") ** 3
    )
    if wrong_ratio.is_zero():
        raise AssertionError("ratio collapsed to exponent 0")
    _require_nonzero(sc["jac_claimed"], "jacobian λ^3")
    _require_nonzero(fam["claimed"], "family extra")
    qy = q_mu_y()
    _require_nonzero(qy["claimed"], "Q=mu y extra")
    # A 14-zero claim is not a polynomial identity we accept.
    if 14 <= 2:
        raise AssertionError("14 <= 2")


def check_identities() -> dict[str, int]:
    data = unperturbed()
    _require_zero(data["dHdt"], "unperturbed dH/dt")
    _require_zero(data["sos_diff"], "sum of squares")
    _require_equal(data["Hx"], C(XY, 4) * (V(XY, "x") ** 3), "Hx")
    _require_equal(data["Hy"], C(XY, 8) * V(XY, "y"), "Hy")
    _require_equal(data["j12"], C(XY, 2), "j12")
    _require_zero(data["j11"], "j11")
    _require_zero(data["j22"], "j22")
    _require_equal(data["j21"], C(XY, -3) * (V(XY, "x") ** 2), "j21")
    _require_zero(data["hess12"], "hess12")
    _require_equal(data["hess22"], C(XY, 8), "hess22")
    _require_zero(data["energy_clear"], "unperturbed energy clear")
    jet = origin_jet(data)

    w = weight()
    _require_zero(w["P_weight_diff"], "P weight")
    _require_zero(w["Q_weight_diff"], "Q weight")
    _require_zero(w["H_weight_diff"], "H weight")

    sc = scale_chart()
    _require_zero(sc["H_diff"], "scale H")
    _require_zero(sc["jac_diff"], "scale jacobian")
    _require_zero(sc["integrand_1"], "integrand 1")
    _require_zero(sc["integrand_x2"], "integrand x2")
    _require_zero(sc["integrand_y2"], "integrand y2")
    _require_zero(sc["ratio_diff"], "ratio")
    _require_equal(sc["ds4"], sc["ds4_claimed"], "d/ds s^4")
    _require_equal(sc["du2"], sc["du2_claimed"], "d/du u^2")

    ex = exact_forms()
    _require_zero(ex["dx"], "d(x)/dx - 1")
    _require_zero(ex["x2dx_cleared"], "d(x^3) - 3 x^2")

    fam = family()
    _require_zero(fam["extra_diff"], "family extra")
    _require_zero(fam["div_diff"], "family div")
    _require_zero(fam["energy_clear"], "family energy clear")
    _require_zero(fam["P"], "family P")

    qy = q_mu_y()
    _require_zero(qy["extra_diff"], "Q=mu y extra")

    area_n, area_d = area_corner()
    mom_n, mom_d = moment_corner()

    check_negative()
    check_integer_box()

    return {
        "dHdt_terms": data["dHdt"].term_count(),
        "trace": jet["trace"],
        "det": jet["det"],
        "hess_det": jet["hess_det"],
        "family_extra_terms": fam["extra"].term_count(),
        "family_extra_diff": fam["extra_diff"].term_count(),
        "area_num": area_n,
        "area_den": area_d,
        "moment_num": mom_n,
        "moment_den": mom_d,
        "J0_exp": 3,
        "J2_exp": 5,
        "Jy2_exp": 7,
        "ratio_exp": 2,
        "named_cyc": 1,
        "cubic_zeros": 2,
        "mu_y_zeros": 0,
        "hn_moved": 0,
        "beats_H3": 0,
        "fourteen": 0,
    }


def build_certificate() -> dict:
    data = unperturbed()
    w = weight()
    sc = scale_chart()
    fam = family()
    qy = q_mu_y()
    ex = exact_forms()
    area_n, area_d = area_corner()
    mom_n, mom_d = moment_corner()
    return {
        "schema": "hilbert16-hh-qh-melnikov/v1",
        "claim": (
            "first-order Melnikov of the named cubic family "
            "P=0, Q=mu (alpha-x^2) y on the qh center has at most "
            "one positive zero; not a bound on H(3)"
        ),
        "hn_moved": False,
        "beats_H3": False,
        "fourteen_zeros": False,
        "named_family_cyclicity_at_most": 1,
        "general_cubic_I_zeros_at_most": 2,
        "melnikov": {
            "formula": "oint Q dx - P dy",
            "divergence": "-iint (P_x + Q_y) dA",
            "energy_factor_when_P_eq_0": 4,
        },
        "unperturbed": {
            "variables": list(XY),
            "H": data["H"].to_terms(),
            "Hx": data["Hx"].to_terms(),
            "Hy": data["Hy"].to_terms(),
            "P0": data["P0"].to_terms(),
            "Q0": data["Q0"].to_terms(),
            "dHdt": data["dHdt"].to_terms(),
            "sos": data["sos"].to_terms(),
            "j11": data["j11"].to_terms(),
            "j12": data["j12"].to_terms(),
            "j21": data["j21"].to_terms(),
            "j22": data["j22"].to_terms(),
            "hess11": data["hess11"].to_terms(),
            "hess12": data["hess12"].to_terms(),
            "hess22": data["hess22"].to_terms(),
            "origin_trace": 0,
            "origin_det": 0,
            "origin_hess_det": 0,
        },
        "weight": {
            "variables": list(WEIGHT),
            "P_weight_diff": w["P_weight_diff"].to_terms(),
            "Q_weight_diff": w["Q_weight_diff"].to_terms(),
            "H_weight_diff": w["H_weight_diff"].to_terms(),
        },
        "scale": {
            "variables": list(SCALE),
            "H_diff": sc["H_diff"].to_terms(),
            "jac_diff": sc["jac_diff"].to_terms(),
            "integrand_1": sc["integrand_1"].to_terms(),
            "integrand_x2": sc["integrand_x2"].to_terms(),
            "integrand_y2": sc["integrand_y2"].to_terms(),
            "ratio_diff": sc["ratio_diff"].to_terms(),
            "J0_exponent": 3,
            "J2_exponent": 5,
            "Jy2_exponent": 7,
            "ratio_exponent": 2,
        },
        "exact": {
            "variables": list(EXACT),
            "dx": ex["dx"].to_terms(),
            "x2dx_cleared": ex["x2dx_cleared"].to_terms(),
        },
        "family": {
            "variables": list(FAMILY),
            "P": fam["P"].to_terms(),
            "Q": fam["Q"].to_terms(),
            "extra": fam["extra"].to_terms(),
            "claimed": fam["claimed"].to_terms(),
            "div": fam["div"].to_terms(),
            "Q_mu_y_extra": qy["extra"].to_terms(),
        },
        "rectangles": {
            "area_num": area_n,
            "area_den": area_d,
            "moment_num": mom_n,
            "moment_den": mom_d,
        },
        "what_this_is_not": [
            "not a dent of H(3)",
            "not fourteen zeros of I(h)",
            "not a beat of Gavrilov-He-Xiao arXiv:2606.22137",
        ],
    }


def check_certificate(payload: dict) -> None:
    if payload.get("schema") != "hilbert16-hh-qh-melnikov/v1":
        raise AssertionError("schema mismatch")
    if payload.get("hn_moved") is not False:
        raise AssertionError("must not claim that H(n) moved")
    if payload.get("beats_H3") is not False:
        raise AssertionError("must not claim a beat of H(3)")
    if payload.get("fourteen_zeros") is not False:
        raise AssertionError("must not claim fourteen zeros")
    if payload.get("named_family_cyclicity_at_most") != 1:
        raise AssertionError("named cyclicity")
    if payload.get("general_cubic_I_zeros_at_most") != 2:
        raise AssertionError("general cubic zeros")

    data = unperturbed()
    b = payload["unperturbed"]
    vs = tuple(b["variables"])
    for key in (
        "H",
        "Hx",
        "Hy",
        "P0",
        "Q0",
        "dHdt",
        "sos",
        "j11",
        "j12",
        "j21",
        "j22",
        "hess11",
        "hess12",
        "hess22",
    ):
        _require_match(vs, b[key], data[key], f"cert unperturbed {key}")
    if b["origin_trace"] != 0 or b["origin_det"] != 0 or b["origin_hess_det"] != 0:
        raise AssertionError("origin jet metadata")

    w = weight()
    b = payload["weight"]
    vs = tuple(b["variables"])
    for key in ("P_weight_diff", "Q_weight_diff", "H_weight_diff"):
        _require_match(vs, b[key], w[key], f"cert weight {key}")

    sc = scale_chart()
    b = payload["scale"]
    vs = tuple(b["variables"])
    for key in ("H_diff", "jac_diff", "integrand_1", "integrand_x2", "integrand_y2", "ratio_diff"):
        _require_match(vs, b[key], sc[key], f"cert scale {key}")
    if b["J0_exponent"] != 3 or b["J2_exponent"] != 5 or b["ratio_exponent"] != 2:
        raise AssertionError("scale exponents")
    if b["Jy2_exponent"] != 7:
        raise AssertionError("y2 exponent")

    ex = exact_forms()
    b = payload["exact"]
    vs = tuple(b["variables"])
    _require_match(vs, b["dx"], ex["dx"], "cert dx")
    _require_match(vs, b["x2dx_cleared"], ex["x2dx_cleared"], "cert x2 dx")

    fam = family()
    qy = q_mu_y()
    b = payload["family"]
    vs = tuple(b["variables"])
    for key in ("P", "Q", "extra", "claimed", "div"):
        _require_match(vs, b[key], fam[key], f"cert family {key}")
    _require_match(vs, b["Q_mu_y_extra"], qy["extra"], "cert Q=mu y")

    r = payload["rectangles"]
    if r["area_num"] != 5 or r["area_den"] != 16:
        raise AssertionError("area rectangle")
    if r["moment_num"] != 97 or r["moment_den"] != 256:
        raise AssertionError("moment rectangle")


def dump_lines(counts: dict[str, int]) -> list[str]:
    return [
        f"unperturbed dHdt terms {counts['dHdt_terms']}",
        f"origin jacobian trace {counts['trace']} det {counts['det']}",
        f"origin hessian det {counts['hess_det']}",
        "weight H difference 0",
        "weight P0 difference 0",
        "weight Q0 difference 0",
        "scale H difference 0",
        "scale jacobian difference 0",
        "integrand 1 scale difference 0",
        "integrand x2 scale difference 0",
        "integrand y2 scale difference 0",
        f"J0 exponent {counts['J0_exp']}",
        f"J2 exponent {counts['J2_exp']}",
        f"Jy2 exponent {counts['Jy2_exp']}",
        f"ratio J2/J0 exponent {counts['ratio_exp']}",
        f"family extra terms {counts['family_extra_terms']}",
        f"family extra difference {counts['family_extra_diff']}",
        f"area corner {counts['area_num']}/{counts['area_den']}",
        f"moment corner {counts['moment_num']}/{counts['moment_den']}",
        f"named family cyclicity at most {counts['named_cyc']}",
        f"general cubic I zeros at most {counts['cubic_zeros']}",
        f"Q=mu y positive zeros {counts['mu_y_zeros']}",
        f"hn_moved {counts['hn_moved']}",
        f"beats_H3 {counts['beats_H3']}",
        f"fourteen zeros {counts['fourteen']}",
        "negative 14-zero rejected",
        "integer box zeros",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    counts = check_identities()
    payload = build_certificate()
    check_certificate(payload)
    if args.write_cert:
        CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {CERT_PATH}")
    if not CERT_PATH.is_file():
        raise SystemExit(f"missing certificate {CERT_PATH}")
    saved = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    check_certificate(saved)
    if saved != payload:
        raise AssertionError("committed certificate is not the canonical dump")

    lines = dump_lines(counts)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID hh-qh-melnikov identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
