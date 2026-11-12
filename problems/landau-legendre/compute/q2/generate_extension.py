#!/usr/bin/env python3
"""Generate an Oppermann extension with recursive Lucas certificates."""

from __future__ import annotations

import argparse
import math
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

PUBLISHED_END = 70_500_000_000_000
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
            47, 53, 59, 61, 67, 71)
SMALL_PRIMES = MR_BASES


@dataclass(frozen=True)
class LucasNode:
    prime: int
    witness: int
    factors: tuple[tuple[int, int], ...]


def strong_probable_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in SMALL_PRIMES:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    odd_part = value - 1
    power_of_two = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        power_of_two += 1
    for base in MR_BASES:
        residue = pow(base, odd_part, value)
        if residue in (1, value - 1):
            continue
        for _ in range(power_of_two - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


def factor_integer(value: int, timeout: float) -> Counter[int]:
    if value < 2:
        return Counter()
    remainder = value
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= remainder and divisor <= 10_000:
        while remainder % divisor == 0:
            factors.append(divisor)
            remainder //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remainder > 1:
        if strong_probable_prime(remainder):
            factors.append(remainder)
        else:
            result = subprocess.run(
                ["factor", str(remainder)],
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            prefix, separator, body = result.stdout.strip().partition(":")
            if separator != ":" or int(prefix) != remainder:
                raise RuntimeError(f"unexpected factor output for {remainder}")
            factors.extend(int(item) for item in body.split())
    product = math.prod(factors)
    if product != value:
        raise RuntimeError(f"factorization product {product} != {value}")
    return Counter(factors)


class CertificateBuilder:
    def __init__(self, factor_timeout: float) -> None:
        self.factor_timeout = factor_timeout
        self.nodes: dict[int, LucasNode] = {
            2: LucasNode(2, 0, ()),
        }

    def certify(self, prime: int) -> None:
        if prime in self.nodes:
            return
        factors = factor_integer(prime - 1, self.factor_timeout)
        factor_tuple = tuple(sorted(factors.items()))
        for factor, _ in factor_tuple:
            self.certify(factor)
        unique_factors = tuple(factors)
        for witness in range(2, 10_000):
            if pow(witness, prime - 1, prime) != 1:
                continue
            if all(
                math.gcd(pow(witness, (prime - 1) // factor, prime) - 1, prime) == 1
                for factor in unique_factors
            ):
                self.nodes[prime] = LucasNode(prime, witness, factor_tuple)
                return
        raise RuntimeError(f"no Lucas witness found for {prime}")

    def first_certified_prime(self, lower: int, upper: int) -> int:
        candidate = lower + 1
        if candidate % 2 == 0:
            candidate += 1
        while candidate < upper:
            if strong_probable_prime(candidate):
                checkpoint = set(self.nodes)
                try:
                    self.certify(candidate)
                    return candidate
                except (RuntimeError, subprocess.SubprocessError):
                    for added in set(self.nodes) - checkpoint:
                        del self.nodes[added]
            candidate += 2
        raise RuntimeError(f"no certifiable prime in ({lower}, {upper})")


def render(
    start: int,
    end: int,
    witnesses: list[tuple[int, int, int]],
    nodes: dict[int, LucasNode],
) -> str:
    lines = [
        "H\tschema\tlandau-legendre.oppermann-extension.v1",
        f"H\tpublished_end\t{PUBLISHED_END}",
        f"H\tstart\t{start}",
        f"H\tend\t{end}",
        f"H\trows\t{len(witnesses)}",
    ]
    for n_value, left, right in witnesses:
        lines.append(f"W\t{n_value}\t{left}\t{right}")
    for prime in sorted(nodes):
        node = nodes[prime]
        factor_text = ",".join(f"{factor}^{exponent}" for factor, exponent in node.factors)
        lines.append(f"P\t{prime}\t{node.witness}\t{factor_text}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=PUBLISHED_END + 1)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--factor-timeout", type=float, default=20.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.start != PUBLISHED_END + 1 or args.end < args.start:
        raise SystemExit("range must begin immediately after the published endpoint")

    builder = CertificateBuilder(args.factor_timeout)
    witnesses: list[tuple[int, int, int]] = []
    for n_value in range(args.start, args.end + 1):
        middle = n_value * (n_value + 1)
        left = builder.first_certified_prime(n_value * n_value, middle)
        right = builder.first_certified_prime(middle, (n_value + 1) * (n_value + 1))
        witnesses.append((n_value, left, right))
        if len(witnesses) % 100 == 0:
            print(f"generated {len(witnesses)} rows", flush=True)

    args.output.write_text(
        render(args.start, args.end, witnesses, builder.nodes), encoding="ascii"
    )
    print(
        f"PASS generated rows={len(witnesses)} prime_nodes={len(builder.nodes)} "
        f"end={args.end}"
    )


if __name__ == "__main__":
    main()
