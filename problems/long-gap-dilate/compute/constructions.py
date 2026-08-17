"""Families that might minimise max_d g(dA) for |A| ~ sqrt(p)."""

from __future__ import annotations

import random

from gaplib import primitive_root, uniq_mod


def small_squares(p: int, n: int) -> list[int]:
    """{0,1,4,...,k^2} truncated/padded to size n."""
    A = []
    j = 0
    while len(A) < n and j < p:
        v = (j * j) % p
        if v not in A:
            A.append(v)
        j += 1
    if len(A) < n:
        for x in range(p):
            if x not in A:
                A.append(x)
            if len(A) == n:
                break
    return uniq_mod(A, p)[:n]


def geometric(p: int, n: int, base: int | None = None) -> list[int]:
    g = base if base is not None else primitive_root(p)
    A = [0]
    x = 1
    seen = {0}
    while len(A) < n:
        if x not in seen:
            A.append(x)
            seen.add(x)
        x = (x * g) % p
        if x == 1 and len(A) < n:
            # full orbit; fill with leftovers
            for y in range(p):
                if y not in seen:
                    A.append(y)
                    seen.add(y)
                if len(A) == n:
                    break
            break
    return uniq_mod(A, p)[:n]


def subgroup(p: int, n: int) -> list[int] | None:
    """The unique subgroup of F_p^* of order n, plus 0 if n+1 wanted.
    Returns None if n does not divide p-1."""
    if n <= 0 or (p - 1) % n != 0:
        return None
    g = primitive_root(p)
    step = (p - 1) // n
    h = pow(g, step, p)
    A = []
    x = 1
    for _ in range(n):
        A.append(x)
        x = (x * h) % p
    return uniq_mod(A, p)


def nearest_subgroup(p: int, n: int) -> tuple[list[int], int]:
    """Subgroup of order dividing p-1 nearest n, padded/truncated to n."""
    best_k = 1
    for k in range(1, p):
        if (p - 1) % k == 0 and abs(k - n) < abs(best_k - n):
            best_k = k
    H = subgroup(p, best_k)
    assert H is not None
    if len(H) >= n:
        return H[:n], best_k
    S = set(H)
    for x in range(p):
        if x not in S:
            H.append(x)
            S.add(x)
        if len(H) == n:
            break
    return uniq_mod(H, p), best_k


def equally_spaced(p: int, n: int) -> list[int]:
    return uniq_mod([(i * p) // n for i in range(n)], p)


def random_set(p: int, n: int, rng: random.Random) -> list[int]:
    return sorted(rng.sample(range(p), n))


def jittered_grid(p: int, n: int, rng: random.Random, width: int | None = None) -> list[int]:
    """Equally spaced points with a modular jitter of size ~width."""
    if width is None:
        width = max(1, int(round((p / n) ** 0.5)))
    A = []
    seen = set()
    for i in range(n):
        base = (i * p) // n
        for _try in range(20):
            x = (base + rng.randrange(-width, width + 1)) % p
            if x not in seen:
                seen.add(x)
                A.append(x)
                break
        else:
            for y in range(p):
                if y not in seen:
                    seen.add(y)
                    A.append(y)
                    break
    return uniq_mod(A, p)[:n]


def singer_prime_pairs(limit_q: int = 80) -> list[tuple[int, int]]:
    """(q, p=q^2+q+1) with p prime. q a prime power is required for a plane,
    but we only list p prime; construction below needs prime q or 2^k."""
    from gaplib import is_prime

    out = []
    for q in range(2, limit_q + 1):
        p = q * q + q + 1
        if is_prime(p):
            out.append((q, p))
    return out


def gf_mul(a: int, b: int, irr: list[int], q: int) -> int:
    """Multiply two degree<3 polynomials packed as a0+a1 q+a2 q^2, mod irr and q."""
    # unpack
    aa = [(a // q**i) % q for i in range(3)]
    bb = [(b // q**i) % q for i in range(3)]
    prod = [0, 0, 0, 0, 0]
    for i in range(3):
        for j in range(3):
            prod[i + j] = (prod[i + j] + aa[i] * bb[j]) % q
    # irr is monic cubic x^3 + c2 x^2 + c1 x + c0, stored [c0,c1,c2,1]
    for deg in range(4, 2, -1):
        if prod[deg] == 0:
            continue
        coef = prod[deg]
        # subtract coef * irr * x^{deg-3}
        for k in range(4):
            prod[deg - 3 + k] = (prod[deg - 3 + k] - coef * irr[k]) % q
    return prod[0] + q * prod[1] + q * q * prod[2]


def find_irreducible_cubic(q: int) -> list[int]:
    """Monic irreducible x^3 + c2 x^2 + c1 x + c0 over F_q, q prime."""
    # brute: a cubic is irreducible over F_q iff it has no root
    for c0 in range(q):
        for c1 in range(q):
            for c2 in range(q):
                ok = True
                for x in range(q):
                    val = (x * x * x + c2 * x * x + c1 * x + c0) % q
                    if val == 0:
                        ok = False
                        break
                if ok:
                    return [c0, c1, c2, 1]
    raise RuntimeError(f"no irr cubic over F_{q}")


def singer_difference_set(q: int) -> list[int]:
    """Singer difference set in Z/(q^2+q+1). Requires q prime."""
    """Singer difference set in Z/(q^2+q+1), q prime.

    Elements i in 0..q^2+q such that Tr_{q^3/q}(ω^i)=0 for a primitive ω.
    Trace of a0+a1 x+a2 x^2 (with x^3=...) is 3 a0 if we use a normal basis
    naively — we use the power basis and Tr(c) = c + c^q + c^{q^2}.
    """
    p = q * q + q + 1
    irr = find_irreducible_cubic(q)
    order = q**3 - 1
    # find a primitive element of F_{q^3}
    # elements encoded 0..q^3-1

    def pow_el(a: int, e: int) -> int:
        r = 1  # 1 + 0x + 0x^2
        while e:
            if e & 1:
                r = gf_mul(r, a, irr, q)
            a = gf_mul(a, a, irr, q)
            e >>= 1
        return r

    def is_primitive(a: int) -> bool:
        if a == 0:
            return False
        # order divides q^3-1 = (q-1)(q^2+q+1)
        if pow_el(a, order) != 1:
            return False
        if pow_el(a, (q**3 - 1) // (q - 1)) == 1:
            return False
        if pow_el(a, q - 1) == 1:
            return False
        # also check other prime factors of q-1 if q-1 is composite
        m = q - 1
        f = 2
        facts = []
        mm = m
        while f * f <= mm:
            if mm % f == 0:
                facts.append(f)
                while mm % f == 0:
                    mm //= f
            f += 1 if f == 2 else 2
        if mm > 1:
            facts.append(mm)
        for pr in facts:
            if pow_el(a, order // pr) == 1:
                return False
        # and p = q^2+q+1 may be composite-factored already as a single prime often
        if not _is_prime_small(p):
            # factor p
            pp = p
            f = 2
            while f * f <= pp:
                if pp % f == 0:
                    if pow_el(a, order // f) == 1:
                        return False
                    while pp % f == 0:
                        pp //= f
                f += 1
            if pp > 1 and pow_el(a, order // pp) == 1:
                return False
        else:
            if pow_el(a, order // p) == 1:
                return False
        return True

    prim = None
    for a in range(1, q**3):
        if is_primitive(a):
            prim = a
            break
    if prim is None:
        raise RuntimeError(f"no primitive element in F_{q}^3")

    def trace(c: int) -> int:
        # c + c^q + c^{q^2} as an element of the prime field (degree 0)
        s = c
        cq = pow_el(c, q)
        s_un = _add3(c, cq, pow_el(c, q * q), q)
        # result should lie in F_q, i.e. higher coeffs 0
        return s_un % q

    D = []
    x = 1
    for i in range(p):
        if trace(x) == 0:
            D.append(i)
        x = gf_mul(x, prim, irr, q)
    # Singer difference set has size q+1
    return D


def _add3(a: int, b: int, c: int, q: int) -> int:
    def unpack(z):
        return [(z // q**i) % q for i in range(3)]

    aa, bb, cc = unpack(a), unpack(b), unpack(c)
    s = [(aa[i] + bb[i] + cc[i]) % q for i in range(3)]
    return s[0] + q * s[1] + q * q * s[2]


def _is_prime_small(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return False
        f += 2
    return True
