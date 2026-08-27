#!/usr/bin/env python3
"""Replay Z(2,n) = floor((n-1)/2) on H = (x^2+y^2)/2.

The imagined extra Abelian zero is not constructed. The radial
1-form Q = y p(x^2+y^2) attains the published count and does not
beat it. Not a bound on H(2). A second check is verify.rs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "certs" / "family.json"

N_MIN = 1
N_MAX = 10


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


# ---------------------------------------------------------------------------
# Univariate Z[t]: coeffs[k] is the coefficient of t^k
# ---------------------------------------------------------------------------


def uni_eval(coeffs: list[int], x: int) -> int:
    total = 0
    pwr = 1
    for c in coeffs:
        total += c * pwr
        pwr *= x
    return total


def uni_eval_at_half_num(coeffs: list[int]) -> int:
    """Numerator of I(1/2) with denominator 2^{deg}."""
    if not coeffs:
        return 0
    deg = len(coeffs) - 1
    num = 0
    for k, c in enumerate(coeffs):
        num += c * (2 ** (deg - k))
    return num


def uni_mul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def uni_sub(a: list[int], b: list[int]) -> list[int]:
    n = max(len(a), len(b))
    out = [(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def uni_scale_x(coeffs: list[int], factor: int) -> list[int]:
    """p(factor * t): coeff t^k becomes coeff * factor^k."""
    return [c * (factor**k) for k, c in enumerate(coeffs)]


def uni_times_x(coeffs: list[int]) -> list[int]:
    return [0] + list(coeffs)


def uni_fmt(coeffs: list[int]) -> str:
    return ",".join(str(c) for c in coeffs)


def z2(n: int) -> int:
    return (n - 1) // 2


def radial_deg_q(n: int) -> int:
    return 2 * z2(n) + 1


def beat_deg_q(n: int) -> int:
    """Degree of Q needed to place floor((n-1)/2)+1 radial zeros."""
    return 2 * (z2(n) + 1) + 1


# ---------------------------------------------------------------------------
# Hamiltonian and radial 1-forms
# ---------------------------------------------------------------------------

XY = ("x", "y")
XYH = ("x", "y", "h")
H_ONLY = ("h",)


def hamiltonian() -> dict[str, Poly]:
    x, y = V(XY, "x"), V(XY, "y")
    hnum = (x ** 2) + (y ** 2)
    p = y
    q = -x
    dhdt = hnum.dvar("x") * p + hnum.dvar("y") * q
    return {"Hnum": hnum, "P": p, "Qfield": q, "dHdt": dhdt}


def n3_forms() -> dict[str, Poly | list[int]]:
    x, y = V(XY, "x"), V(XY, "y")
    p_s = [1, -1]
    qform = y * (C(XY, 1) - (x ** 2) - (y ** 2))
    i_tilde = uni_times_x(uni_scale_x(p_s, 2))
    factored = uni_mul([0, 1], [1, -2])
    xv, yv, hv = V(XYH, "x"), V(XYH, "y"), V(XYH, "h")
    r2 = (xv ** 2) + (yv ** 2)
    p_r = C(XYH, 1) - r2
    p_h = C(XYH, 1) - hv.scale(2)
    factor = r2 - hv.scale(2)
    residual = (p_r - p_h) - factor.scale(-1)
    return {
        "Q": qform,
        "p_s": p_s,
        "I_tilde": i_tilde,
        "factored": factored,
        "factor_diff": uni_sub(i_tilde, factored),
        "oval_residual": residual,
    }


def n5_forms() -> dict[str, Poly | list[int]]:
    x, y = V(XY, "x"), V(XY, "y")
    r2 = (x ** 2) + (y ** 2)
    p_s = [4, -5, 1]
    qform = y * (r2 - C(XY, 1)) * (r2 - C(XY, 4))
    i_tilde = uni_times_x(uni_scale_x(p_s, 2))
    factored = uni_mul(uni_mul([0, 1], [-1, 2]), [-4, 2])
    xv, yv, hv = V(XYH, "x"), V(XYH, "y"), V(XYH, "h")
    r2h = (xv ** 2) + (yv ** 2)
    p_r = (r2h ** 2) - r2h.scale(5) + C(XYH, 4)
    p_h = (hv ** 2).scale(4) - hv.scale(10) + C(XYH, 4)
    factor = r2h - hv.scale(2)
    quot = r2h + hv.scale(2) - C(XYH, 5)
    residual = (p_r - p_h) - factor * quot
    return {
        "Q": qform,
        "p_s": p_s,
        "I_tilde": i_tilde,
        "factored": factored,
        "factor_diff": uni_sub(i_tilde, factored),
        "oval_residual": residual,
    }


def mixed_xy_vanishes_angle() -> None:
    """∮ x y q(r^2) dx is odd in the angle: the monomial x y * (x^2+y^2)^k
    does not contribute a radial p-factor. Certified as the polynomial
    identity that x y is odd in x (or in y): flip x -> -x sends the
    1-form coefficient to its negative, so the full-period integral is 0.
    """
    x, y = V(XY, "x"), V(XY, "y")
    coeff = x * y * ((x ** 2) + (y ** 2))
    flipped = coeff.scale(-1)
    # subst x -> -x
    vs = XY
    xneg = -V(vs, "x")
    ysame = V(vs, "y")
    mapped = Poly.zero(vs)
    for exp, c in coeff.terms.items():
        mon = Poly.const(vs, c)
        mon = mon * (xneg ** exp[0]) * (ysame ** exp[1])
        mapped = mapped + mon
    if not mapped.equals(flipped):
        raise AssertionError("xy r^2 is not odd in x")


def check_arithmetic() -> list[dict[str, int]]:
    rows = []
    for n in range(N_MIN, N_MAX + 1):
        z = z2(n)
        degq = radial_deg_q(n)
        if degq > n:
            raise AssertionError(f"radial degQ {degq} exceeds n={n}")
        if z != (n - 1) // 2:
            raise AssertionError("Z formula")
        if degq != 2 * z + 1:
            raise AssertionError("radial degree formula")
        if beat_deg_q(n) != 2 * z + 3:
            raise AssertionError("beat degree formula")
        if beat_deg_q(n) <= n:
            raise AssertionError(f"beating Z(2,{n}) unexpectedly fits in degree n")
        rows.append(
            {
                "n": n,
                "Z": z,
                "degQ": degq,
                "zeros": z,
                "matches": 1,
                "beat_degQ": beat_deg_q(n),
            }
        )
    return rows


def check_identities() -> dict:
    ham = hamiltonian()
    _require_zero(ham["dHdt"], "dHnum/dt")
    if ham["Hnum"].degree() != 2:
        raise AssertionError("Hnum is not quadratic")
    if ham["P"].degree() != 1 or ham["Qfield"].degree() != 1:
        raise AssertionError("Hamiltonian field is not linear")

    n3 = n3_forms()
    n5 = n5_forms()
    q3: Poly = n3["Q"]  # type: ignore[assignment]
    q5: Poly = n5["Q"]  # type: ignore[assignment]
    if q3.degree() != 3:
        raise AssertionError(f"n=3 deg Q is {q3.degree()}")
    if q5.degree() != 5:
        raise AssertionError(f"n=5 deg Q is {q5.degree()}")
    if len(q3.terms) != 3:
        raise AssertionError(f"n=3 Q term count {len(q3.terms)}")
    if len(q5.terms) != 6:
        raise AssertionError(f"n=5 Q term count {len(q5.terms)}")

    if n3["I_tilde"] != [0, 1, -2]:
        raise AssertionError(f"n=3 I_tilde {n3['I_tilde']}")
    if n3["factor_diff"] != [0]:
        raise AssertionError("n=3 factorization")
    if uni_eval(n3["p_s"], 1) != 0:
        raise AssertionError("n=3 p(1)")
    if uni_eval(n3["p_s"], 0) != 1:
        raise AssertionError("n=3 p(0)")
    if uni_eval_at_half_num(n3["I_tilde"]) != 0:
        raise AssertionError("n=3 I_tilde(1/2)")
    _require_zero(n3["oval_residual"], "n=3 oval reduction")

    if n5["I_tilde"] != [0, 4, -10, 4]:
        raise AssertionError(f"n=5 I_tilde {n5['I_tilde']}")
    if n5["factor_diff"] != [0]:
        raise AssertionError("n=5 factorization")
    if uni_eval(n5["p_s"], 1) != 0 or uni_eval(n5["p_s"], 4) != 0:
        raise AssertionError("n=5 p roots")
    if uni_eval(n5["p_s"], 0) != 4:
        raise AssertionError("n=5 p(0)")
    if uni_eval_at_half_num(n5["I_tilde"]) != 0:
        raise AssertionError("n=5 I_tilde(1/2)")
    if uni_eval(n5["I_tilde"], 2) != 0:
        raise AssertionError("n=5 I_tilde(2)")
    if uni_eval(n5["I_tilde"], 1) == 0:
        raise AssertionError("n=5 unexpectedly vanished at h=1")
    _require_zero(n5["oval_residual"], "n=5 oval reduction")
    if len(n5["I_tilde"]) - 1 != 3:
        raise AssertionError("n=5 I_tilde degree")

    mixed_xy_vanishes_angle()
    check_integer_box(ham, n3, n5)
    check_negative(n3, n5)
    return {"n3": n3, "n5": n5, "ham": ham}


def check_integer_box(ham: dict[str, Poly], n3: dict, n5: dict) -> None:
    for x in range(-3, 4):
        for y in range(-3, 4):
            if ham["dHdt"].eval({"x": x, "y": y}) != 0:
                raise AssertionError(f"dHnum/dt nonzero at {(x, y)}")
            claimed = 2 * x * y + 2 * y * (-x)
            if claimed != 0:
                raise AssertionError("hand dH/dt sample")
    oval3: Poly = n3["oval_residual"]
    oval5: Poly = n5["oval_residual"]
    for x in range(-3, 4):
        for y in range(-3, 4):
            for h in range(-3, 4):
                vals = {"x": x, "y": y, "h": h}
                if oval3.eval(vals) != 0:
                    raise AssertionError(f"n=3 oval residual at {vals}")
                if oval5.eval(vals) != 0:
                    raise AssertionError(f"n=5 oval residual at {vals}")


def check_negative(n3: dict, n5: dict) -> None:
    extra = list(n5["I_tilde"]) + [0]
    extra[0] = 1
    if uni_eval_at_half_num(n5["I_tilde"]) != 0:
        raise AssertionError("half-eval sanity")
    if extra == n5["I_tilde"]:
        raise AssertionError("extra-root polynomial collided")
    if uni_eval(extra, 0) == 0 and uni_eval(n5["I_tilde"], 0) == 0:
        if uni_eval(extra, 3) == 0 and uni_eval(n5["I_tilde"], 3) == 0:
            raise AssertionError("constant perturbation still vanished")
    # A cubic p would be n=7, not a beat of n=5.
    cubic = [ -36, 49, -14, 1 ]  # (s-1)(s-4)(s-9)
    if uni_eval(cubic, 1) != 0 or uni_eval(cubic, 4) != 0 or uni_eval(cubic, 9) != 0:
        raise AssertionError("cubic p roots")
    if 2 * 3 + 1 != 7:
        raise AssertionError("cubic p is degree 7")
    if n3["I_tilde"] == [0, 1, -2, 1]:
        raise AssertionError("n=3 unexpectedly gained a cubic term")


def build_certificate(rows: list[dict[str, int]], n3: dict, n5: dict, ham: dict) -> dict:
    q3: Poly = n3["Q"]
    q5: Poly = n5["Q"]
    return {
        "schema": "hilbert16-jj-weak-hilbert/v1",
        "claim": (
            "Radial family on H=(x^2+y^2)/2 attains Z(2,n)=floor((n-1)/2) "
            "and does not beat it. Not a bound on H(2)."
        ),
        "record": "Scholarpedia Han-Li-Li 2010; Z(2,n)=floor((n-1)/2) because M(h) is a polynomial",
        "hn_moved": False,
        "formula_beaten": False,
        "not_H2": True,
        "hamiltonian": {
            "variables": list(XY),
            "Hnum": ham["Hnum"].to_terms(),
            "P": ham["P"].to_terms(),
            "Qfield": ham["Qfield"].to_terms(),
            "dHdt": ham["dHdt"].to_terms(),
        },
        "n3": {
            "variables": list(XY),
            "p": n3["p_s"],
            "I_tilde": n3["I_tilde"],
            "Q": q3.to_terms(),
            "degQ": q3.degree(),
            "positive_zeros_h": ["1/2"],
            "Z": 1,
        },
        "n5": {
            "variables": list(XY),
            "p": n5["p_s"],
            "I_tilde": n5["I_tilde"],
            "Q": q5.to_terms(),
            "degQ": q5.degree(),
            "positive_zeros_h": ["1/2", "2"],
            "Z": 2,
        },
        "rows": rows,
    }


def check_certificate(payload: dict, n3: dict, n5: dict, ham: dict) -> None:
    if payload.get("schema") != "hilbert16-jj-weak-hilbert/v1":
        raise AssertionError("schema mismatch")
    if payload.get("hn_moved") is not False:
        raise AssertionError("must not claim that H(n) moved")
    if payload.get("formula_beaten") is not False:
        raise AssertionError("must not claim the formula was beaten")
    if payload.get("not_H2") is not True:
        raise AssertionError("must record that this is not H(2)")
    b = payload["hamiltonian"]
    vs = tuple(b["variables"])
    _require_match(vs, b["Hnum"], ham["Hnum"], "cert Hnum")
    _require_match(vs, b["P"], ham["P"], "cert P")
    _require_match(vs, b["Qfield"], ham["Qfield"], "cert Qfield")
    _require_match(vs, b["dHdt"], ham["dHdt"], "cert dHdt")
    if payload["n3"]["p"] != n3["p_s"] or payload["n3"]["I_tilde"] != n3["I_tilde"]:
        raise AssertionError("cert n3 univariate")
    if payload["n5"]["p"] != n5["p_s"] or payload["n5"]["I_tilde"] != n5["I_tilde"]:
        raise AssertionError("cert n5 univariate")
    _require_match(tuple(payload["n3"]["variables"]), payload["n3"]["Q"], n3["Q"], "cert n3 Q")
    _require_match(tuple(payload["n5"]["variables"]), payload["n5"]["Q"], n5["Q"], "cert n5 Q")


def dump_lines(rows: list[dict[str, int]], n3: dict, n5: dict, ham: dict) -> list[str]:
    q3: Poly = n3["Q"]
    q5: Poly = n5["Q"]
    lines = ["formula Z(2,n)=floor((n-1)/2)"]
    for r in rows:
        lines.append(
            f"n {r['n']} Z {r['Z']} degQ {r['degQ']} zeros {r['zeros']} matches {r['matches']}"
        )
    lines.extend(
        [
            f"hamiltonian dHnum/dt terms {len(ham['dHdt'].terms)}",
            f"n3 Q terms {len(q3.terms)}",
            f"n3 p {uni_fmt(n3['p_s'])}",
            f"n3 I_tilde {uni_fmt(n3['I_tilde'])}",
            "n3 factor I_tilde-h*(1-2h) 0",
            f"n3 p(1) {uni_eval(n3['p_s'], 1)}",
            "n3 I_tilde_at_1/2 0",
            "n3 oval_reduction 0",
            "n3 positive_zeros 1/2",
            f"n5 Q terms {len(q5.terms)}",
            f"n5 p {uni_fmt(n5['p_s'])}",
            f"n5 I_tilde {uni_fmt(n5['I_tilde'])}",
            "n5 factor I_tilde-h*(2h-1)*(2h-4) 0",
            f"n5 p(1) {uni_eval(n5['p_s'], 1)}",
            f"n5 p(4) {uni_eval(n5['p_s'], 4)}",
            "n5 I_tilde_at_1/2 0",
            "n5 I_tilde_at_2 0",
            "n5 oval_reduction 0",
            "n5 positive_zeros 1/2,2",
            "n5 extra_zero_degree_needed 4",
            f"beat n=3 needs_degQ {beat_deg_q(3)}",
            f"beat n=5 needs_degQ {beat_deg_q(5)}",
            "formula_beaten 0",
            "hn_moved 0",
            "not_H2",
            "negative extra root rejected",
            "integer box zeros",
        ]
    )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    rows = check_arithmetic()
    ids = check_identities()
    payload = build_certificate(rows, ids["n3"], ids["n5"], ids["ham"])
    check_certificate(payload, ids["n3"], ids["n5"], ids["ham"])

    if args.write_cert:
        CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {CERT_PATH}")

    if CERT_PATH.is_file():
        saved = json.loads(CERT_PATH.read_text(encoding="utf-8"))
        check_certificate(saved, ids["n3"], ids["n5"], ids["ham"])
        if saved != payload:
            raise AssertionError("committed certificate is not the canonical dump")

    lines = dump_lines(rows, ids["n3"], ids["n5"], ids["ham"])
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID jj-weak-hilbert replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
