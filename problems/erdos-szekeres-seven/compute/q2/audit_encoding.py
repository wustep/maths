#!/usr/bin/env python3
"""Exhaust the local truth tables used by encode.py."""

from __future__ import annotations

import itertools

from encode import parity_clauses, signotope_clauses


def satisfies(clause: list[int], values: dict[int, int]) -> bool:
    return any(values[abs(literal)] == (literal > 0) for literal in clause)


def main() -> None:
    variables = [1, 2, 3, 4]
    signotope = list(signotope_clauses(variables))
    parity = list(parity_clauses(variables, 5))
    assert len(signotope) == 8
    assert len(parity) == 16

    allowed_sign_sequences = 0
    parity_rows = 0
    for bits in itertools.product((0, 1), repeat=4):
        values = dict(zip(variables, bits))
        allowed = all(satisfies(clause, values) for clause in signotope)
        expected = sum(bits[i] != bits[i + 1] for i in range(3)) <= 1
        assert allowed == expected
        allowed_sign_sequences += allowed

        for parity_bit in (0, 1):
            values[5] = parity_bit
            accepted = all(satisfies(clause, values) for clause in parity)
            assert accepted == (parity_bit == (sum(bits) & 1))
            parity_rows += accepted

    assert allowed_sign_sequences == 8
    assert parity_rows == 16
    print("encoding audit: 8 signotope patterns and all 16 XOR rows verified")


if __name__ == "__main__":
    main()
