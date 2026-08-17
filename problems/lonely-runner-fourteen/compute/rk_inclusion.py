"""Exact check of ST26 Lemma 4.3's inclusion r_k(1/(k+1) Z) ⊆ r_k(1/p Z).

r_k(t)_i = floor( (k+1) * {i t} ), i=1..k.

On the grid t = n/(k+1) this is exactly (n i mod (k+1)).
On the grid t = j/p it is  ((k+1) * ((i j) mod p)) // p.

The inclusion is a finite statement for each pair (k,p). ST26 prove it for
every prime p > k(k+1), and list a few smaller primes that still work:
  k=10: 103, 107, 109   (threshold 110)
  k=12: 149, 151        (threshold 156)
Those four footnotes are replayed as a self-test.
"""

from __future__ import annotations

import argparse
import math


def rk_frac(k: int, n: int, den: int) -> tuple[int, ...]:
    """r_k(n/den) by exact integer arithmetic."""
    return tuple(((k + 1) * ((i * n) % den)) // den for i in range(1, k + 1))


def rk_on_denominator(k: int, den: int) -> set[tuple[int, ...]]:
    return {rk_frac(k, n, den) for n in range(den)}


def targets_ap(k: int) -> set[tuple[int, ...]]:
    m = k + 1
    return {tuple((n * i) % m for i in range(1, k + 1)) for n in range(m)}


def inclusion_holds(k: int, p: int) -> bool:
    have = rk_on_denominator(k, p)
    return targets_ap(k).issubset(have)


def primes_upto(n: int) -> list[int]:
    if n < 2:
        return []
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i * i :: i] = [False] * len(s[i * i :: i])
    return [i for i, v in enumerate(s) if v]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=13)
    ap.add_argument("--pmax", type=int, default=0, help="scan primes ≤ pmax; 0 = auto")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        # ST26 footnote 4
        want_ok = {
            (10, 103),
            (10, 107),
            (10, 109),
            (12, 149),
            (12, 151),
        }
        want_fail_examples = [
            (10, 101),  # just below their listed extras
            (12, 139),
        ]
        bad = []
        for k, p in want_ok:
            if not inclusion_holds(k, p):
                bad.append(f"expected hold k={k} p={p}")
        # threshold theorem: every prime p > k(k+1) holds
        for k in (10, 12, 13):
            thr = k * (k + 1)
            for p in primes_upto(thr + 40):
                if p <= k + 1:
                    continue
                got = inclusion_holds(k, p)
                if p > thr and not got:
                    bad.append(f"threshold fail k={k} p={p}")
        if bad:
            print("SELFTEST FAIL")
            for b in bad:
                print(" ", b)
            raise SystemExit(1)
        print("SELFTEST OK  (ST26 footnote primes + p>k(k+1) threshold)")

    k = args.k
    thr = k * (k + 1)
    pmax = args.pmax or (thr + 30)
    holds = []
    fails = []
    for p in primes_upto(pmax):
        if p == 2:
            continue
        if inclusion_holds(k, p):
            holds.append(p)
        else:
            fails.append(p)
    below = [p for p in holds if p <= thr]
    above = [p for p in holds if p > thr]
    print(f"k={k} threshold k(k+1)={thr}")
    print(f"holds_below_threshold {below}")
    print(f"holds_above_count {len(above)} first={above[:8]}")
    print(f"fails {fails[:20]}{'...' if len(fails) > 20 else ''}")
    # dump machine-readable
    print("HOLDS", ",".join(map(str, holds)))


if __name__ == "__main__":
    main()
