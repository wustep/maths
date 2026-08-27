#!/usr/bin/env python3
"""Exact sparse checks for the homogeneous plane Keller family."""

from __future__ import annotations

import json
from pathlib import Path

Polynomial = dict[tuple[int, int], int]


def clean(polynomial: Polynomial) -> Polynomial:
    return {monomial: value for monomial, value in polynomial.items() if value}


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    answer = dict(left)
    for monomial, value in right.items():
        answer[monomial] = answer.get(monomial, 0) + value
    return clean(answer)


def scale(value: int, polynomial: Polynomial) -> Polynomial:
    return clean({monomial: value * coefficient for monomial, coefficient in polynomial.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for (lx, ly), left_value in left.items():
        for (rx, ry), right_value in right.items():
            monomial = (lx + rx, ly + ry)
            answer[monomial] = answer.get(monomial, 0) + left_value * right_value
    return clean(answer)


def power(base: Polynomial, exponent: int) -> Polynomial:
    answer: Polynomial = {(0, 0): 1}
    while exponent:
        if exponent & 1:
            answer = multiply(answer, base)
        base = multiply(base, base)
        exponent //= 2
    return answer


def derivative(polynomial: Polynomial, variable: int) -> Polynomial:
    answer: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        exponent = exponents[variable]
        if exponent:
            reduced = list(exponents)
            reduced[variable] -= 1
            answer[tuple(reduced)] = coefficient * exponent
    return answer


def jacobian(first: Polynomial, second: Polynomial) -> Polynomial:
    return add(
        multiply(derivative(first, 0), derivative(second, 1)),
        scale(-1, multiply(derivative(first, 1), derivative(second, 0))),
    )


def degree(polynomial: Polynomial) -> int:
    return max(sum(monomial) for monomial in polynomial)


def verify_case(d: int, a: int, b: int, c: int) -> None:
    x: Polynomial = {(1, 0): 1}
    y: Polynomial = {(0, 1): 1}
    linear = add(scale(a, x), scale(b, y))
    nonlinear = scale(c, power(linear, d))
    first = add(x, scale(b, nonlinear))
    second = add(y, scale(-a, nonlinear))

    invariant = add(scale(a, first), scale(b, second))
    assert invariant == linear
    assert jacobian(first, second) == {(0, 0): 1}

    inverse_first_after_map = add(first, scale(-b * c, power(invariant, d)))
    inverse_second_after_map = add(second, scale(a * c, power(invariant, d)))
    assert inverse_first_after_map == x
    assert inverse_second_after_map == y

    inverse_first = add(x, scale(-b, nonlinear))
    inverse_second = add(y, scale(a, nonlinear))
    inverse_invariant = add(scale(a, inverse_first), scale(b, inverse_second))
    assert inverse_invariant == linear
    map_first_after_inverse = add(inverse_first, scale(b * c, power(inverse_invariant, d)))
    map_second_after_inverse = add(inverse_second, scale(-a * c, power(inverse_invariant, d)))
    assert map_first_after_inverse == x
    assert map_second_after_inverse == y
    assert degree(first) == d or b * c == 0
    assert degree(second) == d or a * c == 0

    print(f"HOMOGENEOUS_FAMILY_PASS degree={d} a={a} b={b} c={c}")


def main() -> None:
    root = Path(__file__).resolve().parent
    certificate = json.loads((root / "certificate.json").read_text())
    for case in certificate["exact_cases"]:
        verify_case(case["degree"], case["a"], case["b"], case["c"])
    print("Q2_HOMOGENEOUS_CLASS_PASS")


if __name__ == "__main__":
    main()
