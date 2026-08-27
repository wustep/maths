#!/usr/bin/env python3
"""Create the exact certificate for the RH conditional overlap."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

N = 70_500_000_000_000
DELTA = Fraction(901, 4000)
PUBLISHED_DELTA = Fraction(2253, 10_000)
TERMS = 8

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def rational(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def unit_log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    if not Fraction(1) <= value <= Fraction(2):
        raise ValueError("unit logarithm input must lie in [1, 2]")
    z = (value - 1) / (value + 1)
    partial = Fraction(0)
    power = z
    for j in range(terms):
        partial += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return partial, partial + tail


def log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    if value <= 0:
        raise ValueError("logarithm input must be positive")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if exponent >= 0:
        reduced = value / (1 << exponent)
    else:
        reduced = value * (1 << (-exponent))
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


def build_certificate() -> dict[str, object]:
    alpha = 2 + DELTA
    exponent = DELTA / alpha
    coefficient = Fraction(44, 25) / alpha
    log_n_lower, log_n_upper = log_bounds(Fraction(N), TERMS)
    rhs_lower = coefficient * log_n_lower
    rhs_upper = coefficient * log_n_upper
    log_rhs_lower = log_bounds(rhs_lower, TERMS)[0]
    log_rhs_upper = log_bounds(rhs_upper, TERMS)[1]
    overlap_lower = exponent * log_n_lower - log_rhs_upper
    overlap_upper = exponent * log_n_upper - log_rhs_lower
    monotonicity_lower = exponent * log_n_lower - 1
    comparison_margin = PUBLISHED_DELTA - DELTA
    if min(overlap_lower, monotonicity_lower, comparison_margin) <= 0:
        raise ArithmeticError("certificate margin is not positive")

    interval = lambda lo, hi: {"lower": rational(lo), "upper": rational(hi)}
    return {
        "schema": "landau-legendre.rh-delta.v1",
        "N": str(N),
        "delta": rational(DELTA),
        "published_delta": rational(PUBLISHED_DELTA),
        "terms": TERMS,
        "constants": {
            "alpha": rational(alpha),
            "overlap_exponent": rational(exponent),
            "rhs_coefficient": rational(coefficient),
        },
        "ln_N": interval(log_n_lower, log_n_upper),
        "ln_rhs": interval(log_rhs_lower, log_rhs_upper),
        "overlap_margin": interval(overlap_lower, overlap_upper),
        "monotonicity_margin_lower": rational(monotonicity_lower),
        "published_comparison_margin": rational(comparison_margin),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
