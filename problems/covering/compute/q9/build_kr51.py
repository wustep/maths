#!/usr/bin/env python3
"""Recover the Kaikkonen-Rosendahl 51-column radius-2 seed at r=10.

Source: A.A. Davydov, S. Marcugini, F. Pambianco, "New upper bounds for binary
linear covering codes", arXiv:2511.02542v1, Theorem 4.3, display (4.9), which
reprints the matrix of M.K. Kaikkonen, P. Rosendahl, "New covering codes from
an ADS-like construction", IEEE Trans. Inform. Theory 49(7) 1809-1812 (2003),
p. 1812.  H_KR = [ I_10 | M_KR ], M_KR given as 41 hexadecimal columns.

Emits problems/covering/compute/q9/H_r10_n51_KR.txt in the same row-text format
as compute/H_r10_n50.txt (LSB = row 1), and checks the covering property.
"""
import sys

# (4.9), transcribed line by line from arXiv:2511.02542v1.
M_KR_HEX = (
    "1B6 193 1CC 187 1F6 F7 16E 140 3C 296 22F 303 381 365 "
    "11D 1A3 274 2F2 254 56 F 41 357 208 34 329 28D 31D 3D5 129 3D7 "
    "B7 3EC 2E2 23C AD 34E 155 2E6 371 D4"
).split()

R = 10


def columns():
    cols = [1 << i for i in range(R)]            # I_10
    cols += [int(w, 16) for w in M_KR_HEX]        # M_KR
    return cols


def cover_stats(cols):
    n = len(cols)
    hit = bytearray(1 << R)
    hit[0] = 1
    for c in cols:
        hit[c] = 1
    for i in range(n):
        for j in range(i + 1, n):
            hit[cols[i] ^ cols[j]] = 1
    return sum(hit)


def rank(cols):
    basis, rk = [], 0
    for c in cols:
        for b in basis:
            c = min(c, c ^ b)
        if c:
            basis.append(c)
            basis.sort(reverse=True)
            rk += 1
    return rk


def main():
    cols = columns()
    assert len(M_KR_HEX) == 41, len(M_KR_HEX)
    assert len(cols) == 51
    assert len(set(cols)) == 51, "repeated column"
    assert 0 not in cols, "zero column"
    assert max(cols) < (1 << R)
    rk = rank(cols)
    cov = cover_stats(cols)
    print(f"n={len(cols)} distinct={len(set(cols))} rank={rk} covered={cov}/{1<<R}")
    out = "problems/covering/compute/q9/H_r10_n51_KR.txt"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    with open(out, "w") as f:
        for row in range(R):
            f.write("".join("1" if (c >> row) & 1 else "0" for c in cols) + "\n")
    print("wrote", out)
    return 0 if (rk == R and cov == (1 << R)) else 1


if __name__ == "__main__":
    sys.exit(main())
