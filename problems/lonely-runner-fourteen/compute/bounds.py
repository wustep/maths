"""Exact MSS product bound B_k and the prime-product gap for k=13."""

from __future__ import annotations

import math
from fractions import Fraction


def B_k(k: int) -> Fraction:
    # B_k = ( binom(k+1,2)^{k-1} / k )^k
    binom = (k + 1) * k // 2
    return Fraction(binom ** (k - 1), k) ** k


def primes_between(a: int, b: int) -> list[int]:
    n = b
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            s[i * i :: i] = [False] * len(s[i * i :: i])
    return [p for p in range(max(a, 2), b + 1) if s[p]]


def main() -> None:
    for k in range(6, 15):
        B = B_k(k)
        lnB = k * ((k - 1) * math.log(k * (k + 1) / 2) - math.log(k))
        print(f"k={k:2d} ln B_k = {lnB:.6f}  log10 B_k = {lnB / math.log(10):.6f}")

    B = B_k(13)
    print(f"\nB_13 exact numerator digits {len(str(B.numerator))}")
    print(f"B_13 exact denominator digits {len(str(B.denominator))}")
    # ST26 table 1 ln values
    print("\nST26 Table 1 replay (natural log):")
    table = {
        10: 338,
        11: 435,
        12: 546,
    }
    for k, printed in table.items():
        lnB = k * ((k - 1) * math.log(k * (k + 1) / 2) - math.log(k))
        print(f"  k={k} ln B_k = {lnB:.6f}  paper says < {printed}  ok={lnB < printed}")

    print("\nPrimes useful for a 14-runner sieve (p > 14, since 14 | l is required")
    print("to kill (1..13), or any p if we only want a modular constraint):")
    ps = primes_between(3, 250)
    prod = 1
    acc = []
    target = float(B.numerator.bit_length() * math.log(2) - B.denominator.bit_length() * math.log(2))
    # better: ln B
    lnB = 13 * (12 * math.log(91) - math.log(13))
    lnprod = 0.0
    for p in ps:
        lnprod += math.log(p)
        acc.append(p)
        if lnprod >= lnB:
            print(f"  first prefix of primes from {acc[0]} with prod >= B_13 ends at p={p}, count={len(acc)}")
            break
    else:
        print(f"  primes 3..250 give ln prod={lnprod:.3f} < ln B_13={lnB:.3f}")

    # how many large primes like ST26's style (p around 200+)
    large = primes_between(191, 800)
    lnL = sum(math.log(p) for p in large)
    print(f"  primes in [191,800]: {len(large)}, ln prod={lnL:.3f}, ln B_13={lnB:.3f}, enough={lnL>=lnB}")


if __name__ == "__main__":
    main()
