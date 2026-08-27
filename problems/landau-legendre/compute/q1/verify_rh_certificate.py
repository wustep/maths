#!/usr/bin/env python3
"""Independently reconstruct and verify the RH overlap certificate."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def decode_fraction(value: object) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise AssertionError("malformed rational")
    numerator = value["numerator"]
    denominator = value["denominator"]
    if not isinstance(numerator, str) or not isinstance(denominator, str):
        raise AssertionError("rational fields must be decimal strings")
    result = Fraction(int(numerator), int(denominator))
    if encode_fraction(result) != value:
        raise AssertionError("rational is not normalized")
    return result


def series_log_on_unit(value: Fraction, count: int) -> tuple[Fraction, Fraction]:
    if value < 1 or value > 2:
        raise AssertionError("range reduction failed")
    transform = (value - 1) / (value + 1)
    total = Fraction(0)
    for index in range(count):
        total += 2 * transform ** (2 * index + 1) / (2 * index + 1)
    next_power = transform ** (2 * count + 1)
    error = 2 * next_power / ((2 * count + 1) * (1 - transform * transform))
    return total, total + error


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
    two_lo, two_hi = series_log_on_unit(Fraction(2), count)
    norm_lo, norm_hi = series_log_on_unit(normalized, count)
    candidates = (power * two_lo, power * two_hi)
    return min(candidates) + norm_lo, max(candidates) + norm_hi


def expected_certificate() -> dict[str, object]:
    n_value = 70_500_000_000_000
    delta = Fraction(901, 4000)
    published = Fraction(2253, 10_000)
    terms = 8
    alpha = Fraction(2) + delta
    overlap_power = delta / alpha
    rhs_coefficient = Fraction(44, 25) / alpha

    n_lo, n_hi = enclose_log(Fraction(n_value), terms)
    rhs_input_lo = rhs_coefficient * n_lo
    rhs_input_hi = rhs_coefficient * n_hi
    rhs_lo = enclose_log(rhs_input_lo, terms)[0]
    rhs_hi = enclose_log(rhs_input_hi, terms)[1]
    f_lo = overlap_power * n_lo - rhs_hi
    f_hi = overlap_power * n_hi - rhs_lo
    derivative_lo = overlap_power * n_lo - 1
    published_margin = published - delta

    if f_lo <= 0 or derivative_lo <= 0 or published_margin <= 0:
        raise AssertionError("an exact sign check failed")

    as_interval = lambda lo, hi: {
        "lower": encode_fraction(lo),
        "upper": encode_fraction(hi),
    }
    return {
        "schema": "landau-legendre.rh-delta.v1",
        "N": str(n_value),
        "delta": encode_fraction(delta),
        "published_delta": encode_fraction(published),
        "terms": terms,
        "constants": {
            "alpha": encode_fraction(alpha),
            "overlap_exponent": encode_fraction(overlap_power),
            "rhs_coefficient": encode_fraction(rhs_coefficient),
        },
        "ln_N": as_interval(n_lo, n_hi),
        "ln_rhs": as_interval(rhs_lo, rhs_hi),
        "overlap_margin": as_interval(f_lo, f_hi),
        "monotonicity_margin_lower": encode_fraction(derivative_lo),
        "published_comparison_margin": encode_fraction(published_margin),
    }


def decimal_string(value: Fraction) -> str:
    with localcontext() as context:
        context.prec = 18
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    actual = json.loads(args.certificate.read_text(encoding="utf-8"))

    def walk_rationals(value: object) -> None:
        if isinstance(value, dict):
            if set(value) == {"numerator", "denominator"}:
                decode_fraction(value)
            else:
                for child in value.values():
                    walk_rationals(child)
        elif isinstance(value, list):
            for child in value:
                walk_rationals(child)

    walk_rationals(actual)
    expected = expected_certificate()
    if actual != expected:
        raise AssertionError("certificate differs from independent reconstruction")
    margin = decode_fraction(actual["overlap_margin"]["lower"])
    monotone = decode_fraction(actual["monotonicity_margin_lower"])
    print(
        "PASS rh_delta",
        "delta=901/4000",
        f"overlap_lower={decimal_string(margin)}",
        f"monotonicity_lower={decimal_string(monotone)}",
    )


if __name__ == "__main__":
    main()
