#!/usr/bin/env python3
"""Search residue / short-interval / factorization templates.

A clean run with no holes on a finite prefix is residue, not a bound.
The script records every hole so the failure is checkable.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smooth_lib import largest_prime_factor, primes_upto

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "covering_search.json"


def lpf_sieve(limit: int) -> list[int]:
    P = [0] * (limit + 1)
    P[1] = 1
    for i in range(2, limit + 1):
        if P[i] == 0:
            for j in range(i, limit + 1, i):
                P[j] = i
    return P


def short_interval_holes(P: list[int], alpha: float, limit: int) -> dict:
    """n where [n-floor(n^alpha), n-1] has no n^alpha-smooth integer.

    If there are no such n, the short-interval template would give
    F(n) <= n^alpha on this range (still not an asymptotic theorem).
    """
    holes = []
    first = None
    for n in range(2, limit + 1):
        y = n**alpha
        h = max(1, int(y))
        ok = False
        lo = n - h
        if lo < 1:
            lo = 1
        for k in range(lo, n):
            if P[k] <= y:
                ok = True
                break
        if not ok:
            if first is None:
                first = n
            if len(holes) < 30:
                holes.append(n)
    return {
        "alpha": alpha,
        "limit": limit,
        "n_holes": None if first is None else ">=1",
        "first_hole": first,
        "first_holes": holes,
        "hole_count_recorded": len(holes),
        "exhausted": first is None,
    }


def short_interval_count(P: list[int], alpha: float, limit: int) -> dict:
    first = None
    count = 0
    worst_n = None
    worst_ratio = 0.0
    for n in range(2, limit + 1):
        y = n**alpha
        h = max(1, int(y))
        ok = False
        lo = max(1, n - h)
        for k in range(lo, n):
            if P[k] <= y:
                ok = True
                break
        if not ok:
            count += 1
            if first is None:
                first = n
        # Track F via this template only: min P+ on the interval, over y.
        best = min(P[k] for k in range(lo, n)) if lo < n else n
        ratio = best / (n**0.5)
        if ratio > worst_ratio:
            worst_ratio = ratio
            worst_n = n
    return {
        "alpha": alpha,
        "limit": limit,
        "first_hole": first,
        "n_holes": count,
        "worst_short_P_over_sqrt": {"n": worst_n, "ratio": worst_ratio},
        "covers_the_range": first is None,
    }


def residue_small_shift(P: list[int], modulus: int, alpha: float, limit: int, shifts: int = 40) -> dict:
    """For each class r mod M, try the first `shifts` many M-smooth-or-small
    offsets a. A class is covered on the range if every n≡r (mod M) has some
    tried a < n with P+(n-a) <= n^alpha.

    This is the literal 'finite list of residue templates' search. It fails
    as soon as n-a stays n^alpha-rough for every short list of a.
    """
    # Candidate offsets: all k <= shifts*modulus that are 1 or M-smooth-ish
    # (in practice: all k <= max(200, 4*modulus) with P+(k) <= max(modulus, 30)).
    cap = max(200, 4 * modulus)
    y0 = max(modulus, 30)
    candidates = [k for k in range(1, cap + 1) if P[k] <= y0][:shifts]
    holes_by_r = {r: [] for r in range(modulus)}
    first_fail = {r: None for r in range(modulus)}
    for n in range(2, limit + 1):
        r = n % modulus
        y = n**alpha
        ok = False
        for a in candidates:
            if a >= n:
                break
            if P[n - a] <= y:
                ok = True
                break
        if not ok:
            if first_fail[r] is None:
                first_fail[r] = n
            if len(holes_by_r[r]) < 5:
                holes_by_r[r].append(n)
    uncovered = [r for r, n0 in first_fail.items() if n0 is not None]
    return {
        "modulus": modulus,
        "alpha": alpha,
        "limit": limit,
        "n_candidates": len(candidates),
        "uncovered_classes": uncovered,
        "n_uncovered_classes": len(uncovered),
        "first_fail_by_class": {str(r): first_fail[r] for r in range(modulus)},
        "sample_holes": {str(r): holes_by_r[r] for r in uncovered[:12]},
        "covers_all_classes": len(uncovered) == 0,
    }


def balog_reduction_holes(P: list[int], alpha: float, limit: int) -> dict:
    """Among n-alpha-rough n, does a short list of smooth a still work?

    Balog reduces the asymptotic problem to these n. If even the rough
    n refuse a finite shift list, a residue cover of this shape cannot lift.
    """
    holes = []
    for n in range(2, limit + 1):
        y = n**alpha
        if P[n] <= y and n > y:
            # has a prime factor <= y: Balog splits off the smooth kernel
            continue
        # n is y-rough (or a prime power of a large prime)
        h = max(1, int(y))
        ok = False
        lo = max(1, n - h)
        for k in range(lo, n):
            if P[k] <= y:
                ok = True
                break
        if not ok:
            holes.append(n)
            if len(holes) >= 40:
                break
    return {
        "alpha": alpha,
        "limit": limit,
        "first_rough_short_interval_holes": holes[:20],
        "n_recorded": len(holes),
        "stopped_early": len(holes) >= 40,
    }


def even_reduces_to_odd(limit: int) -> dict:
    """F(2m) <= max(2, F(m)) via 2m = 2a+2b whenever m=a+b.

    This is an identity, recorded so the cover search can restrict to odd n.
    It does not improve the exponent: the odd kernel can be ~ n.
    """
    return {
        "identity": "if m=a+b then 2m=(2a)+(2b) and P+(2a)=max(2,P+(a))",
        "consequence": "F(n) <= max(2, F(odd_part(n)))",
        "does_not_remove_the_odd_obstruction": True,
    }


def main() -> int:
    limit = 50_000
    P = lpf_sieve(limit)
    alphas = [0.5, 0.45, 0.4, 1.0 / 3.0, 0.3]
    short = [short_interval_count(P, a, limit) for a in alphas]
    # The actual trivial covering uses a window of 2*sqrt(n)+1, not n^{1/2}.
    trivial_window = {"window": "2*sqrt(n)+1", "limit": limit, "n_holes": 0, "first_hole": None}
    for n in range(2, limit + 1):
        h = int(2 * math.sqrt(n) + 1)
        lo = max(1, n - h)
        if not any(P[k] <= h for k in range(lo, n)):
            trivial_window["n_holes"] += 1
            if trivial_window["first_hole"] is None:
                trivial_window["first_hole"] = n
    trivial_window["covers_the_range"] = trivial_window["first_hole"] is None
    residues = []
    for M in (8, 24, 120):
        for a in (0.4, 1.0 / 3.0):
            residues.append(residue_small_shift(P, M, a, min(limit, 20_000)))
    rough = [balog_reduction_holes(P, a, limit) for a in (0.4, 1.0 / 3.0)]

    out = {
        "limit": limit,
        "short_interval": short,
        "trivial_2sqrt_window": trivial_window,
        "residue_small_shift": residues,
        "rough_short_interval": rough,
        "even_reduction": even_reduces_to_odd(limit),
        "is_dent": False,
        "reason": (
            "No template covered every residue class at any alpha<1/2. "
            "Short-interval alpha=1/2 is the trivial covering. "
            "Holes are recorded in certs/covering_search.json."
        ),
    }
    # Promote is_dent only if some alpha<1/2 short-interval cover is total
    # AND some residue cover is total — still would be finite-range residue
    # unless we also have an infinite lift. We never set is_dent here.
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print("short-interval:")
    for row in short:
        print(
            f"  alpha={row['alpha']:.4f} holes={row['n_holes']} "
            f"first={row['first_hole']} covers={row['covers_the_range']}"
        )
    print("residue templates:")
    for row in residues:
        print(
            f"  M={row['modulus']} alpha={row['alpha']:.4f} "
            f"uncovered={row['n_uncovered_classes']} "
            f"total={row['covers_all_classes']}"
        )
    print("rough short-interval first holes:")
    for row in rough:
        print(f"  alpha={row['alpha']:.4f} {row['first_rough_short_interval_holes'][:8]}")
    print(f"wrote {CERT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
