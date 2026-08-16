#!/usr/bin/env python3
"""Explore the exact consecutive-factor form of the Brown equation.

For n >= 4, a solution n! + 1 = m^2 is equivalent to

    n! / 4 = a (a + 1),   m = 2a + 1.

Because gcd(a, a + 1) = 1, every prime-power block in n! / 4 must be
assigned wholly to one factor.  Thus a is a *unitary divisor* of n! / 4.
This script enumerates those choices exactly with meet in the middle and
finds the closest possible factor pair around sqrt(n! / 4).

The default n <= 100 range is an illustration of the structural condition,
not an extension of q1's much larger quadratic-residue sieve bound.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_JSON = HERE / "q2-results.json"
DEFAULT_LOG = HERE / "q2-run.txt"


def primes_up_to(bound: int) -> list[int]:
    """Return all primes at most ``bound`` by an Eratosthenes sieve."""

    if bound < 2:
        return []
    sieve = bytearray(b"\x01") * (bound + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(bound) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : bound + 1 : p] = b"\x00" * (((bound - start) // p) + 1)
    return [p for p, flag in enumerate(sieve) if flag]


def factorial_valuation(n: int, prime: int) -> int:
    """Legendre's exact exponent of ``prime`` in ``n!``."""

    exponent = 0
    quotient = n
    while quotient:
        quotient //= prime
        exponent += quotient
    return exponent


def factorial_quarter_blocks(n: int) -> list[tuple[int, int]]:
    """Pair each prime with its full prime-power block in ``n! / 4``."""

    if n < 4:
        raise ValueError("n! / 4 is integral only in the range used here, n >= 4")
    blocks: list[tuple[int, int]] = []
    for prime in primes_up_to(n):
        exponent = factorial_valuation(n, prime) - (2 if prime == 2 else 0)
        if exponent > 0:
            blocks.append((prime, prime**exponent))
    return blocks


def subset_products(blocks: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return (product, mask) for every subset of the supplied blocks."""

    products = [(1, 0)]
    for index, (_, block) in enumerate(blocks):
        bit = 1 << index
        products += [(value * block, mask | bit) for value, mask in products]
    return products


def selected_primes(blocks: list[tuple[int, int]], mask: int) -> list[int]:
    return [prime for index, (prime, _) in enumerate(blocks) if mask & (1 << index)]


def closest_unitary_pair(
    blocks: list[tuple[int, int]],
) -> tuple[int, int, int, list[int], list[int]]:
    """Find the exact unitary divisor pair with smallest nonnegative gap.

    Every unitary divisor is a subset product of the pairwise-coprime blocks.
    Among divisors ``a <= sqrt(N)``, the gap ``N/a - a`` decreases as ``a``
    increases.  It therefore suffices to find the largest subset product not
    exceeding ``isqrt(N)``.  Meet in the middle enumerates both half-subsets.
    """

    midpoint = len(blocks) // 2
    left_blocks = blocks[:midpoint]
    right_blocks = blocks[midpoint:]
    left = subset_products(left_blocks)
    right = sorted(subset_products(right_blocks))
    right_values = [value for value, _ in right]

    total = math.prod(block for _, block in blocks)
    root = math.isqrt(total)
    best_value = 1
    best_left_mask = 0
    best_right_mask = 0
    for left_value, left_mask in left:
        if left_value > root:
            continue
        index = bisect_right(right_values, root // left_value) - 1
        if index < 0:
            continue
        right_value, right_mask = right[index]
        candidate = left_value * right_value
        if candidate > best_value:
            best_value = candidate
            best_left_mask = left_mask
            best_right_mask = right_mask

    small_primes = selected_primes(left_blocks, best_left_mask) + selected_primes(
        right_blocks, best_right_mask
    )
    small_prime_set = set(small_primes)
    large_primes = [prime for prime, _ in blocks if prime not in small_prime_set]
    other = total // best_value
    return best_value, other, other - best_value, small_primes, large_primes


def direct_square_solutions(max_n: int) -> list[dict[str, int]]:
    factorial = 1
    solutions: list[dict[str, int]] = []
    for n in range(max_n + 1):
        if n:
            factorial *= n
        if n < 4:
            continue
        root = math.isqrt(factorial + 1)
        if root * root == factorial + 1:
            solutions.append({"n": n, "m": root})
    return solutions


def prime_power_signs(n: int, m: int) -> list[dict[str, object]]:
    """Record the full odd-prime-power congruence selected by a solution."""

    signs: list[dict[str, object]] = []
    for prime in primes_up_to(n):
        if prime == 2:
            continue
        modulus = prime ** factorial_valuation(n, prime)
        minus = (m - 1) % modulus == 0
        plus = (m + 1) % modulus == 0
        if minus == plus:
            raise AssertionError("an odd prime power must divide exactly one neighbor")
        signs.append(
            {
                "prime": prime,
                "modulus": str(modulus),
                "congruence": "+1" if minus else "-1",
            }
        )
    return signs


def decimal_log(value: int) -> float:
    """Accurate-enough base-10 log without converting a huge int to float."""

    digits = str(value)
    prefix_length = min(16, len(digits))
    prefix = int(digits[:prefix_length])
    return math.log10(prefix) + len(digits) - prefix_length


def run(max_n: int) -> dict[str, object]:
    if max_n < 7:
        raise ValueError("--max-n must include the known n = 7 solution")

    records: list[dict[str, object]] = []
    structural_solutions: list[dict[str, object]] = []
    factorial = math.factorial(3)
    for n in range(4, max_n + 1):
        factorial *= n
        blocks = factorial_quarter_blocks(n)
        quarter = factorial // 4
        if math.prod(block for _, block in blocks) != quarter:
            raise AssertionError("prime-power blocks did not reconstruct n! / 4")
        a, b, gap, small_primes, large_primes = closest_unitary_pair(blocks)
        if a * b != quarter or math.gcd(a, b) != 1:
            raise AssertionError("invalid unitary factor certificate")
        is_solution = gap == 1
        record: dict[str, object] = {
            "n": n,
            "prime_power_block_count": len(blocks),
            "sign_vectors_up_to_swap": str(1 << (len(blocks) - 1)),
            "closest_a": str(a),
            "closest_b": str(b),
            "gap": str(gap),
            "log10_gap": round(decimal_log(gap), 12),
            "small_factor_primes": small_primes,
            "large_factor_primes": large_primes,
            "is_consecutive": is_solution,
        }
        records.append(record)
        if is_solution:
            m = 2 * a + 1
            solution = {
                "n": n,
                "m": m,
                "a": a,
                "b": b,
                "odd_prime_power_signs": prime_power_signs(n, m),
            }
            structural_solutions.append(solution)

    direct = direct_square_solutions(max_n)
    structural_pairs = [
        {"n": item["n"], "m": item["m"]} for item in structural_solutions
    ]
    if structural_pairs != direct:
        raise AssertionError("unitary-divisor and direct-square tests disagree")

    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "range_inclusive": [4, max_n],
        "method": (
            "exact meet-in-the-middle enumeration of unitary divisors of n!/4; "
            "the largest divisor at most sqrt(n!/4) gives the minimum gap"
        ),
        "source_sha256": source_hash,
        "structural_solutions": structural_solutions,
        "direct_square_solutions": direct,
        "methods_agree": True,
        "records": records,
    }


def render_log(results: dict[str, object], command: Iterable[str]) -> str:
    records = results["records"]
    assert isinstance(records, list)
    last = records[-1]
    assert isinstance(last, dict)
    lines = [
        "Brocard--Ramanujan q2 unitary-factorization run",
        "command: " + " ".join(command),
        f"source sha256: {results['source_sha256']}",
        f"range: {results['range_inclusive']}",
        "method: " + str(results["method"]),
        f"structural solutions: {results['structural_solutions']}",
        f"direct square solutions: {results['direct_square_solutions']}",
        f"methods agree: {results['methods_agree']}",
        (
            f"at n={last['n']}: blocks={last['prime_power_block_count']}, "
            f"sign vectors up to swap={last['sign_vectors_up_to_swap']}, "
            f"minimum gap={last['gap']}"
        ),
        "",
        "Selected exact closest pairs:",
    ]
    selected = {4, 5, 6, 7, 8, 10, 20, 50, int(last["n"])}
    for record in records:
        assert isinstance(record, dict)
        if int(record["n"]) in selected:
            lines.append(
                f"  n={record['n']}: a={record['closest_a']}, "
                f"b={record['closest_b']}, gap={record['gap']}, "
                f"blocks={record['prime_power_block_count']}"
            )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run(args.max_n)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    log = render_log(results, sys.argv)
    args.log.write_text(log)
    print(log, end="")


if __name__ == "__main__":
    main()
