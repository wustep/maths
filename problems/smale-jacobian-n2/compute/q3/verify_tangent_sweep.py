#!/usr/bin/env python3
"""Formal-coefficient check of the two-dimensional tangent-sweep obstruction."""

from __future__ import annotations

import json
from pathlib import Path

AtomMonomial = tuple[str, ...]
Expression = dict[AtomMonomial, int]
Polynomial = dict[tuple[int, int], Expression]  # powers of w and gamma


def expression_add(left: Expression, right: Expression) -> Expression:
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if answer[monomial] == 0:
            del answer[monomial]
    return answer


def expression_scale(value: int, expression: Expression) -> Expression:
    return {
        monomial: value * coefficient
        for monomial, coefficient in expression.items()
        if value * coefficient
    }


def expression_multiply(left: Expression, right: Expression) -> Expression:
    answer: Expression = {}
    for left_monomial, left_value in left.items():
        for right_monomial, right_value in right.items():
            monomial = tuple(sorted(left_monomial + right_monomial))
            answer[monomial] = answer.get(monomial, 0) + left_value * right_value
            if answer[monomial] == 0:
                del answer[monomial]
    return answer


def polynomial_add(left: Polynomial, right: Polynomial) -> Polynomial:
    answer = {powers: dict(expression) for powers, expression in left.items()}
    for powers, expression in right.items():
        answer[powers] = expression_add(answer.get(powers, {}), expression)
        if not answer[powers]:
            del answer[powers]
    return answer


def polynomial_scale(value: int, polynomial: Polynomial) -> Polynomial:
    return {
        powers: scaled
        for powers, expression in polynomial.items()
        if (scaled := expression_scale(value, expression))
    }


def polynomial_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    answer: Polynomial = {}
    for (lw, lg), left_expression in left.items():
        for (rw, rg), right_expression in right.items():
            powers = (lw + rw, lg + rg)
            product = expression_multiply(left_expression, right_expression)
            answer[powers] = expression_add(answer.get(powers, {}), product)
            if not answer[powers]:
                del answer[powers]
    return answer


def derivative(polynomial: Polynomial, variable: int) -> Polynomial:
    answer: Polynomial = {}
    for powers, expression in polynomial.items():
        exponent = powers[variable]
        if exponent:
            reduced = list(powers)
            reduced[variable] -= 1
            answer[tuple(reduced)] = expression_scale(exponent, expression)
    return answer


def atom_polynomial(prefix: str, degree: int) -> Polynomial:
    return {
        (exponent, 0): {(f"{prefix}{exponent}",): 1}
        for exponent in range(degree + 1)
    }


def gamma_times(polynomial: Polynomial) -> Polynomial:
    gamma: Polynomial = {(0, 1): {(): 1}}
    return polynomial_multiply(gamma, polynomial)


def jacobian(first: Polynomial, second: Polynomial) -> Polynomial:
    return polynomial_add(
        polynomial_multiply(derivative(first, 0), derivative(second, 1)),
        polynomial_scale(-1, polynomial_multiply(derivative(first, 1), derivative(second, 0))),
    )


def verify_degree(degree: int) -> None:
    p = atom_polynomial("p", degree)
    q = atom_polynomial("q", degree)
    p_prime = derivative(p, 0)
    q_prime = derivative(q, 0)
    sweep_p = polynomial_add(p, gamma_times(p_prime))
    sweep_q = polynomial_add(q, gamma_times(q_prime))

    actual = jacobian(sweep_p, sweep_q)
    curvature = polynomial_add(
        polynomial_multiply(derivative(p_prime, 0), q_prime),
        polynomial_scale(-1, polynomial_multiply(p_prime, derivative(q_prime, 0))),
    )
    expected = gamma_times(curvature)
    assert actual == expected
    assert all(gamma_power >= 1 for _, gamma_power in actual)
    print(f"TANGENT_SWEEP_IDENTITY_PASS symbolic_degree={degree}")


def main() -> None:
    root = Path(__file__).resolve().parent
    certificate = json.loads((root / "certificate.json").read_text())
    for degree in certificate["symbolic_degrees_checked"]:
        verify_degree(degree)
    print("Q3_TANGENT_SWEEP_OBSTRUCTION_PASS")


if __name__ == "__main__":
    main()

