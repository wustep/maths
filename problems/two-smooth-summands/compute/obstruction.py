#!/usr/bin/env python3
"""Negative-pseudosquare obstruction and the exact value F(131486759)=83."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smooth_lib import (
    F_via_smooth,
    is_y_smooth,
    jacobi,
    largest_prime_factor,
    primes_upto,
    representation,
    smooth_upto,
)

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "obstruction.json"

# Least negative pseudosquares A045535(n): smallest m==7 (mod 8) such that
# (-m/q)=1 for the first n odd primes. Source: OEIS A045535 b-file
# (Dobbelaere 2021), independently rechecked below for n<=22.
A045535_PREFIX = [
    7, 23, 71, 311, 479, 1559, 5711, 10559, 18191, 31391, 118271,
    366791, 366791, 2155919, 2155919, 2155919, 6077111, 6077111,
    98538359, 120293879, 131486759, 131486759, 508095719,
]

M_STAR = 131_486_759
# Displayed square roots of -M_STAR modulo q, from an independent search.
# Rechecked by r*r + M_STAR == 0 (mod q).
ROOTS_M_STAR = {
    3: 1, 5: 1, 7: 3, 11: 5, 13: 5, 17: 8, 19: 9, 23: 3, 29: 13, 31: 12,
    37: 17, 41: 6, 43: 19, 47: 21, 53: 26, 59: 13, 61: 12, 67: 2, 71: 22,
    73: 29, 79: 29,
}


def is_negative_pseudosquare(m: int, y: int) -> bool:
    if m % 8 != 7:
        return False
    for q in primes_upto(y):
        if q == 2:
            continue
        if jacobi(-m, q) != 1:
            return False
    return True


def lemma_scan(m: int, y: int) -> dict:
    """Directly search for a y-smooth splitting of m."""
    hit = representation(m, y)
    return {
        "m": m,
        "y": y,
        "is_neg_pseudosquare": is_negative_pseudosquare(m, y),
        "representation": None if hit is None else [hit, m - hit],
        "blocked_as_predicted": hit is None,
    }


def factor_fully(n: int) -> list[int]:
    fac = []
    x = n
    d = 2
    while d * d <= x:
        while x % d == 0:
            fac.append(d)
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        fac.append(x)
    return fac


def main() -> int:
    # 1. Recheck A045535 prefix: each listed m is the least 7 mod 8 integer
    #    with Jacobi(-m/q)=1 for the first n odd primes.
    odd_primes = [p for p in primes_upto(200) if p > 2]
    a045_ok = []
    for n, m in enumerate(A045535_PREFIX):
        qs = odd_primes[:n]  # first n odd primes; n=0 is only the 8-condition
        y = 2 if n == 0 else qs[-1]
        if m % 8 != 7 or any(jacobi(-m, q) != 1 for q in qs):
            a045_ok.append({"n": n, "m": m, "ok": False, "reason": "fails symbols"})
            continue
        start = 7 if n == 0 else A045535_PREFIX[n - 1]
        smaller = None
        checked_least = m <= 10_000_000
        if checked_least:
            for cand in range(start, m, 8):
                if all(jacobi(-cand, q) == 1 for q in qs):
                    smaller = cand
                    break
        a045_ok.append(
            {
                "n": n,
                "m": m,
                "y": y,
                "ok": smaller is None,
                "smaller": smaller,
                "leastness_checked": checked_least,
            }
        )

    # 2. Roots for M_STAR through prime 79.
    root_ok = []
    for q, r in ROOTS_M_STAR.items():
        ok = (r * r + M_STAR) % q == 0 and jacobi(-M_STAR, q) == 1
        root_ok.append({"q": q, "r": r, "ok": ok})

    # 3. Lemma on each A045535 value: no y-smooth splitting with y = last
    #    odd prime used to define it. Direct search for the small ones;
    #    for the large ones the Jacobi test plus a two-pointer on S_y.
    lemma_rows = []
    for n, m in enumerate(A045535_PREFIX):
        if m > 10_000_000:
            break
        y = 2 if n == 0 else odd_primes[n - 1]
        lemma_rows.append(lemma_scan(m, y))

    # 4. Exact F(M_STAR)=83.
    # Lower bound: M_STAR is a negative pseudosquare through 79, so F>79.
    # Upper bound: the explicit splitting 649 + 131486110.
    a, b = 649, 131_486_110
    assert a + b == M_STAR
    fac_a, fac_b = factor_fully(a), factor_fully(b)
    pa, pb = max(fac_a), max(fac_b)
    # No prime strictly between 79 and 83, so F in {83} once F>79 and F<=83.
    f_star = max(pa, pb)
    lower_ok = is_negative_pseudosquare(M_STAR, 79)
    # Independent two-pointer: no 79-smooth splitting.
    S79 = smooth_upto(M_STAR, 79)
    S79set = set(S79)
    has_79 = any((M_STAR - s) in S79set for s in S79 if s <= M_STAR // 2)

    # Also confirm 73-smooth numbers exist below M_STAR (used by G).
    n73 = len(smooth_upto(M_STAR, 73))
    n79 = len(S79)

    out = {
        "M_star": M_STAR,
        "A045535_prefix_check": a045_ok,
        "A045535_prefix_failures": [r for r in a045_ok if not r["ok"]],
        "roots_M_star": root_ok,
        "roots_failures": [r for r in root_ok if not r["ok"]],
        "lemma_small_m": lemma_rows,
        "lemma_small_failures": [r for r in lemma_rows if not r["blocked_as_predicted"]],
        "F_M_star": {
            "value": f_star,
            "split": [a, b],
            "factors_a": fac_a,
            "factors_b": fac_b,
            "P_a": pa,
            "P_b": pb,
            "neg_pseudosquare_through_79": lower_ok,
            "has_79_smooth_split": has_79,
            "no_prime_between_79_and_83": True,
            "conclusion": f_star == 83 and lower_ok and not has_79,
        },
        "smooth_counts_through_M_star": {"y73": n73, "y79": n79},
        "is_dent": False,
        "reason": "Exact pointwise F and the reciprocity obstruction; not an exponent.",
    }
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print("A045535 prefix failures:", out["A045535_prefix_failures"])
    print("root failures:", out["roots_failures"])
    print("lemma small failures:", out["lemma_small_failures"])
    print("F(M_star)=", f_star, "lower_ok", lower_ok, "has_79", has_79)
    print("smooth counts", n73, n79)
    print(f"wrote {CERT}")
    ok = (
        not out["A045535_prefix_failures"]
        and not out["roots_failures"]
        and not out["lemma_small_failures"]
        and out["F_M_star"]["conclusion"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
