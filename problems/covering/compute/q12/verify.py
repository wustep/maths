#!/usr/bin/env python3
"""Verify the seed, the elementary p>=18 obstruction, and an 18-block witness."""
import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ok37_seed import M_HEX, is_partition_3ell, ok37_columns


def read_numbers(path):
    return [int(token) for line in path.read_text().splitlines()
            for token in line.split("#", 1)[0].split()]


def certificate():
    rows = [[int(t) for t in line.split("#", 1)[0].split()]
            for line in (HERE.parent / "H_OK37_r12_n37.txt").read_text().splitlines()
            if line.split("#", 1)[0].strip()]
    assert len(rows) == 12 and all(len(row) == 37 for row in rows)
    assert all(bit in (0, 1) for row in rows for bit in row)
    columns = [sum(rows[r][i] << r for r in range(12)) for i in range(37)]
    assert columns == ok37_columns()
    words = [int(t, 16) for line in (HERE.parent / "M_OK37_hex.txt").read_text().splitlines()
             for t in line.split("#", 1)[0].split()]
    assert tuple(words) == M_HEX
    # The first twelve columns form I_12, independently establishing rank 12.
    assert columns[:12] == [1 << i for i in range(12)]
    reps = [[] for _ in range(4096)]
    counts = []
    for k in range(4):
        for support in combinations(range(37), k):
            syndrome = 0
            for i in support:
                syndrome ^= columns[i]
            reps[syndrome].append(support)
        counts.append(sum(bool(r) for r in reps))
    assert counts == [1, 38, 591, 4096]
    assert reps[0] == [()], "ell>=1 obstruction failed"
    edges = {edge for r in reps if len(r) == 1 for edge in combinations(r[0], 2)}
    degrees = Counter(i for edge in edges for i in edge)
    singles = [i for i in range(37) if degrees[i] == 36]
    assert len(singles) == 15
    target = 277
    assert reps[target] and all(len(r) == 3 and not set(r).intersection(singles)
                               for r in reps[target])
    # All representations of this syndrome require three different blocks
    # outside the fifteen forced singletons. Thus at least eighteen blocks.
    labels = read_numbers(HERE / "partition_p18_ell0.txt")
    assert len(labels) == 37 and set(labels) == set(range(18))
    assert is_partition_3ell(columns, labels, 0)
    # Syndrome-driven check, in addition to the seed helper's sum-driven check.
    for syndrome, supports in enumerate(reps):
        assert any(len({labels[i] for i in r}) == len(r) for r in supports), syndrome
    return {
        "seed": {"r": 12, "n": 37, "rank": 12, "covering_radius": 3,
                 "covered_le0_to_le3": counts, "nonempty_zero_representations_le3": 0},
        "unique_representation_conflict_edges": len(edges),
        "forced_singletons_one_based": [i + 1 for i in singles],
        "obstruction_syndrome_lsb_integer": target,
        "all_obstruction_representations_one_based": [[i + 1 for i in r] for r in reps[target]],
        "ell0_minimum_blocks": 18,
        "ell1_ell2_ell3": "impossible for every block count: syndrome zero",
        "partition_p18_one_based": [[i + 1 for i, b in enumerate(labels) if b == j]
                                     for j in range(18)],
        "at_m4_indicator_capacity": 17,
        "target_length_not_constructed": 607,
        "published_length_arxiv_2511_02542v1_table7_1_r24": 618,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = certificate()
    path = HERE / "certificate.json"
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        assert json.loads(path.read_text()) == result
    print("PASS Python: seed rank=12, radius=3, coverage=4096/4096; "
          "15 forced singletons + syndrome 277 require >=18 blocks; "
          "18-block witness covers 4096/4096; ell>=1 impossible at zero")


if __name__ == "__main__":
    main()
