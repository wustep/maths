#!/usr/bin/env python3
"""Write and sample-check the Wilson-offset Brocard certificate.

The proof rows are symbolic: for p = n + c, Wilson's theorem determines n!
modulo p.  The bounded prime scan is only a replay check of those rows, not
the reason that the families are infinite.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROWS = ((2, 3, 2, 1), (2, 5, 2, 1), (3, 3, 1, 2), (3, 5, 1, 2))


def primes_through(bound: int) -> list[int]:
    sieve = bytearray(b"\x01") * (bound + 1)
    if bound >= 0:
        sieve[0] = 0
    if bound >= 1:
        sieve[1] = 0
    for p in range(2, int(bound**0.5) + 1):
        if sieve[p]:
            sieve[p * p : bound + 1 : p] = b"\x00" * (
                (bound - p * p) // p + 1
            )
    return [p for p in range(2, bound + 1) if sieve[p]]


def factorial_mod(n: int, p: int) -> int:
    value = 1
    for factor in range(2, n + 1):
        value = value * factor % p
    return value


def is_square_mod(value: int, p: int) -> bool:
    value %= p
    return value == 0 or pow(value, (p - 1) // 2, p) == 1


def replay_row(
    primes: list[int], offset: int, prime_residue: int, numerator: int, denominator: int
) -> dict[str, int]:
    tested = [p for p in primes if p > offset and p % 8 == prime_residue]
    for p in tested:
        n = p - offset
        observed = (factorial_mod(n, p) + 1) % p
        expected = numerator * pow(denominator, -1, p) % p
        assert observed == expected
        assert not is_square_mod(expected, p)
    return {
        "offset": offset,
        "prime_residue_mod_8": prime_residue,
        "index_residue_mod_8": (prime_residue - offset) % 8,
        "target_numerator": numerator,
        "target_denominator": denominator,
        "sample_prime_count": len(tested),
        "first_sample_prime": tested[0],
        "last_sample_prime": tested[-1],
    }


def render_sample(bound: int, rows: list[dict[str, int]]) -> str:
    lines = ["Wilson-offset Brocard certificate sample", f"prime_bound={bound}"]
    for row in rows:
        lines.append(
            "offset={offset},prime_mod_8={prime_residue_mod_8},"
            "index_mod_8={index_residue_mod_8},count={sample_prime_count},"
            "first={first_sample_prime},last={last_sample_prime}".format(**row)
        )
    lines.append("verification=PASS")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-bound", type=int, default=10_000)
    args = parser.parse_args()
    if args.prime_bound < 13:
        raise SystemExit("--prime-bound must be at least 13")

    primes = primes_through(args.prime_bound)
    rows = [replay_row(primes, *row) for row in ROWS]
    certificate = {
        "schema_version": 1,
        "claim": (
            "For each row, no Brown index n=p-c exists when p is prime in "
            "the stated class modulo 8. Each family is infinite by Dirichlet."
        ),
        "proof_identity": (
            "If p=n+c is prime, Wilson gives "
            "n! = (-1)^c / (c-1)! (mod p)."
        ),
        "nonresidue_fact": "2 is a non-square modulo primes p = 3 or 5 (mod 8).",
        "sample_prime_bound": args.prime_bound,
        "rows": rows,
    }
    (HERE / "offset-certificate.json").write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    sample = render_sample(args.prime_bound, rows)
    (HERE / "python-sample.txt").write_text(sample)
    print(sample, end="")


if __name__ == "__main__":
    main()
