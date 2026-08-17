#!/usr/bin/env python3
"""Certify the square-plus-remainder covering F(n) < 2*sqrt(n)+1."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from smooth_lib import largest_prime_factor

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "certs" / "trivial_cover.json"


def split(n: int) -> tuple[int, int]:
    m = int(math.isqrt(n))
    r = n - m * m
    if r == 0:
        if n == 1:
            return 1, 0
        return (m - 1) * (m - 1), 2 * m - 1
    return m * m, r


def check_one(n: int) -> dict:
    a, b = split(n)
    assert a + b == n and a >= 1 and b >= 1
    pa, pb = largest_prime_factor(a), largest_prime_factor(b)
    f = max(pa, pb)
    bound = 2 * math.sqrt(n) + 1
    ok = f < bound
    return {
        "n": n,
        "a": a,
        "b": b,
        "P_a": pa,
        "P_b": pb,
        "F_split": f,
        "bound": bound,
        "ok": ok,
    }


def main() -> int:
    limit = 200_000
    worst_ratio = 0.0
    worst_n = 2
    fails = []
    for n in range(2, limit + 1):
        rec = check_one(n)
        if not rec["ok"]:
            fails.append(n)
        ratio = rec["F_split"] / math.sqrt(n)
        if ratio > worst_ratio:
            worst_ratio = ratio
            worst_n = n
    # Spot-check a few large explicit n, including a square and a 7 mod 8 prime.
    extras = [10**12, 10**12 + 7, 10**18 + 3, 99991 * 99991, 131486759]
    extra_recs = [check_one(n) for n in extras]
    extra_fail = [r["n"] for r in extra_recs if not r["ok"]]
    out = {
        "range": [2, limit],
        "failures_in_range": fails,
        "worst_ratio_in_range": {"n": worst_n, "F_split_over_sqrt": worst_ratio},
        "large_spot": extra_recs,
        "extra_failures": extra_fail,
        "statement": "F(n) < 2*sqrt(n)+1 for every n>=2 via n = m^2+r or (m-1)^2+(2m-1).",
        "is_dent": False,
        "reason": "Balog 1989 already calls the N^{1/2} statement almost trivial.",
    }
    CERT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"range [2,{limit}]: failures={len(fails)} worst_ratio={worst_ratio:.6f} at n={worst_n}")
    print(f"large spot failures={extra_fail}")
    print(f"wrote {CERT}")
    return 0 if not fails and not extra_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
