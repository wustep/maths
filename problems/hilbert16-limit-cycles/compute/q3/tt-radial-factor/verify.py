#!/usr/bin/env python3
"""Exact identities for Y = (x^2+y^2) X on the radial cubic.

Imagined: a perturbation of Y is an explicit degree-5 field with
two hyperbolic cycles, hence H(5) >= 2. Not written.

Kept: polar identities for the unperturbed Y, unique positive
periodic orbit r = rho, degree 5, and the comparison that
line-multiplication is degree n+1 while this factor is n+2.
That is H(5) >= 1, not a +1, until a second cycle is certified.

A second check is verify.rs (BTreeMap expansion plus integer-box
evaluation of the polar residuals).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
IDENT_PATH = CERTS / "identities.json"
CORE_PATH = CERTS / "core.json"

POLAR_VARS = ("x", "y", "rho")
RADIAL_VARS = ("r", "rho")
XY_VARS = ("x", "y")
R_VARS = ("r",)


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

    def spatial_degrees(self) -> list[int]:
        ix = self.variables.index("x")
        iy = self.variables.index("y")
        return [exp[ix] + exp[iy] for exp in self.terms]

    def jet_order(self) -> int:
        degs = self.spatial_degrees()
        return min(degs) if degs else -1

    def spatial_degree(self) -> int:
        degs = self.spatial_degrees()
        return max(degs) if degs else -1

    def spatial_part(self, deg: int) -> "Poly":
        ix = self.variables.index("x")
        iy = self.variables.index("y")
        out = Poly.zero(self.variables)
        for exp, coeff in self.terms.items():
            if exp[ix] + exp[iy] == deg:
                out.terms[exp] = coeff
        out._prune()
        return out

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


def _require_zero(poly: Poly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: Poly, right: Poly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(
            f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}"
        )


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    _require_equal(Poly.from_terms(variables, terms), poly, label)


def _require(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(label)


# ---------------------------------------------------------------------------
# Fields
# ---------------------------------------------------------------------------


def radial_cubic(vars: tuple[str, ...]) -> tuple[Poly, Poly]:
    x, y, rho = (V(vars, n) for n in POLAR_VARS)
    r2 = x * x + y * y
    rho2 = rho * rho
    p = y - x * (r2 - rho2)
    q = -x - y * (r2 - rho2)
    return p, q


def radial_factor_field(vars: tuple[str, ...]) -> tuple[Poly, Poly, Poly, Poly, Poly]:
    x, y = V(vars, "x"), V(vars, "y")
    r2 = x * x + y * y
    px, qx = radial_cubic(vars)
    py, qy = r2 * px, r2 * qx
    return px, qx, py, qy, r2


def polar_y() -> dict[str, Poly]:
    vars = POLAR_VARS
    x, y, rho = (V(vars, n) for n in vars)
    _px, _qx, py, qy, r2 = radial_factor_field(vars)
    radial_left = x * py + y * qy
    radial_right = (r2 ** 2) * (rho * rho - r2)
    angular_left = x * qy - y * py
    angular_right = -(r2 ** 2)
    return {
        "PX": _px,
        "QX": _qx,
        "PY": py,
        "QY": qy,
        "r2": r2,
        "radial_left": radial_left,
        "radial_right": radial_right,
        "radial_diff": radial_left - radial_right,
        "angular_left": angular_left,
        "angular_right": angular_right,
        "angular_diff": angular_left - angular_right,
    }


def rdot_factorization() -> dict[str, Poly]:
    r, rho = V(RADIAL_VARS, "r"), V(RADIAL_VARS, "rho")
    left = (r ** 3) * (rho * rho - r * r)
    right = (r ** 3) * (rho - r) * (rho + r)
    return {"rdot": left, "factored": right, "diff": left - right}


def specialized_cleared() -> dict[str, Poly]:
    """4 Y at rho^2 = 1/4, so every identity stays in Z[x, y]."""
    x, y = V(XY_VARS, "x"), V(XY_VARS, "y")
    r2 = x * x + y * y
    # 4P = x + 4y - 4x r2, 4Q = -4x + y - 4y r2
    p4 = x + y.scale(4) - x.scale(4) * r2
    q4 = x.scale(-4) + y - y.scale(4) * r2
    py = r2 * p4
    qy = r2 * q4
    radial_left = x * py + y * qy
    radial_right = (r2 ** 2) * (C(XY_VARS, 1) - r2.scale(4))
    angular_left = x * qy - y * py
    angular_right = -(r2 ** 2).scale(4)
    return {
        "P4": p4,
        "Q4": q4,
        "PY": py,
        "QY": qy,
        "radial_left": radial_left,
        "radial_right": radial_right,
        "radial_diff": radial_left - radial_right,
        "angular_left": angular_left,
        "angular_right": angular_right,
        "angular_diff": angular_left - angular_right,
        "r2": r2,
    }


def specialized_rdot() -> dict[str, Poly]:
    r = V(R_VARS, "r")
    left = (r ** 3) * (C(R_VARS, 1) - (r ** 2).scale(4))
    right = (r ** 3) * (C(R_VARS, 1) - r.scale(2)) * (C(R_VARS, 1) + r.scale(2))
    return {"rdot": left, "factored": right, "diff": left - right}


def line_multiplication() -> dict[str, Poly]:
    vars = POLAR_VARS
    x, y, rho = (V(vars, n) for n in vars)
    px, qx = radial_cubic(vars)
    line = x + y
    pl, ql = line * px, line * qx
    r2 = x * x + y * y
    radial_left = x * pl + y * ql
    radial_right = line * r2 * (rho * rho - r2)
    angular_left = x * ql - y * pl
    angular_right = -line * r2
    return {
        "L": line,
        "PL": pl,
        "QL": ql,
        "radial_left": radial_left,
        "radial_right": radial_right,
        "radial_diff": radial_left - radial_right,
        "angular_left": angular_left,
        "angular_right": angular_right,
        "angular_diff": angular_left - angular_right,
    }


def leading_y() -> dict[str, Poly]:
    vars = POLAR_VARS
    x, y = V(vars, "x"), V(vars, "y")
    _px, _qx, py, qy, r2 = radial_factor_field(vars)
    claimed_p = -(r2 ** 2) * x
    claimed_q = -(r2 ** 2) * y
    return {
        "PY5": py.spatial_part(5),
        "QY5": qy.spatial_part(5),
        "claimed_P": claimed_p,
        "claimed_Q": claimed_q,
        "diff_P": py.spatial_part(5) - claimed_p,
        "diff_Q": qy.spatial_part(5) - claimed_q,
    }


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def field_degree(p: Poly, q: Poly) -> int:
    return max(p.spatial_degree(), q.spatial_degree())


def field_jet(p: Poly, q: Poly) -> int:
    orders = [d for d in (p.jet_order(), q.jet_order()) if d >= 0]
    return min(orders) if orders else -1


def check_origin_box(py: Poly, qy: Poly) -> None:
    for x in range(-2, 3):
        for y in range(-2, 3):
            for rho in range(-2, 3):
                vals = {"x": x, "y": y, "rho": rho}
                pv, qv = py.eval(vals), qy.eval(vals)
                if x == 0 and y == 0:
                    _require(pv == 0 and qv == 0, "Y origin is not an equilibrium")
                elif pv == 0 and qv == 0:
                    raise AssertionError(f"unexpected Y equilibrium at {(x, y, rho)}")


def check_polar_box(diff: Poly) -> None:
    # Degree of the Y polar forms is 6. Vanishing on {-3..3}^3
    # kills every monomial of degree <= 6 in three variables.
    for x in range(-3, 4):
        for y in range(-3, 4):
            for rho in range(-3, 4):
                if diff.eval({"x": x, "y": y, "rho": rho}) != 0:
                    raise AssertionError(f"polar residual nonzero at {(x, y, rho)}")


def check_negative(polar: dict[str, Poly]) -> None:
    x, y, rho = (V(POLAR_VARS, n) for n in POLAR_VARS)
    py_bad = polar["PY"] + C(POLAR_VARS, 1)
    radial = x * py_bad + y * polar["QY"]
    if radial.equals(polar["radial_right"]):
        raise AssertionError("perturbed Y unexpectedly satisfied the radial identity")
    angular = x * polar["QY"] - y * py_bad
    if angular.equals(polar["angular_right"]):
        raise AssertionError("perturbed Y unexpectedly satisfied the angular identity")


def check_identities() -> dict[str, int]:
    polar = polar_y()
    _require_zero(polar["radial_diff"], "Y polar radial")
    _require_zero(polar["angular_diff"], "Y polar angular")
    check_polar_box(polar["radial_diff"])
    check_polar_box(polar["angular_diff"])
    check_origin_box(polar["PY"], polar["QY"])
    check_negative(polar)

    deg_x = field_degree(polar["PX"], polar["QX"])
    deg_y = field_degree(polar["PY"], polar["QY"])
    jet_x = field_jet(polar["PX"], polar["QX"])
    jet_y = field_jet(polar["PY"], polar["QY"])
    _require(deg_x == 3, f"X degree {deg_x}")
    _require(deg_y == 5, f"Y degree {deg_y}")
    _require(jet_x == 1, f"X jet {jet_x}")
    _require(jet_y == 3, f"Y jet {jet_y}")

    radial = rdot_factorization()
    _require_zero(radial["diff"], "rdot_Y factorization")

    spec = specialized_cleared()
    _require_zero(spec["radial_diff"], "cleared radial")
    _require_zero(spec["angular_diff"], "cleared angular")
    spec_deg = field_degree(spec["PY"], spec["QY"])
    _require(spec_deg == 5, f"specialized degree {spec_deg}")
    _require(field_jet(spec["PY"], spec["QY"]) == 3, "specialized jet")

    spec_rdot = specialized_rdot()
    _require_zero(spec_rdot["diff"], "specialized rdot factorization")
    _require(spec_rdot["rdot"].eval({"r": 0}) == 0, "rdot at 0")
    _require(spec_rdot["rdot"].eval({"r": 1}) != 0, "rdot vanished at r=1")
    # r = 1/2 is a root of 1-2r; cleared rdot(1) = 1-4 = -3.
    # 2r-1 divides after the substitution r |-> 2s? Check (2s)^3 (1-4(2s)^2)
    # at s=1/2 is the original; evaluate 16 * rdot at the doubled
    # integer: rdot_cleared(r) = r^3 - 4 r^5, and (1-2r) is a factor.

    line = line_multiplication()
    _require_zero(line["radial_diff"], "line-mult radial")
    _require_zero(line["angular_diff"], "line-mult angular")
    deg_line = field_degree(line["PL"], line["QL"])
    _require(deg_line == 4, f"line-multiplication degree {deg_line}")

    lead = leading_y()
    _require_zero(lead["diff_P"], "leading PY")
    _require_zero(lead["diff_Q"], "leading QY")

    return {
        "deg_x": deg_x,
        "deg_y": deg_y,
        "deg_line": deg_line,
        "jet_x": jet_x,
        "jet_y": jet_y,
        "radial_terms": len(polar["radial_left"].terms),
        "angular_terms": len(polar["angular_left"].terms),
        "spec_p_terms": len(spec["PY"].terms),
        "spec_q_terms": len(spec["QY"].terms),
        "spec_deg": spec_deg,
        "px_terms": len(polar["PX"].terms),
        "py_terms": len(polar["PY"].terms),
    }


def core_payload() -> dict:
    return {
        "schema": "hilbert16-tt-radial-factor/v1",
        "claim": (
            "Y=(x^2+y^2)X on the radial cubic is degree 5 with unique "
            "positive periodic orbit r=rho. That is H(5)>=1, not a +1."
        ),
        "paper": "Gasull-Santana arXiv:2407.13465v2 section 4 remark",
        "record": "Prohens-Torregrosa Nonlinearity 32 (2019) H(5)>=37",
        "hn_moved": False,
        "two_cycles": False,
        "plus_one_certified": False,
        "h5_at_least_1": True,
        "h5_at_least_2": False,
        "dent_of_h5_37": False,
        "unique_positive_orbit": "r=rho",
        "degree_Y": 5,
        "degree_X": 3,
        "degree_line_multiplication": 4,
        "rho2": "1/4",
        "specialized_unique_orbit": "r=1/2",
    }


def build_identities() -> dict:
    polar = polar_y()
    radial = rdot_factorization()
    spec = specialized_cleared()
    spec_rdot = specialized_rdot()
    line = line_multiplication()
    lead = leading_y()
    return {
        "schema": "hilbert16-tt-radial-factor/v1",
        "claim": (
            "polar identities for Y=(x^2+y^2)X; unique positive orbit r=rho; "
            "degree 5; line-multiplication degree 4"
        ),
        "polar": {
            "variables": list(POLAR_VARS),
            "PX": polar["PX"].to_terms(),
            "QX": polar["QX"].to_terms(),
            "PY": polar["PY"].to_terms(),
            "QY": polar["QY"].to_terms(),
            "radial_left": polar["radial_left"].to_terms(),
            "radial_right": polar["radial_right"].to_terms(),
            "angular_left": polar["angular_left"].to_terms(),
            "angular_right": polar["angular_right"].to_terms(),
        },
        "radial_speed": {
            "variables": list(RADIAL_VARS),
            "rdot": radial["rdot"].to_terms(),
            "factored": radial["factored"].to_terms(),
        },
        "specialized": {
            "variables": list(XY_VARS),
            "rho2": "1/4",
            "PY": spec["PY"].to_terms(),
            "QY": spec["QY"].to_terms(),
            "radial_left": spec["radial_left"].to_terms(),
            "radial_right": spec["radial_right"].to_terms(),
            "angular_left": spec["angular_left"].to_terms(),
            "angular_right": spec["angular_right"].to_terms(),
        },
        "specialized_rdot": {
            "variables": list(R_VARS),
            "rdot": spec_rdot["rdot"].to_terms(),
            "factored": spec_rdot["factored"].to_terms(),
        },
        "line_multiplication": {
            "variables": list(POLAR_VARS),
            "L": line["L"].to_terms(),
            "PL": line["PL"].to_terms(),
            "QL": line["QL"].to_terms(),
            "radial_left": line["radial_left"].to_terms(),
            "radial_right": line["radial_right"].to_terms(),
            "angular_left": line["angular_left"].to_terms(),
            "angular_right": line["angular_right"].to_terms(),
        },
        "leading": {
            "variables": list(POLAR_VARS),
            "PY5": lead["PY5"].to_terms(),
            "QY5": lead["QY5"].to_terms(),
            "claimed_P": lead["claimed_P"].to_terms(),
            "claimed_Q": lead["claimed_Q"].to_terms(),
        },
    }


def check_core(payload: dict) -> None:
    _require(payload.get("schema") == "hilbert16-tt-radial-factor/v1", "core schema")
    _require(payload.get("hn_moved") is False, "must not claim H(n) moved")
    _require(payload.get("two_cycles") is False, "must not claim two cycles")
    _require(payload.get("plus_one_certified") is False, "must not claim a +1")
    _require(payload.get("h5_at_least_1") is True, "must record H(5)>=1")
    _require(payload.get("h5_at_least_2") is False, "must not claim H(5)>=2")
    _require(payload.get("dent_of_h5_37") is False, "must not claim a dent of 37")
    _require(payload.get("unique_positive_orbit") == "r=rho", "unique orbit")
    _require(payload.get("degree_Y") == 5, "degree Y")
    _require(payload.get("degree_X") == 3, "degree X")
    _require(payload.get("degree_line_multiplication") == 4, "line-mult degree")
    _require(payload.get("rho2") == "1/4", "rho2")
    _require(payload.get("specialized_unique_orbit") == "r=1/2", "specialized orbit")


def check_identities_cert(payload: dict) -> None:
    _require(payload.get("schema") == "hilbert16-tt-radial-factor/v1", "ident schema")
    polar = polar_y()
    block = payload["polar"]
    variables = tuple(block["variables"])
    _require(variables == POLAR_VARS, "polar variables")
    _require_match(variables, block["PX"], polar["PX"], "cert PX")
    _require_match(variables, block["QX"], polar["QX"], "cert QX")
    _require_match(variables, block["PY"], polar["PY"], "cert PY")
    _require_match(variables, block["QY"], polar["QY"], "cert QY")
    _require_match(variables, block["radial_left"], polar["radial_left"], "cert radial_left")
    _require_match(variables, block["radial_right"], polar["radial_right"], "cert radial_right")
    _require_match(variables, block["angular_left"], polar["angular_left"], "cert angular_left")
    _require_match(variables, block["angular_right"], polar["angular_right"], "cert angular_right")

    radial = rdot_factorization()
    rblock = payload["radial_speed"]
    rvars = tuple(rblock["variables"])
    _require_match(rvars, rblock["rdot"], radial["rdot"], "cert rdot")
    _require_match(rvars, rblock["factored"], radial["factored"], "cert rdot factor")

    spec = specialized_cleared()
    sblock = payload["specialized"]
    svars = tuple(sblock["variables"])
    _require(sblock.get("rho2") == "1/4", "cert specialized rho2")
    _require_match(svars, sblock["PY"], spec["PY"], "cert spec PY")
    _require_match(svars, sblock["QY"], spec["QY"], "cert spec QY")
    _require_match(svars, sblock["radial_left"], spec["radial_left"], "cert spec radial_left")
    _require_match(svars, sblock["radial_right"], spec["radial_right"], "cert spec radial_right")
    _require_match(svars, sblock["angular_left"], spec["angular_left"], "cert spec angular_left")
    _require_match(svars, sblock["angular_right"], spec["angular_right"], "cert spec angular_right")

    spec_rdot = specialized_rdot()
    sr = payload["specialized_rdot"]
    srvars = tuple(sr["variables"])
    _require_match(srvars, sr["rdot"], spec_rdot["rdot"], "cert spec rdot")
    _require_match(srvars, sr["factored"], spec_rdot["factored"], "cert spec rdot factor")

    line = line_multiplication()
    lblock = payload["line_multiplication"]
    lvars = tuple(lblock["variables"])
    _require_match(lvars, lblock["L"], line["L"], "cert L")
    _require_match(lvars, lblock["PL"], line["PL"], "cert PL")
    _require_match(lvars, lblock["QL"], line["QL"], "cert QL")
    _require_match(lvars, lblock["radial_left"], line["radial_left"], "cert L radial_left")
    _require_match(lvars, lblock["radial_right"], line["radial_right"], "cert L radial_right")
    _require_match(lvars, lblock["angular_left"], line["angular_left"], "cert L angular_left")
    _require_match(lvars, lblock["angular_right"], line["angular_right"], "cert L angular_right")

    lead = leading_y()
    leadb = payload["leading"]
    leadvars = tuple(leadb["variables"])
    _require_match(leadvars, leadb["PY5"], lead["PY5"], "cert PY5")
    _require_match(leadvars, leadb["QY5"], lead["QY5"], "cert QY5")
    _require_match(leadvars, leadb["claimed_P"], lead["claimed_P"], "cert leading P")
    _require_match(leadvars, leadb["claimed_Q"], lead["claimed_Q"], "cert leading Q")


def dump_lines(counts: dict[str, int]) -> list[str]:
    return [
        f"X degree {counts['deg_x']}",
        f"Y degree {counts['deg_y']}",
        f"line-multiplication degree {counts['deg_line']}",
        f"radial-factor degree {counts['deg_y']}",
        f"polar Y radial terms {counts['radial_terms']} difference 0",
        f"polar Y angular terms {counts['angular_terms']} difference 0",
        "rdot_Y r^3 (rho^2-r^2)",
        "rdot_Y factored r^3 (rho-r)(rho+r) difference 0",
        "unique positive orbit r=rho",
        f"origin X jet {counts['jet_x']}",
        f"origin Y jet {counts['jet_y']}",
        f"specialized rho2=1/4 P terms {counts['spec_p_terms']}",
        f"specialized rho2=1/4 Q terms {counts['spec_q_terms']}",
        f"specialized degree {counts['spec_deg']}",
        "specialized unique positive orbit r=1/2",
        "cleared polar radial difference 0",
        "cleared polar angular difference 0",
        "leading Y +(x^2+y^2)^2 (x,y) difference 0",
        "Y origin only integer-box equilibrium",
        "negative perturbation rejected",
        "H(5) >= 1",
        "plus_one certified 0",
        "two cycles 0",
        "dent of H(5)>=37 0",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    counts = check_identities()
    ident = build_identities()
    core = core_payload()
    check_identities_cert(ident)
    check_core(core)

    if args.write_cert:
        CERTS.mkdir(parents=True, exist_ok=True)
        IDENT_PATH.write_text(json.dumps(ident, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        CORE_PATH.write_text(json.dumps(core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {IDENT_PATH}")
        print(f"wrote {CORE_PATH}")

    if not IDENT_PATH.is_file() or not CORE_PATH.is_file():
        raise SystemExit(f"missing certificate under {CERTS}")
    saved_ident = json.loads(IDENT_PATH.read_text(encoding="utf-8"))
    saved_core = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    check_identities_cert(saved_ident)
    check_core(saved_core)
    if saved_ident != ident:
        raise AssertionError("committed identities.json is not the canonical dump")
    if saved_core != core:
        raise AssertionError("committed core.json is not the canonical dump")

    lines = dump_lines(counts)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID tt-radial-factor identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
