#!/usr/bin/env python3
"""Build an exact rational certificate for the quadratic-Taylor RH splice."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

N = 70_500_000_000_000
DELTA = Fraction("0.22524401991935")
PREVIOUS_DELTA = Fraction(901, 4000)
PUBLISHED_DELTA = Fraction(2253, 10_000)
TERMS = 16
X_LOWER = Fraction(2_000_000_000_000)
X_UPPER = Fraction(2_800_000_000_000)
A_LOWER = Fraction(25)
A_UPPER = Fraction(26)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def unit_log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    if not Fraction(1) <= value <= Fraction(2):
        raise ValueError("unit logarithm input must lie in [1, 2]")
    z = (value - 1) / (value + 1)
    partial = Fraction(0)
    power = z
    for index in range(terms):
        partial += 2 * power / (2 * index + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return partial, partial + tail


def log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    if value <= 0:
        raise ValueError("logarithm input must be positive")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    reduced = value / (1 << exponent) if exponent >= 0 else value * (1 << -exponent)
    while reduced < 1:
        exponent -= 1
        reduced *= 2
    while reduced >= 2:
        exponent += 1
        reduced /= 2
    log2_lower, log2_upper = unit_log_bounds(Fraction(2), terms)
    reduced_lower, reduced_upper = unit_log_bounds(reduced, terms)
    if exponent >= 0:
        return (
            exponent * log2_lower + reduced_lower,
            exponent * log2_upper + reduced_upper,
        )
    return (
        exponent * log2_upper + reduced_lower,
        exponent * log2_lower + reduced_upper,
    )


def interval(lower: Fraction, upper: Fraction) -> dict[str, dict[str, str]]:
    return {"lower": encode(lower), "upper": encode(upper)}


def build_certificate() -> dict[str, object]:
    alpha = 2 + DELTA
    exponent = DELTA / alpha
    rhs_coefficient = Fraction(44, 25) / alpha
    quadratic_coefficient = (alpha - 1) / 2

    log_n_lower, log_n_upper = log_bounds(Fraction(N), TERMS)
    rhs_lower = rhs_coefficient * log_n_lower
    rhs_upper = rhs_coefficient * log_n_upper
    log_rhs_lower = log_bounds(rhs_lower, TERMS)[0]
    log_rhs_upper = log_bounds(rhs_upper, TERMS)[1]
    condition5_lower = exponent * log_n_lower - log_rhs_upper
    condition5_upper = exponent * log_n_upper - log_rhs_lower

    log_x_lower = Fraction(2, 1) / alpha * log_n_lower
    log_x_upper = Fraction(2, 1) / alpha * log_n_upper
    log_a_lower = exponent * log_n_lower
    log_a_upper = exponent * log_n_upper
    x_lower_margin = log_x_lower - log_bounds(X_LOWER, TERMS)[1]
    x_upper_margin = log_bounds(X_UPPER, TERMS)[0] - log_x_upper
    a_lower_margin = log_a_lower - log_bounds(A_LOWER, TERMS)[1]
    a_upper_margin = log_bounds(A_UPPER, TERMS)[0] - log_a_upper

    relative_lower = (
        quadratic_coefficient / X_UPPER
        - Fraction(1, 1) / (alpha * N * A_LOWER)
    )
    log1p_lower = relative_lower / (1 + relative_lower)
    taylor_overlap_lower = condition5_lower + log1p_lower

    derivative_lower = (
        DELTA / 2 * A_LOWER
        - Fraction(22, 25)
        - quadratic_coefficient
        * (1 - DELTA / 2)
        * A_UPPER
        / X_LOWER
    )
    record_margin = PREVIOUS_DELTA - DELTA

    positive = [
        x_lower_margin,
        x_upper_margin,
        a_lower_margin,
        a_upper_margin,
        relative_lower,
        taylor_overlap_lower,
        derivative_lower,
        record_margin,
        PUBLISHED_DELTA - PREVIOUS_DELTA,
    ]
    if min(positive) <= 0:
        raise ArithmeticError("a required exact margin is not positive")
    if condition5_upper >= 0:
        raise ArithmeticError("the candidate unexpectedly satisfies condition (5)")

    return {
        "schema": "landau-legendre.rh-delta-taylor.v1",
        "N": str(N),
        "delta": encode(DELTA),
        "previous_delta": encode(PREVIOUS_DELTA),
        "published_delta": encode(PUBLISHED_DELTA),
        "terms": TERMS,
        "constants": {
            "alpha": encode(alpha),
            "overlap_exponent": encode(exponent),
            "rhs_coefficient": encode(rhs_coefficient),
            "quadratic_coefficient": encode(quadratic_coefficient),
        },
        "coarse_bounds": {
            "X_lower": encode(X_LOWER),
            "X_upper": encode(X_UPPER),
            "A_lower": encode(A_LOWER),
            "A_upper": encode(A_UPPER),
        },
        "ln_N": interval(log_n_lower, log_n_upper),
        "ln_rhs": interval(log_rhs_lower, log_rhs_upper),
        "condition5_log_margin": interval(condition5_lower, condition5_upper),
        "coarse_log_margins": {
            "X_above_lower": encode(x_lower_margin),
            "X_below_upper": encode(x_upper_margin),
            "A_above_lower": encode(a_lower_margin),
            "A_below_upper": encode(a_upper_margin),
        },
        "taylor_relative_lower": encode(relative_lower),
        "log1p_lower": encode(log1p_lower),
        "taylor_overlap_log_lower": encode(taylor_overlap_lower),
        "derivative_lower": encode(derivative_lower),
        "previous_comparison_margin": encode(record_margin),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
