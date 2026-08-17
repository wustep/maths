#!/usr/bin/env python3
"""Bevan–Erskine–Lewis k=2 directed template, checked in the product group.

T = Z_r1 × Z_r2 × Z_6, pairwise coprime orders so T is cyclic of order 6 r1 r2.
Connection set X as in arXiv:1506.04962, Theorem 9 with B={0,1,2,4}.
Diameter ≤ 2 iff (X ∪ {0}) + (X ∪ {0}) = T.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

BEL = math.sqrt(8 / 3)


def pick_r(q: int) -> tuple[int, int] | None:
    """Paper Thm 10(a): r1=q, r2=q-2, q>=7, q≡1 (mod 6)."""
    if q < 7 or q % 6 != 1:
        return None
    r1, r2 = q, q - 2
    if r2 <= 1:
        return None
    if math.gcd(r1, r2) != 1:
        return None
    if math.gcd(r1, 6) != 1 or math.gcd(r2, 6) != 1:
        return None
    return r1, r2


def generators(r1: int, r2: int):
    m = r1 - r2
    co = r2 + 2 * m  # = 2 r1 - r2
    cu = r1
    X = set()
    # (x, 0, 0), x ≠ 0
    for x in range(1, r1):
        X.add((x, 0, 0))
    # (0, y, 1)
    for y in range(r2):
        X.add((0, y, 1))
    # (t, t, 2), 0 ≤ t < co
    for t in range(co):
        X.add((t % r1, t % r2, 2))
    # (t, 2t, 4), 0 ≤ t < cu
    for t in range(cu):
        X.add((t % r1, (2 * t) % r2, 4))
    return X, co, cu


def add(a, b, r1, r2):
    return ((a[0] + b[0]) % r1, (a[1] + b[1]) % r2, (a[2] + b[2]) % 6)


def covered_count(X, r1, r2):
    n = r1 * r2 * 6
    seen = set()
    A = list(X | {(0, 0, 0)})
    for i, a in enumerate(A):
        seen.add(add(a, a, r1, r2))
        for b in A[i + 1 :]:
            seen.add(add(a, b, r1, r2))
    return len(seen), n, A


def embed(pt, r1, r2):
    """CRT: val ≡ x (mod r1), ≡ y (mod r2), ≡ z (mod 6)."""
    x, y, z = pt
    n = r1 * r2 * 6
    n1, n2, n3 = r2 * 6, r1 * 6, r1 * r2
    v = 0
    v += x * n1 * pow(n1, -1, r1)
    v += y * n2 * pow(n2, -1, r2)
    v += z * n3 * pow(n3, -1, 6)
    return v % n


def run_one(r1, r2):
    X, co, cu = generators(r1, r2)
    cov, n, A = covered_count(X, r1, r2)
    m = len(A)
    return {
        "r1": r1,
        "r2": r2,
        "n": n,
        "m": m,
        "co": co,
        "cu": cu,
        "degree": len(X),
        "covered": cov,
        "ok": cov == n,
        "ratio": m / math.sqrt(n),
        "bel": BEL,
        "A": sorted(embed(p, r1, r2) for p in A) if cov == n else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qs", default="7,13,19,25,31,37,43")
    ap.add_argument("--out", default="compute/bel_eval.json")
    args = ap.parse_args()
    rows = []
    for q in [int(x) for x in args.qs.split(",")]:
        rs = pick_r(q)
        if rs is None:
            print(f"q={q} no r1,r2", flush=True)
            continue
        rec = run_one(*rs)
        rec["q"] = q
        print(
            f"q={q} r1={rec['r1']} r2={rec['r2']} n={rec['n']} m={rec['m']} "
            f"covered={rec['covered']} ok={rec['ok']} ratio={rec['ratio']:.5f}",
            flush=True,
        )
        if rec["A"] is not None:
            rec["A_preview"] = rec["A"][:12]
            # keep full A only for small n
            if rec["n"] > 4000:
                rec["A"] = None
        rows.append(rec)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(rows, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
