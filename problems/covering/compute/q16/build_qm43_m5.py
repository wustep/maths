#!/usr/bin/env python3
"""Build the r=41, n=26175 QM_4^3 lift from a merged q13 seed partition."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPUTE = HERE.parent
sys.path.insert(0, str(COMPUTE))

from build_qm3 import MODULUS, binary_rank, gf_mul, gf_selftest, read_matrix, write_matrix

SEED = COMPUTE / "H_R3_r26_n817.txt"
COARSE = COMPUTE / "q13/partition_r26_n817_p34.txt"
PARTITION = HERE / "partition_r26_n817_p33.txt"
OUTPUT = HERE / "H_R3_r41_n26175.txt"
MANIFEST = HERE / "manifest.json"
M = 5
Q = 1 << M


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    r, n, seed = read_matrix(SEED)
    assert (r, n) == (26, 817)
    coarse = [int(x) for line in COARSE.read_text().splitlines()
              if not line.startswith("#") for x in line.split()]
    assert len(coarse) == n and set(coarse) == set(range(34))
    # The exact search found two valid pairs; choose (7,31). Relabel to 0..32.
    labels = [7 if old == 31 else old - (old > 31) for old in coarse]
    assert set(labels) == set(range(33))
    PARTITION.write_text(
        "# q16 merge of q13 inherited blocks 7 and 31; 33 nonempty blocks.\n"
        "# Labels correspond to seed columns 0..816; independent full sweep in verify_q16.c.\n"
        + " ".join(map(str, labels)) + "\n"
    )

    gf_selftest(M)
    assert MODULUS[M] == 0x25
    out = [beta << (r + M) for beta in range(1, Q)]
    for h, label in zip(seed, labels):
        if label == 0:  # star
            out.extend(h | (xi << (r + 2 * M)) for xi in range(Q))
        else:
            beta = label - 1
            beta2 = gf_mul(beta, beta, M)
            out.extend(
                h | (xi << r)
                | (gf_mul(beta, xi, M) << (r + M))
                | (gf_mul(beta2, xi, M) << (r + 2 * M))
                for xi in range(Q)
            )
    assert len(out) == Q * (n + 1) - 1 == 26175
    assert len(set(out)) == len(out) and all(out)
    assert binary_rank(out) == 41
    write_matrix(OUTPUT, 41, out, [
        "QM_4^3, arXiv:2511.02542 Theorem 6.1, equations (6.4), (6.8).",
        "Seed r=26 n=817; q16 33-block (3,0) partition; GF(32) modulus 0x25.",
        "Indicators: block 0 star; block k=1..32 field element k-1.",
        "r=26+3*5=41; n=32*(817+1)-1=26175.",
        "LSB-first: bit i of a column integer is row i+1.",
    ])
    MANIFEST.write_text(json.dumps({
        "claim": "ell_2(41,3) <= 26175",
        "construction": "QM_4^3, Theorem 6.1 (6.4), (6.8)",
        "seed_sha256": digest(SEED),
        "partition_sha256": digest(PARTITION),
        "output_sha256": digest(OUTPUT),
        "field_modulus_hex": "0x25",
        "blocks": 33,
        "merged_q13_blocks": [7, 31],
        "rank": binary_rank(out),
        "length": len(out),
        "published_table_length": 26238,
        "previous_notebook_length": 26206,
        "certificate": "compute/q16/verify_q16.c and run_all.sh",
    }, indent=2, sort_keys=True) + "\n")
    print("built r=41 n=26175 rank=41")


if __name__ == "__main__":
    main()
