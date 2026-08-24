#!/usr/bin/env python3
"""Enumerate QM_2^2 at m=4 over GF(16), polynomial x^4+x+1 (0x13).

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


PUBLISHED_N = 831
PUBLISHED_MU = 1.31873


def main():
    r0, n0, columns0 = read_matrix()
    blob = read_partition()
    assert blob["columns"] == columns0
    r, columns = qm2_squared(r0, columns0, blob["block_of_column"], m=4)
    n = len(columns)
    total = 1 << r
    assert (r, n) == (18, 815), (r, n)
    mult = cover_mult(columns, r)
    covered = sum(1 for s in range(total) if mult[s] > 0)
    mu = density(n, r)
    print("QM_2^2  m=4  GF(16)  poly x^4+x+1 (0x13)")
    print("n=%d  r=%d" % (n, r))
    print("coverage: %d/%d" % (covered, total))
    print("density: %.5f" % mu)
    print("published: n=%d  density=%.5f" % (PUBLISHED_N, PUBLISHED_MU))
    assert covered == total
    assert abs(mu - 1.26847) < 5e-6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
