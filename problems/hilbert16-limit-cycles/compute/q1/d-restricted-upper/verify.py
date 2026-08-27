#!/usr/bin/env python3
"""Exact polynomial identities for three restricted planar families.

Primary: the radial cubic
    P = y - x (x^2 + y^2 - rho^2)
    Q = -x - y (x^2 + y^2 - rho^2)
satisfies the polar identities
    x P + y Q = (x^2 + y^2) (rho^2 - x^2 - y^2)
    x Q - y P = -(x^2 + y^2)
in Z[x, y, rho]. Those are r * rdot = r^2 (rho^2 - r^2) and
r^2 * thetadot = -r^2. Uniqueness of the periodic orbit is the
elementary consequence recorded in LINE.md; this program only
certifies the identities and the two secondary algebraic lemmas.

Secondary:
    dH/dt = 0 for a cubic Hamiltonian (quadratic field);
    weighted Dulac identity and the Delta = 0 parallel reduction
    for Lotka-Volterra.

A second, independent check is verify.rs (degree-bounded integer
evaluation plus sparse expansion).
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


# ---------------------------------------------------------------------------
# Primary family
# ---------------------------------------------------------------------------

POLAR_VARS = ("x", "y", "rho")
RADIAL_VARS = ("r", "rho")


def polar_field() -> tuple[Poly, Poly]:
    x, y, rho = (V(POLAR_VARS, n) for n in POLAR_VARS)
    r2 = x * x + y * y
    rho2 = rho * rho
    p = y - x * (r2 - rho2)
    q = -x - y * (r2 - rho2)
    return p, q


def polar_identities() -> dict[str, Poly]:
    x, y, rho = (V(POLAR_VARS, n) for n in POLAR_VARS)
    p, q = polar_field()
    r2 = x * x + y * y
    radial_left = x * p + y * q
    radial_right = r2 * (rho * rho - r2)
    angular_left = x * q - y * p
    angular_right = -r2
    return {
        "P": p,
        "Q": q,
        "radial_left": radial_left,
        "radial_right": radial_right,
        "radial_diff": radial_left - radial_right,
        "angular_left": angular_left,
        "angular_right": angular_right,
        "angular_diff": angular_left - angular_right,
    }


def radial_factorization() -> dict[str, Poly]:
    r, rho = V(RADIAL_VARS, "r"), V(RADIAL_VARS, "rho")
    left = r * (rho * rho - r * r)
    right = r * (rho - r) * (rho + r)
    return {"rdot_over_r_times_r": left, "factored": right, "diff": left - right}


# ---------------------------------------------------------------------------
# Quadratic Hamiltonian
# ---------------------------------------------------------------------------

HAM_VARS = (
    "x",
    "y",
    "a30",
    "a21",
    "a12",
    "a03",
    "a20",
    "a11",
    "a02",
    "a10",
    "a01",
    "a00",
)


def cubic_hamiltonian() -> dict[str, Poly]:
    x, y = V(HAM_VARS, "x"), V(HAM_VARS, "y")
    a30, a21, a12, a03 = (V(HAM_VARS, n) for n in ("a30", "a21", "a12", "a03"))
    a20, a11, a02 = (V(HAM_VARS, n) for n in ("a20", "a11", "a02"))
    a10, a01, a00 = (V(HAM_VARS, n) for n in ("a10", "a01", "a00"))
    h = (
        a30 * (x ** 3)
        + a21 * (x ** 2) * y
        + a12 * x * (y ** 2)
        + a03 * (y ** 3)
        + a20 * (x ** 2)
        + a11 * x * y
        + a02 * (y ** 2)
        + a10 * x
        + a01 * y
        + a00
    )
    hx = h.dvar("x")
    hy = h.dvar("y")
    p = hy
    q = -hx
    dhdt = hx * p + hy * q
    return {"H": h, "Hx": hx, "Hy": hy, "P": p, "Q": q, "dHdt": dhdt}


# ---------------------------------------------------------------------------
# Lotka-Volterra
# ---------------------------------------------------------------------------

LV_VARS = ("x", "y", "a", "b", "c", "d", "e", "f", "alpha", "beta")
CRAMER_VARS = ("b", "c", "e", "f")
PARA_VARS = ("x", "y", "a", "b", "c", "d", "lam")


def lotka_volterra() -> dict[str, Poly]:
    x, y = V(LV_VARS, "x"), V(LV_VARS, "y")
    a, b, c = (V(LV_VARS, n) for n in ("a", "b", "c"))
    d, e, f = (V(LV_VARS, n) for n in ("d", "e", "f"))
    alpha, beta = V(LV_VARS, "alpha"), V(LV_VARS, "beta")
    p = x * (a + b * x + c * y)
    q = y * (d + e * x + f * y)
    # div(B X) / B for B = x^{alpha-1} y^{beta-1}, which is polynomial:
    # (alpha-1) P/x + dP/dx + (beta-1) Q/y + dQ/dy.
    growth_p = a + b * x + c * y
    growth_q = d + e * x + f * y
    weighted = (
        (alpha - C(LV_VARS, 1)) * growth_p
        + p.dvar("x")
        + (beta - C(LV_VARS, 1)) * growth_q
        + q.dvar("y")
    )
    claimed = (
        alpha * a
        + beta * d
        + (alpha * b + beta * e + b) * x
        + (alpha * c + beta * f + f) * y
    )
    return {
        "P": p,
        "Q": q,
        "weighted_div_over_B": weighted,
        "claimed_linear": claimed,
        "diff": weighted - claimed,
    }


def cramer_identities() -> dict[str, Poly]:
    """(alpha Delta, beta Delta) really kill the linear coefficients."""
    b, c, e, f = (V(CRAMER_VARS, n) for n in CRAMER_VARS)
    delta = b * f - e * c
    alpha_delta = f * (e - b)
    beta_delta = b * (c - f)
    # (alpha b + beta e + b) * Delta
    x_coeff = alpha_delta * b + beta_delta * e + delta * b
    y_coeff = alpha_delta * c + beta_delta * f + delta * f
    return {
        "Delta": delta,
        "alpha_Delta": alpha_delta,
        "beta_Delta": beta_delta,
        "x_coeff_times_Delta": x_coeff,
        "y_coeff_times_Delta": y_coeff,
    }


def parallel_identity() -> dict[str, Poly]:
    x, y = V(PARA_VARS, "x"), V(PARA_VARS, "y")
    a, b, c, d, lam = (V(PARA_VARS, n) for n in ("a", "b", "c", "d", "lam"))
    e = lam * b
    f = lam * c
    left = lam * (a + b * x + c * y) - (d + e * x + f * y)
    right = lam * a - d
    return {"left": left, "right": right, "diff": left - right}


# ---------------------------------------------------------------------------
# Certificate I/O
# ---------------------------------------------------------------------------


def build_certificate() -> dict:
    polar = polar_identities()
    radial = radial_factorization()
    ham = cubic_hamiltonian()
    lv = lotka_volterra()
    cramer = cramer_identities()
    para = parallel_identity()
    return {
        "schema": "hilbert16-d-restricted-upper/v1",
        "claim": (
            "polar identities for the radial cubic; Hamiltonian dH/dt = 0; "
            "Lotka-Volterra weighted Dulac and Delta=0 reduction"
        ),
        "polar": {
            "variables": list(POLAR_VARS),
            "P": polar["P"].to_terms(),
            "Q": polar["Q"].to_terms(),
            "radial_left": polar["radial_left"].to_terms(),
            "radial_right": polar["radial_right"].to_terms(),
            "angular_left": polar["angular_left"].to_terms(),
            "angular_right": polar["angular_right"].to_terms(),
        },
        "radial_speed": {
            "variables": list(RADIAL_VARS),
            "r_times_rho2_minus_r2": radial["rdot_over_r_times_r"].to_terms(),
            "factored": radial["factored"].to_terms(),
        },
        "hamiltonian": {
            "variables": list(HAM_VARS),
            "H": ham["H"].to_terms(),
            "Hx": ham["Hx"].to_terms(),
            "Hy": ham["Hy"].to_terms(),
            "dHdt": ham["dHdt"].to_terms(),
        },
        "lotka_volterra": {
            "variables": list(LV_VARS),
            "weighted_div_over_B": lv["weighted_div_over_B"].to_terms(),
            "claimed_linear": lv["claimed_linear"].to_terms(),
        },
        "cramer": {
            "variables": list(CRAMER_VARS),
            "Delta": cramer["Delta"].to_terms(),
            "alpha_Delta": cramer["alpha_Delta"].to_terms(),
            "beta_Delta": cramer["beta_Delta"].to_terms(),
            "x_coeff_times_Delta": cramer["x_coeff_times_Delta"].to_terms(),
            "y_coeff_times_Delta": cramer["y_coeff_times_Delta"].to_terms(),
        },
        "parallel": {
            "variables": list(PARA_VARS),
            "left": para["left"].to_terms(),
            "right": para["right"].to_terms(),
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


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    loaded = Poly.from_terms(variables, terms)
    _require_equal(loaded, poly, label)


def check_negative() -> None:
    """A constant perturbation of P must break the polar identities."""
    x, y, rho = (V(POLAR_VARS, n) for n in POLAR_VARS)
    p, q = polar_field()
    p_bad = p + C(POLAR_VARS, 1)
    radial = x * p_bad + y * q
    right = (x * x + y * y) * (rho * rho - x * x - y * y)
    if radial.equals(right):
        raise AssertionError("perturbed field unexpectedly satisfied the radial identity")
    angular = x * q - y * p_bad
    if angular.equals(-(x * x + y * y)):
        raise AssertionError("perturbed field unexpectedly satisfied the angular identity")


def check_origin_is_only_equilibrium_sample() -> None:
    """Off the origin, xQ-yP = -r^2 != 0, so the field cannot vanish."""
    p, q = polar_field()
    for x in range(-2, 3):
        for y in range(-2, 3):
            for rho in range(-2, 3):
                pv = p.eval({"x": x, "y": y, "rho": rho})
                qv = q.eval({"x": x, "y": y, "rho": rho})
                if x == 0 and y == 0:
                    if pv != 0 or qv != 0:
                        raise AssertionError("origin is not an equilibrium")
                else:
                    if pv == 0 and qv == 0:
                        raise AssertionError(f"unexpected equilibrium at {(x, y, rho)}")


def check_identities() -> dict[str, int]:
    polar = polar_identities()
    _require_zero(polar["radial_diff"], "polar radial difference")
    _require_zero(polar["angular_diff"], "polar angular difference")
    if polar["P"].eval({"x": 0, "y": 0, "rho": 1}) != 0:
        raise AssertionError("P(0,0) != 0")
    if polar["Q"].eval({"x": 0, "y": 0, "rho": 1}) != 0:
        raise AssertionError("Q(0,0) != 0")

    radial = radial_factorization()
    _require_zero(radial["diff"], "r(rho^2-r^2) factorization")

    ham = cubic_hamiltonian()
    _require_zero(ham["dHdt"], "Hamiltonian dH/dt")

    lv = lotka_volterra()
    _require_zero(lv["diff"], "Lotka-Volterra weighted divergence")

    cramer = cramer_identities()
    _require_zero(cramer["x_coeff_times_Delta"], "Cramer x-coefficient")
    _require_zero(cramer["y_coeff_times_Delta"], "Cramer y-coefficient")
    # Regression: the JSON key for coefficients used to be "c", which
    # collided with the LV / Cramer parameter c and dropped the minus
    # on Delta = bf - ce.
    minus_ce = V(CRAMER_VARS, "e") * V(CRAMER_VARS, "c")
    bf = V(CRAMER_VARS, "b") * V(CRAMER_VARS, "f")
    _require_equal(cramer["Delta"], bf - minus_ce, "Delta = bf - ce")
    loaded_delta = Poly.from_terms(CRAMER_VARS, cramer["Delta"].to_terms())
    _require_equal(loaded_delta, cramer["Delta"], "Delta term round-trip")

    para = parallel_identity()
    _require_zero(para["diff"], "parallel Lotka-Volterra reduction")

    check_negative()
    check_origin_is_only_equilibrium_sample()

    return {
        "polar_P_terms": len(polar["P"].terms),
        "polar_Q_terms": len(polar["Q"].terms),
        "polar_radial_terms": len(polar["radial_left"].terms),
        "polar_angular_terms": len(polar["angular_left"].terms),
        "hamiltonian_dHdt_terms": len(ham["dHdt"].terms),
        "lv_weighted_terms": len(lv["weighted_div_over_B"].terms),
        "cramer_x_terms": len(cramer["x_coeff_times_Delta"].terms),
        "cramer_y_terms": len(cramer["y_coeff_times_Delta"].terms),
        "parallel_diff_terms": len(para["diff"].terms),
    }


def check_certificate(payload: dict) -> None:
    polar = polar_identities()
    block = payload["polar"]
    variables = tuple(block["variables"])
    if variables != POLAR_VARS:
        raise AssertionError("polar variable list mismatch")
    _require_match(variables, block["P"], polar["P"], "cert P")
    _require_match(variables, block["Q"], polar["Q"], "cert Q")
    _require_match(variables, block["radial_left"], polar["radial_left"], "cert radial_left")
    _require_match(variables, block["radial_right"], polar["radial_right"], "cert radial_right")
    _require_match(variables, block["angular_left"], polar["angular_left"], "cert angular_left")
    _require_match(variables, block["angular_right"], polar["angular_right"], "cert angular_right")

    radial = radial_factorization()
    rblock = payload["radial_speed"]
    rvars = tuple(rblock["variables"])
    _require_match(rvars, rblock["r_times_rho2_minus_r2"], radial["rdot_over_r_times_r"], "cert rdot")
    _require_match(rvars, rblock["factored"], radial["factored"], "cert rdot factor")

    ham = cubic_hamiltonian()
    hblock = payload["hamiltonian"]
    hvars = tuple(hblock["variables"])
    _require_match(hvars, hblock["H"], ham["H"], "cert H")
    _require_match(hvars, hblock["Hx"], ham["Hx"], "cert Hx")
    _require_match(hvars, hblock["Hy"], ham["Hy"], "cert Hy")
    _require_match(hvars, hblock["dHdt"], ham["dHdt"], "cert dHdt")

    lv = lotka_volterra()
    lblock = payload["lotka_volterra"]
    lvars = tuple(lblock["variables"])
    _require_match(lvars, lblock["weighted_div_over_B"], lv["weighted_div_over_B"], "cert LV weighted")
    _require_match(lvars, lblock["claimed_linear"], lv["claimed_linear"], "cert LV claimed")

    cramer = cramer_identities()
    cblock = payload["cramer"]
    cvars = tuple(cblock["variables"])
    _require_match(cvars, cblock["Delta"], cramer["Delta"], "cert Delta")
    _require_match(cvars, cblock["alpha_Delta"], cramer["alpha_Delta"], "cert alpha_Delta")
    _require_match(cvars, cblock["beta_Delta"], cramer["beta_Delta"], "cert beta_Delta")
    _require_match(
        cvars, cblock["x_coeff_times_Delta"], cramer["x_coeff_times_Delta"], "cert Cramer x"
    )
    _require_match(
        cvars, cblock["y_coeff_times_Delta"], cramer["y_coeff_times_Delta"], "cert Cramer y"
    )

    para = parallel_identity()
    pblock = payload["parallel"]
    pvars = tuple(pblock["variables"])
    _require_match(pvars, pblock["left"], para["left"], "cert parallel left")
    _require_match(pvars, pblock["right"], para["right"], "cert parallel right")


def dump_lines(counts: dict[str, int]) -> list[str]:
    return [
        f"polar P terms {counts['polar_P_terms']}",
        f"polar Q terms {counts['polar_Q_terms']}",
        f"polar radial identity terms {counts['polar_radial_terms']} difference 0",
        f"polar angular identity terms {counts['polar_angular_terms']} difference 0",
        f"hamiltonian dHdt terms {counts['hamiltonian_dHdt_terms']}",
        f"lv weighted terms {counts['lv_weighted_terms']} difference 0",
        f"cramer x terms {counts['cramer_x_terms']}",
        f"cramer y terms {counts['cramer_y_terms']}",
        f"parallel diff terms {counts['parallel_diff_terms']}",
        "negative perturbation rejected",
        "origin is the only integer-box equilibrium",
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
    print("VALID restricted-family identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
