#!/usr/bin/env python3
"""Exact polynomial identities for homogeneous and quasi-homogeneous fields.

A homogeneous planar field of degree n does not have n isolated
periodic orbits. Scaling-equivariance and the polar forms

    r * rdot = xP + yQ = F,     r^2 * thetadot = xQ - yP = G

are polynomial identities after clearing the radius (F and G are
homogeneous of degree n+1). Unperturbed homogeneous fields, and
the unperturbed weight-(1,2) center, have zero isolated periodic
orbits. Not a bound on H(n).

A second, independent check is verify.rs (BTreeMap expansion plus
integer-box evaluation of the concrete residuals).
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
        self.n = len(variables)
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
        idx = variables.index(name)
        exp = [0] * len(variables)
        exp[idx] = 1
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
                mon = mon * (factor ** power)
            out = out + mon
        return out

    def subst_xy(self, xnew: "Poly", ynew: "Poly") -> "Poly":
        return self.subst({"x": xnew, "y": ynew})

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
        if "coeff" in self.variables:
            raise ValueError("variable name 'coeff' collides with the term schema")
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
            if "coeff" not in item:
                raise ValueError(f"term missing coeff: {item}")
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


HOMOG2_VARS = ("x", "y", "lam", "a20", "a11", "a02", "b20", "b11", "b02")
HOMOG3_VARS = ("x", "y", "lam", "a30", "a21", "a12", "a03", "b30", "b21", "b12", "b03")
XY_VARS = ("x", "y")
SCALE_VARS = ("x", "y", "lam")
QH_VARS = ("x", "y")
QH_W_VARS = ("x", "y", "lam")


def _radial_angular(variables: tuple[str, ...], p: Poly, q: Poly) -> tuple[Poly, Poly]:
    x, y = V(variables, "x"), V(variables, "y")
    return x * p + y * q, x * q - y * p


def _scale_xy(variables: tuple[str, ...], weight_y: int = 1) -> tuple[Poly, Poly]:
    lam, x, y = V(variables, "lam"), V(variables, "x"), V(variables, "y")
    return lam * x, (lam ** weight_y) * y


def homog2() -> dict[str, Poly]:
    vs = HOMOG2_VARS
    x, y = V(vs, "x"), V(vs, "y")
    a20, a11, a02 = (V(vs, n) for n in ("a20", "a11", "a02"))
    b20, b11, b02 = (V(vs, n) for n in ("b20", "b11", "b02"))
    p = a20 * (x ** 2) + a11 * x * y + a02 * (y ** 2)
    q = b20 * (x ** 2) + b11 * x * y + b02 * (y ** 2)
    f, g = _radial_angular(vs, p, q)
    xs, ys = _scale_xy(vs)
    lam = V(vs, "lam")
    return {
        "P": p,
        "Q": q,
        "F": f,
        "G": g,
        "P_scaled_diff": p.subst_xy(xs, ys) - (lam ** 2) * p,
        "Q_scaled_diff": q.subst_xy(xs, ys) - (lam ** 2) * q,
        "F_scaled_diff": f.subst_xy(xs, ys) - (lam ** 3) * f,
        "G_scaled_diff": g.subst_xy(xs, ys) - (lam ** 3) * g,
    }


def homog3() -> dict[str, Poly]:
    vs = HOMOG3_VARS
    x, y = V(vs, "x"), V(vs, "y")
    a30, a21, a12, a03 = (V(vs, n) for n in ("a30", "a21", "a12", "a03"))
    b30, b21, b12, b03 = (V(vs, n) for n in ("b30", "b21", "b12", "b03"))
    p = a30 * (x ** 3) + a21 * (x ** 2) * y + a12 * x * (y ** 2) + a03 * (y ** 3)
    q = b30 * (x ** 3) + b21 * (x ** 2) * y + b12 * x * (y ** 2) + b03 * (y ** 3)
    f, g = _radial_angular(vs, p, q)
    xs, ys = _scale_xy(vs)
    lam = V(vs, "lam")
    return {
        "P": p,
        "Q": q,
        "F": f,
        "G": g,
        "P_scaled_diff": p.subst_xy(xs, ys) - (lam ** 3) * p,
        "Q_scaled_diff": q.subst_xy(xs, ys) - (lam ** 3) * q,
        "F_scaled_diff": f.subst_xy(xs, ys) - (lam ** 4) * f,
        "G_scaled_diff": g.subst_xy(xs, ys) - (lam ** 4) * g,
    }


def circles() -> dict[str, Poly]:
    """Homogeneous cubic with F ≡ 0: every circle about 0 is periodic."""
    vs = XY_VARS
    x, y = V(vs, "x"), V(vs, "y")
    r2 = x * x + y * y
    p = -(y * r2)
    q = x * r2
    f, g = _radial_angular(vs, p, q)
    g_claimed = r2 * r2
    return {
        "P": p,
        "Q": q,
        "F": f,
        "G": g,
        "G_claimed": g_claimed,
        "G_diff": g - g_claimed,
    }


def rays() -> dict[str, Poly]:
    """Homogeneous quadratic with F ≢ 0: invariant rays, not cycles."""
    vs = XY_VARS
    x, y = V(vs, "x"), V(vs, "y")
    p = x * x
    q = y * y
    f, g = _radial_angular(vs, p, q)
    g_factored = x * y * (y - x)
    zero = C(vs, 0)
    ray_x0 = p.subst({"x": zero})
    ray_y0 = q.subst({"y": zero})
    ray_yx = (p - q).subst({"y": x})
    f_on_antidiag = f.subst({"y": -x})
    # Normal to x+y=0 is (1,1); P+Q on that line is 2x^2 ≢ 0.
    not_invariant = (p + q).subst({"y": -x})
    return {
        "P": p,
        "Q": q,
        "F": f,
        "G": g,
        "G_factored": g_factored,
        "G_diff": g - g_factored,
        "ray_x0": ray_x0,
        "ray_y0": ray_y0,
        "ray_yx": ray_yx,
        "F_zero_line": f_on_antidiag,
        "F_zero_line_normal": not_invariant,
    }


def scale_cubic() -> dict[str, Poly]:
    """Concrete homogeneous cubic: scaled curve satisfies the ODE."""
    vs = SCALE_VARS
    x, y = V(vs, "x"), V(vs, "y")
    p = -(y ** 3)
    q = x ** 3
    xs, ys = _scale_xy(vs)
    lam = V(vs, "lam")
    return {
        "P": p,
        "Q": q,
        "P_scaled_diff": p.subst_xy(xs, ys) - (lam ** 3) * p,
        "Q_scaled_diff": q.subst_xy(xs, ys) - (lam ** 3) * q,
    }


def quasihomogeneous() -> dict[str, Poly]:
    """ẋ = 2y, ẏ = −x³, first integral H = x⁴ + 4y²."""
    vs = QH_VARS
    x, y = V(vs, "x"), V(vs, "y")
    p = C(vs, 2) * y
    q = -(x ** 3)
    h = (x ** 4) + C(vs, 4) * (y ** 2)
    dhdt = h.dvar("x") * p + h.dvar("y") * q
    return {"H": h, "Hx": h.dvar("x"), "Hy": h.dvar("y"), "P": p, "Q": q, "dHdt": dhdt}


def quasihomogeneous_weight() -> dict[str, Poly]:
    vs = QH_W_VARS
    x, y = V(vs, "x"), V(vs, "y")
    p = C(vs, 2) * y
    q = -(x ** 3)
    h = (x ** 4) + C(vs, 4) * (y ** 2)
    xs, ys = _scale_xy(vs, weight_y=2)
    lam = V(vs, "lam")
    return {
        "P": p,
        "Q": q,
        "H": h,
        "P_weight_diff": p.subst_xy(xs, ys) - (lam ** 2) * p,
        "Q_weight_diff": q.subst_xy(xs, ys) - (lam ** 3) * q,
        "H_weight_diff": h.subst_xy(xs, ys) - (lam ** 4) * h,
    }


def build_certificate() -> dict:
    h2 = homog2()
    h3 = homog3()
    circ = circles()
    r = rays()
    sc = scale_cubic()
    qh = quasihomogeneous()
    qw = quasihomogeneous_weight()
    return {
        "schema": "hilbert16-f-homogeneous/v1",
        "claim": (
            "unperturbed homogeneous and quasi-homogeneous planar fields "
            "have zero isolated periodic orbits; not a bound on H(n)"
        ),
        "homog2": {
            "variables": list(HOMOG2_VARS),
            "P": h2["P"].to_terms(),
            "Q": h2["Q"].to_terms(),
            "F": h2["F"].to_terms(),
            "G": h2["G"].to_terms(),
            "P_scaled_diff": h2["P_scaled_diff"].to_terms(),
            "Q_scaled_diff": h2["Q_scaled_diff"].to_terms(),
            "F_scaled_diff": h2["F_scaled_diff"].to_terms(),
            "G_scaled_diff": h2["G_scaled_diff"].to_terms(),
        },
        "homog3": {
            "variables": list(HOMOG3_VARS),
            "P": h3["P"].to_terms(),
            "Q": h3["Q"].to_terms(),
            "F": h3["F"].to_terms(),
            "G": h3["G"].to_terms(),
            "P_scaled_diff": h3["P_scaled_diff"].to_terms(),
            "Q_scaled_diff": h3["Q_scaled_diff"].to_terms(),
            "F_scaled_diff": h3["F_scaled_diff"].to_terms(),
            "G_scaled_diff": h3["G_scaled_diff"].to_terms(),
        },
        "circles": {
            "variables": list(XY_VARS),
            "P": circ["P"].to_terms(),
            "Q": circ["Q"].to_terms(),
            "F": circ["F"].to_terms(),
            "G": circ["G"].to_terms(),
            "G_claimed": circ["G_claimed"].to_terms(),
        },
        "rays": {
            "variables": list(XY_VARS),
            "P": r["P"].to_terms(),
            "Q": r["Q"].to_terms(),
            "F": r["F"].to_terms(),
            "G": r["G"].to_terms(),
            "G_factored": r["G_factored"].to_terms(),
            "ray_x0": r["ray_x0"].to_terms(),
            "ray_y0": r["ray_y0"].to_terms(),
            "ray_yx": r["ray_yx"].to_terms(),
            "F_zero_line": r["F_zero_line"].to_terms(),
            "F_zero_line_normal": r["F_zero_line_normal"].to_terms(),
        },
        "scale": {
            "variables": list(SCALE_VARS),
            "P": sc["P"].to_terms(),
            "Q": sc["Q"].to_terms(),
            "P_scaled_diff": sc["P_scaled_diff"].to_terms(),
            "Q_scaled_diff": sc["Q_scaled_diff"].to_terms(),
        },
        "quasihomogeneous": {
            "variables": list(QH_VARS),
            "H": qh["H"].to_terms(),
            "Hx": qh["Hx"].to_terms(),
            "Hy": qh["Hy"].to_terms(),
            "P": qh["P"].to_terms(),
            "Q": qh["Q"].to_terms(),
            "dHdt": qh["dHdt"].to_terms(),
        },
        "quasihomogeneous_weight": {
            "variables": list(QH_W_VARS),
            "P_weight_diff": qw["P_weight_diff"].to_terms(),
            "Q_weight_diff": qw["Q_weight_diff"].to_terms(),
            "H_weight_diff": qw["H_weight_diff"].to_terms(),
        },
    }


def _require_zero(poly: Poly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: Poly, right: Poly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(
            f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}"
        )


def _require_nonzero(poly: Poly, label: str) -> None:
    if poly.is_zero():
        raise AssertionError(f"{label} is unexpectedly the zero polynomial")


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    loaded = Poly.from_terms(variables, terms)
    _require_equal(loaded, poly, label)


def check_negative() -> None:
    vs = XY_VARS
    x, y = V(vs, "x"), V(vs, "y")
    circ = circles()
    p_bad = circ["P"] + C(vs, 1)
    radial = x * p_bad + y * circ["Q"]
    if radial.is_zero():
        raise AssertionError("perturbed circle field unexpectedly had F ≡ 0")
    if radial.eval({"x": 1, "y": 0}) == 0:
        raise AssertionError("perturbed F vanished at (1,0)")


def check_integer_box() -> None:
    circ = circles()
    r = rays()
    sc = scale_cubic()
    qh = quasihomogeneous()
    h2 = homog2()
    for x in range(-3, 4):
        for y in range(-3, 4):
            vals = {"x": x, "y": y}
            if circ["F"].eval(vals) != 0:
                raise AssertionError(f"circles F nonzero at {(x, y)}")
            g = circ["G"].eval(vals)
            claimed = (x * x + y * y) ** 2
            if g != claimed:
                raise AssertionError(f"circles G mismatch at {(x, y)}")
            if (x == 0 and y == 0) != (g == 0):
                raise AssertionError(f"circles G zero-set failed at {(x, y)}")
            if qh["dHdt"].eval(vals) != 0:
                raise AssertionError(f"qh dH/dt nonzero at {(x, y)}")
            hval = qh["H"].eval(vals)
            if (x == 0 and y == 0) != (hval == 0):
                raise AssertionError(f"H zero-set failed at {(x, y)}")
            if x == 0 and r["P"].eval(vals) != 0:
                raise AssertionError(f"ray x=0 not invariant at y={y}")
            if y == 0 and r["Q"].eval(vals) != 0:
                raise AssertionError(f"ray y=0 not invariant at x={x}")
            if y == x and r["P"].eval(vals) != r["Q"].eval(vals):
                raise AssertionError(f"ray y=x not invariant at x={x}")
            if r["F"].eval({"x": x, "y": -x}) != 0:
                raise AssertionError(f"F not zero on x+y=0 at x={x}")
            if x != 0 and r["F_zero_line_normal"].eval(vals) == 0:
                raise AssertionError(f"F-zero line unexpectedly invariant at x={x}")
    if r["F"].eval({"x": 1, "y": 0}) == 0:
        raise AssertionError("rays F vanished at (1,0)")
    for x in range(-3, 4):
        for y in range(-3, 4):
            for lam in range(-3, 4):
                vals = {"x": x, "y": y, "lam": lam}
                if sc["P_scaled_diff"].eval(vals) != 0:
                    raise AssertionError(f"scale P residual at {(x, y, lam)}")
                if sc["Q_scaled_diff"].eval(vals) != 0:
                    raise AssertionError(f"scale Q residual at {(x, y, lam)}")
                p_at = sc["P"].eval({"x": lam * x, "y": lam * y, "lam": 0})
                if p_at != (lam ** 3) * sc["P"].eval(vals):
                    raise AssertionError(f"scale P eval identity at {(x, y, lam)}")
                q_at = sc["Q"].eval({"x": lam * x, "y": lam * y, "lam": 0})
                if q_at != (lam ** 3) * sc["Q"].eval(vals):
                    raise AssertionError(f"scale Q eval identity at {(x, y, lam)}")
                qw_vals = {"x": x, "y": y, "lam": lam}
                qw = quasihomogeneous_weight()
                if qw["P_weight_diff"].eval(qw_vals) != 0:
                    raise AssertionError(f"qh P weight residual at {(x, y, lam)}")
                if qw["Q_weight_diff"].eval(qw_vals) != 0:
                    raise AssertionError(f"qh Q weight residual at {(x, y, lam)}")
                if qw["H_weight_diff"].eval(qw_vals) != 0:
                    raise AssertionError(f"qh H weight residual at {(x, y, lam)}")
    sample = {
        "x": 2,
        "y": -1,
        "lam": 3,
        "a20": 1,
        "a11": -2,
        "a02": 1,
        "b20": 0,
        "b11": 1,
        "b02": -1,
    }
    p_at = h2["P"].eval({**sample, "x": sample["lam"] * sample["x"], "y": sample["lam"] * sample["y"]})
    if p_at != (sample["lam"] ** 2) * h2["P"].eval(sample):
        raise AssertionError("homog2 sample scale failed")


def check_identities() -> dict[str, int]:
    h2 = homog2()
    for key in ("P_scaled_diff", "Q_scaled_diff", "F_scaled_diff", "G_scaled_diff"):
        _require_zero(h2[key], f"homog2 {key}")

    h3 = homog3()
    for key in ("P_scaled_diff", "Q_scaled_diff", "F_scaled_diff", "G_scaled_diff"):
        _require_zero(h3[key], f"homog3 {key}")

    circ = circles()
    _require_zero(circ["F"], "circles F")
    _require_zero(circ["G_diff"], "circles G claimed")
    _require_nonzero(circ["G"], "circles G")

    r = rays()
    _require_nonzero(r["F"], "rays F")
    _require_zero(r["G_diff"], "rays G factor")
    _require_zero(r["ray_x0"], "ray x=0")
    _require_zero(r["ray_y0"], "ray y=0")
    _require_zero(r["ray_yx"], "ray y=x")
    _require_zero(r["F_zero_line"], "F zero line")
    _require_nonzero(r["F_zero_line_normal"], "F zero line normal")

    sc = scale_cubic()
    _require_zero(sc["P_scaled_diff"], "scale cubic P")
    _require_zero(sc["Q_scaled_diff"], "scale cubic Q")

    qh = quasihomogeneous()
    _require_zero(qh["dHdt"], "qh dH/dt")

    qw = quasihomogeneous_weight()
    _require_zero(qw["P_weight_diff"], "qh P weight")
    _require_zero(qw["Q_weight_diff"], "qh Q weight")
    _require_zero(qw["H_weight_diff"], "qh H weight")

    check_negative()
    check_integer_box()

    return {
        "homog2_P": len(h2["P"].terms),
        "homog2_Q": len(h2["Q"].terms),
        "homog2_F": len(h2["F"].terms),
        "homog2_G": len(h2["G"].terms),
        "homog3_P": len(h3["P"].terms),
        "homog3_Q": len(h3["Q"].terms),
        "homog3_F": len(h3["F"].terms),
        "homog3_G": len(h3["G"].terms),
        "circles_F": len(circ["F"].terms),
        "circles_G": len(circ["G"].terms),
        "rays_F": len(r["F"].terms),
        "rays_G": len(r["G"].terms),
        "f_zero_normal": len(r["F_zero_line_normal"].terms),
        "qh_dHdt": len(qh["dHdt"].terms),
    }


def check_certificate(payload: dict) -> None:
    if payload.get("schema") != "hilbert16-f-homogeneous/v1":
        raise AssertionError("schema mismatch")

    h2 = homog2()
    b = payload["homog2"]
    vs = tuple(b["variables"])
    if vs != HOMOG2_VARS:
        raise AssertionError("homog2 variables")
    for key in ("P", "Q", "F", "G", "P_scaled_diff", "Q_scaled_diff", "F_scaled_diff", "G_scaled_diff"):
        _require_match(vs, b[key], h2[key], f"cert homog2 {key}")

    h3 = homog3()
    b = payload["homog3"]
    vs = tuple(b["variables"])
    if vs != HOMOG3_VARS:
        raise AssertionError("homog3 variables")
    for key in ("P", "Q", "F", "G", "P_scaled_diff", "Q_scaled_diff", "F_scaled_diff", "G_scaled_diff"):
        _require_match(vs, b[key], h3[key], f"cert homog3 {key}")

    circ = circles()
    b = payload["circles"]
    vs = tuple(b["variables"])
    for key, poly in (("P", circ["P"]), ("Q", circ["Q"]), ("F", circ["F"]), ("G", circ["G"]), ("G_claimed", circ["G_claimed"])):
        _require_match(vs, b[key], poly, f"cert circles {key}")

    r = rays()
    b = payload["rays"]
    vs = tuple(b["variables"])
    for key in (
        "P",
        "Q",
        "F",
        "G",
        "G_factored",
        "ray_x0",
        "ray_y0",
        "ray_yx",
        "F_zero_line",
        "F_zero_line_normal",
    ):
        _require_match(vs, b[key], r[key], f"cert rays {key}")

    sc = scale_cubic()
    b = payload["scale"]
    vs = tuple(b["variables"])
    for key in ("P", "Q", "P_scaled_diff", "Q_scaled_diff"):
        _require_match(vs, b[key], sc[key], f"cert scale {key}")

    qh = quasihomogeneous()
    b = payload["quasihomogeneous"]
    vs = tuple(b["variables"])
    for key in ("H", "Hx", "Hy", "P", "Q", "dHdt"):
        _require_match(vs, b[key], qh[key], f"cert qh {key}")

    qw = quasihomogeneous_weight()
    b = payload["quasihomogeneous_weight"]
    vs = tuple(b["variables"])
    for key in ("P_weight_diff", "Q_weight_diff", "H_weight_diff"):
        _require_match(vs, b[key], qw[key], f"cert qh-weight {key}")


def dump_lines(counts: dict[str, int]) -> list[str]:
    return [
        f"homog2 P terms {counts['homog2_P']}",
        f"homog2 Q terms {counts['homog2_Q']}",
        f"homog2 F terms {counts['homog2_F']}",
        f"homog2 G terms {counts['homog2_G']}",
        "homog2 P scale difference 0",
        "homog2 Q scale difference 0",
        "homog2 F scale difference 0",
        "homog2 G scale difference 0",
        f"homog3 P terms {counts['homog3_P']}",
        f"homog3 Q terms {counts['homog3_Q']}",
        f"homog3 F terms {counts['homog3_F']}",
        f"homog3 G terms {counts['homog3_G']}",
        "homog3 P scale difference 0",
        "homog3 Q scale difference 0",
        "homog3 F scale difference 0",
        "homog3 G scale difference 0",
        f"circles F terms {counts['circles_F']}",
        f"circles G terms {counts['circles_G']}",
        "circles G claimed difference 0",
        f"rays F terms {counts['rays_F']}",
        f"rays G terms {counts['rays_G']}",
        "rays G factor difference 0",
        "ray x=0 residual 0",
        "ray y=0 residual 0",
        "ray y=x residual 0",
        "F zero line residual 0",
        f"F zero line not invariant terms {counts['f_zero_normal']}",
        "scale cubic P difference 0",
        "scale cubic Q difference 0",
        f"qh dHdt terms {counts['qh_dHdt']}",
        "qh H weight difference 0",
        "qh P weight difference 0",
        "qh Q weight difference 0",
        "negative perturbation rejected",
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
    print("VALID homogeneous / quasi-homogeneous identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
