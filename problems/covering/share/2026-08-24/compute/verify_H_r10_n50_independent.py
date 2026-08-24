#!/usr/bin/env python3
"""Independent check of the committed 10 x 50 matrix.

Reads sibling H_r10_n50.txt (row 1 = LSB) and witness_r10_n50.json.
Does not consult a stored certificate.
"""

from covering_seed_io import (
    MATRIX_PATH,
    WITNESS_PATH,
    cover_mult,
    f2_rank,
    read_matrix,
    read_witness,
)


def main():
    r, n, columns = read_matrix()
    witness = read_witness()
    total = 1 << r
    assert (r, n) == (10, 50), "expected a 10 x 50 matrix, got %d x %d" % (r, n)
    assert 0 not in columns, "a column is zero"
    assert all(0 < c < total for c in columns), "a column left F_2^10"
    assert len(set(columns)) == 50, "columns are not 50 distinct values"
    rank = f2_rank(columns)
    assert rank == 10, "F_2 rank is %d, expected 10" % rank
    assert columns == witness, "witness columns do not match the matrix text"
    mult = cover_mult(columns, r)
    covered = sum(1 for s in range(total) if mult[s] > 0)
    assert covered == total, "coverage %d/%d" % (covered, total)
    column_set = set(columns)
    needs_pair = [s for s in range(total) if s != 0 and s not in column_set]
    assert needs_pair, "covering radius is at most 1, not 2"
    print("H: 10 x 50")
    print("distinct nonzero columns: 50")
    print("F2-rank: 10")
    print("coverage: %d/%d" % (covered, total))
    print("radius: exactly 2 (%d syndromes need a pair)" % len(needs_pair))
    print("witness columns match: %s" % MATRIX_PATH.name)
    print("witness file: %s" % WITNESS_PATH.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
