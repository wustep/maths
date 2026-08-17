#!/usr/bin/env python3
"""
Exact count of degree-n 0/1 polynomials (ends 1) that factor as A*B
with A,B monic 0/1 of positive degree. Splits:
  - some factor reciprocal of the form 1+x^d
  - both factors non-reciprocal (hence each has >= 3 terms)

Compares the second count to the proven majorant
    4 * (sqrt(2) * 3**(1/4))**n
derived in RESEARCH.md (Fibonacci residue-class bound).
"""

from __future__ import annotations

import json
import os


def popcount(x: int) -> int:
    return x.bit_count()


def is_01_product(a: int, b: int) -> bool:
    """a,b bitmasks; convolution has coefficients in {0,1} and no overflow."""
    # shift-and-or with collision detection
    acc = 0
    bb = b
    while a:
        if a & 1:
            if acc & bb:
                return False
            acc |= bb
        a >>= 1
        bb <<= 1
    return True


def support_palindromic(bits: int) -> bool:
    if bits <= 1:
        return True
    m = bits.bit_length() - 1
    rev = 0
    x = bits
    for _ in range(m + 1):
        rev = (rev << 1) | (x & 1)
        x >>= 1
    return rev == bits


def count_n(n: int) -> dict:
    """Enumerate A of deg k=1..n//2, B of deg n-k, both ends 1."""
    both_nr = 0
    some_recip = 0
    seen = set()
    for k in range(1, n // 2 + 1):
        nA = 1 << max(k - 1, 0)
        nB = 1 << max(n - k - 1, 0)
        for fa in range(nA):
            A = 1 | (fa << 1) | (1 << k) if k >= 1 else 1
            if k == 0:
                A = 1
            recA = support_palindromic(A)
            for fb in range(nB):
                B = 1 | (fb << 1) | (1 << (n - k))
                if not is_01_product(A, B):
                    continue
                # product bitmask
                P = 0
                bb = B
                aa = A
                while aa:
                    if aa & 1:
                        P |= bb
                    aa >>= 1
                    bb <<= 1
                if P in seen:
                    continue
                seen.add(P)
                recB = support_palindromic(B)
                if recA or recB:
                    some_recip += 1
                else:
                    both_nr += 1
    majorant = 4 * (2 ** 0.5 * 3 ** 0.25) ** n
    return {
        "n": n,
        "both_nonrecip_01_factors": both_nr,
        "has_recip_01_factor": some_recip,
        "distinct_01_products": len(seen),
        "majorant_1_8612n": majorant,
        "both_nr_below_majorant": both_nr <= majorant,
    }


def main() -> None:
    out = []
    print("n  both_nr  with_recip  distinct  majorant  ok")
    for n in range(2, 17):
        row = count_n(n)
        out.append(row)
        print(
            f"{n:2d}  {row['both_nonrecip_01_factors']:6d}  "
            f"{row['has_recip_01_factor']:8d}  "
            f"{row['distinct_01_products']:8d}  "
            f"{row['majorant_1_8612n']:12.1f}  "
            f"{row['both_nr_below_majorant']}",
            flush=True,
        )
    path = os.path.join(os.path.dirname(__file__), "count_01_factors.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
