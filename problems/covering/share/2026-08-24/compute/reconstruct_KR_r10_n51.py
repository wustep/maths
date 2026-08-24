#!/usr/bin/env python3
"""Reconstruct the Kaikkonen--Rosendahl length-51 seed.

Theorem 4.3 of arXiv:2511.02542 lists 41 hexadecimal columns of M_KR,
MSB-first (row 1 = high bit). This script reads those words as 10-bit
integers, prepends the 10 identity columns, and checks coverage.
The repository stores columns LSB-first; the two readings differ by
bit reversal. Coverage is preserved either way. Expected values below
are for the listing as printed: length 51, 51 distinct, max 1004,
1024/1024. No matrix file is written.
"""

from covering_seed_io import KR_HEX, cover_mult, f2_rank


def build_kr():
    assert len(KR_HEX) == 41
    identity = [1 << i for i in range(10)]
    tail = [int(word, 16) for word in KR_HEX]
    columns = identity + tail
    assert len(columns) == 51
    assert len(set(columns)) == 51
    assert 0 not in columns
    return columns


def main():
    columns = build_kr()
    r = 10
    total = 1 << r
    rank = f2_rank(columns)
    mult = cover_mult(columns, r)
    covered = sum(1 for s in range(total) if mult[s] > 0)
    print("KR from Theorem 4.3 hex (MSB-first listing, 10 identity columns)")
    print("length: %d" % len(columns))
    print("distinct: %d" % len(set(columns)))
    print("max: %d" % max(columns))
    print("F2-rank: %d" % rank)
    print("coverage: %d/%d" % (covered, total))
    assert len(columns) == 51
    assert len(set(columns)) == 51
    assert max(columns) == 1004
    assert covered == total
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
