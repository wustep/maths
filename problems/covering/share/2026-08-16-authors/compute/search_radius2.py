#!/usr/bin/env python3
"""Reproduce the fixed-cardinality local search that found the q1 witness.

The search keeps exactly 50 distinct nonzero columns in F_2^10.  Its objective
is the number of syndromes not represented by zero, one, or two columns.  A
targeted proposal chooses an uncovered syndrome most of the time and proposes a
column that would cover it; simulated annealing supplies the uphill moves.

Numba is used only to make the discovery run short.  The committed witness and
its independent verifier do not depend on NumPy or Numba.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
KR_EXTRA_HEX = """
1B6 193 1CC 187 1F6 F7 16E 140 3C 296 22F 303 381 365
11D 1A3 274 2F2 254 56 F 41 357 208 34 329 28D 31D 3D5 129 3D7
B7 3EC 2E2 23C AD 34E 155 2E6 371 D4
""".split()
KR_COLUMNS = [1 << bit for bit in range(10)] + [int(value, 16) for value in KR_EXTRA_HEX]


def covered_syndromes(columns: list[int], redundancy: int = 10) -> set[int]:
    covered = {0, *columns}
    covered.update(
        columns[left] ^ columns[right]
        for left in range(len(columns))
        for right in range(left + 1, len(columns))
    )
    return covered


def verify_committed_witness() -> None:
    data = json.loads((HERE / "witness_r10_n50.json").read_text())
    columns = [int(value) for value in data["columns_decimal"]]
    covered = covered_syndromes(columns)
    if len(columns) != 50 or len(set(columns)) != 50 or len(covered) != 1024:
        raise SystemExit("committed witness failed the search-side coverage check")
    print("PASS: committed 50-column witness covers all 1024 syndromes")


def run_search(max_iterations: int) -> tuple[int, int, list[int]]:
    try:
        import numpy as np
        from numba import njit
    except ImportError as error:
        raise SystemExit(
            "discovery mode needs NumPy and Numba (Numba 0.67.0 is pinned in "
            "the repository's requirements.lock.txt)"
        ) from error

    base = np.array(KR_COLUMNS, dtype=np.int16)

    @njit
    def next_random(state):
        state ^= (state << 13) & np.uint64(0xFFFFFFFFFFFFFFFF)
        state ^= state >> 7
        state ^= (state << 17) & np.uint64(0xFFFFFFFFFFFFFFFF)
        return state

    @njit
    def make_counts(columns):
        counts = np.zeros(1024, np.int16)
        counts[0] = 1
        for left in range(50):
            counts[columns[left]] += 1
            for right in range(left):
                counts[columns[left] ^ columns[right]] += 1
        return counts

    @njit
    def anneal(iteration_limit):
        # This is run 0 from the search log.  Column 419 is the least-cost
        # deletion from the published 51-column seed.
        state = np.uint64(0x6A09E667F3BCC909) ^ np.uint64(0x9E3779B97F4A7C15)
        columns = np.empty(50, np.int16)
        position = 0
        for index in range(51):
            if index != 25:
                columns[position] = base[index]
                position += 1

        membership = np.zeros(1024, np.uint8)
        for column in columns:
            membership[column] = 1
        counts = make_counts(columns)
        uncovered = 0
        for syndrome in range(1024):
            if counts[syndrome] == 0:
                uncovered += 1
        best_uncovered = uncovered
        best = columns.copy()
        cycle = 80000

        for iteration in range(iteration_limit):
            state = next_random(state)
            if (state & 255) < 220:
                state = next_random(state)
                choice = int(state % uncovered)
                target = 0
                for syndrome in range(1, 1024):
                    if counts[syndrome] == 0:
                        if choice == 0:
                            target = syndrome
                            break
                        choice -= 1
                proposal = 0
                for _ in range(100):
                    state = next_random(state)
                    if (state & 63) == 0:
                        proposal = target
                    else:
                        proposal = target ^ columns[int((state >> 8) % 50)]
                    if proposal != 0 and membership[proposal] == 0:
                        break
                if proposal == 0 or membership[proposal] != 0:
                    while True:
                        state = next_random(state)
                        proposal = 1 + int(state % 1023)
                        if membership[proposal] == 0:
                            break
            else:
                while True:
                    state = next_random(state)
                    proposal = 1 + int(state % 1023)
                    if membership[proposal] == 0:
                        break

            state = next_random(state)
            slot = int(state % 50)
            removed = columns[slot]
            old_uncovered = uncovered

            old = counts[removed]
            counts[removed] = old - 1
            if old == 1:
                uncovered += 1
            for index in range(50):
                if index != slot:
                    syndrome = removed ^ columns[index]
                    old = counts[syndrome]
                    counts[syndrome] = old - 1
                    if old == 1:
                        uncovered += 1

            old = counts[proposal]
            counts[proposal] = old + 1
            if old == 0:
                uncovered -= 1
            for index in range(50):
                if index != slot:
                    syndrome = proposal ^ columns[index]
                    old = counts[syndrome]
                    counts[syndrome] = old + 1
                    if old == 0:
                        uncovered -= 1

            delta = uncovered - old_uncovered
            phase = (iteration % cycle) / (cycle - 1.0)
            temperature = 3.5 * (0.015**phase)
            state = next_random(state)
            uniform = float(state & np.uint64(0xFFFFFFFF)) / 4294967296.0
            if delta <= 0 or uniform < math.exp(-delta / temperature):
                membership[removed] = 0
                membership[proposal] = 1
                columns[slot] = proposal
                if uncovered < best_uncovered:
                    best_uncovered = uncovered
                    best = columns.copy()
                    if best_uncovered == 0:
                        return iteration + 1, best_uncovered, best
            else:
                counts[proposal] -= 1
                for index in range(50):
                    if index != slot:
                        counts[proposal ^ columns[index]] -= 1
                counts[removed] += 1
                for index in range(50):
                    if index != slot:
                        counts[removed ^ columns[index]] += 1
                uncovered = old_uncovered

            if iteration % cycle == cycle - 1:
                columns = best.copy()
                membership[:] = 0
                for column in columns:
                    membership[column] = 1
                counts = make_counts(columns)
                uncovered = best_uncovered

        return -1, best_uncovered, best

    iterations_used, best_uncovered, result = anneal(max_iterations)
    return int(iterations_used), int(best_uncovered), sorted(int(value) for value in result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true", help="rerun deterministic discovery search")
    parser.add_argument("--iterations", type=int, default=3_700_000)
    args = parser.parse_args()
    if not args.search:
        verify_committed_witness()
        return

    started = time.perf_counter()
    iterations_used, best_uncovered, columns = run_search(args.iterations)
    elapsed = time.perf_counter() - started
    print(f"iterations_used={iterations_used}")
    print(f"best_uncovered={best_uncovered}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"columns={columns}")
    if best_uncovered == 0:
        print("PASS: search rediscovered a 50-column covering set")
    else:
        raise SystemExit("bounded run ended without a covering witness")


if __name__ == "__main__":
    main()
