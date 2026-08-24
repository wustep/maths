#!/usr/bin/env python3
"""Enumerate QM_2^2 at m=5 over GF(32), polynomial x^5+x^2+1 (0x25).

Builds the output from (4.2) and (4.4) of arXiv:2511.02542, using the
committed 50-set and the certified 10-block partition. Enumerates the
full syndrome space. Writes no matrix.
"""

from covering_seed_io import (
    cover_mult,
    density,
    qm2_squared,
    read_matrix,
    read_partition,
)


PUBLISHED_N = 1663
PUBLISHED_MU = 1.31952


def main():
    r0, n0, columns0 = read_matrix()
    blob = read_partition()
    assert blob["columns"] == columns0
    r, columns = qm2_squared(r0, columns0, blob["block_of_column"], m=5)
    n = len(columns)
    total = 1 << r
    assert (r, n) == (20, 1631), (r, n)
    mult = cover_mult(columns, r)
    covered = sum(1 for s in range(total) if mult[s] > 0)
    mu = density(n, r)
    print("QM_2^2  m=5  GF(32)  poly x^5+x^2+1 (0x25)")
    print("n=%d  r=%d" % (n, r))
    print("coverage: %d/%d" % (covered, total))
    print("density: %.5f" % mu)
    print("published: n=%d  density=%.5f" % (PUBLISHED_N, PUBLISHED_MU))
    assert covered == total
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
