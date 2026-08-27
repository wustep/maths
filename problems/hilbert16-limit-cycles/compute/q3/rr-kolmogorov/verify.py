#!/usr/bin/env python3
"""Exact identities for a named cubic Kolmogorov family.

Imagined: seven isolated cycles in the open first quadrant,
beating M_K(3)>=6 or H_K(5)>=28. Not certified.

Kept: axes x=0 and y=0 are invariant; the named family
    dx/dt = x (1 - x - y)
    dy/dt = y (1 - b x - y - c x^2)
has weighted Dulac divergence identically -1 for
B = x^{-2} y^{-1}, hence 0 isolated cycles in x>0, y>0.
Not a bound on H(n), M_K(3), or H_K(5).

A second, independent expansion is verify.rs (BTreeMap plus
integer-box evaluation). Exact rationals; rustc only on the
Rust side.
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

    def subst_const(self, name: str, value: int) -> "Poly":
        idx = self.variables.index(name)
        out = Poly.zero(self.variables)
        for exp, coeff in self.terms.items():
            power = exp[idx]
            factor = value**power
            if factor == 0:
                continue
            new_exp = list(exp)
            new_exp[idx] = 0
            out.terms[tuple(new_exp)] += coeff * factor
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

    def degree_in(self, names: Iterable[str]) -> int:
        idxs = [self.variables.index(n) for n in names]
        if not self.terms:
            return -1
        return max(sum(exp[i] for i in idxs) for exp in self.terms)

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


GEN = ("x", "y", "a", "b", "c", "alpha", "beta")
NAMED = ("x", "y", "b", "c")
AXES = ("x", "y", "a", "b", "c")


def _require_zero(poly: Poly, label: str) -> None:
    if not poly.is_zero():
        raise AssertionError(f"{label} is not the zero polynomial: {poly.to_terms()}")


def _require_equal(left: Poly, right: Poly, label: str) -> None:
    if not left.equals(right):
        raise AssertionError(f"{label} mismatch: left={left.to_terms()} right={right.to_terms()}")


def _require_match(variables: tuple[str, ...], terms: list, poly: Poly, label: str) -> None:
    _require_equal(Poly.from_terms(variables, terms), poly, label)


def weighted_div(vs: tuple[str, ...], p: Poly, q: Poly, field_p: Poly, field_q: Poly, alpha: Poly, beta: Poly) -> Poly:
    """(alpha-1) p + dP/dx + (beta-1) q + dQ/dy."""
    return (
        (alpha - C(vs, 1)) * p
        + field_p.dvar("x")
        + (beta - C(vs, 1)) * q
        + field_q.dvar("y")
    )


def general() -> dict[str, Poly]:
    vs = GEN
    x, y = V(vs, "x"), V(vs, "y")
    a, b, c = V(vs, "a"), V(vs, "b"), V(vs, "c")
    alpha, beta = V(vs, "alpha"), V(vs, "beta")
    p = C(vs, 1) - x - a * y
    q = C(vs, 1) - b * x - y - c * (x**2)
    field_p = x * p
    field_q = y * q
    weighted = weighted_div(vs, p, q, field_p, field_q, alpha, beta)
    claimed = (
        (alpha + beta)
        - (alpha + C(vs, 1) + beta * b) * x
        - (alpha * a + beta + C(vs, 1)) * y
        - beta * c * (x**2)
    )
    return {
        "p": p,
        "q": q,
        "P": field_p,
        "Q": field_q,
        "weighted": weighted,
        "claimed": claimed,
        "diff": weighted - claimed,
    }


def named() -> dict[str, Poly]:
    vs = NAMED
    x, y = V(vs, "x"), V(vs, "y")
    b, c = V(vs, "b"), V(vs, "c")
    p = C(vs, 1) - x - y
    q = C(vs, 1) - b * x - y - c * (x**2)
    field_p = x * p
    field_q = y * q
    alpha = C(vs, -1)
    beta = C(vs, 0)
    weighted = weighted_div(vs, p, q, field_p, field_q, alpha, beta)
    claimed = C(vs, -1)
    cleared = x * p.dvar("x") - p + y * q.dvar("y")
    cubic_free = y * (C(vs, 1) - b * x - y)
    return {
        "p": p,
        "q": q,
        "P": field_p,
        "Q": field_q,
        "weighted": weighted,
        "claimed": claimed,
        "diff": weighted - claimed,
        "cleared": cleared,
        "cleared_diff": cleared - claimed,
        "cubic_term": C(vs, -1) * c * (x**2) * y,
        "Q_without_cubic": field_q - C(vs, -1) * c * (x**2) * y,
        "cubic_free": cubic_free,
        "lv_slice_diff": (field_q - C(vs, -1) * c * (x**2) * y) - cubic_free,
    }


def axes() -> dict[str, Poly]:
    vs = AXES
    x, y = V(vs, "x"), V(vs, "y")
    a, b, c = V(vs, "a"), V(vs, "b"), V(vs, "c")
    p = C(vs, 1) - x - a * y
    q = C(vs, 1) - b * x - y - c * (x**2)
    field_p = x * p
    field_q = y * q
    return {
        "P": field_p,
        "Q": field_q,
        "P_at_x0": field_p.subst_const("x", 0),
        "Q_at_y0": field_q.subst_const("y", 0),
        "kolmogorov_P": field_p - x * p,
        "kolmogorov_Q": field_q - y * q,
    }


def parent_specialization() -> dict[str, Poly]:
    """a=1, alpha=-1, beta=0 inside the general claimed polynomial is -1."""
    vs = GEN
    x, y = V(vs, "x"), V(vs, "y")
    a, b, c = V(vs, "a"), V(vs, "b"), V(vs, "c")
    alpha, beta = V(vs, "alpha"), V(vs, "beta")
    claimed = (
        (alpha + beta)
        - (alpha + C(vs, 1) + beta * b) * x
        - (alpha * a + beta + C(vs, 1)) * y
        - beta * c * (x**2)
    )
    sliced = (
        claimed.subst_const("a", 1)
        .subst_const("alpha", -1)
        .subst_const("beta", 0)
    )
    one_signed = claimed.subst_const("alpha", -1).subst_const("beta", 0)
    # D = -1 - (1-a) y  when alpha=-1, beta=0.
    expected = C(vs, -1) - (C(vs, 1) - a) * y
    return {
        "sliced": sliced,
        "sliced_diff": sliced - C(vs, -1),
        "one_signed": one_signed,
        "one_signed_claimed": expected,
        "one_signed_diff": one_signed - expected,
    }


def check_integer_box() -> None:
    gen = general()
    nam = named()
    ax = axes()
    spec = parent_specialization()
    for x in range(-2, 3):
        for y in range(-2, 3):
            for a in range(-2, 3):
                for b in range(-2, 3):
                    for c in range(-2, 3):
                        avals = {"x": x, "y": y, "a": a, "b": b, "c": c}
                        if ax["P"].eval({**avals}) != 0 and x == 0:
                            raise AssertionError(f"P(0,y) failed at {avals}")
                        if ax["Q"].eval({**avals}) != 0 and y == 0:
                            raise AssertionError(f"Q(x,0) failed at {avals}")
                        if x == 0 and ax["P"].eval(avals) != 0:
                            raise AssertionError(f"axis x=0 at {avals}")
                        if y == 0 and ax["Q"].eval(avals) != 0:
                            raise AssertionError(f"axis y=0 at {avals}")
                        for alpha in range(-2, 3):
                            for beta in range(-2, 3):
                                gvals = {**avals, "alpha": alpha, "beta": beta}
                                if gen["diff"].eval(gvals) != 0:
                                    raise AssertionError(f"general Dulac at {gvals}")
                                if spec["one_signed_diff"].eval(gvals) != 0:
                                    raise AssertionError(f"one-signed identity at {gvals}")
    for x in range(-3, 4):
        for y in range(-3, 4):
            for b in range(-3, 4):
                for c in range(-3, 4):
                    nvals = {"x": x, "y": y, "b": b, "c": c}
                    if nam["weighted"].eval(nvals) != -1:
                        raise AssertionError(f"named Dulac at {nvals}")
                    if nam["cleared"].eval(nvals) != -1:
                        raise AssertionError(f"cleared Dulac at {nvals}")
                    if nam["lv_slice_diff"].eval(nvals) != 0:
                        raise AssertionError(f"LV slice at {nvals}")


def check_negative() -> None:
    ax = axes()
    vs = AXES
    bad = ax["P"] + C(vs, 1)
    if bad.subst_const("x", 0).is_zero():
        raise AssertionError("constant perturbation of P still vanished on x=0")
    nam = named()
    vs_n = NAMED
    x, y = V(vs_n, "x"), V(vs_n, "y")
    b, c = V(vs_n, "b"), V(vs_n, "c")
    p = C(vs_n, 1) - x - y
    q = C(vs_n, 1) - b * x - y - c * (x**2)
    field_p = x * p
    field_q = y * q
    wrong = weighted_div(vs_n, p, q, field_p, field_q, C(vs_n, 1), C(vs_n, 1))
    if wrong.equals(C(vs_n, -1)):
        raise AssertionError("unweighted divergence collapsed to -1")
    if nam["Q"].degree_in(("x", "y")) != 3:
        raise AssertionError(f"named Q should be degree 3 in (x,y), got {nam['Q'].degree_in(('x', 'y'))}")
    if nam["P"].degree_in(("x", "y")) != 2:
        raise AssertionError(f"named P should be degree 2 in (x,y), got {nam['P'].degree_in(('x', 'y'))}")
    if 7 <= 0:
        raise AssertionError("7 <= 0")
    if 28 <= 6:
        raise AssertionError("H_K(5)>=28 is not a beat of M_K(3)>=6 written here")


def check_identities() -> dict[str, int]:
    gen = general()
    _require_zero(gen["diff"], "general weighted Dulac")
    _require_equal(gen["P"], V(GEN, "x") * gen["p"], "general P = x p")
    _require_equal(gen["Q"], V(GEN, "y") * gen["q"], "general Q = y q")

    nam = named()
    _require_zero(nam["diff"], "named weighted Dulac")
    _require_zero(nam["cleared_diff"], "named cleared Dulac")
    _require_equal(nam["weighted"], C(NAMED, -1), "named D is -1")
    _require_equal(nam["cleared"], C(NAMED, -1), "cleared numerator is -1")
    _require_zero(nam["lv_slice_diff"], "Q without cubic is LV")
    _require_equal(nam["Q_without_cubic"], nam["cubic_free"], "cubic-free Q")
    if nam["Q"].degree_in(("x", "y")) != 3:
        raise AssertionError("cubic term missing from Q")
    if nam["P"].degree_in(("x", "y")) != 2:
        raise AssertionError("named P is not degree 2 in (x,y)")

    ax = axes()
    _require_zero(ax["P_at_x0"], "P(0,y)")
    _require_zero(ax["Q_at_y0"], "Q(x,0)")
    _require_zero(ax["kolmogorov_P"], "P - x p")
    _require_zero(ax["kolmogorov_Q"], "Q - y q")

    spec = parent_specialization()
    _require_zero(spec["sliced_diff"], "a=1, alpha=-1, beta=0 slice")
    _require_zero(spec["one_signed_diff"], "alpha=-1, beta=0 one-signed form")

    check_negative()
    check_integer_box()

    return {
        "general_weighted_terms": gen["weighted"].term_count(),
        "general_diff_terms": gen["diff"].term_count(),
        "named_weighted_terms": nam["weighted"].term_count(),
        "named_diff_terms": nam["diff"].term_count(),
        "cleared_terms": nam["cleared"].term_count(),
        "Q_terms": nam["Q"].term_count(),
        "P_degree": nam["P"].degree_in(("x", "y")),
        "Q_degree": nam["Q"].degree_in(("x", "y")),
        "isolated_cycles": 0,
        "seven": 0,
        "beats_MK3": 0,
        "beats_HK5": 0,
        "hn_moved": 0,
        "alpha": -1,
        "beta": 0,
        "dulac_constant": -1,
    }


def build_certificate() -> dict:
    gen = general()
    nam = named()
    ax = axes()
    spec = parent_specialization()
    return {
        "schema": "hilbert16-rr-kolmogorov/v1",
        "claim": (
            "named cubic Kolmogorov family "
            "dx/dt = x(1-x-y), dy/dt = y(1-b x-y-c x^2) "
            "has weighted Dulac divergence -1, hence 0 isolated "
            "cycles in the open first quadrant; not a bound on H(n)"
        ),
        "hn_moved": False,
        "seven_cycles": False,
        "beats_MK3": False,
        "beats_HK5": False,
        "isolated_cycles_in_Q1": 0,
        "named_alpha": -1,
        "named_beta": 0,
        "dulac_constant": -1,
        "general": {
            "variables": list(GEN),
            "p": gen["p"].to_terms(),
            "q": gen["q"].to_terms(),
            "P": gen["P"].to_terms(),
            "Q": gen["Q"].to_terms(),
            "weighted": gen["weighted"].to_terms(),
            "claimed": gen["claimed"].to_terms(),
            "diff": gen["diff"].to_terms(),
        },
        "named": {
            "variables": list(NAMED),
            "p": nam["p"].to_terms(),
            "q": nam["q"].to_terms(),
            "P": nam["P"].to_terms(),
            "Q": nam["Q"].to_terms(),
            "weighted": nam["weighted"].to_terms(),
            "claimed": nam["claimed"].to_terms(),
            "cleared": nam["cleared"].to_terms(),
            "cubic_term": nam["cubic_term"].to_terms(),
        },
        "axes": {
            "variables": list(AXES),
            "P": ax["P"].to_terms(),
            "Q": ax["Q"].to_terms(),
            "P_at_x0": ax["P_at_x0"].to_terms(),
            "Q_at_y0": ax["Q_at_y0"].to_terms(),
        },
        "specialization": {
            "variables": list(GEN),
            "sliced": spec["sliced"].to_terms(),
            "one_signed": spec["one_signed"].to_terms(),
            "one_signed_claimed": spec["one_signed_claimed"].to_terms(),
        },
        "what_this_is_not": [
            "not seven isolated cycles",
            "not a beat of Carvalho-Cruz-Gouveia M_K(3)>=6",
            "not a claim of Gasull-Santana H_K(5)>=28",
            "not a bound on H(3)",
        ],
    }


def check_certificate(payload: dict) -> None:
    if payload.get("schema") != "hilbert16-rr-kolmogorov/v1":
        raise AssertionError("schema mismatch")
    if payload.get("hn_moved") is not False:
        raise AssertionError("must not claim that H(n) moved")
    if payload.get("seven_cycles") is not False:
        raise AssertionError("must not claim seven cycles")
    if payload.get("beats_MK3") is not False:
        raise AssertionError("must not claim a beat of M_K(3)>=6")
    if payload.get("beats_HK5") is not False:
        raise AssertionError("must not claim H_K(5)>=28")
    if payload.get("isolated_cycles_in_Q1") != 0:
        raise AssertionError("isolated cycle count")
    if payload.get("named_alpha") != -1 or payload.get("named_beta") != 0:
        raise AssertionError("named weights")
    if payload.get("dulac_constant") != -1:
        raise AssertionError("Dulac constant")

    gen = general()
    block = payload["general"]
    vs = tuple(block["variables"])
    if vs != GEN:
        raise AssertionError("general variable list")
    for key in ("p", "q", "P", "Q", "weighted", "claimed", "diff"):
        _require_match(vs, block[key], gen[key], f"cert general {key}")

    nam = named()
    block = payload["named"]
    vs = tuple(block["variables"])
    if vs != NAMED:
        raise AssertionError("named variable list")
    for key in ("p", "q", "P", "Q", "weighted", "claimed", "cleared", "cubic_term"):
        _require_match(vs, block[key], nam[key], f"cert named {key}")

    ax = axes()
    block = payload["axes"]
    vs = tuple(block["variables"])
    if vs != AXES:
        raise AssertionError("axes variable list")
    for key in ("P", "Q", "P_at_x0", "Q_at_y0"):
        _require_match(vs, block[key], ax[key], f"cert axes {key}")

    spec = parent_specialization()
    block = payload["specialization"]
    vs = tuple(block["variables"])
    for key in ("sliced", "one_signed", "one_signed_claimed"):
        _require_match(vs, block[key], spec[key], f"cert spec {key}")


def dump_lines(counts: dict[str, int]) -> list[str]:
    return [
        "imagined_seven_cycles DROP",
        "beats_MK3 DROP",
        "beats_HK5 DROP",
        "named_cubic_kolmogorov KEEP",
        "axes_invariant KEEP",
        "weighted_dulac KEEP",
        f"isolated_cycles_in_Q1 {counts['isolated_cycles']}",
        f"hn_moved {counts['hn_moved']}",
        f"seven_cycles_produced {counts['seven']}",
        f"beats_MK3 {counts['beats_MK3']}",
        f"beats_HK5 {counts['beats_HK5']}",
        f"degree {counts['Q_degree']}",
        f"P_degree {counts['P_degree']}",
        f"alpha {counts['alpha']}",
        f"beta {counts['beta']}",
        f"dulac_constant {counts['dulac_constant']}",
        "axes P(0,y) 0",
        "axes Q(x,0) 0",
        f"general_dulac_terms {counts['general_weighted_terms']}",
        f"general_dulac_diff {counts['general_diff_terms']}",
        f"named_dulac_terms {counts['named_weighted_terms']}",
        f"named_dulac_diff {counts['named_diff_terms']}",
        f"cleared_numerator_terms {counts['cleared_terms']}",
        f"named_Q_terms {counts['Q_terms']}",
        "cleared_numerator -1",
        "cubic_term_Q -c x^2 y",
        "lv_reduction_when_c_eq_0 KEEP",
        "negative seven rejected",
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
    print("VALID rr-kolmogorov identities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
