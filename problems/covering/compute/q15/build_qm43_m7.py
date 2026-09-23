#!/usr/bin/env python3
"""Regenerate the r=47, n=104703 QM_4^3 matrix from the 817 seed."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

COMPUTE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPUTE))
from build_qm3 import binary_rank, gf_mul, gf_selftest, read_matrix, write_matrix

M = 7
SIZE = 1 << M


def labels(path: Path) -> list[int]:
    return [int(word) for line in path.read_text().splitlines()
            for word in line.split('#', 1)[0].split()]


def refine(old: list[int]) -> list[int]:
    groups = [[i for i, block in enumerate(old) if block == b]
              for b in range(65)]
    assert all(groups) and len(groups[1]) == 31
    assert len(groups[2]) == len(groups[3]) == 32
    refined = [-1] * len(old)
    next_label = 0
    for block, members in enumerate(groups):
        if block in (1, 2):
            pieces = [[i] for i in members]
        elif block == 3:
            pieces = [[members[0]], [members[1]], [members[2]], members[3:]]
        else:
            pieces = [members]
        for piece in pieces:
            for i in piece:
                refined[i] = next_label
            next_label += 1
    assert next_label == 129 and sorted(set(refined)) == list(range(129))
    assert all(x >= 0 for x in refined)
    return refined


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('seed', type=Path)
    parser.add_argument('partition65', type=Path)
    parser.add_argument('partition129', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    r, n, seed = read_matrix(args.seed)
    assert (r, n) == (26, 817)
    old = labels(args.partition65)
    assert len(old) == n and sorted(set(old)) == list(range(65))
    new = refine(old)
    args.partition129.write_text(
        '# q15 129-block refinement of q13 p65; block 0 uses star.\n'
        + ' '.join(map(str, new)) + '\n')
    gf_selftest(M)
    output = [xi << (r + M) for xi in range(1, SIZE)]
    for h, block in zip(seed, new):
        if block == 0:
            output.extend(h | (xi << (r + 2*M)) for xi in range(SIZE))
        else:
            beta = block - 1
            beta2 = gf_mul(beta, beta, M)
            output.extend(
                h | (xi << r) | (gf_mul(beta, xi, M) << (r+M))
                | (gf_mul(beta2, xi, M) << (r+2*M))
                for xi in range(SIZE))
    assert len(output) == 104703 and len(set(output)) == len(output)
    assert binary_rank(output) == 47
    write_matrix(args.output, 47, output,
                 ['q15 QM_4^3, m=7, GF(128) modulus 0x83.',
                  'r=47, n=104703; LSB-first rows.'])
    manifest = {
        'claim': 'ell_2(47,3) <= 104703',
        'construction': 'QM_4^3, Theorem 6.1 (6.4), (6.8)',
        'field_modulus_hex': '0x83',
        'seed_sha256': sha256(args.seed),
        'partition65_sha256': sha256(args.partition65),
        'partition129_sha256': sha256(args.partition129),
        'output_sha256': sha256(args.output),
        'seed_blocks': 129,
        'rank': 47,
        'length': 104703,
        'published_length': 104831,
        'improvement': 128,
    }
    args.manifest.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    print('built r=47 n=104703 rank=47; paper n=104831')


if __name__ == '__main__':
    main()
