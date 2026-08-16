#!/usr/bin/env python3
"""Dependency-free independent audit of the q2 seven-hole residue.

This verifier intentionally exits successfully only after confirming that the
file is *not* a covering witness: it must leave exactly its recorded seven
syndromes uncovered.  It also exhausts all genuine one-column swaps.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESIDUE_PATH = HERE / "q2_best_residue_r10_n49.json"


def binary_rank(vectors: list[int], width: int) -> int:
    pivots = [0] * width
    rank = 0
    for vector in vectors:
        reduced = vector
        while reduced:
            lead = reduced.bit_length() - 1
            if pivots[lead]:
                reduced ^= pivots[lead]
            else:
                pivots[lead] = reduced
                rank += 1
                break
    return rank


def enumerate_representations(columns: list[int], redundancy: int) -> list[int]:
    total = 1 << redundancy
    multiplicity = [0] * total
    multiplicity[0] = 1
    for right, column in enumerate(columns):
        multiplicity[column] += 1
        for left in range(right):
            multiplicity[column ^ columns[left]] += 1
    return multiplicity


def audit_one_swaps(columns: list[int], redundancy: int) -> tuple[int, int, int]:
    total = 1 << redundancy
    original_members = set(columns)
    best = total
    best_count = 0
    checked = 0
    for removed_index in range(len(columns)):
        retained = columns[:removed_index] + columns[removed_index + 1 :]
        after_removal = enumerate_representations(retained, redundancy)
        missing_after_removal = sum(value == 0 for value in after_removal)
        for inserted in range(1, total):
            if inserted in original_members:
                continue
            newly_covered = int(after_removal[inserted] == 0)
            for retained_column in retained:
                newly_covered += after_removal[inserted ^ retained_column] == 0
            final_missing = missing_after_removal - newly_covered
            checked += 1
            if final_missing < best:
                best = final_missing
                best_count = 1
            elif final_missing == best:
                best_count += 1
    return checked, best, best_count


def main() -> None:
    raw = RESIDUE_PATH.read_bytes()
    residue = json.loads(raw)
    redundancy = residue.get("redundancy")
    length = residue.get("length")
    columns = residue.get("columns_decimal")
    if redundancy != 10 or length != 49 or not isinstance(columns, list):
        raise AssertionError("unexpected q2 residue parameters")
    if len(columns) != length or len(set(columns)) != length:
        raise AssertionError("residue columns are not a 49-element set")
    if any(not isinstance(column, int) or not 0 < column < (1 << redundancy) for column in columns):
        raise AssertionError("residue contains a zero or out-of-range column")
    if [f"{column:03X}" for column in columns] != residue.get("columns_hex"):
        raise AssertionError("decimal and hexadecimal column encodings disagree")
    rank = binary_rank(columns, redundancy)
    if rank != redundancy or residue.get("rank") != rank:
        raise AssertionError("residue does not have F2-rank 10")

    multiplicity = enumerate_representations(columns, redundancy)
    missing = [syndrome for syndrome, count in enumerate(multiplicity) if count == 0]
    if missing != residue.get("uncovered_syndromes_decimal"):
        raise AssertionError("independent enumeration disagrees on uncovered syndromes")
    if [f"{syndrome:03X}" for syndrome in missing] != residue.get("uncovered_syndromes_hex"):
        raise AssertionError("decimal and hexadecimal uncovered encodings disagree")
    if len(missing) != 7 or residue.get("best_uncovered") != 7:
        raise AssertionError("this artifact is not the recorded seven-hole residue")
    if not missing:
        raise AssertionError("residue unexpectedly became a covering witness")
    histogram = dict(sorted(Counter(multiplicity).items()))
    stored_histogram = {int(key): value for key, value in residue["representation_multiplicities"].items()}
    if histogram != stored_histogram:
        raise AssertionError("representation histogram disagrees")

    checked, swap_best, swap_count = audit_one_swaps(columns, redundancy)
    neighborhood = residue["exact_nontrivial_one_swap_neighborhood"]
    if (checked, swap_best, swap_count) != (
        neighborhood["moves_checked"],
        neighborhood["best_uncovered"],
        neighborhood["number_of_best_moves"],
    ):
        raise AssertionError("independent one-swap audit disagrees")
    if (checked, swap_best, swap_count) != (47726, 20, 6):
        raise AssertionError("unexpected canonical one-swap spectrum")

    digest = hashlib.sha256(raw).hexdigest()
    print("PASS: independently verified q2 search residue (NOT a covering witness)")
    print(f"parameters: n={length}, redundancy={redundancy}, rank={rank}")
    print(f"syndromes covered: {(1 << redundancy) - len(missing)}/{1 << redundancy}")
    print(f"uncovered decimal: {missing}")
    print(f"uncovered hex: {[f'{syndrome:03X}' for syndrome in missing]}")
    print(f"representation multiplicities: {histogram}")
    print(f"nontrivial one-swaps: {checked}; best leaves {swap_best} uncovered ({swap_count} moves)")
    print(f"residue sha256: {digest}")
    print("CONCLUSION: no n=49 witness was found; this is not a lower bound")


if __name__ == "__main__":
    main()
