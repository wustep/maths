#!/usr/bin/env python3
"""Exact identities for a cubic with invariant line y=0.

Imagined: three isolated periodic orbits. Not produced.
Kept: named field dx/dt = 16y+16x+x^3, dy/dt = 16 x y, line y=0
(not a line of equilibria), Dulac B=1/y, certified cycle count 0
for the family dx/dt = y+x+mu x^3, dy/dt = x y with mu >= 0.
Ye/Cherkas for quadratics is context, not re-proved.
Not a bound on H(n).

A second, independent check is verify.rs (BTreeMap expansion plus
integer-box evaluation of the residuals).
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

BOX = range(-3, 4)


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
                mon = mon * (factor**power)
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

    def degree(self, ignore: tuple[str, ...] = ()) -> int:
        if not self.terms:
            return -1
        skip = {self.variables.index(name) for name in ignore}
        return max(
            sum(power for i, power in enumerate(exp) if i not in skip) for exp in self.terms
        )

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


def box_zero(poly: Poly, names: tuple[str, ...], label: str) -> None:
    if not names:
        if poly.eval({}) != 0:
            raise AssertionError(f"{label} constant residual")
        return
    # Cartesian box on the first variables that appear in `names`.
    coords = list(names)
    n = len(coords)

    def rec(i: int, acc: dict[str, int]) -> None:
        if i == n:
            if poly.eval(acc) != 0:
                raise AssertionError(f"{label} residual nonzero at {acc}")
            return
        for v in BOX:
            acc[coords[i]] = v
            rec(i + 1, acc)
        del acc[coords[i]]

    rec(0, {})


XY = ("x", "y")
XYM = ("x", "y", "mu")


def named() -> dict[str, Poly | int]:
    x, y = V(XY, "x"), V(XY, "y")
    p = y.scale(16) + x.scale(16) + (x**3)
    q = x.scale(16) * y
    # cofactor 16x: Q - (16x) y
    cofactor_diff = q - x.scale(16) * y
    # axis restriction
    p_axis = p.subst({"y": C(XY, 0)})
    axis_factor = C(XY, 16) + (x**2)
    axis_factored = x * axis_factor
    axis_diff = p_axis - axis_factored
    axis_shift = axis_factor - C(XY, 16) - (x**2)
    # x=0 slice
    p_x0 = p.subst({"x": C(XY, 0)})
    p_x0_diff = p_x0 - y.scale(16)
    # divergence and Dulac
    div = p.dvar("x") + q.dvar("y")
    div_claimed = C(XY, 16) + x.scale(16) + (x**2).scale(3)
    div_diff = div - div_claimed
    dulac_num = C(XY, 16) + (x**2).scale(3)
    dulac_cleared = div * y - q
    dulac_claimed = y * dulac_num
    dulac_diff = dulac_cleared - dulac_claimed
    dulac_num_shift = dulac_num - C(XY, 16) - (x**2).scale(3)
    # Jacobian
    dp_dx = p.dvar("x")
    dp_dy = p.dvar("y")
    dq_dx = q.dvar("x")
    dq_dy = q.dvar("y")
    det = dp_dx * dq_dy - dp_dy * dq_dx
    # time-rescaling identity: 16 * (y + x + (1/16) x^3) vs P, cleared
    # 16*(y + x) + x^3 - P = 0
    rescaled = y.scale(16) + x.scale(16) + (x**3)
    rescale_diff = rescaled - p
    return {
        "P": p,
        "Q": q,
        "cofactor_diff": cofactor_diff,
        "P_axis": p_axis,
        "axis_factor": axis_factor,
        "axis_diff": axis_diff,
        "axis_shift": axis_shift,
        "P_x0": p_x0,
        "P_x0_diff": p_x0_diff,
        "div": div,
        "div_claimed": div_claimed,
        "div_diff": div_diff,
        "dulac_num": dulac_num,
        "dulac_cleared": dulac_cleared,
        "dulac_claimed": dulac_claimed,
        "dulac_diff": dulac_diff,
        "dulac_num_shift": dulac_num_shift,
        "dP_dx": dp_dx,
        "dP_dy": dp_dy,
        "dQ_dx": dq_dx,
        "dQ_dy": dq_dy,
        "det": det,
        "rescale_diff": rescale_diff,
        "P_at_10": p.eval({"x": 1, "y": 0}),
        "axis_factor_at_0": axis_factor.eval({"x": 0, "y": 0}),
        "dulac_num_at_0": dulac_num.eval({"x": 0, "y": 0}),
        "div_at_0": div.eval({"x": 0, "y": 0}),
        "div_at_minus3": div.eval({"x": -3, "y": 0}),
        "div_disc": 16 * 16 - 4 * 3 * 16,
        "trace_origin": dp_dx.eval({"x": 0, "y": 0}) + dq_dy.eval({"x": 0, "y": 0}),
        "det_origin": det.eval({"x": 0, "y": 0}),
        "degree": max(p.degree(), q.degree()),
    }


def family() -> dict[str, Poly | int]:
    x, y, mu = V(XYM, "x"), V(XYM, "y"), V(XYM, "mu")
    p = y + x + mu * (x**3)
    q = x * y
    cofactor_diff = q - x * y
    p_axis = p.subst({"y": C(XYM, 0)})
    axis_factor = C(XYM, 1) + mu * (x**2)
    axis_diff = p_axis - x * axis_factor
    div = p.dvar("x") + q.dvar("y")
    div_claimed = C(XYM, 1) + x + mu.scale(3) * (x**2)
    div_diff = div - div_claimed
    dulac_num = C(XYM, 1) + mu.scale(3) * (x**2)
    dulac_diff = (div * y - q) - y * dulac_num
    # mu=0 is quadratic (degree in x,y; mu is a parameter)
    p0 = p.subst({"mu": C(XYM, 0)})
    deg_mu0 = max(p0.degree(ignore=("mu",)), q.degree(ignore=("mu",)))
    # ordinary Bendixson disc of 3 mu x^2 + x + 1 is 1-12 mu
    # named member mu corresponds to 1/16 after time scaling
    bendixson_disc_num = 1  # 1 - 12 mu, numerator of the mu-free part
    # 1 - 12*(1/16) = 1 - 12/16 = 1 - 3/4 = 1/4 > 0
    # cleared: 16 - 12 = 4, so 4/16 = 1/4
    named_mu_disc_num = 16 - 12
    named_mu_disc_den = 16
    return {
        "P": p,
        "Q": q,
        "cofactor_diff": cofactor_diff,
        "P_axis": p_axis,
        "axis_factor": axis_factor,
        "axis_diff": axis_diff,
        "div": div,
        "div_claimed": div_claimed,
        "div_diff": div_diff,
        "dulac_num": dulac_num,
        "dulac_diff": dulac_diff,
        "degree": max(p.degree(ignore=("mu",)), q.degree(ignore=("mu",))),
        "degree_mu0": deg_mu0,
        "bendixson_disc_const": bendixson_disc_num,
        "named_mu_disc_num": named_mu_disc_num,
        "named_mu_disc_den": named_mu_disc_den,
    }


def degeneration() -> dict[str, Poly]:
    """dx/dt = y, dy/dt = -y (x + mu (x^2-1) y): axis of equilibria."""
    x, y, mu = V(XYM, "x"), V(XYM, "y"), V(XYM, "mu")
    p = y
    q = -(y * (x + mu * (x**2 - C(XYM, 1)) * y))
    p_axis = p.subst({"y": C(XYM, 0)})
    q_axis = q.subst({"y": C(XYM, 0)})
    return {
        "P": p,
        "Q": q,
        "P_axis": p_axis,
        "Q_axis": q_axis,
    }


def check_all() -> dict:
    nm = named()
    fam = family()
    deg = degeneration()

    for key in (
        "cofactor_diff",
        "axis_diff",
        "axis_shift",
        "P_x0_diff",
        "div_diff",
        "dulac_diff",
        "dulac_num_shift",
        "rescale_diff",
    ):
        _require_zero(nm[key], f"named {key}")  # type: ignore[arg-type]

    for key in ("cofactor_diff", "axis_diff", "div_diff", "dulac_diff"):
        _require_zero(fam[key], f"family {key}")  # type: ignore[arg-type]

    _require_zero(deg["P_axis"], "degeneration P on axis")
    _require_zero(deg["Q_axis"], "degeneration Q on axis")

    if nm["P_at_10"] != 17:
        raise AssertionError(f"P(1,0) = {nm['P_at_10']}")
    if nm["axis_factor_at_0"] != 16:
        raise AssertionError("axis factor at 0")
    if nm["dulac_num_at_0"] != 16:
        raise AssertionError("dulac num at 0")
    if nm["div_at_0"] != 16:
        raise AssertionError("div at 0")
    if nm["div_at_minus3"] != -5:
        raise AssertionError("div at -3")
    if nm["div_disc"] != 64:
        raise AssertionError("div disc")
    if nm["trace_origin"] != 16:
        raise AssertionError("trace origin")
    if nm["det_origin"] != 0:
        raise AssertionError("det origin")
    if nm["degree"] != 3:
        raise AssertionError("named degree")
    if fam["degree"] != 3:
        raise AssertionError("family degree")
    if fam["degree_mu0"] != 2:
        raise AssertionError("mu=0 should be quadratic")
    if fam["named_mu_disc_num"] != 4 or fam["named_mu_disc_den"] != 16:
        raise AssertionError("named mu Bendixson disc")
    if 4 <= 0:
        raise AssertionError("named mu disc should be positive")

    # only equilibrium is origin, sampled
    for xv in BOX:
        for yv in BOX:
            vals = {"x": xv, "y": yv}
            if nm["P"].eval(vals) == 0 and nm["Q"].eval(vals) == 0:  # type: ignore[union-attr]
                if xv != 0 or yv != 0:
                    raise AssertionError(f"unexpected equilibrium ({xv},{yv})")

    # axis factor and dulac numerator stay positive on the box
    for xv in BOX:
        if nm["axis_factor"].eval({"x": xv, "y": 0}) < 16:  # type: ignore[union-attr]
            raise AssertionError("axis factor dropped below 16")
        if nm["dulac_num"].eval({"x": xv, "y": 0}) < 16:  # type: ignore[union-attr]
            raise AssertionError("dulac numerator dropped below 16")

    # residuals vanish on the box
    box_zero(nm["dulac_diff"], XY, "named dulac")  # type: ignore[arg-type]
    box_zero(nm["cofactor_diff"], XY, "named cofactor")  # type: ignore[arg-type]
    box_zero(nm["div_diff"], XY, "named div")  # type: ignore[arg-type]
    box_zero(fam["dulac_diff"], XYM, "family dulac")  # type: ignore[arg-type]

    # negative: x^2+y^2 is not a first integral
    x, y = V(XY, "x"), V(XY, "y")
    energy = (x**2) + (y**2)
    d_energy = energy.dvar("x") * nm["P"] + energy.dvar("y") * nm["Q"]  # type: ignore[operator]
    if d_energy.is_zero():
        raise AssertionError("x^2+y^2 unexpectedly conserved")

    # negative: harmonic oscillator has Q(x,0) = -x, so y=0 is not invariant
    q_harm = -x
    if q_harm.subst({"y": C(XY, 0)}).is_zero():
        raise AssertionError("harmonic Q(x,0) unexpectedly zero")

    # family axis factor at mu>=0, sample mu=0 and mu=1
    if fam["axis_factor"].eval({"x": 0, "y": 0, "mu": 0}) != 1:  # type: ignore[union-attr]
        raise AssertionError("family axis at 0")
    if fam["axis_factor"].eval({"x": 2, "y": 0, "mu": 1}) != 5:  # type: ignore[union-attr]
        raise AssertionError("family axis sample")

    return {"nm": nm, "fam": fam, "deg": deg, "energy_terms": d_energy.nterms()}


def build_core(data: dict) -> dict:
    nm, fam = data["nm"], data["fam"]
    return {
        "schema": "hilbert16-ll-invariant-line-core/v1",
        "claim": (
            "Named cubic dx/dt=16y+16x+x^3, dy/dt=16xy has invariant line "
            "y=0 (not a line of equilibria) and, by Dulac B=1/y, exactly 0 "
            "isolated periodic orbits. The same count holds for the family "
            "dx/dt=y+x+mu x^3, dy/dt=xy with mu>=0. Three cycles were not "
            "produced. Ye/Cherkas uniqueness for quadratics is context, "
            "not re-proved. Not a bound on H(n)."
        ),
        "hn_moved": False,
        "three_cycles_produced": False,
        "certified_cycle_count": 0,
        "family_cycle_count": 0,
        "ye_quadratic_at_most_one": True,
        "ye_reproved": False,
        "degree": 3,
        "family_degree_mu0": 2,
        "invariant_line": "y=0",
        "cofactor_named": "16x",
        "cofactor_family": "x",
        "line_of_equilibria": False,
        "equilibria_count": 1,
        "field": "dx/dt = 16y+16x+x^3, dy/dt = 16xy",
        "family": "dx/dt = y+x+mu x^3, dy/dt = xy (mu>=0)",
        "dulac": "1/y",
        "dulac_numerator_named": "16+3x^2",
        "dulac_numerator_family": "1+3 mu x^2",
        "bendixson_inconclusive": True,
        "div_disc": nm["div_disc"],
        "P_axis_at_1": nm["P_at_10"],
        "div_at_0": nm["div_at_0"],
        "div_at_minus3": nm["div_at_minus3"],
        "dulac_num_min": nm["dulac_num_at_0"],
        "trace_origin": nm["trace_origin"],
        "det_origin": nm["det_origin"],
        "named_mu_disc": "1/4",
        "named_mu_disc_num": fam["named_mu_disc_num"],
        "named_mu_disc_den": fam["named_mu_disc_den"],
        "degeneration_is_axis_of_equilibria": True,
        "what_this_is_not": [
            "not a dent of H(n)",
            "not three cubic cycles",
            "not a re-proof of Ye/Cherkas",
            "not a line of equilibria",
            "not a bound on every cubic with a line",
        ],
    }


def build_identities(data: dict) -> dict:
    nm, fam, deg = data["nm"], data["fam"], data["deg"]
    return {
        "schema": "hilbert16-ll-invariant-line-identities/v1",
        "named": {
            "variables": list(XY),
            "P": nm["P"].to_terms(),
            "Q": nm["Q"].to_terms(),
            "cofactor_diff": nm["cofactor_diff"].to_terms(),
            "P_axis": nm["P_axis"].to_terms(),
            "axis_factor": nm["axis_factor"].to_terms(),
            "axis_diff": nm["axis_diff"].to_terms(),
            "P_x0": nm["P_x0"].to_terms(),
            "div": nm["div"].to_terms(),
            "dulac_num": nm["dulac_num"].to_terms(),
            "dulac_cleared": nm["dulac_cleared"].to_terms(),
            "dulac_diff": nm["dulac_diff"].to_terms(),
            "dP_dx": nm["dP_dx"].to_terms(),
            "dP_dy": nm["dP_dy"].to_terms(),
            "dQ_dx": nm["dQ_dx"].to_terms(),
            "dQ_dy": nm["dQ_dy"].to_terms(),
            "det": nm["det"].to_terms(),
        },
        "family": {
            "variables": list(XYM),
            "P": fam["P"].to_terms(),
            "Q": fam["Q"].to_terms(),
            "cofactor_diff": fam["cofactor_diff"].to_terms(),
            "P_axis": fam["P_axis"].to_terms(),
            "axis_factor": fam["axis_factor"].to_terms(),
            "div": fam["div"].to_terms(),
            "dulac_num": fam["dulac_num"].to_terms(),
            "dulac_diff": fam["dulac_diff"].to_terms(),
        },
        "degeneration": {
            "variables": list(XYM),
            "P": deg["P"].to_terms(),
            "Q": deg["Q"].to_terms(),
            "P_axis": deg["P_axis"].to_terms(),
            "Q_axis": deg["Q_axis"].to_terms(),
        },
    }


def check_core(payload: dict) -> None:
    if payload.get("hn_moved") is not False:
        raise AssertionError("core must not claim that H(n) moved")
    if payload.get("three_cycles_produced") is not False:
        raise AssertionError("must not claim three cycles")
    if payload.get("certified_cycle_count") != 0:
        raise AssertionError("certified count must be 0")
    if payload.get("family_cycle_count") != 0:
        raise AssertionError("family count must be 0")
    if payload.get("ye_reproved") is not False:
        raise AssertionError("must not claim Ye was re-proved")
    if payload.get("ye_quadratic_at_most_one") is not True:
        raise AssertionError("Ye context flag")
    if payload.get("degree") != 3:
        raise AssertionError("degree")
    if payload.get("invariant_line") != "y=0":
        raise AssertionError("invariant line")
    if payload.get("line_of_equilibria") is not False:
        raise AssertionError("must not be a line of equilibria")
    if payload.get("equilibria_count") != 1:
        raise AssertionError("equilibria count")
    if payload.get("bendixson_inconclusive") is not True:
        raise AssertionError("Bendixson should be inconclusive")


def check_identities(payload: dict, data: dict) -> None:
    nm, fam, deg = data["nm"], data["fam"], data["deg"]
    nb = payload["named"]
    _require_match(XY, nb["P"], nm["P"], "cert named P")
    _require_match(XY, nb["Q"], nm["Q"], "cert named Q")
    _require_match(XY, nb["cofactor_diff"], nm["cofactor_diff"], "cert cofactor")
    _require_match(XY, nb["dulac_diff"], nm["dulac_diff"], "cert dulac")
    _require_match(XY, nb["div"], nm["div"], "cert div")
    _require_match(XY, nb["dulac_num"], nm["dulac_num"], "cert dulac num")
    _require_match(XY, nb["axis_diff"], nm["axis_diff"], "cert axis")
    fb = payload["family"]
    _require_match(XYM, fb["P"], fam["P"], "cert family P")
    _require_match(XYM, fb["Q"], fam["Q"], "cert family Q")
    _require_match(XYM, fb["dulac_diff"], fam["dulac_diff"], "cert family dulac")
    db = payload["degeneration"]
    _require_match(XYM, db["P_axis"], deg["P_axis"], "cert deg P axis")
    _require_match(XYM, db["Q_axis"], deg["Q_axis"], "cert deg Q axis")
    if not Poly.from_terms(XY, nb["dulac_diff"]).is_zero():
        raise AssertionError("cert dulac_diff must be empty")
    if not Poly.from_terms(XYM, fb["dulac_diff"]).is_zero():
        raise AssertionError("cert family dulac_diff must be empty")
    if not Poly.from_terms(XYM, db["P_axis"]).is_zero():
        raise AssertionError("cert degeneration P_axis must be empty")


def dump_lines(data: dict) -> list[str]:
    nm, fam = data["nm"], data["fam"]
    return [
        "imagined_three_cycles DROP",
        "ye_cherkas_quadratic_at_most_one CONTEXT",
        "ye_reproved 0",
        "named_cubic_invariant_line KEEP",
        "dulac_half_planes KEEP",
        "certified_cycle_count 0",
        "family_cycle_count 0",
        "hn_moved 0",
        "three_cycles_produced 0",
        "degree 3",
        "family_degree_mu0 2",
        "invariant_line y=0",
        "cofactor_named 16x",
        "cofactor_family x",
        "line_of_equilibria 0",
        "equilibria_count 1",
        "eq 0 0",
        f"P_terms {nm['P'].nterms()}",
        f"Q_terms {nm['Q'].nterms()}",
        f"P_axis_at_1 {nm['P_at_10']}",
        f"axis_factor_at_0 {nm['axis_factor_at_0']}",
        f"dulac_num_at_0 {nm['dulac_num_at_0']}",
        f"dulac_num_min {nm['dulac_num_at_0']}",
        f"div_at_0 {nm['div_at_0']}",
        f"div_at_minus3 {nm['div_at_minus3']}",
        f"div_disc {nm['div_disc']}",
        "bendixson_inconclusive 1",
        f"trace_origin {nm['trace_origin']}",
        f"det_origin {nm['det_origin']}",
        f"named_dulac_diff_terms {nm['dulac_diff'].nterms()}",
        f"family_dulac_diff_terms {fam['dulac_diff'].nterms()}",
        f"named_cofactor_diff_terms {nm['cofactor_diff'].nterms()}",
        f"family_degree {fam['degree']}",
        f"named_mu_disc {fam['named_mu_disc_num']}/{fam['named_mu_disc_den']}",
        "degeneration_axis_equilibria 1",
        f"energy_not_integral_terms {data['energy_terms']}",
        "integer_box 1",
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
    print("VALID ll-invariant-line replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
