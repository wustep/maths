#!/usr/bin/env python3
"""Scan primes for quadratic-residue 7-AP-free cycles longer than 617.

A hit with p > 617 would give a linear coloring of length 6p >= 3708.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vdw import first_mono_ap, max_monochrome_run, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent


def primes_upto(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i * i : limit + 1 : i] = b"\x00" * (((limit - i * i) // i) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-p", type=int, default=619)
    parser.add_argument("--max-p", type=int, default=20000)
    args = parser.parse_args()
    hits = []
    near = []
    for p in primes_upto(args.max_p):
        if p < args.min_p:
            continue
        cycle = quadratic_residue_cycle(p, zero_color=0)
        run = max_monochrome_run(cycle, cyclic=True)
        if run <= 8:
            cyclic_hit = None
            if run <= 6:
                cyclic_hit = first_mono_ap(cycle, k=7, cyclic=True)
            rec = {
                "p": p,
                "max_cyclic_run": run,
                "cyclic_7ap_free": run <= 6 and cyclic_hit is None,
            }
            near.append(rec)
            if rec["cyclic_7ap_free"]:
                hits.append(rec)
                print("HIT", rec, flush=True)
    payload = {
        "min_p": args.min_p,
        "max_p": args.max_p,
        "hits": hits,
        "near_run_le_8": near,
    }
    out = HERE / "prime_scan.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"hits": hits, "near_count": len(near), "wrote": str(out)}))


if __name__ == "__main__":
    main()
