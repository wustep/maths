#!/usr/bin/env python3
"""Sanity-check the four explicit groups of order 42 used in the Cayley census."""


def check(name, mul, n=42):
    inv = {}
    for a in range(n):
        if mul(a, 0) != a or mul(0, a) != a:
            return f"{name}: id fail {a}"
        found = None
        for b in range(n):
            if mul(a, b) == 0 and mul(b, a) == 0:
                found = b
                break
        if found is None:
            return f"{name}: no inv {a}"
        inv[a] = found
    for a in range(n):
        for b in range(n):
            for c in range(n):
                if mul(mul(a, b), c) != mul(a, mul(b, c)):
                    return f"{name}: assoc {a,b,c}"
    return f"{name}: ok n={n} ninv={sum(1 for a in range(1,n) if inv[a]==a)}"


def d21(a, b):
    ak, as_, bk, bs = a % 21, a // 21, b % 21, b // 21
    if as_ == 0:
        return ((ak + bk) % 21) + 21 * bs
    return ((ak - bk + 21) % 21) + 21 * (1 - bs)


def d7(a, b):
    ak, as_, bk, bs = a % 7, a // 7, b % 7, b // 7
    if as_ == 0:
        return ((ak + bk) % 7) + 7 * bs
    return ((ak - bk + 7) % 7) + 7 * (1 - bs)


def c3d7(a, b):
    return 14 * ((a // 14 + b // 14) % 3) + d7(a % 14, b % 14)


def agl(a, b):
    ax, as_ = a // 6, a % 6 + 1
    bx, bs = b // 6, b % 6 + 1
    x = (ax + as_ * bx) % 7
    s = (as_ * bs) % 7
    return 6 * x + (s - 1)


# S3 from the same 6 perms
P = [
    (0, 1, 2),
    (1, 2, 0),
    (2, 0, 1),
    (0, 2, 1),
    (2, 1, 0),
    (1, 0, 2),
]
s3mul = {}
for a in range(6):
    for b in range(6):
        q = (P[a][P[b][0]], P[a][P[b][1]], P[a][P[b][2]])
        s3mul[a, b] = P.index(q)


def c7s3(a, b):
    return 6 * ((a // 6 + b // 6) % 7) + s3mul[a % 6, b % 6]


A = [1, 2, 4]


def f21(p, q):
    px, pa = p // 3, A[p % 3]
    qx, qa = q // 3, A[q % 3]
    x = (px + pa * qx) % 7
    a = (pa * qa) % 7
    ai = {1: 0, 2: 1, 4: 2}[a]
    return 3 * x + ai


def c2f21(a, b):
    return 21 * ((a // 21 + b // 21) & 1) + f21(a % 21, b % 21)


if __name__ == "__main__":
    for name, fn in [
        ("D21", d21),
        ("C3xD7", c3d7),
        ("AGL17", agl),
        ("C7xS3", c7s3),
        ("C2xF21", c2f21),
    ]:
        print(check(name, fn))
