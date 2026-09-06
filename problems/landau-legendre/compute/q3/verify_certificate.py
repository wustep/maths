#!/usr/bin/env python3
"""Independently reconstruct and check the quadratic-Taylor RH certificate."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def decode(value: object) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise AssertionError("malformed rational")
    numerator = value["numerator"]
    denominator = value["denominator"]
    if not isinstance(numerator, str) or not isinstance(denominator, str):
        raise AssertionError("rational fields must be strings")
    result = Fraction(int(numerator), int(denominator))
    if encode(result) != value:
        raise AssertionError("rational is not normalized")
    return result


def unit_log(value: Fraction, count: int) -> tuple[Fraction, Fraction]:
    if not 1 <= value <= 2:
        raise AssertionError("range reduction failed")
    z = (value - 1) / (value + 1)
    total = sum(
        (2 * z ** (2 * index + 1) / (2 * index + 1) for index in range(count)),
        Fraction(0),
    )
    next_term_power = z ** (2 * count + 1)
    remainder = 2 * next_term_power / ((2 * count + 1) * (1 - z * z))
    return total, total + remainder


def enclose_log(value: Fraction, count: int) -> tuple[Fraction, Fraction]:
    if value <= 0:
        raise AssertionError("nonpositive logarithm input")
    power = 0
    normalized = value
    while normalized >= 2:
        normalized /= 2
        power += 1
    while normalized < 1:
        normalized *= 2
        power -= 1
    two_lower, two_upper = unit_log(Fraction(2), count)
    norm_lower, norm_upper = unit_log(normalized, count)
    shifted = (power * two_lower, power * two_upper)
    return min(shifted) + norm_lower, max(shifted) + norm_upper


def expected_certificate() -> dict[str, object]:
    n_value = 70_500_000_000_000
    delta = Fraction(4_504_880_398_387, 20_000_000_000_000)
    previous = Fraction(901, 4000)
    published = Fraction(2253, 10_000)
    terms = 16
    x_lower = Fraction(2_000_000_000_000)
    x_upper = Fraction(2_800_000_000_000)
    a_lower = Fraction(25)
    a_upper = Fraction(26)

    alpha = 2 + delta
    exponent = delta / alpha
    rhs_coefficient = Fraction(44, 25) / alpha
    quadratic_coefficient = (alpha - 1) / 2
    n_lower, n_upper = enclose_log(Fraction(n_value), terms)
    rhs_lower = rhs_coefficient * n_lower
    rhs_upper = rhs_coefficient * n_upper
    rhs_log_lower = enclose_log(rhs_lower, terms)[0]
    rhs_log_upper = enclose_log(rhs_upper, terms)[1]
    condition5_lower = exponent * n_lower - rhs_log_upper
    condition5_upper = exponent * n_upper - rhs_log_lower

    x_lower_margin = 2 / alpha * n_lower - enclose_log(x_lower, terms)[1]
    x_upper_margin = enclose_log(x_upper, terms)[0] - 2 / alpha * n_upper
    a_lower_margin = exponent * n_lower - enclose_log(a_lower, terms)[1]
    a_upper_margin = enclose_log(a_upper, terms)[0] - exponent * n_upper
    relative_lower = (
        quadratic_coefficient / x_upper
        - Fraction(1, 1) / (alpha * n_value * a_lower)
    )
    log1p_lower = relative_lower / (1 + relative_lower)
    taylor_overlap_lower = condition5_lower + log1p_lower
    derivative_lower = (
        delta / 2 * a_lower
        - Fraction(22, 25)
        - quadratic_coefficient * (1 - delta / 2) * a_upper / x_lower
    )
    record_margin = previous - delta

    assert 2 < alpha < 3
    assert condition5_upper < 0
    for margin in (
        x_lower_margin,
        x_upper_margin,
        a_lower_margin,
        a_upper_margin,
        relative_lower,
        taylor_overlap_lower,
        derivative_lower,
        record_margin,
        published - previous,
    ):
        assert margin > 0

    as_interval = lambda lower, upper: {
        "lower": encode(lower),
        "upper": encode(upper),
    }
    return {
        "schema": "landau-legendre.rh-delta-taylor.v1",
        "N": str(n_value),
        "delta": encode(delta),
        "previous_delta": encode(previous),
        "published_delta": encode(published),
        "terms": terms,
        "constants": {
            "alpha": encode(alpha),
            "overlap_exponent": encode(exponent),
            "rhs_coefficient": encode(rhs_coefficient),
            "quadratic_coefficient": encode(quadratic_coefficient),
        },
        "coarse_bounds": {
            "X_lower": encode(x_lower),
            "X_upper": encode(x_upper),
            "A_lower": encode(a_lower),
            "A_upper": encode(a_upper),
        },
        "ln_N": as_interval(n_lower, n_upper),
        "ln_rhs": as_interval(rhs_log_lower, rhs_log_upper),
        "condition5_log_margin": as_interval(condition5_lower, condition5_upper),
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


def decimal(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 24
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    actual = json.loads(args.certificate.read_text(encoding="utf-8"))

    def validate_rationals(value: object) -> None:
        if isinstance(value, dict):
            if set(value) == {"numerator", "denominator"}:
                decode(value)
            else:
                for child in value.values():
                    validate_rationals(child)
        elif isinstance(value, list):
            for child in value:
                validate_rationals(child)

    validate_rationals(actual)
    if actual != expected_certificate():
        raise AssertionError("certificate differs from independent reconstruction")

    basic_upper = decode(actual["condition5_log_margin"]["upper"])
    taylor_lower = decode(actual["taylor_overlap_log_lower"])
    derivative_lower = decode(actual["derivative_lower"])
    print(
        "PASS rh_delta_taylor",
        "delta=0.22524401991935",
        f"condition5_upper={decimal(basic_upper)}",
        f"taylor_overlap_lower={decimal(taylor_lower)}",
        f"derivative_lower={decimal(derivative_lower)}",
    )


if __name__ == "__main__":
    main()
