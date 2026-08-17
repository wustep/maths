#!/usr/bin/env python3
"""Inspect the non-homogeneous Rédei polynomial for an interval B.

w(d,t) = d * prod_{a in A} prod_{j=1..m} (t + j + d*a)   over F_p.
Compare deg of the full w against the homogeneous analysis.
Also reconstruct u,v in w = (t^p-t)u + (d^p-d)v and look at degrees.
"""

from __future__ import annotations

import itertools

import numpy as np


def poly_mul_2d(A, B, p):
    """Multiply two 2-var polynomials given as arrays A[i,j] = coeff d^i t^j."""
    di, dj = A.shape
    ei, ej = B.shape
    out = np.zeros((di + ei - 1, dj + ej - 1), dtype=object)
    for i in range(di):
        for j in range(dj):
            if A[i, j] == 0:
                continue
            out[i : i + ei, j : j + ej] = (
                out[i : i + ei, j : j + ej] + A[i, j] * B
            ) % p
    return out % p


def linear(c0, cd, ct, p):
    """c0 + cd*d + ct*t"""
    M = np.zeros((2, 2), dtype=object)
    M[0, 0] = c0 % p
    M[1, 0] = cd % p
    M[0, 1] = ct % p
    return M


def build_w(A, m, p):
    w = np.zeros((2, 1), dtype=object)
    w[1, 0] = 1  # the front factor d
    for a in A:
        for j in range(1, m + 1):
            w = poly_mul_2d(w, linear(j, a, 1, p), p)
    return w


def reduce_mod_fermat(w, p):
    """Write w = (t^p-t)u + (d^p-d)v + r with r deg <p in each var.
    For deg < 2p this is straightforward reduction.
    """
    Di, Dj = w.shape
    # first reduce high t powers using t^p = t
    # we only handle deg < 2p
    R = np.zeros((min(Di, p), p), dtype=object)
    for i in range(Di):
        for j in range(Dj):
            coef = int(w[i, j]) % p
            if coef == 0:
                continue
            ii = i
            jj = j
            # reduce d^i : if i>=p, d^p=d so d^p * d^{i-p} = d^{i-p+1}
            while ii >= p:
                ii = ii - p + 1
            while jj >= p:
                jj = jj - p + 1
            if ii < p and jj < p:
                R[ii, jj] = (R[ii, jj] + coef) % p
    return R


def degrees(w):
    Di, Dj = w.shape
    max_tot = -1
    max_d = -1
    max_t = -1
    nterms = 0
    for i in range(Di):
        for j in range(Dj):
            if int(w[i, j]) % 1 == 0 and int(w[i, j]) != 0:
                nterms += 1
                max_tot = max(max_tot, i + j)
                max_d = max(max_d, i)
                max_t = max(max_t, j)
    return {"deg_tot": max_tot, "deg_d": max_d, "deg_t": max_t, "nterms": nterms, "shape": w.shape}


def main():
    # small example: p=11, A={0,1,3}, n=3, Shakan m >= 2*11/3-1 ≈ 6.3
    p = 11
    A = [0, 1, 3]
    for m in range(3, 9):
        w = build_w(A, m, p)
        info = degrees(w)
        R = reduce_mod_fermat(w, p)
        rinfo = degrees(R)
        # is R identically 0? (w vanishes on F_p^2)
        nz = int(np.sum(R.astype(int) % p != 0))
        print(f"p={p} A={A} m={m} nm={len(A)*m} w={info} remain_nz={nz} R={rinfo}")


if __name__ == "__main__":
    main()
