#!/usr/bin/env python3
"""Independently re-derive the prime list and check the P2 factorizations.

Does not trust sieve_n2p1 internals:
  * every even n (and n=1) is Miller–Rabin tested from scratch
  * every claimed P2 is multiplied back and each factor is re-tested
  * a second pass factors every even n^2+1 by trial+Pollard and checks
    that the P2 file is exactly the Ω=2 composites
  * prefix compared to the OEIS A005574 b-file if present
  * π_q(10^k) compared to Wolf / A083844 on the reachable powers
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from n2p1_lib import WOLF_PI_Q, factor_int, miller_rabin, primes_upto
from sieve_n2p1 import pi_q_from_primes

HERE = Path(__file__).resolve().parent


def load_int_column(path: Path) -> list[int]:
    out: list[int] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(int(s.split()[0]))
    return out


def load_p2(path: Path) -> list[tuple[int, list[int]]]:
    rows: list[tuple[int, list[int]]] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = [int(x) for x in s.split()]
        rows.append((parts[0], parts[1:]))
    return rows


def load_oeis_n(path: Path) -> list[int]:
    vals: list[int] = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        bits = s.split()
        if len(bits) >= 2:
            vals.append(int(bits[1]))
    return vals


def scan_primes(n_max: int) -> list[int]:
    found: list[int] = []
    if n_max >= 1 and miller_rabin(2):
        found.append(1)
    for n in range(2, n_max + 1, 2):
        if miller_rabin(n * n + 1):
            found.append(n)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=HERE / "n2p1.json")
    parser.add_argument("--skip-complete-p2", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.summary.read_text())
    n_max = int(data["n_max"])
    print(f"loaded summary n_max={n_max}", flush=True)
    claimed = load_int_column(HERE / "prime_n.txt")
    p2_rows = load_p2(HERE / "p2_omega2.txt")
    print(f"loaded lists primes={len(claimed)} p2={len(p2_rows)}; scanning primes", flush=True)

    found = scan_primes(n_max)
    extra = [n for n in claimed if n not in set(found)]
    missing = [n for n in found if n not in set(claimed)]
    print(
        f"primes n_max={n_max} claimed={len(claimed)} found={len(found)} "
        f"extra={len(extra)} missing={len(missing)}",
        flush=True,
    )
    if extra[:8]:
        print("extra sample", extra[:8], flush=True)
    if missing[:8]:
        print("missing sample", missing[:8], flush=True)
    if extra or missing:
        sys.exit(1)
    if len(claimed) != int(data["count_prime"]):
        print("summary count_prime mismatch", flush=True)
        sys.exit(1)
    print("primes OK", flush=True)

    bad = 0
    for n, fs in p2_rows:
        m = n * n + 1
        if not fs or math.prod(fs) != m or len(fs) != 2:
            bad += 1
            if bad <= 5:
                print("p2 product fail", n, fs, m)
            continue
        if any(not miller_rabin(p) for p in fs):
            bad += 1
            if bad <= 5:
                print("p2 composite factor", n, fs)
            continue
        if miller_rabin(m):
            bad += 1
            if bad <= 5:
                print("p2 but m prime", n)
    if bad:
        print(f"P2 factorization failures: {bad}")
        sys.exit(1)
    if len(p2_rows) != int(data["count_p2_omega_eq_2_composite"]):
        print("summary P2 count mismatch")
        sys.exit(1)
    print(f"P2 factorizations OK ({len(p2_rows)} rows)", flush=True)

    if not args.skip_complete_p2:
        # Independent factorization of every even n^2+1. Trial bound is
        # deliberately small; leftover composites go to Pollard, not a
        # sqrt(n) search. This is a different algorithm from the residue sieve.
        trial = primes_upto(2_003)
        p2_set = {n for n, _ in p2_rows}
        prime_set = set(claimed)
        miss_p2 = []
        extra_p2 = []
        scanned = 0
        for n in range(2, n_max + 1, 2):
            scanned += 1
            if scanned % 100_000 == 0:
                print(f"  completeness scanned {scanned} even n", flush=True)
            m = n * n + 1
            if n in prime_set:
                continue
            fs = factor_int(m, trial)
            if len(fs) == 2:
                if n not in p2_set:
                    miss_p2.append(n)
            else:
                if n in p2_set:
                    extra_p2.append(n)
        print(f"complete P2 scan miss={len(miss_p2)} extra={len(extra_p2)}", flush=True)
        if miss_p2[:8]:
            print("missing P2 sample", miss_p2[:8], flush=True)
        if extra_p2[:8]:
            print("extra P2 sample", extra_p2[:8], flush=True)
        if miss_p2 or extra_p2:
            sys.exit(1)
        print("P2 completeness OK", flush=True)

    oeis = HERE / "refs" / "b005574.txt"
    if oeis.is_file():
        oeis_n = load_oeis_n(oeis)
        take = [n for n in oeis_n if n <= n_max]
        if claimed[: len(take)] != take:
            print("OEIS A005574 prefix mismatch")
            for i, (a, b) in enumerate(zip(claimed, take), 1):
                if a != b:
                    print("first diff at", i, "ours", a, "oeis", b)
                    break
            if len(claimed) < len(take):
                print("ours shorter", len(claimed), len(take))
            sys.exit(1)
        print(f"OEIS A005574 prefix OK ({len(take)} terms)", flush=True)

    for row in data.get("wolf_A083844", []):
        k_x = int(row["x"])
        got = pi_q_from_primes(claimed, k_x)
        pub = WOLF_PI_Q.get(int(round(math.log10(k_x))))
        if got != int(row["pi_q"]):
            print("stored wolf row disagrees with recomputation", row, got)
            sys.exit(1)
        if pub is not None and got != pub:
            print(f"Wolf/A083844 mismatch at x={k_x}: got {got} published {pub}")
            sys.exit(1)
        print(f"Wolf π_q({k_x}) = {got} OK", flush=True)

    print("OK", flush=True)


if __name__ == "__main__":
    main()
