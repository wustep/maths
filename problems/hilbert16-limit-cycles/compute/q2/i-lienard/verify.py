#!/usr/bin/env python3
"""Replay Chen–Dai–Kaloshin–Li arXiv:2608.17773v1 Theorem 3 arithmetic,
and the algebraic lemmas for the named family
    dx/dt = y - (alpha x + beta x^3),  dy/dt = -x.

This is their Liénard number H(2n+1, 5), not planar H(n). The
imagined field that beats B(n) is not constructed. The full
deg-F≤3 conjecture is not proved. A second check is verify.rs.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
ARITH_PATH = CERTS / "arithmetic.json"
FAMILY_PATH = CERTS / "family.json"

N_MIN = 2
N_MAX = 40


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
# Theorem 3 arithmetic (their Liénard number, not planar H(n))
# ---------------------------------------------------------------------------


def B(n: int) -> int:
    return 2 * n + n // 3 + (n + 1) // 3 - 2


def N_of(n: int) -> int:
    return 2 * n + 1


def HR(N: int) -> int:
    """Han–Romanovski H(N,5) ≥ 2 floor((N-1)/3) + floor((N-1)/2)."""
    return 2 * ((N - 1) // 3) + (N - 1) // 2


def HR2(N: int) -> int:
    """Xiong–Han +2 bound H(N,5) ≥ 2 floor((N-1)/3) + floor(N/2) + 2."""
    return 2 * ((N - 1) // 3) + (N // 2) + 2


def Xiong(N: int) -> int:
    """Xiong H(N,3) ≥ N + floor(N/4), hence also a lower bound for H(N,5)."""
    return N + N // 4


def delta1(n: int) -> int:
    return B(n) - (2 * ((2 * n) // 3) + n)


def delta2(n: int) -> int:
    return B(n) - (2 * ((2 * n) // 3) + n + 2)


def delta3(n: int) -> int:
    return B(n) - Xiong(N_of(n))


def row(n: int) -> dict[str, int]:
    N = N_of(n)
    hr = HR(N)
    hr2 = HR2(N)
    if hr != 2 * ((2 * n) // 3) + n:
        raise AssertionError(f"HR(N) substitution failed at n={n}")
    if hr2 != 2 * ((2 * n) // 3) + n + 2:
        raise AssertionError(f"HR2(N) substitution failed at n={n}")
    if delta1(n) != B(n) - hr:
        raise AssertionError(f"delta1 is not B-HR at n={n}")
    if delta2(n) != B(n) - hr2:
        raise AssertionError(f"delta2 is not B-HR2 at n={n}")
    if delta3(n) != B(n) - Xiong(N):
        raise AssertionError(f"delta3 is not B-Xiong at n={n}")
    return {
        "n": n,
        "N": N,
        "B": B(n),
        "HR": hr,
        "HR2": hr2,
        "Xiong": Xiong(N),
        "delta1": delta1(n),
        "delta2": delta2(n),
        "delta3": delta3(n),
    }


def enumerate_rows() -> list[dict[str, int]]:
    return [row(n) for n in range(N_MIN, N_MAX + 1)]


def first_positive(rows: list[dict[str, int]], key: str) -> int | None:
    for r in rows:
        if r[key] > 0:
            return r["n"]
    return None


def check_arithmetic(rows: list[dict[str, int]]) -> dict:
    d1_pos = [r["n"] for r in rows if r["delta1"] > 0]
    d2_pos = [r["n"] for r in rows if r["delta2"] > 0]
    d1_zero = [r["n"] for r in rows if r["delta1"] == 0]
    d1_neg = [r["n"] for r in rows if r["delta1"] < 0]
    d2_zero = [r["n"] for r in rows if r["delta2"] == 0]
    d3_pos = [r["n"] for r in rows if r["delta3"] > 0]

    expected_d1 = list(range(7, N_MAX + 1))
    expected_d2 = list(range(13, N_MAX + 1))
    if d1_pos != expected_d1:
        raise AssertionError(f"delta1>0 is {d1_pos}, expected n>=7 in the range")
    if d2_pos != expected_d2:
        raise AssertionError(f"delta2>0 is {d2_pos}, expected n>=13 in the range")
    if d1_neg != [2, 3]:
        raise AssertionError(f"delta1<0 is {d1_neg}, paper says n=2,3")
    if d1_zero != [4, 5, 6]:
        raise AssertionError(f"delta1=0 is {d1_zero}, paper says n=4,5,6")
    if d2_zero != [10, 11, 12]:
        raise AssertionError(f"delta2=0 is {d2_zero}, paper says n=10,11,12")

    # Paper: Delta3>0 for n=21 and all n>=23 (checked on 2..40).
    expected_d3 = [21] + list(range(23, N_MAX + 1))
    if d3_pos != expected_d3:
        raise AssertionError(f"delta3>0 is {d3_pos}, paper says n=21 and n>=23")

    if first_positive(rows, "delta1") != 7:
        raise AssertionError("first n with delta1>0 is not 7")
    if first_positive(rows, "delta2") != 13:
        raise AssertionError("first n with delta2>0 is not 13")

    return {
        "schema": "hilbert16-i-lienard-arithmetic/v1",
        "paper": "arXiv:2608.17773v1 Theorem 3",
        "claim": (
            "Replay B(n) against Han-Romanovski, the Xiong-Han +2 bound, "
            "and Xiong H(N,3). This is their Liénard H(2n+1,5), not planar H(n)."
        ),
        "hn_moved": False,
        "beats_B_n": False,
        "n_min": N_MIN,
        "n_max": N_MAX,
        "formulas": {
            "B": "2n + n//3 + (n+1)//3 - 2",
            "N": "2n+1",
            "HR": "2*((N-1)//3) + (N-1)//2",
            "HR2": "2*((N-1)//3) + (N//2) + 2",
            "Xiong": "N + N//4",
            "delta1": "B(n) - (2*((2n)//3) + n)",
            "delta2": "B(n) - (2*((2n)//3) + n + 2)",
            "delta3": "B(n) - (N + N//4)",
        },
        "rows": rows,
        "delta1_positive_iff_n_ge": 7,
        "delta2_positive_iff_n_ge": 13,
        "delta1_negative_n": d1_neg,
        "delta1_zero_n": d1_zero,
        "delta2_zero_n": d2_zero,
        "delta3_positive_n": d3_pos,
        "paper_delta3": "positive at n=21 and for all n>=23",
    }


# ---------------------------------------------------------------------------
# Named family  dx/dt = y-(alpha x + beta x^3),  dy/dt = -x
# ---------------------------------------------------------------------------

ENERGY_VARS = ("x", "y", "alpha", "beta")
F_VARS = ("x", "alpha", "beta")
VDP_VARS = ("x", "a", "beta")
EVEN_VARS = ("x", "alpha", "beta", "gamma")
LIN_VARS = ("x", "y", "alpha")


def energy_identities() -> dict[str, Poly]:
    x, y, alpha, beta = (V(ENERGY_VARS, n) for n in ENERGY_VARS)
    p = y - (alpha * x + beta * (x ** 3))
    q = -x
    dedt = x * p + y * q
    claimed = -(alpha * (x ** 2) + beta * (x ** 4))
    factored = -(x ** 2) * (alpha + beta * (x ** 2))
    return {
        "P": p,
        "Q": q,
        "dEdt": dedt,
        "claimed": claimed,
        "factored": factored,
        "diff_claimed": dedt - claimed,
        "diff_factored": claimed - factored,
    }


def F_identities() -> dict[str, Poly]:
    x, alpha, beta = (V(F_VARS, n) for n in F_VARS)
    F = alpha * x + beta * (x ** 3)
    F_minus = alpha * (-x) + beta * ((-x) ** 3)
    factored = x * (alpha + beta * (x ** 2))
    Fp = F.dvar("x")
    claimed_Fp = alpha + C(F_VARS, 3) * beta * (x ** 2)
    f = claimed_Fp
    g = x
    # Numerator of (f/g)': g f' - f g' = 3 beta x^2 - alpha.
    fg_num = g * f.dvar("x") - f * g.dvar("x")
    fg_claimed = C(F_VARS, 3) * beta * (x ** 2) - alpha
    return {
        "F": F,
        "odd_sum": F + F_minus,
        "factored": factored,
        "factor_diff": F - factored,
        "Fprime": Fp,
        "Fprime_claimed": claimed_Fp,
        "Fprime_diff": Fp - claimed_Fp,
        "fg_num": fg_num,
        "fg_claimed": fg_claimed,
        "fg_diff": fg_num - fg_claimed,
    }


def vdp_identities() -> dict[str, Poly]:
    """alpha = -beta a^2, the (beta>0, alpha<0) chart with unique positive root a."""
    x, a, beta = (V(VDP_VARS, n) for n in VDP_VARS)
    F = (-(beta * (a ** 2))) * x + beta * (x ** 3)
    factored = beta * x * (x - a) * (x + a)
    sign_pos = beta * x * (a - x) * (a + x)  # equals -F
    Fp = F.dvar("x")
    # F' = beta (3 x^2 - a^2) and F'(a) = 2 beta a^2.
    Fp_claimed = beta * (C(VDP_VARS, 3) * (x ** 2) - (a ** 2))
    two_beta_a2 = C(VDP_VARS, 2) * beta * (a ** 2)
    tail = two_beta_a2 + C(VDP_VARS, 3) * beta * (x ** 2 - a ** 2)
    return {
        "F": F,
        "factored": factored,
        "factor_diff": F - factored,
        "minus_F": -F,
        "sign_pos": sign_pos,
        "sign_diff": (-F) - sign_pos,
        "Fprime": Fp,
        "Fprime_claimed": Fp_claimed,
        "Fprime_diff": Fp - Fp_claimed,
        "two_beta_a2": two_beta_a2,
        "tail": tail,
        "tail_diff": Fp - tail,
    }


def vdp_Fprime_at_a() -> Poly:
    """F'(a) - 2 beta a^2 as a polynomial in (a, beta)."""
    names = ("a", "beta")
    a, beta = V(names, "a"), V(names, "beta")
    # F'(x) = -beta a^2 + 3 beta x^2, so F'(a) = 2 beta a^2.
    Fp_at_a = -(beta * (a ** 2)) + C(names, 3) * beta * (a ** 2)
    return Fp_at_a - C(names, 2) * beta * (a ** 2)


def even_term_obstruction() -> dict[str, Poly]:
    x, alpha, beta, gamma = (V(EVEN_VARS, n) for n in EVEN_VARS)
    F = alpha * x + gamma * (x ** 2) + beta * (x ** 3)
    F_minus = alpha * (-x) + gamma * ((-x) ** 2) + beta * ((-x) ** 3)
    odd_sum = F + F_minus
    claimed = C(EVEN_VARS, 2) * gamma * (x ** 2)
    return {"odd_sum": odd_sum, "claimed": claimed, "diff": odd_sum - claimed}


def linear_identities() -> dict[str, Poly]:
    """beta = 0:  dx/dt = y - alpha x,  dy/dt = -x."""
    x, y, alpha = (V(LIN_VARS, n) for n in LIN_VARS)
    p = y - alpha * x
    q = -x
    # Jacobian [[-alpha, 1], [-1, 0]]; charpoly lambda^2 + alpha lambda + 1
    # is recorded as numbers, not a poly in lambda. Energy: -alpha x^2.
    e = (x * x + y * y).scale(1)  # 2E = x^2+y^2; d(2E)/dt = 2 dE/dt
    d2Edt = (x.scale(2) * p) + (y.scale(2) * q)
    claimed_2 = (alpha * (x ** 2)).scale(-2)
    return {
        "P": p,
        "Q": q,
        "d2Edt": d2Edt,
        "claimed_2": claimed_2,
        "diff": d2Edt - claimed_2,
    }


def check_samples() -> dict[str, int]:
    energy = energy_identities()
    for x in range(-3, 4):
        for y in range(-3, 4):
            for alpha in range(-3, 4):
                for beta in range(-3, 4):
                    vals = {"x": x, "y": y, "alpha": alpha, "beta": beta}
                    if energy["diff_claimed"].eval(vals) != 0:
                        raise AssertionError(f"energy identity failed at {vals}")
                    pv = energy["P"].eval(vals)
                    qv = energy["Q"].eval(vals)
                    if x == 0 and y == 0:
                        if pv != 0 or qv != 0:
                            raise AssertionError("origin is not an equilibrium")
                    if x == 0:
                        if pv != y or qv != 0:
                            raise AssertionError(f"x=0 slice is not (y,0) at {vals}")

    # Unique equilibrium: Q = -x = 0 forces x = 0, then P = y.
    if energy["Q"].eval({"x": 1, "y": 0, "alpha": 0, "beta": 0}) != -1:
        raise AssertionError("Q is not -x")

    # Sample van der Pol cousin: a=2, beta=1, alpha=-4.
    F_vals = {"x": 0, "alpha": -4, "beta": 1}
    F = F_identities()["F"]
    if F.eval({**F_vals, "x": 1}) != -3:
        raise AssertionError("F(1) for (alpha,beta)=(-4,1) should be -3")
    if F.eval({**F_vals, "x": 3}) != 15:
        raise AssertionError("F(3) for (alpha,beta)=(-4,1) should be 15")
    if F.eval({**F_vals, "x": 2}) != 0:
        raise AssertionError("F(2) should vanish (the unique positive root)")
    if F.eval({**F_vals, "x": -2}) != 0:
        raise AssertionError("F(-2) should vanish")
    Fp = F_identities()["Fprime"]
    if Fp.eval({**F_vals, "x": 2}) != 8:
        raise AssertionError("F'(2) should be 8 = 2*beta*a^2")
    if Fp.eval({**F_vals, "x": 0}) != -4:
        raise AssertionError("F'(0) should be alpha = -4")

    # No-cycle samples: dE/dt ≤ 0 and not identically zero.
    dEdt = energy["dEdt"]
    if dEdt.eval({"x": 1, "y": 0, "alpha": 1, "beta": 0}) != -1:
        raise AssertionError("linear damping energy at x=1")
    if dEdt.eval({"x": 1, "y": 0, "alpha": 0, "beta": 1}) != -1:
        raise AssertionError("pure cubic damping energy at x=1")
    if dEdt.eval({"x": 1, "y": 0, "alpha": 1, "beta": 1}) != -2:
        raise AssertionError("both-nonnegative energy at x=1")
    if dEdt.eval({"x": 0, "y": 5, "alpha": 1, "beta": 1}) != 0:
        raise AssertionError("energy vanishes on x=0")

    return {
        "sample_F_at_1": -3,
        "sample_F_at_3": 15,
        "sample_F_at_a": 0,
        "sample_Fprime_at_a": 8,
        "sample_Fprime_at_0": -4,
    }


def check_negative() -> None:
    x, y, alpha, beta = (V(ENERGY_VARS, n) for n in ENERGY_VARS)
    energy = energy_identities()
    bad = energy["dEdt"] + C(ENERGY_VARS, 1)
    claimed = energy["claimed"]
    if bad.equals(claimed):
        raise AssertionError("constant perturbation of dE/dt still matched")
    # Wrong power: -alpha x^2 - beta x^2 is not the energy derivative.
    wrong = -(alpha * (x ** 2) + beta * (x ** 2))
    if energy["dEdt"].equals(wrong):
        raise AssertionError("energy unexpectedly matched the wrong-power formula")
    if y.degree() != 1:
        raise AssertionError("y is missing from the energy ring")


def check_family() -> dict[str, int]:
    energy = energy_identities()
    _require_zero(energy["diff_claimed"], "energy claimed")
    _require_zero(energy["diff_factored"], "energy factored")
    if energy["dEdt"].is_zero():
        raise AssertionError("energy derivative is identically zero")

    F = F_identities()
    _require_zero(F["odd_sum"], "F odd")
    _require_zero(F["factor_diff"], "F = x(alpha + beta x^2)")
    _require_zero(F["Fprime_diff"], "F' = alpha + 3 beta x^2")
    _require_zero(F["fg_diff"], "fg numerator")

    vdp = vdp_identities()
    _require_zero(vdp["factor_diff"], "vdp F factorization")
    _require_zero(vdp["sign_diff"], "vdp -F = beta x (a-x)(a+x)")
    _require_zero(vdp["Fprime_diff"], "vdp F'")
    _require_zero(vdp["tail_diff"], "vdp tail F'")
    _require_zero(vdp_Fprime_at_a(), "F'(a) = 2 beta a^2")

    even = even_term_obstruction()
    _require_zero(even["diff"], "even-term oddness obstruction")
    if even["odd_sum"].is_zero():
        raise AssertionError("even term unexpectedly preserved oddness")

    lin = linear_identities()
    _require_zero(lin["diff"], "linear energy")

    samples = check_samples()
    check_negative()
    return {
        "energy_dEdt_terms": len(energy["dEdt"].terms),
        "energy_diff_terms": len(energy["diff_claimed"].terms),
        "F_terms": len(F["F"].terms),
        "F_odd_diff_terms": len(F["odd_sum"].terms),
        "F_factor_diff_terms": len(F["factor_diff"].terms),
        "Fprime_diff_terms": len(F["Fprime_diff"].terms),
        "fg_diff_terms": len(F["fg_diff"].terms),
        "vdp_factor_diff_terms": len(vdp["factor_diff"].terms),
        "vdp_sign_diff_terms": len(vdp["sign_diff"].terms),
        "vdp_tail_diff_terms": len(vdp["tail_diff"].terms),
        "even_odd_sum_terms": len(even["odd_sum"].terms),
        "linear_diff_terms": len(lin["diff"].terms),
        **samples,
    }


def build_family_certificate() -> dict:
    energy = energy_identities()
    F = F_identities()
    vdp = vdp_identities()
    even = even_term_obstruction()
    lin = linear_identities()
    return {
        "schema": "hilbert16-i-lienard-family/v1",
        "claim": (
            "Energy identity dE/dt = -alpha x^2 - beta x^4 for "
            "dx/dt = y-(alpha x + beta x^3), dy/dt = -x. "
            "Odd cubic F meets the Liénard algebraic hypotheses when "
            "beta>0 and alpha<0. Not a bound on planar H(n) or on all "
            "deg-F<=3 fields."
        ),
        "hn_moved": False,
        "H31_full_proved": False,
        "isolated_periodic_orbits_when_beta_pos_alpha_neg": 1,
        "isolated_periodic_orbits_when_alpha_beta_nonneg_not_both_zero": 0,
        "field": {
            "P": "y - (alpha*x + beta*x**3)",
            "Q": "-x",
        },
        "energy": {
            "variables": list(ENERGY_VARS),
            "P": energy["P"].to_terms(),
            "Q": energy["Q"].to_terms(),
            "dEdt": energy["dEdt"].to_terms(),
            "claimed": energy["claimed"].to_terms(),
            "factored": energy["factored"].to_terms(),
        },
        "F": {
            "variables": list(F_VARS),
            "F": F["F"].to_terms(),
            "factored": F["factored"].to_terms(),
            "Fprime": F["Fprime"].to_terms(),
            "fg_num": F["fg_num"].to_terms(),
            "odd_sum": F["odd_sum"].to_terms(),
        },
        "vdp_chart": {
            "variables": list(VDP_VARS),
            "substitution": "alpha = -beta * a**2",
            "F": vdp["F"].to_terms(),
            "factored": vdp["factored"].to_terms(),
            "minus_F": vdp["minus_F"].to_terms(),
            "sign_pos": vdp["sign_pos"].to_terms(),
            "Fprime": vdp["Fprime"].to_terms(),
            "two_beta_a2": vdp["two_beta_a2"].to_terms(),
            "tail": vdp["tail"].to_terms(),
        },
        "even_term": {
            "variables": list(EVEN_VARS),
            "odd_sum": even["odd_sum"].to_terms(),
            "claimed": even["claimed"].to_terms(),
            "note": "F(x)+F(-x)=2 gamma x^2. A quadratic term kills oddness; full deg-F<=3 is dropped.",
        },
        "linear": {
            "variables": list(LIN_VARS),
            "P": lin["P"].to_terms(),
            "Q": lin["Q"].to_terms(),
            "d2Edt": lin["d2Edt"].to_terms(),
            "charpoly": "lambda**2 + alpha*lambda + 1",
            "trace": "-alpha",
            "det": "1",
        },
        "cousin_of_van_der_Pol": {
            "classical_F": "mu*(x**3/3 - x)",
            "slice": "alpha = -mu, beta = mu/3, equivalently alpha + 3*beta = 0 with beta>0",
            "new_H3": False,
        },
        "what_this_is_not": [
            "not a dent of planar H(n)",
            "not a field that beats B(n)",
            "not a proof that every deg-F<=3 Liénard has at most one cycle",
            "not a new H(3)",
        ],
    }


def check_family_certificate(payload: dict) -> None:
    energy = energy_identities()
    block = payload["energy"]
    ev = tuple(block["variables"])
    if ev != ENERGY_VARS:
        raise AssertionError("energy variables mismatch")
    _require_match(ev, block["P"], energy["P"], "cert energy P")
    _require_match(ev, block["Q"], energy["Q"], "cert energy Q")
    _require_match(ev, block["dEdt"], energy["dEdt"], "cert dEdt")
    _require_match(ev, block["claimed"], energy["claimed"], "cert energy claimed")
    _require_match(ev, block["factored"], energy["factored"], "cert energy factored")

    F = F_identities()
    fblock = payload["F"]
    fv = tuple(fblock["variables"])
    _require_match(fv, fblock["F"], F["F"], "cert F")
    _require_match(fv, fblock["factored"], F["factored"], "cert F factored")
    _require_match(fv, fblock["Fprime"], F["Fprime"], "cert Fprime")
    _require_match(fv, fblock["fg_num"], F["fg_num"], "cert fg_num")
    _require_match(fv, fblock["odd_sum"], F["odd_sum"], "cert F odd_sum")

    vdp = vdp_identities()
    vblock = payload["vdp_chart"]
    vv = tuple(vblock["variables"])
    _require_match(vv, vblock["F"], vdp["F"], "cert vdp F")
    _require_match(vv, vblock["factored"], vdp["factored"], "cert vdp factored")
    _require_match(vv, vblock["minus_F"], vdp["minus_F"], "cert vdp minus_F")
    _require_match(vv, vblock["sign_pos"], vdp["sign_pos"], "cert vdp sign")
    _require_match(vv, vblock["Fprime"], vdp["Fprime"], "cert vdp Fprime")
    _require_match(vv, vblock["two_beta_a2"], vdp["two_beta_a2"], "cert two_beta_a2")
    _require_match(vv, vblock["tail"], vdp["tail"], "cert vdp tail")

    even = even_term_obstruction()
    eblock = payload["even_term"]
    evv = tuple(eblock["variables"])
    _require_match(evv, eblock["odd_sum"], even["odd_sum"], "cert even odd_sum")
    _require_match(evv, eblock["claimed"], even["claimed"], "cert even claimed")

    lin = linear_identities()
    lblock = payload["linear"]
    lv = tuple(lblock["variables"])
    _require_match(lv, lblock["P"], lin["P"], "cert linear P")
    _require_match(lv, lblock["Q"], lin["Q"], "cert linear Q")
    _require_match(lv, lblock["d2Edt"], lin["d2Edt"], "cert linear d2Edt")

    if payload.get("hn_moved") is not False:
        raise AssertionError("family cert must not claim that H(n) moved")
    if payload.get("H31_full_proved") is not False:
        raise AssertionError("family cert must not claim the full H(3,1) conjecture")
    if payload.get("cousin_of_van_der_Pol", {}).get("new_H3") is not False:
        raise AssertionError("must not claim a new H(3)")


def dump_lines(rows: list[dict[str, int]], counts: dict[str, int]) -> list[str]:
    lines = []
    for r in rows:
        lines.append(
            f"n {r['n']} N {r['N']} B {r['B']} HR {r['HR']} HR2 {r['HR2']} "
            f"Xiong {r['Xiong']} delta1 {r['delta1']} delta2 {r['delta2']} delta3 {r['delta3']}"
        )
    d1_neg = ",".join(str(r["n"]) for r in rows if r["delta1"] < 0)
    d1_zero = ",".join(str(r["n"]) for r in rows if r["delta1"] == 0)
    d2_zero = ",".join(str(r["n"]) for r in rows if r["delta2"] == 0)
    d3_pos = ",".join(str(r["n"]) for r in rows if r["delta3"] > 0)
    lines.extend(
        [
            "delta1_gt0_iff_n_ge 7",
            "delta2_gt0_iff_n_ge 13",
            f"delta1_negative_n {d1_neg}",
            f"delta1_zero_n {d1_zero}",
            f"delta2_zero_n {d2_zero}",
            f"delta3_positive_n {d3_pos}",
            "HR_formula_matches_N_substitution",
            f"energy_dEdt_terms {counts['energy_dEdt_terms']} difference {counts['energy_diff_terms']}",
            f"F_odd_difference {counts['F_odd_diff_terms']}",
            f"F_factor_difference {counts['F_factor_diff_terms']}",
            f"Fprime_difference {counts['Fprime_diff_terms']}",
            f"fg_numerator_difference {counts['fg_diff_terms']}",
            f"vdp_factor_difference {counts['vdp_factor_diff_terms']}",
            f"vdp_sign_difference {counts['vdp_sign_diff_terms']}",
            f"vdp_tail_difference {counts['vdp_tail_diff_terms']}",
            f"even_odd_sum_terms {counts['even_odd_sum_terms']}",
            f"linear_diff_terms {counts['linear_diff_terms']}",
            f"sample_a2_beta1 F(1)={counts['sample_F_at_1']} F(3)={counts['sample_F_at_3']} "
            f"F(a)={counts['sample_F_at_a']} Fprime(a)={counts['sample_Fprime_at_a']} "
            f"Fprime(0)={counts['sample_Fprime_at_0']}",
            "linear_charpoly lambda^2+alpha*lambda+1",
            "hn_moved 0",
            "beats_B_n 0",
            "H31_full_proved 0",
            "new_H3 0",
            "negative energy perturbation rejected",
        ]
    )
    return lines


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-cert", action="store_true")
    parser.add_argument("--dump", type=Path)
    args = parser.parse_args()

    rows = enumerate_rows()
    arith = check_arithmetic(rows)
    counts = check_family()
    family = build_family_certificate()
    check_family_certificate(family)

    if args.write_cert:
        write_json(ARITH_PATH, arith)
        write_json(FAMILY_PATH, family)
        print(f"wrote {ARITH_PATH}")
        print(f"wrote {FAMILY_PATH}")

    if not ARITH_PATH.is_file() or not FAMILY_PATH.is_file():
        raise SystemExit("missing certificates; run with --write-cert")

    saved_arith = json.loads(ARITH_PATH.read_text(encoding="utf-8"))
    saved_family = json.loads(FAMILY_PATH.read_text(encoding="utf-8"))
    if saved_arith != arith:
        raise AssertionError("committed arithmetic.json is not the canonical dump")
    check_family_certificate(saved_family)
    if saved_family != family:
        raise AssertionError("committed family.json is not the canonical dump")
    if saved_arith.get("hn_moved") is not False:
        raise AssertionError("arithmetic cert must not claim that H(n) moved")
    if saved_arith.get("beats_B_n") is not False:
        raise AssertionError("must not claim a field that beats B(n)")

    lines = dump_lines(rows, counts)
    text = "\n".join(lines) + "\n"
    if args.dump:
        args.dump.write_text(text, encoding="utf-8")
    print(text, end="")
    print("VALID i-lienard replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
