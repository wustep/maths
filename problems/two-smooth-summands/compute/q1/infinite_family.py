"""Infinite failure families for two closed-form templates at any ε<1/2.

1. Floor-divisor. For a prime P and u ~ P^{ε/(1-ε)}, the integer
   n = P*u + 1 has floor(n^ε) near u, first summand P*u, and
   P > n^ε precisely because ε<1/2. A short search around that u
   produces an explicit n for every large prime.

2. Largest power of two. For each k>=3, if there is a prime q in
   (2^{k-1}, 2^k), then n = 2^k + q has largest power of two below n
   equal to 2^k and complement q > n^{1/2} > n^ε.

Neither family is a lower bound on F. They kill those two templates
as infinite coverings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from smooth_lib import largest_prime_factor, primes_upto

from templates import (
    exceeds_pow,
    floor_divisor,
    floor_n_pow,
    largest_pow2,
    template_fails,
)

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "infinite_family.json"

# Rational exponents below 1/2 that we actually test.
EXPONENTS = ((2, 5), (1, 3), (27, 100))


def next_prime_after(n: int, primes: list[int]) -> int | None:
    for p in primes:
        if p > n:
            return p
    return None


def floor_divisor_witness(P: int, p: int, q: int, slop: int = 40) -> dict | None:
    """Search u near P^{p/(q-p)} for n=P*u+1 that kills the template."""
    # ε/(1-ε) = p/(q-p).
    target = floor_n_pow(P, p, q - p)
    for u in range(max(2, target - slop), target + slop + 1):
        n = P * u + 1
        if n <= P:
            continue
        a = floor_divisor(n, p, q)
        if not template_fails(a, n, p, q):
            continue
        u0 = floor_n_pow(n, p, q)
        return {
            "prime": P,
            "u": u,
            "n": n,
            "u0": u0,
            "a": a,
            "b": n - a,
            "P_a": largest_prime_factor(a),
            "P_b": largest_prime_factor(b := n - a),
            "P_exceeds": exceeds_pow(P, n, p, q),
        }
    return None


def pow2_witness(k: int, primes: list[int]) -> dict | None:
    lo = 1 << (k - 1)
    hi = 1 << k
    q = next_prime_after(lo, primes)
    if q is None or q >= hi:
        # Fall back: 2^k + 3 is often composite; try small odd offsets.
        for odd in range(3, min(2000, hi), 2):
            cand = odd
            if cand > lo and cand < hi and largest_prime_factor(cand) == cand:
                q = cand
                break
        else:
            return None
    n = hi + q
    a = largest_pow2(n)
    return {
        "k": k,
        "pow2": hi,
        "q": q,
        "n": n,
        "a": a,
        "b": n - a,
        "P_b": largest_prime_factor(n - a),
        # Fail every ε<1: P_b = q > n^{1/2} for k>=3.
        "fails_half": exceeds_pow(largest_prime_factor(n - a), n, 1, 2),
    }


def main() -> int:
    primes = primes_upto(200_000)
    test_primes = [p for p in primes if 11 <= p <= 541]
    # A few larger ones, still inside the sieve.
    test_primes += [p for p in primes if 10_000 <= p <= 10_300]

    floor_rows = []
    floor_misses = []
    for p, q in EXPONENTS:
        hits = []
        misses = []
        for P in test_primes:
            w = floor_divisor_witness(P, p, q)
            if w is None:
                misses.append(P)
            else:
                hits.append(w)
        floor_rows.append(
            {
                "exponent": f"{p}/{q}",
                "n_primes_tested": len(test_primes),
                "n_hits": len(hits),
                "n_misses": len(misses),
                "sample_hits": hits[:8] + hits[-4:],
                "misses": misses[:20],
            }
        )
        floor_misses.extend((f"{p}/{q}", P) for P in misses)

    pow2_rows = []
    pow2_misses = []
    for k in range(4, 17):
        w = pow2_witness(k, primes)
        if w is None or not w["fails_half"]:
            pow2_misses.append(k)
        else:
            pow2_rows.append(w)

    out = {
        "floor_divisor_family": floor_rows,
        "pow2_family": pow2_rows,
        "pow2_misses": pow2_misses,
        "is_dent": False,
        "reason": (
            "Explicit infinite-looking failure families for two closed-form "
            "templates. Not a lower bound on F; the square template still "
            "covers every n at exponent 1/2."
        ),
    }
    CERT.parent.mkdir(parents=True, exist_ok=True)
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print("floor-divisor misses:", floor_misses)
    print("pow2 misses:", pow2_misses)
    print(
        "floor hits:",
        [ (r["exponent"], r["n_hits"], r["n_misses"]) for r in floor_rows ],
    )
    print("pow2 hits:", len(pow2_rows))
    print(f"wrote {CERT}")
    return 0 if not floor_misses and not pow2_misses else 1


if __name__ == "__main__":
    raise SystemExit(main())
