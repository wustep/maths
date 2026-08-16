#!/usr/bin/env python3
"""Reproduce finite Brocard--Ramanujan searches by exact modular arithmetic.

The default run has three independent pieces:

* exact integer-square testing through Gupta's published n <= 63 range;
* a Berndt--Galway quadratic-residue sieve on the explicitly reported slice
  8 <= n <= 10^7 (their paper ran the same test through 10^9);
* a small-modulus hunt producing a four-prime cover of 8 <= n <= 150 and
  the maximal bad interval 16 <= n <= 31 for p = 151 among primes p <= 200.

The large finite scan is delegated to the adjacent auditable C kernel.  This
Python file chooses and verifies the prime moduli, compiles the kernel in a
temporary directory, parses every survivor count, and writes the replay log.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Iterable


HERE = Path(__file__).resolve().parent
KERNEL_SOURCE = HERE / "sieve_kernel.c"
DEFAULT_JSON = HERE / "q1-results.json"
DEFAULT_LOG = HERE / "q1-run.log"


def is_prime(n: int) -> bool:
    """Deterministic trial-division primality test for the sizes used here."""

    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def primes_after(bound: int, count: int) -> list[int]:
    result: list[int] = []
    candidate = bound + 1
    if candidate % 2 == 0:
        candidate += 1
    while len(result) < count:
        if is_prime(candidate):
            result.append(candidate)
        candidate += 2
    return result


def primes_between(lower: int, upper: int) -> list[int]:
    return [n for n in range(max(2, lower), upper + 1) if is_prime(n)]


def square_residues(modulus: int) -> set[int]:
    """All square residues modulo an odd modulus (used only with primes)."""

    return {x * x % modulus for x in range(modulus // 2 + 1)}


def modular_bad_indices(prime: int, min_n: int, max_n: int) -> set[int]:
    if prime <= max_n:
        raise ValueError("the finite-cover modulus must exceed max_n")
    squares = square_residues(prime)
    factorial = 1
    bad: set[int] = set()
    for n in range(max_n + 1):
        if n:
            factorial = factorial * n % prime
        if n >= min_n and (factorial + 1) % prime not in squares:
            bad.add(n)
    return bad


def exact_square_replay(bound: int) -> dict[str, object]:
    factorial = 1
    solutions: list[dict[str, int]] = []
    for n in range(bound + 1):
        if n:
            factorial *= n
        root = math.isqrt(factorial + 1)
        if root * root == factorial + 1:
            solutions.append({"n": n, "m": root})
    return {
        "bound_inclusive": bound,
        "method": "exact integers plus math.isqrt",
        "solutions": solutions,
    }


def greedy_small_cover(
    min_n: int = 8,
    max_n: int = 150,
    max_prime: int = 997,
) -> dict[str, object]:
    universe = set(range(min_n, max_n + 1))
    candidates = {
        p: modular_bad_indices(p, min_n, max_n)
        for p in primes_between(max_n + 1, max_prime)
    }
    uncovered = set(universe)
    selected: list[dict[str, object]] = []
    while uncovered:
        prime, bad = max(
            candidates.items(),
            key=lambda item: (len(item[1] & uncovered), -item[0]),
        )
        assigned = sorted(bad & uncovered)
        if not assigned:
            raise RuntimeError(f"candidate moduli failed to cover {sorted(uncovered)}")
        uncovered.difference_update(assigned)
        selected.append(
            {
                "prime": prime,
                "newly_covered_count": len(assigned),
                "newly_covered_n": assigned,
                "all_bad_n": sorted(bad),
                "remaining_count": len(uncovered),
            }
        )
        del candidates[prime]
    return {
        "range_inclusive": [min_n, max_n],
        "candidate_primes_inclusive": [max_n + 1, max_prime],
        "selection": "greedy maximum new coverage; smallest prime breaks ties",
        "selected": selected,
        "uncovered": sorted(uncovered),
    }


def longest_run(values: set[int], lower: int, upper: int) -> tuple[int, int]:
    best = (lower, lower - 1)
    start: int | None = None
    for n in range(lower, upper + 2):
        if n <= upper and n in values:
            if start is None:
                start = n
        elif start is not None:
            candidate = (start, n - 1)
            if candidate[1] - candidate[0] > best[1] - best[0]:
                best = candidate
            start = None
    return best


def sharp_interval_hunt(
    min_n: int = 8,
    max_prime: int = 200,
) -> dict[str, object]:
    records: list[tuple[int, int, int]] = []
    bad_by_prime: dict[int, set[int]] = {}
    for prime in primes_between(min_n + 1, max_prime):
        bad = modular_bad_indices(prime, min_n, prime - 1)
        bad_by_prime[prime] = bad
        first, last = longest_run(bad, min_n, prime - 1)
        records.append((last - first + 1, -prime, first))
    length, neg_prime, first = max(records)
    prime = -neg_prime
    last = first + length - 1
    bad = bad_by_prime[prime]

    factorial = 1
    targets: dict[int, int] = {}
    for n in range(last + 2):
        if n:
            factorial = factorial * n % prime
        if first - 1 <= n <= last + 1:
            targets[n] = (factorial + 1) % prime

    squares = square_residues(prime)
    return {
        "search_primes_at_most": max_prime,
        "tie_break": "smallest prime, then first interval",
        "prime": prime,
        "bad_interval_inclusive": [first, last],
        "length": length,
        "factorial_plus_one_residues": {
            str(n): targets[n] for n in range(first, last + 1)
        },
        "distinct_nonresidues": sorted({targets[n] for n in range(first, last + 1)}),
        "left_boundary": {
            "n": first - 1,
            "residue": targets[first - 1],
            "is_square_residue": targets[first - 1] in squares,
        },
        "right_boundary": {
            "n": last + 1,
            "residue": targets[last + 1],
            "is_square_residue": targets[last + 1] in squares,
        },
        "maximal_for_this_prime": (first - 1 not in bad and last + 1 not in bad),
    }


def compile_kernel(directory: Path) -> Path:
    binary = directory / "sieve_kernel"
    subprocess.run(
        [
            "gcc",
            "-O3",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(KERNEL_SOURCE),
            "-o",
            str(binary),
        ],
        check=True,
    )
    return binary


def run_large_sieve(bound: int, min_n: int, primes: Iterable[int]) -> dict[str, object]:
    prime_list = list(primes)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="brocard-sieve-") as temp_name:
        binary = compile_kernel(Path(temp_name))
        completed = subprocess.run(
            [str(binary), str(bound), str(min_n), *(str(p) for p in prime_list)],
            check=True,
            text=True,
            capture_output=True,
        )
    elapsed = time.monotonic() - started

    start_count: int | None = None
    steps: list[dict[str, int]] = []
    survivor_count: int | None = None
    survivors: list[int] = []
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "START":
            start_count = int(fields[1])
        elif fields[0] == "PRIME":
            steps.append(
                {
                    "prime": int(fields[1]),
                    "eliminated": int(fields[2]),
                    "survivors": int(fields[3]),
                }
            )
        elif fields[0] == "SURVIVORS":
            survivor_count = int(fields[1])
            survivors = [int(value) for value in fields[2:]]
        else:
            raise RuntimeError(f"unrecognized kernel output: {line}")
    if start_count is None or survivor_count is None:
        raise RuntimeError(f"incomplete kernel output:\n{completed.stdout}")

    return {
        "range_inclusive": [min_n, bound],
        "requested_primes": prime_list,
        "used_prime_count": len(steps),
        "start_count": start_count,
        "steps": steps,
        "survivor_count": survivor_count,
        "survivors_first_100": survivors,
        "elapsed_seconds": round(elapsed, 6),
        "kernel_stdout": completed.stdout.splitlines(),
    }


def render_log(results: dict[str, object], command: str) -> str:
    exact = results["published_range_replay"]
    large = results["berndt_galway_method_slice"]
    small = results["small_modular_cover"]
    sharp = results["sharp_interval"]
    assert isinstance(exact, dict)
    assert isinstance(large, dict)
    assert isinstance(small, dict)
    assert isinstance(sharp, dict)
    lines = [
        "Brocard--Ramanujan q1 exact replay log",
        f"command: {command}",
        f"kernel sha256: {results['kernel_sha256']}",
        "",
        "Published-range replay:",
        f"  exact n = 0..{exact['bound_inclusive']}",
        f"  solutions: {exact['solutions']}",
        "",
        "Berndt--Galway method, explicitly smaller slice than their 10^9 run:",
        f"  range: {large['range_inclusive']}",
        f"  used primes: {large['used_prime_count']}",
        f"  final survivors: {large['survivor_count']}",
        f"  elapsed seconds: {large['elapsed_seconds']}",
    ]
    for step in large["steps"]:
        lines.append(
            f"    p={step['prime']}: eliminated={step['eliminated']}, "
            f"survivors={step['survivors']}"
        )
    lines.extend(
        [
            "",
            "Small exact cover:",
            f"  range: {small['range_inclusive']}",
            "  primes: " + ", ".join(str(item["prime"]) for item in small["selected"]),
            f"  uncovered: {small['uncovered']}",
            "",
            "Sharp interval:",
            f"  p={sharp['prime']}, interval={sharp['bad_interval_inclusive']}, "
            f"length={sharp['length']}",
            f"  distinct nonresidues: {sharp['distinct_nonresidues']}",
            f"  boundaries: {sharp['left_boundary']}, {sharp['right_boundary']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=10_000_000)
    parser.add_argument("--min-n", type=int, default=8)
    parser.add_argument("--prime-count", type=int, default=40)
    parser.add_argument("--published-exact-bound", type=int, default=63)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.bound < args.min_n:
        raise SystemExit("--bound must be at least --min-n")
    if args.published_exact_bound < 7:
        raise SystemExit("--published-exact-bound must include the known n=7 solution")

    chosen_primes = primes_after(args.bound, args.prime_count)
    results: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact integer and modular arithmetic only",
        "kernel_sha256": hashlib.sha256(KERNEL_SOURCE.read_bytes()).hexdigest(),
        "published_range_replay": exact_square_replay(args.published_exact_bound),
        "berndt_galway_method_slice": run_large_sieve(
            args.bound, args.min_n, chosen_primes
        ),
        "small_modular_cover": greedy_small_cover(),
        "sharp_interval": sharp_interval_hunt(),
    }

    command = (
        "python3 compute/modular_hunt.py "
        f"--bound {args.bound} --prime-count {args.prime_count} "
        f"--published-exact-bound {args.published_exact_bound}"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    args.log.write_text(render_log(results, command))
    print(render_log(results, command), end="")
    print(f"JSON: {args.output}")
    print(f"log:  {args.log}")


if __name__ == "__main__":
    main()
