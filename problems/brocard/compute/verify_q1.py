#!/usr/bin/env python3
"""Independent replay checks for q1-results.json.

This verifier deliberately does not import modular_hunt.py.  It:

1. recomputes the exact n <= 63 search with integer square roots;
2. recomputes the four-prime cover and p=151 interval in pure Python;
3. cross-checks the C kernel against a pure-Python sieve through n=5000;
4. reruns the full 10^7 certificate with its 25 used primes reversed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve().parent
RESULTS_PATH = HERE / "q1-results.json"
KERNEL_PATH = HERE / "sieve_kernel.c"
LOG_PATH = HERE / "q1-verification.txt"


def prime_is_exact(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def bad_indices(prime: int, lower: int, upper: int) -> set[int]:
    squares = {x * x % prime for x in range(prime)}
    factorial = 1
    result: set[int] = set()
    for n in range(upper + 1):
        if n:
            factorial = factorial * n % prime
        if n >= lower and (factorial + 1) % prime not in squares:
            result.add(n)
    return result


def python_sieve(bound: int, lower: int, primes: list[int]) -> list[int]:
    alive = set(range(lower, bound + 1))
    for prime in primes:
        alive.difference_update(bad_indices(prime, lower, bound))
        if not alive:
            break
    return sorted(alive)


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
            str(KERNEL_PATH),
            "-o",
            str(binary),
        ],
        check=True,
    )
    return binary


def kernel_sieve(binary: Path, bound: int, lower: int, primes: list[int]) -> list[int]:
    completed = subprocess.run(
        [str(binary), str(bound), str(lower), *(str(p) for p in primes)],
        check=True,
        text=True,
        capture_output=True,
    )
    final = completed.stdout.splitlines()[-1].split(",")
    if final[0] != "SURVIVORS":
        raise AssertionError(f"unexpected kernel output: {completed.stdout}")
    count = int(final[1])
    survivors = [int(n) for n in final[2:]]
    if count != len(survivors):
        raise AssertionError("verifier expects fewer than 100 survivors")
    return survivors


def exact_solutions(bound: int) -> list[dict[str, int]]:
    factorial = 1
    result: list[dict[str, int]] = []
    for n in range(bound + 1):
        if n:
            factorial *= n
        root = math.isqrt(factorial + 1)
        if root * root == factorial + 1:
            result.append({"n": n, "m": root})
    return result


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text())
    messages: list[str] = []

    digest = hashlib.sha256(KERNEL_PATH.read_bytes()).hexdigest()
    assert digest == data["kernel_sha256"]
    messages.append(f"kernel sha256 matches: {digest}")

    exact = data["published_range_replay"]
    replayed_solutions = exact_solutions(exact["bound_inclusive"])
    assert replayed_solutions == exact["solutions"]
    messages.append(
        f"exact replay n=0..{exact['bound_inclusive']}: {replayed_solutions}"
    )

    cover = data["small_modular_cover"]
    lower, upper = cover["range_inclusive"]
    union: set[int] = set()
    for item in cover["selected"]:
        prime = item["prime"]
        assert prime_is_exact(prime)
        recomputed = bad_indices(prime, lower, upper)
        assert recomputed == set(item["all_bad_n"])
        union.update(recomputed)
    assert union == set(range(lower, upper + 1))
    messages.append(
        "small cover recomputed in pure Python: "
        + ", ".join(str(item["prime"]) for item in cover["selected"])
    )

    sharp = data["sharp_interval"]
    prime = sharp["prime"]
    first, last = sharp["bad_interval_inclusive"]
    recomputed_bad = bad_indices(prime, 0, prime - 1)
    assert set(range(first, last + 1)) <= recomputed_bad
    assert first - 1 not in recomputed_bad
    assert last + 1 not in recomputed_bad
    messages.append(
        f"sharp p={prime} interval and both passing boundaries recomputed: "
        f"{first}..{last}"
    )

    with tempfile.TemporaryDirectory(prefix="brocard-verify-") as temp_name:
        binary = compile_kernel(Path(temp_name))

        sample_bound = 5000
        sample_primes = [5003, 5009, 5011, 5021, 5023, 5039, 5051, 5059]
        assert all(prime_is_exact(p) for p in sample_primes)
        expected = python_sieve(sample_bound, 8, sample_primes)
        observed = kernel_sieve(binary, sample_bound, 8, sample_primes)
        assert observed == expected
        messages.append(
            f"C kernel agrees with independent Python through n={sample_bound}: "
            f"{len(observed)} survivors"
        )

        large = data["berndt_galway_method_slice"]
        used_primes = [step["prime"] for step in large["steps"]]
        started = time.monotonic()
        reversed_survivors = kernel_sieve(
            binary,
            large["range_inclusive"][1],
            large["range_inclusive"][0],
            list(reversed(used_primes)),
        )
        elapsed = time.monotonic() - started
        assert reversed_survivors == []
        messages.append(
            "full certificate rerun in reverse prime order: "
            f"0 survivors ({elapsed:.6f} seconds)"
        )

    text = "Brocard--Ramanujan q1 independent verification\n\n" + "\n".join(
        f"- {message}" for message in messages
    ) + "\n"
    LOG_PATH.write_text(text)
    print(text, end="")
    print(LOG_PATH)


if __name__ == "__main__":
    main()
