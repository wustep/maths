#!/usr/bin/env python3
"""Build or byte-check the canonical q2 n=49 search residue and run log.

The output is deliberately labelled as a residue, not a covering certificate.
Its seven uncovered syndromes are independently checked by
``verify_q2_residue.py``.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "q2_search_checkpoint.json"
RESIDUE = HERE / "q2_best_residue_r10_n49.json"
RUN_LOG = HERE / "q2_search_results.json"


def binary_rank(vectors: list[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for original in vectors:
        value = original
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def multiplicities(columns: list[int], redundancy: int) -> list[int]:
    counts = [0] * (1 << redundancy)
    counts[0] = 1
    for left, column in enumerate(columns):
        counts[column] += 1
        for right in range(left):
            counts[column ^ columns[right]] += 1
    return counts


def best_nontrivial_swap(columns: list[int], redundancy: int) -> tuple[int, int]:
    """Return (least uncovered, number of swaps attaining it)."""
    size = 1 << redundancy
    member = set(columns)
    best = size
    number = 0
    for slot, removed in enumerate(columns):
        retained = columns[:slot] + columns[slot + 1 :]
        counts = multiplicities(retained, redundancy)
        base_missing = sum(count == 0 for count in counts)
        for added in range(1, size):
            if added in member:
                continue
            gained = counts[added] == 0
            gained += sum(counts[added ^ other] == 0 for other in retained)
            missing = base_missing - gained
            if missing < best:
                best = missing
                number = 1
            elif missing == best:
                number += 1
    return best, number


def render_residue() -> str:
    source = json.loads(SOURCE.read_text())
    redundancy = int(source["redundancy"])
    columns = sorted(int(value) for value in source["columns_decimal"])
    counts = multiplicities(columns, redundancy)
    missing = [syndrome for syndrome, count in enumerate(counts) if count == 0]
    swap_best, swap_number = best_nontrivial_swap(columns, redundancy)
    if len(columns) != 49 or len(set(columns)) != 49:
        raise RuntimeError("source checkpoint is not a 49-set")
    if binary_rank(columns, redundancy) != redundancy:
        raise RuntimeError("source checkpoint does not have full rank")
    if len(missing) != 7 or missing != source["uncovered_syndromes_decimal"]:
        raise RuntimeError("source checkpoint no longer has the recorded seven-hole residue")
    payload = {
        "format": "binary-radius-two-search-residue-v1",
        "status": "no witness found; not a lower bound",
        "quest": "q2: attempt to push ell_2(10,2) from 50 to 49",
        "field": "GF(2)",
        "redundancy": redundancy,
        "length": len(columns),
        "rank": binary_rank(columns, redundancy),
        "columns_decimal": columns,
        "columns_hex": [f"{column:03X}" for column in columns],
        "best_uncovered": len(missing),
        "uncovered_syndromes_decimal": missing,
        "uncovered_syndromes_hex": [f"{syndrome:03X}" for syndrome in missing],
        "representation_multiplicities": dict(sorted(Counter(counts).items())),
        "exact_nontrivial_one_swap_neighborhood": {
            "moves_checked": len(columns) * ((1 << redundancy) - 1 - len(columns)),
            "best_uncovered": swap_best,
            "number_of_best_moves": swap_number,
            "interpretation": "Every genuine one-out/one-in move from this residue leaves at least 20 syndromes uncovered.",
        },
        "source_q1_matrix": "H_r10_n50.txt",
        "source_raw_checkpoint": SOURCE.name,
        "warning": "Seven uncovered syndromes are a stochastic search residue, not evidence that an n=49 code is impossible.",
    }
    return json.dumps(payload, indent=2) + "\n"


def render_log() -> str:
    runs = [
        {
            "method": "direct fixed-cardinality targeted annealing",
            "wall_seconds": 10,
            "threads": 8,
            "master_seed": "0x243F6A8885A308D3",
            "best_uncovered": 7,
        },
        {
            "method": "longer heterogeneous annealing and breakout weights",
            "wall_seconds": 90,
            "threads": 8,
            "master_seed": "0x13198A2E03707344",
            "best_uncovered": 7,
        },
        {
            "method": "multi-column annealing moves",
            "wall_seconds": 30,
            "threads": 8,
            "master_seed": "0x082EFA98EC4E6C89",
            "best_uncovered": 7,
        },
        {
            "method": "best-admissible tabu walks",
            "wall_seconds": 45,
            "threads": 8,
            "master_seed": "0xBE5466CF34E90C6C",
            "best_uncovered": 7,
        },
        {
            "method": "heavy q1 perturbations plus tabu",
            "wall_seconds": 120,
            "threads": 8,
            "master_seed": "0xD1310BA698DFB5AC",
            "best_uncovered": 7,
        },
        {
            "method": "q1/GL(10,2)-image crossovers plus tabu",
            "wall_seconds": 150,
            "threads": 8,
            "master_seed": "0x2FFD72DBD01ADFB7",
            "best_uncovered": 7,
        },
        {
            "method": "50-column lifted search from q1, scored by cheapest deletion",
            "wall_seconds": 45,
            "threads": 8,
            "master_seed": "0xC0AC29B7C97C50DD",
            "best_uncovered": 9,
        },
        {
            "method": "50-column lifted search seeded by the seven-hole residue",
            "wall_seconds": 60,
            "threads": 8,
            "master_seed": "0x9216D5D98979FB1B",
            "best_uncovered": 7,
        },
    ]
    payload = {
        "date": "2026-08-16",
        "quest": "q2",
        "target": {"redundancy": 10, "length": 49},
        "seed_artifact": "H_r10_n50.txt",
        "bounded_wall_seconds_total": sum(run["wall_seconds"] for run in runs),
        "runs": runs,
        "exact_checks": {
            "q1_direct_deletions_best_uncovered": 9,
            "canonical_residue_best_uncovered": 7,
            "canonical_residue_best_nontrivial_one_swap_uncovered": 20,
            "least_damaging_first_swaps_checked_at_two_swap_depth": 126,
            "two_swap_depth_best_nonreversal_uncovered": 20,
            "two_swap_scope": "Only first swaps leaving at most 25 uncovered syndromes; not the full two-swap neighborhood.",
        },
        "conclusion": "No n=49 witness found. All positive deficits are residues, not lower bounds.",
    }
    return json.dumps(payload, indent=2) + "\n"


def check_exact(path: Path, expected: str) -> None:
    if not path.exists():
        raise SystemExit(f"missing generated artifact: {path}")
    if path.read_text() != expected:
        raise SystemExit(f"generated artifact is stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    residue = render_residue()
    run_log = render_log()
    if args.write:
        RESIDUE.write_text(residue)
        RUN_LOG.write_text(run_log)
        print(f"wrote {RESIDUE.name} and {RUN_LOG.name}")
    else:
        check_exact(RESIDUE, residue)
        check_exact(RUN_LOG, run_log)
        print("PASS: q2 residue and run log are byte-for-byte current")


if __name__ == "__main__":
    main()
