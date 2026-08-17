#!/usr/bin/env python3
"""Singer difference sets unfolded to Z, plus greedy extras.

For prime p the cyclic Singer set has size p+1 in Z/(p^2+p+1)Z and unfolds
to a Sidon subset of [0, p^2+p] of size p+1, so

    F(p^2+p+1) >= p+1 = sqrt(N) + 1/2 + o(1).

Adding a bounded number of extra integer points still leaves an O(1)
second term. This script records the extras; it does not claim a dent.
"""

from __future__ import annotations

import json
from pathlib import Path


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def mul(u, v, t, s, r, p):
    """Multiply in F_p[x]/(x^3 - t x^2 - s x - r). u,v are (a0,a1,a2)."""
    # (u0+u1x+u2x^2)(v0+v1x+v2x^2)
    c0 = u[0] * v[0]
    c1 = u[0] * v[1] + u[1] * v[0]
    c2 = u[0] * v[2] + u[1] * v[1] + u[2] * v[0]
    c3 = u[1] * v[2] + u[2] * v[1]
    c4 = u[2] * v[2]
    # x^3 = t x^2 + s x + r
    # x^4 = x * x^3 = t x^3 + s x^2 + r x = t(t x^2+s x+r) + s x^2 + r x
    c0 += c3 * r
    c1 += c3 * s
    c2 += c3 * t
    c0 += c4 * (t * r)
    c1 += c4 * (t * s + r)
    c2 += c4 * (t * t + s)
    return (c0 % p, c1 % p, c2 % p)


def pow_el(g, e, t, s, r, p):
    acc = (1, 0, 0)
    while e:
        if e & 1:
            acc = mul(acc, g, t, s, r, p)
        g = mul(g, g, t, s, r, p)
        e >>= 1
    return acc


def is_nonsquare_disc_cubic(t, s, r, p) -> bool:
    """Irreducible x^3 - t x^2 - s x - r over F_p: no root."""
    for x in range(p):
        if (x * x * x - t * x * x - s * x - r) % p == 0:
            return False
    return True


def factors(n: int) -> list[int]:
    out = []
    f = 2
    m = n
    while f * f <= m:
        if m % f == 0:
            out.append(f)
            while m % f == 0:
                m //= f
        f += 1 if f == 2 else 2
    if m > 1:
        out.append(m)
    return out


def singer(p: int) -> list[int]:
    """Singer set as discrete logs of the trace-zero line in F_{p^3}."""
    order = p ** 3 - 1
    fac = factors(order)
    # find primitive poly and generator x
    for t in range(p):
        for s in range(p):
            for r in range(1, p):
                if not is_nonsquare_disc_cubic(t, s, r, p):
                    continue
                g = (0, 1, 0)  # the element x
                if any(pow_el(g, order // q, t, s, r, p) == (1, 0, 0) for q in fac):
                    continue
                # Trace_{p^3/p}(a0+a1 x+a2 x^2). For a random basis this is not
                # a0. Use the field trace via the companion: Tr(y) = y+y^p+y^{p^2}.
                # Hyperplane { y : Tr(y) = 0 }. Projectivize by F_p^* and take dlog.
                def tr(y):
                    yp = pow_el(y, p, t, s, r, p)
                    yp2 = pow_el(y, p * p, t, s, r, p)
                    return (
                        (y[0] + yp[0] + yp2[0]) % p,
                        (y[1] + yp[1] + yp2[1]) % p,
                        (y[2] + yp[2] + yp2[2]) % p,
                    )

                # Trace lands in the prime field, so tr(y) = (c,0,0).
                cur = (1, 0, 0)
                idxs = []
                for i in range(order):
                    tv = tr(cur)
                    if tv[0] == 0 and tv[1] == 0 and tv[2] == 0:
                        idxs.append(i)
                    cur = mul(cur, g, t, s, r, p)
                # Projectivize: i ~ j if α^i / α^j ∈ F_p^*, i.e. (p^2+p+1) | (i-j)
                # because F_p^* = (α^{(p^3-1)/(p-1)}) = α^{p^2+p+1}.
                mod = p * p + p + 1
                residues = sorted({i % mod for i in idxs})
                return residues
    raise RuntimeError(f"no Singer generator for p={p}")


def is_sidon(xs: list[int]) -> bool:
    seen = set()
    n = len(xs)
    for i in range(n):
        for j in range(i, n):
            s = xs[i] + xs[j]
            if s in seen:
                return False
            seen.add(s)
    return True


def greedy_extend(base: list[int], N: int) -> list[int]:
    sums = set()
    xs = list(base)
    for i, a in enumerate(xs):
        for b in xs[i:]:
            sums.add(a + b)
    for y in range(N + 1):
        if y in xs:
            continue
        doubles = {y + y}
        crosses = {y + x for x in xs}
        if doubles & sums or crosses & sums:
            continue
        xs.append(y)
        sums |= doubles | crosses
    xs.sort()
    return xs


def main():
    primes = [p for p in range(2, 32) if is_prime(p)]
    rows = []
    for p in primes:
        A = singer(p)
        N = p * p + p + 1
        # unfold into [0, N-1]
        A = sorted(set(x % N for x in A))
        ok = is_sidon(A) and len(A) == p + 1
        extra = greedy_extend(A, N - 1)
        rec = {
            "p": p,
            "N": N,
            "size": len(A),
            "sidon": ok,
            "second_term": len(A) - N ** 0.5,
            "extra_in_interval": len(extra) - len(A),
        }
        rows.append(rec)
        print(json.dumps(rec), flush=True)
    Path(__file__).resolve().parent.joinpath("singer_greedy.json").write_text(
        json.dumps(rows, indent=2)
    )
    extras = [r["extra_in_interval"] for r in rows if r["sidon"]]
    print("ok", sum(1 for r in rows if r["sidon"]), "/", len(rows))
    print("extras", extras)


if __name__ == "__main__":
    main()
