#!/usr/bin/env python3
"""Two-flip repair: break the d=617 class-2 AP, then break the created AP."""

from __future__ import annotations

import json
from pathlib import Path

from vdw import first_mono_ap, format_ab, load_coloring

HERE = Path(__file__).resolve().parent
BLOCK = [1, 618, 1235, 1852, 2469, 3086]


def main() -> None:
    seed = load_coloring(str(HERE / "coloring_3703.txt"))
    hits = []
    trials = 0
    for pos in BLOCK:
        colors = seed[:]
        colors[pos] ^= 1
        colors.append(0)
        hit = first_mono_ap(colors, 7)
        if hit is None:
            hits.append({"flips": [pos + 1], "ok": True})
            continue
        a, d = hit
        ap = [a + i * d for i in range(7)]
        for q in ap:
            if q == pos or q == 3703:
                continue
            trials += 1
            cand = seed[:]
            cand[pos] ^= 1
            cand[q] ^= 1
            cand.append(0)
            if first_mono_ap(cand, 7) is None:
                hits.append({"flips_1based": [pos + 1, q + 1], "ok": True})
                path = HERE / "coloring_3704.txt"
                path.write_text(format_ab(cand) + "\n")
                print("HIT", hits[-1], flush=True)
                (HERE / "two_flip.json").write_text(json.dumps({"hits": hits, "trials": trials}, indent=2))
                return
    # also try color 1 at 3704 with one flip on each of two blockers — skip, SAT handles
    (HERE / "two_flip.json").write_text(
        json.dumps({"hits": hits, "trials": trials}, indent=2) + "\n"
    )
    print(json.dumps({"hits": hits, "trials": trials}))


if __name__ == "__main__":
    main()
