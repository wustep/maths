"""Explicit families of candidate cyclic sum covers."""

from __future__ import annotations

import math


def two_ap(n: int) -> list[int]:
    """Elementary interval + AP. Size < 2 sqrt(n)."""
    a = math.ceil(math.sqrt(n))
    A = set(range(a))
    A.update((i * a) % n for i in range(a))
    return sorted(A)


def three_ap(n: int, d: int, e: int, ell: int | None = None) -> list[int]:
    """I ∪ dI ∪ eI with I = {0,...,ell-1}."""
    if ell is None:
        ell = math.ceil(math.sqrt(n / 3))
    A = set(range(ell))
    A.update((i * d) % n for i in range(ell))
    A.update((i * e) % n for i in range(ell))
    return sorted(A)


def mrose(t: int) -> tuple[int, list[int]]:
    """Mrose interval 2-basis: S+S covers [0, 14t^2+10t-1]."""
    A = set()
    A.update(range(0, t + 1))
    A.update(range(2 * t, 3 * t * t + t + 1, t))
    A.update(range(3 * t * t + 2 * t, 4 * t * t + 2 * t, t + 1))
    A.update(range(6 * t * t + 4 * t, 6 * t * t + 5 * t + 1))
    A.update(range(10 * t * t + 7 * t, 10 * t * t + 8 * t + 1))
    n = 14 * t * t + 10 * t
    return n, sorted(A)


def singer_exponents(q: int) -> list[int] | None:
    """Singer difference set in Z/(q^2+q+1), as exponents.

    D = { i : Tr_{q^3/q}(ω^i) = 0 } for a primitive ω of F_{q^3},
    provided q is a prime power. Implemented only for prime q,
    via explicit cubic.
    """
    if not _is_prime(q):
        return None
    n = q * q + q + 1
    # Find a primitive polynomial x^3 - a x^2 - b x - c over F_q
    # and a primitive element of F_{q^3}.
    field = _prime_field_cubic(q)
    if field is None:
        return None
    mul, tr0 = field
    D = []
    x = 1  # ω^0 represented as the vector index of ω^0 = 1
    one = 1
    for i in range(n):
        if tr0(x):
            D.append(i)
        x = mul(x, one)  # multiply by ω; `one` is rebound below
        # fix: multiply by the primitive element, stored as prim
        break
    return None  # replaced by singer.py


def _is_prime(p: int) -> bool:
    if p < 2:
        return False
    if p < 4:
        return True
    if p % 2 == 0:
        return False
    d = 3
    while d * d <= p:
        if p % d == 0:
            return False
        d += 2
    return True


def _prime_field_cubic(q: int):
    return None


def bose_set(q: int, primitive_root: int | None = None) -> tuple[int, list[int]] | None:
    """Bose Sidon set of size q in Z/(q^2-1).

    A = { log_ω (θ + a) : a in F_q } where F_{q^2} = F_q(θ), θ^2 = g
    a non-square, ω primitive in F_{q^2}^*.

    Implemented for prime q.
    """
    if not _is_prime(q):
        return None
    n = q * q - 1
    # Represent F_{q^2} as F_q[x]/(x^2 - s) with s a non-residue.
    s = 2
    while pow(s, (q - 1) // 2, q) == 1:
        s += 1
        if s >= q:
            return None

    # Elements: u + v w, w^2 = s, as pair (u, v) with u,v in 0..q-1.
    # Find a primitive element by testing random candidates.
    def mul(a, b):
        u1, v1 = a
        u2, v2 = b
        return ((u1 * u2 + s * v1 * v2) % q, (u1 * v2 + v1 * u2) % q)

    def pow_el(a, e):
        r = (1, 0)
        while e:
            if e & 1:
                r = mul(r, a)
            a = mul(a, a)
            e >>= 1
        return r

    def order_ok(a):
        if a == (0, 0) or a == (1, 0):
            return False
        # order divides q^2-1; check not 1 at proper divisors
        # enough to check (q^2-1)/p for prime p | q^2-1
        return pow_el(a, n) == (1, 0) and pow_el(a, (n) // _smallest_prime_factor(n)) != (1, 0)

    # brute primitive: try (g, 1)
    prim = None
    for u in range(q):
        for v in range(1, q):
            cand = (u, v)
            if pow_el(cand, n) != (1, 0):
                continue
            ok = True
            m = n
            # factor n = (q-1)(q+1)
            for pdiv in {*_factor(q - 1), *_factor(q + 1)}:
                if pow_el(cand, n // pdiv) == (1, 0):
                    ok = False
                    break
            if ok:
                prim = cand
                break
        if prim is not None:
            break
    if prim is None:
        return None

    # discrete logs of (a, 1) = a + θ, θ = w, w^2 = s. Use θ = (0,1).
    # Build log table of all nonzero field elements.
    log = {}
    x = (1, 0)
    for i in range(n):
        log[x] = i
        x = mul(x, prim)
    A = []
    for a in range(q):
        el = (a, 1)  # a + θ
        if el not in log:
            return None
        A.append(log[el])
    return n, sorted(set(A))


def _factor(m: int) -> list[int]:
    fac = []
    d = 2
    while d * d <= m:
        if m % d == 0:
            fac.append(d)
            while m % d == 0:
                m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        fac.append(m)
    return fac


def _smallest_prime_factor(m: int) -> int:
    return _factor(m)[0]


def bel_product(q: int) -> tuple[int, list[int]] | None:
    """BEL k=2 family. Wrapper around bel.py (paper parameters)."""
    from bel import pick_r, generators, embed

    rs = pick_r(q)
    if rs is None:
        return None
    r1, r2 = rs
    X, _, _ = generators(r1, r2)
    A = sorted({embed(p, r1, r2) for p in X} | {0})
    return r1 * r2 * 6, A
