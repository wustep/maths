#!/usr/bin/env python3
"""Algebraic seeds: quadratic windows and geometric progressions."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, counting_lower
from singer import is_prime

BEL = math.sqrt(8 / 3)


def primitive_root(p: int) -> int | None:
    if not is_prime(p):
        return None
    fac = []
    m = p - 1
    d = 2
    while d * d <= m:
        if m % d == 0:
            fac.append(d)
            while m % d == 0:
                m //= d
        d += 1 if d == 2 else 2
    if m > 1:
        fac.append(m)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in fac):
            return g
    return None


def main():
    rows = []
    primes = [31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    for p in primes:
        c0 = counting_lower(p)
        bel_m = math.floor(BEL * math.sqrt(p) - 1e-9)
        # quadratic window of length m
        for m in (c0, bel_m, math.ceil(math.sqrt(2 * p)) + 2):
            A = sorted({(x * x) % p for x in range(m)})
            st = cover_stats(A, p)
            st.update(kind="quad_window", p=p, window=m)
            rows.append(st)
        # geometric progression
        g = primitive_root(p)
        if g:
            for m in (c0, bel_m):
                A = []
                x = 1
                for _ in range(m):
                    A.append(x)
                    x = (x * g) % p
                st = cover_stats(A, p)
                st.update(kind="geom", p=p, g=g, m0=m)
                rows.append(st)
        # interval of squares plus an AP of length ~sqrt
        m = math.ceil(math.sqrt(p))
        A = set((x * x) % p for x in range(m + 3))
        A.update(range(m))
        st = cover_stats(A, p)
        st.update(kind="quad+interval", p=p)
        rows.append(st)
        print(
            f"p={p} quad+I m={st['m']} cov={st['covered']} ok={st['ok']} "
            f"ratio={st['ratio']:.3f}",
            flush=True,
        )
    Path("compute/algebraic_eval.json").write_text(json.dumps(rows, indent=2))
    # summary: best coverage ratio among algebraic seeds that cover
    covers = [r for r in rows if r["ok"]]
    print("covering algebraic seeds:", len(covers))
    for r in covers[:20]:
        print(r["kind"], r.get("p"), r["m"], r["ratio"])


if __name__ == "__main__":
    main()
