#!/usr/bin/env python3
"""Independent checks for q2's unitary-factorization output.

This verifier deliberately does not import ``unitary_factorization.py``.
It validates every emitted factor certificate and direct-square hit through
n = 100, then exhaustively enumerates every prime-block subset through n = 50
with a simpler brute-force routine to check the reported minimum gaps.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "q2-results.json"
OUTPUT = HERE / "q2-verification.txt"


def trial_primes(bound: int) -> list[int]:
    primes: list[int] = []
    for candidate in range(2, bound + 1):
        if all(candidate % divisor for divisor in range(2, math.isqrt(candidate) + 1)):
            primes.append(candidate)
    return primes


def valuation_of_factorial(n: int, p: int) -> int:
    return sum(n // (p**power) for power in range(1, n.bit_length() + 1) if p**power <= n)


def blocks_of_factorial_quarter(n: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for p in trial_primes(n):
        exponent = valuation_of_factorial(n, p) - (2 if p == 2 else 0)
        if exponent:
            result.append((p, p**exponent))
    return result


def brute_minimum_gap(blocks: list[tuple[int, int]]) -> int:
    divisors = [1]
    for _, block in blocks:
        divisors.extend(value * block for value in tuple(divisors))
    total = math.prod(block for _, block in blocks)
    return min(total // divisor - divisor for divisor in divisors if divisor * divisor <= total)


def direct_solutions(max_n: int) -> list[dict[str, int]]:
    factorial = 1
    hits: list[dict[str, int]] = []
    for n in range(1, max_n + 1):
        factorial *= n
        if n >= 4:
            root = math.isqrt(factorial + 1)
            if root**2 == factorial + 1:
                hits.append({"n": n, "m": root})
    return hits


def main() -> None:
    raw = RESULTS.read_bytes()
    data = json.loads(raw)
    lower, upper = data["range_inclusive"]
    if lower != 4:
        raise AssertionError("unexpected lower bound")

    records = {record["n"]: record for record in data["records"]}
    if sorted(records) != list(range(lower, upper + 1)):
        raise AssertionError("missing or duplicate q2 records")

    for n, record in records.items():
        blocks = blocks_of_factorial_quarter(n)
        quarter = math.factorial(n) // 4
        a = int(record["closest_a"])
        b = int(record["closest_b"])
        gap = int(record["gap"])
        if math.prod(block for _, block in blocks) != quarter:
            raise AssertionError(f"block reconstruction failed at n={n}")
        if a * b != quarter or b - a != gap or math.gcd(a, b) != 1:
            raise AssertionError(f"factor certificate failed at n={n}")
        small = set(record["small_factor_primes"])
        if small | set(record["large_factor_primes"]) != {p for p, _ in blocks}:
            raise AssertionError(f"prime allocation incomplete at n={n}")
        rebuilt_a = math.prod(block for p, block in blocks if p in small)
        if rebuilt_a != a:
            raise AssertionError(f"small-factor allocation failed at n={n}")
        if n <= 50 and brute_minimum_gap(blocks) != gap:
            raise AssertionError(f"independent minimum-gap check failed at n={n}")

    direct = direct_solutions(upper)
    if direct != data["direct_square_solutions"]:
        raise AssertionError("independent direct-square scan disagreed")
    if direct != [{"n": 4, "m": 5}, {"n": 5, "m": 11}, {"n": 7, "m": 71}]:
        raise AssertionError("unexpected direct-square hits")

    for solution in data["structural_solutions"]:
        n = solution["n"]
        m = solution["m"]
        for sign in solution["odd_prime_power_signs"]:
            modulus = int(sign["modulus"])
            if ((m - 1) % modulus, (m + 1) % modulus).count(0) != 1:
                raise AssertionError(f"prime-power concentration failed for n={n}")

    lines = [
        "Brocard--Ramanujan q2 independent verification",
        f"q2-results.json sha256: {hashlib.sha256(raw).hexdigest()}",
        f"validated every emitted factor certificate for n={lower}..{upper}",
        "brute-force subset enumeration independently matched every minimum gap for n=4..50",
        f"direct integer-square scan through n={upper}: {direct}",
        "all recorded full odd-prime-power signs divide exactly one of m-1 and m+1",
        "verification: PASS",
        "",
    ]
    output = "\n".join(lines)
    OUTPUT.write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
