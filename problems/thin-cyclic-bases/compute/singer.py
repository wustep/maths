"""Singer difference sets in Z/(q^2+q+1) for prime q, and their sumsets."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, uncovered


def is_prime(p: int) -> bool:
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


def factor(m: int) -> list[int]:
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


def find_irreducible_cubic(q: int) -> tuple[int, int, int] | None:
    """Monic x^3 + a x^2 + b x + c irreducible over F_q."""
    for a in range(q):
        for b in range(q):
            for c in range(1, q):
                # no root
                ok = True
                for x in range(q):
                    if (x * x * x + a * x * x + b * x + c) % q == 0:
                        ok = False
                        break
                if ok:
                    return a, b, c
    return None


class Fq3:
    """F_{q^3} = F_q[x]/(x^3 + a x^2 + b x + c), elements as u + v ω + w ω^2 packed as u+q(v+q w)."""

    def __init__(self, q: int):
        coef = find_irreducible_cubic(q)
        if coef is None:
            raise ValueError(f"no cubic for q={q}")
        self.q = q
        self.a, self.b, self.c = coef
        self.N = q * q * q
        # primitive: order q^3-1
        self.prim = self._find_primitive()

    def add(self, x, y):
        q = self.q
        u1, v1, w1 = x % q, (x // q) % q, x // (q * q)
        u2, v2, w2 = y % q, (y // q) % q, y // (q * q)
        return (u1 + u2) % q + q * ((v1 + v2) % q) + q * q * ((w1 + w2) % q)

    def mul(self, x, y):
        q, a, b, c = self.q, self.a, self.b, self.c
        u1, v1, w1 = x % q, (x // q) % q, x // (q * q)
        u2, v2, w2 = y % q, (y // q) % q, y // (q * q)
        # (u1 + v1 ω + w1 ω^2)(u2 + v2 ω + w2 ω^2)
        # ω^3 = -a ω^2 - b ω - c
        # ω^4 = ω ω^3 = -a ω^3 - b ω^2 - c ω
        p0 = u1 * u2
        p1 = u1 * v2 + v1 * u2
        p2 = u1 * w2 + v1 * v2 + w1 * u2
        p3 = v1 * w2 + w1 * v2
        p4 = w1 * w2
        # reduce ω^4
        # ω^3 = (-c) + (-b) ω + (-a) ω^2
        rc, rb, ra = (-c) % q, (-b) % q, (-a) % q
        # ω^4 = ω * ω^3 = rc ω + rb ω^2 + ra ω^3
        #       = ra*rc + (rc + ra*rb) ω + (rb + ra*ra) ω^2
        e0 = (ra * rc) % q
        e1 = (rc + ra * rb) % q
        e2 = (rb + ra * ra) % q
        u = (p0 + p3 * rc + p4 * e0) % q
        v = (p1 + p3 * rb + p4 * e1) % q
        w = (p2 + p3 * ra + p4 * e2) % q
        return u + q * v + q * q * w

    def pow(self, x, e):
        r = 1  # 1 + 0ω + 0ω^2
        while e:
            if e & 1:
                r = self.mul(r, x)
            x = self.mul(x, x)
            e >>= 1
        return r

    def tr(self, x):
        """Tr_{q^3/q}(x) = x + x^q + x^{q^2}, which lands in F_q (w=v=0)."""
        q = self.q
        y = self.add(x, self.add(self.pow(x, q), self.pow(x, q * q)))
        # should have v=w=0
        return y % q

    def _find_primitive(self):
        q = self.q
        order = q * q * q - 1
        primes = factor(order)
        # try ω = 0+1*ω+0 = q, then small elements
        for cand in range(2, self.N):
            if self.pow(cand, order) != 1:
                continue
            if all(self.pow(cand, order // p) != 1 for p in primes):
                return cand
        raise RuntimeError(f"no primitive element for q={q}")


def singer_difference_set(q: int) -> tuple[int, list[int]]:
    """Return (v, D) with v = q^2+q+1, D a Singer difference set, |D|=q+1."""
    if not is_prime(q):
        raise ValueError("only prime q implemented")
    F = Fq3(q)
    v = q * q + q + 1
    # Cosets of F_q^* = <ω^v> in F_{q^3}^* are represented by ω^0,...,ω^{v-1}.
    # Tr vanishes on a whole coset or on none.
    omega = F.prim
    D = []
    x = 1
    for i in range(v):
        if F.tr(x) == 0:
            D.append(i)
        x = F.mul(x, omega)
    if len(D) != q + 1:
        raise RuntimeError(f"Singer size {len(D)} != {q+1} for q={q}")
    return v, D


def is_difference_cover(D, v) -> bool:
    seen = [False] * v
    for a in D:
        for b in D:
            seen[(a - b) % v] = True
    return all(seen)


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from bases import cover_stats, uncovered  # noqa: F811

    qs = [3, 5, 7, 11, 13]
    if len(sys.argv) > 1:
        qs = [int(x) for x in sys.argv[1:]]
    out = []
    for q in qs:
        v, D = singer_difference_set(q)
        st = cover_stats(D, v)
        st["q"] = q
        st["v"] = v
        st["diff_cover"] = is_difference_cover(D, v)
        st["missed_list"] = uncovered(D, v)[:20]
        st["D"] = D
        print(
            f"q={q} v={v} |D|={st['m']} sumcover={st['ok']} "
            f"covered={st['covered']} ratio={st['ratio']:.4f} "
            f"diff={st['diff_cover']}"
        )
        out.append(st)
    with open("compute/singer_sumsets.json", "w") as f:
        json.dump(out, f, indent=2)
