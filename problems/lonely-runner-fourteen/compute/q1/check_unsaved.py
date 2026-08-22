"""Independent replay of a single ST26 Lemma-4.3 saving question.

Given k, p and a speed residue v in Z_{k+1}^k, decide by exhaustion over all
(k+1)*p pairs (s,j) whether

    s v + r_k(j/p)  in  {1, ..., k-1}^k   (mod k+1),      r_k(t)_i = floor((k+1){it})

has a solution ("saved") or not ("unsaved").  Also reports whether v is disposed
of by the GCD BRANCH of ST26 Definition 2.1 with l = k+1, namely whether some
prime q | k+1 divides all but at most one coordinate -- such v never needs a
Lemma 4.3 witness, so being unsaved is harmless for it.

Integer arithmetic only.  Written from the paper, independent of cover.c.

    python3 check_unsaved.py --k 13 --p 191 --v 2,4,6,8,10,12,0,2,4,6,8,10,12
    python3 check_unsaved.py --selftest
"""
from __future__ import annotations
import argparse


def rk(k: int, p: int, j: int) -> list[int]:
    m = k + 1
    if p == m:                       # p-independent grid: r_k(j/(k+1)) = j*(1..k)
        return [(j * i) % m for i in range(1, k + 1)]
    return [(m * ((i * j) % p)) // p for i in range(1, k + 1)]


def find_witness(v: list[int], p: int):
    k = len(v)
    m = k + 1
    for s in range(m):
        for j in range(p):
            B = rk(k, p, j)
            if all((s * v[i] + B[i]) % m not in (0, m - 1) for i in range(k)):
                return s, j
    return None


def prime_factors(n: int) -> list[int]:
    f, d = [], 2
    while d * d <= n:
        if n % d == 0:
            f.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        f.append(n)
    return f


def gcd_proper(v: list[int], m: int) -> tuple[bool, str]:
    for q in prime_factors(m):
        c = sum(1 for x in v if x % q != 0)
        if c <= 1:
            return True, f"prime q={q} divides all but {c} coordinate(s)"
    return False, "no prime of m divides all but one coordinate"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=13)
    ap.add_argument("--p", type=int, default=191)
    ap.add_argument("--v")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        # ST26 Proposition 4.1 is a theorem for odd prime k+1: every v in N_k is
        # saved p-independently.  Spot-check k=4 and k=6 exhaustively.
        for k in (4, 6):
            m = k + 1
            from itertools import product
            bad = []
            for v in product(range(m), repeat=k):
                if all(x != 0 for x in v) or all(x == 0 for x in v):
                    continue                       # not in N_k
                if find_witness(list(v), m) is None:
                    bad.append(v)
            print(f"Prop 4.1 replay k={k} (m={m} prime): unsaved in N_k = {len(bad)} (expect 0)")
            if bad:
                raise SystemExit(1)
        # k=8, m=9 composite: ST26's hypothesis fails and so does the conclusion
        w = [0, 0, 0, 0, 0, 1, 0, 0]
        print(f"k=8 m=9 v={w}: witness={find_witness(w, 9)} (expect None)")
        assert find_witness(w, 9) is None
        print("SELFTEST OK")
        return

    v = [int(x) for x in a.v.split(",")]
    assert len(v) == a.k, f"v has {len(v)} entries, k={a.k}"
    m = a.k + 1
    w = find_witness(v, a.p)
    gp, why = gcd_proper(v, m)
    print(f"k={a.k} m={m} p={a.p}")
    print(f"v = {v}")
    print(f"zero coordinates at i = {[i + 1 for i, x in enumerate(v) if x == 0]}")
    print(f"searched all {m * a.p} pairs (s,j)")
    print(f"SAVED  : {w is not None}" + (f"  witness (s,j)={w}" if w else ""))
    print(f"gcd-proper (ST26 Def 2.1, l={m}): {gp}  [{why}]")
    if w is None and not gp:
        print("VERDICT: genuine obstruction -- needs a Lemma 4.3 witness and has none")
    elif w is None and gp:
        print("VERDICT: unsaved but harmless -- disposed of by the gcd branch")
    else:
        print("VERDICT: saved")


if __name__ == "__main__":
    main()


def exhaustive(k: int, p: int, verbose: bool = True):
    """Brute force ALL v in Z_m^k: count those that need a Lemma 4.3 witness
    (a zero coordinate, not gcd-proper) and have none.  Only for small k."""
    from itertools import product
    m = k + 1
    qs = prime_factors(m)
    bad = []
    n_need = 0
    for v in product(range(m), repeat=k):
        if 0 not in v:
            continue                                  # saved by s=1, r=0
        if any(sum(1 for x in v if x % q) <= 1 for q in qs):
            continue                                  # gcd branch of Def 2.1
        n_need += 1
        if find_witness(list(v), p) is None:
            bad.append(v)
            if len(bad) > 4 and not verbose:
                break
    return n_need, bad
