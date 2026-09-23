#!/usr/bin/env python3
"""Regenerate the r=41, n=26175 QM_4^3 matrix from the 33-block seed."""

import argparse
import json
from pathlib import Path

from build_qm43_m7 import labels, sha256
from build_qm3 import binary_rank, gf_mul, gf_selftest, read_matrix, write_matrix

M = 5
SIZE = 1 << M


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('seed', type=Path)
    parser.add_argument('partition33', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    r, n, seed = read_matrix(args.seed)
    partition = labels(args.partition33)
    assert (r, n) == (26, 817) and len(partition) == n
    assert sorted(set(partition)) == list(range(33))
    gf_selftest(M)
    output = [xi << (r + M) for xi in range(1, SIZE)]
    for h, block in zip(seed, partition):
        if block == 0:
            output.extend(h | (xi << (r + 2*M)) for xi in range(SIZE))
        else:
            beta = block - 1
            beta2 = gf_mul(beta, beta, M)
            output.extend(
                h | (xi << r) | (gf_mul(beta, xi, M) << (r+M))
                | (gf_mul(beta2, xi, M) << (r+2*M))
                for xi in range(SIZE))
    assert len(output) == 26175 and len(set(output)) == len(output)
    assert binary_rank(output) == 41
    write_matrix(args.output, 41, output,
                 ['q15 QM_4^3, m=5, GF(32) modulus 0x25.',
                  'r=41, n=26175; LSB-first rows.'])
    manifest = {
        'claim': 'ell_2(41,3) <= 26175',
        'construction': 'QM_4^3, Theorem 6.1 (6.4), (6.8)',
        'field_modulus_hex': '0x25',
        'seed_sha256': sha256(args.seed),
        'partition33_sha256': sha256(args.partition33),
        'output_sha256': sha256(args.output),
        'seed_blocks': 33,
        'rank': 41,
        'length': 26175,
        'published_length': 26238,
        'improvement': 63,
    }
    args.manifest.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    print('built r=41 n=26175 rank=41; paper n=26238')


if __name__ == '__main__':
    main()
