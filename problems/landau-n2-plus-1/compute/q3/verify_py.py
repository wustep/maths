#!/usr/bin/env python3
"""Streaming Python check of the q3 lists. Does not load the P2 file as a whole.

Independent of the residue sieve:
  * every claimed prime n is Miller–Rabin tested
  * every claimed P2 row multiplies back with prime factors
  * OEIS A005574 prefix
  * Wolf / A083844 π_q(10^k) recomputed from the prime list

Completeness of the P2 census (every even n, trial+Pollard) is the C
verifier, a different algorithm. This script does not repeat that scan.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from n2p1_lib import WOLF_PI_Q, miller_rabin  # noqa: E402
from sieve_n2p1 import pi_q_from_primes  # noqa: E402

HERE = Path(__file__).resolve().parent


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=HERE)
    args = parser.parse_args()
    out_dir = args.dir.resolve()
    data = json.loads((out_dir / "n2p1.json").read_text())
    n_max = int(data["n_max"])
    print(f"loaded summary n_max={n_max}", flush=True)

    claimed: list[int] = []
    extra = 0
    with (out_dir / "prime_n.txt").open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            n = int(s.split()[0])
            m = n * n + 1
            if not miller_rabin(m):
                extra += 1
                if extra <= 5:
                    print("claimed composite", n, m, flush=True)
            claimed.append(n)
            if len(claimed) % 200_000 == 0:
                print(f"  prime MR {len(claimed)}", flush=True)
    if extra:
        sys.exit(f"claimed primes that failed MR: {extra}")
    if len(claimed) != int(data["count_prime"]):
        sys.exit("summary count_prime mismatch")
    print(f"claimed primes all prime ({len(claimed)})", flush=True)

    bad = 0
    np2 = 0
    with (out_dir / "p2_omega2.txt").open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = [int(x) for x in s.split()]
            n, fs = parts[0], parts[1:]
            np2 += 1
            m = n * n + 1
            if len(fs) != 2 or math.prod(fs) != m:
                bad += 1
                if bad <= 5:
                    print("p2 product fail", n, fs, m)
                continue
            if any(not miller_rabin(p) for p in fs) or miller_rabin(m):
                bad += 1
                if bad <= 5:
                    print("p2 factor fail", n, fs)
            if np2 % 400_000 == 0:
                print(f"  P2 multiply-back {np2}", flush=True)
    if bad:
        sys.exit(f"P2 factorization failures: {bad}")
    if np2 != int(data["count_p2_omega_eq_2_composite"]):
        sys.exit("summary P2 count mismatch")
    print(f"P2 factorizations OK ({np2} rows)", flush=True)

    oeis = ROOT / "refs" / "b005574.txt"
    if oeis.is_file():
        oeis_n = load_oeis_n(oeis)
        take = [n for n in oeis_n if n <= n_max]
        if claimed[: len(take)] != take:
            sys.exit("OEIS A005574 prefix mismatch")
        print(f"OEIS A005574 prefix OK ({len(take)} terms)", flush=True)

    for row in data.get("wolf_A083844", []):
        k_x = int(row["x"])
        got = pi_q_from_primes(claimed, k_x)
        pub = WOLF_PI_Q.get(int(round(math.log10(k_x))))
        if got != int(row["pi_q"]):
            sys.exit(f"stored wolf row disagrees with recomputation {row} {got}")
        if pub is not None and got != pub:
            sys.exit(f"Wolf/A083844 mismatch at x={k_x}: got {got} published {pub}")
        print(f"Wolf π_q({k_x}) = {got} OK", flush=True)

    print("OK", flush=True)


if __name__ == "__main__":
    main()
