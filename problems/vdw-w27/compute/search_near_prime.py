#!/usr/bin/env python3
"""Flip bits in near-miss QR cycles (max run 7 or 8) to kill monochromatic 7-APs."""

from __future__ import annotations

import json
from pathlib import Path

from vdw import first_mono_ap, format_ab, max_monochrome_run, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent

NEAR = [653, 677, 691, 821, 823]  # run 7 from the 20k scan


def mono_strings(cycle: list[int], k: int = 7) -> list[int]:
    """Start indices of linear k-runs, including wrap."""
    n = len(cycle)
    starts = []
    for a in range(n):
        c0 = cycle[a]
        if all(cycle[(a + i) % n] == c0 for i in range(k)):
            starts.append(a)
    return starts


def main() -> None:
    hits = []
    logs = []
    for p in NEAR:
        cycle = quadratic_residue_cycle(p, zero_color=0)
        runs = mono_strings(cycle, 7)
        rec = {"p": p, "run": max_monochrome_run(cycle, True), "seven_strings": runs}
        # Try flipping each point of each 7-string
        found = None
        for start in runs:
            for off in range(7):
                pos = (start + off) % p
                cand = cycle[:]
                cand[pos] ^= 1
                if first_mono_ap(cand, 7, cyclic=True) is None:
                    found = {"p": p, "flip": pos, "zero": 0}
                    break
            if found:
                break
        if found is None:
            # two flips on the 7-string
            for start in runs:
                for a in range(7):
                    for b in range(a + 1, 7):
                        cand = cycle[:]
                        cand[(start + a) % p] ^= 1
                        cand[(start + b) % p] ^= 1
                        if first_mono_ap(cand, 7, cyclic=True) is None:
                            found = {
                                "p": p,
                                "flips": [(start + a) % p, (start + b) % p],
                            }
                            break
                    if found:
                        break
                if found:
                    break
        rec["repair"] = found
        logs.append(rec)
        print(rec, flush=True)
        if found:
            hits.append(found)
            colors = cycle[:]
            for pos in found.get("flips", [found.get("flip")]):
                if pos is not None:
                    colors[pos] ^= 1
            (HERE / f"cycle_{p}_repaired.txt").write_text(format_ab(colors) + "\n")
    (HERE / "near_prime_repair.json").write_text(json.dumps(logs, indent=2) + "\n")
    print(json.dumps({"hits": hits}, indent=2))


if __name__ == "__main__":
    main()
