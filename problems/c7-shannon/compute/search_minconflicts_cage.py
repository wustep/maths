#!/usr/bin/env python3
"""Min-conflicts from the 367-set plus one extra vertex.

Sibling note: seeded min-conflicts often stalls at exactly one leftover
violation. That is a local cage, not evidence the record is optimal.
"""

from __future__ import annotations

import random
from collections import Counter
from pathlib import Path

from c7_common import NVERTS, adjacent, closed_neighbors, format_word
from verify_set import load_set

HERE = Path(__file__).resolve().parent


def violations_of(v: int, selected: set[int]) -> list[int]:
    return [u for u in selected if u != v and adjacent(u, v)]


def main() -> None:
    seed = set(load_set(HERE / "R367.txt"))
    rng = random.Random(4)
    # vertices just outside the seed: pick those with fewest seed neighbours
    blockers = [0] * NVERTS
    for s in seed:
        for u in closed_neighbors(s):
            if u not in seed:
                blockers[u] += 1
    outside = [v for v in range(NVERTS) if v not in seed]
    outside.sort(key=lambda v: blockers[v])
    stalls = Counter()
    lines = ["minconflicts from 367 plus one extra; stall count is not a bound"]
    for trial, extra in enumerate(outside[:80]):
        selected = set(seed)
        selected.add(extra)
        # one extra is adjacent to blockers[extra] seed verts
        for _ in range(400):
            bad = [v for v in selected if violations_of(v, selected)]
            if not bad:
                out = HERE / f"R{len(selected)}_minconf.txt"
                from verify_set import first_conflict

                if first_conflict(sorted(selected)) is None:
                    out.write_text("\n".join(format_word(v) for v in sorted(selected)) + "\n")
                    lines.append(f"HIT trial={trial} size={len(selected)} wrote {out}")
                    print(lines[-1])
                    (HERE / "minconflicts_cage.txt").write_text("\n".join(lines) + "\n")
                    return
            # flip the worst vertex out, add a random unblocked-ish outsider
            v = rng.choice(bad)
            selected.remove(v)
            # try to add something with few conflicts
            cand = rng.choice(outside)
            if cand not in selected:
                selected.add(cand)
            if len(selected) < 368:
                for w in outside:
                    if w not in selected:
                        selected.add(w)
                        break
        bad = [v for v in selected if violations_of(v, selected)]
        nviol_pairs = sum(len(violations_of(v, selected)) for v in selected) // 2
        stalls[nviol_pairs] += 1
        if trial < 8 or nviol_pairs <= 1:
            lines.append(
                f"trial={trial} extra={format_word(extra)} blockers={blockers[extra]} "
                f"stall_pairs={nviol_pairs} size={len(selected)}"
            )
            print(lines[-1], flush=True)
    lines.append(f"stall_pair_histogram {dict(sorted(stalls.items()))}")
    lines.append("one-pair stalls are a local cage, not alpha<=367")
    (HERE / "minconflicts_cage.txt").write_text("\n".join(lines) + "\n")
    print(lines[-2])


if __name__ == "__main__":
    main()
