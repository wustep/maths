#!/usr/bin/env python3
"""Four-letter support local search (shape 2).

Restrict coordinate 0 to a 4-subset of Z/7. Start from the published 367-set
sliced to that support, then 1-out / 2-out packing of newly free vertices
that stay inside the support. Also try a dim-4 greedy on the two free fibers
plus a {0,1}-slice repair.
"""

from __future__ import annotations

import itertools
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from c7_common import (
    NVERTS,
    closed_neighbors,
    decode,
    encode,
    format_word,
    greedy_mis_fast,
)
from verify_set import first_conflict, load_set

def build_neigh() -> list[list[int]]:
    return [closed_neighbors(v) for v in range(NVERTS)]


def main() -> None:
    t0 = time.time()
    seed = load_set(ROOT / "R367.txt")
    neigh = build_neigh()
    rng = random.Random(0)
    lines = []
    best = 0
    hit = None

    # All 4-subsets of Z/7, up to rotation we still enumerate (C(7,4)=35).
    for supp in itertools.combinations(range(7), 4):
        allowed = [0] * NVERTS
        for v in range(NVERTS):
            if decode(v)[0] in supp:
                allowed[v] = 1
        sliced = [v for v in seed if allowed[v]]
        # grow: blocked counts inside the whole graph, but only add allowed verts
        selected = set(sliced)
        blocked = [0] * NVERTS
        for v in selected:
            for u in neigh[v]:
                blocked[u] += 1
        # add any currently free allowed vertex
        added = 0
        for v in range(NVERTS):
            if allowed[v] and blocked[v] == 0 and v not in selected:
                selected.add(v)
                added += 1
                for u in neigh[v]:
                    blocked[u] += 1
        # 1-out inside support
        cur = list(selected)
        improved = True
        rounds = 0
        while improved and rounds < 8:
            improved = False
            rounds += 1
            rng.shuffle(cur)
            for v in list(cur):
                if v not in selected:
                    continue
                for u in neigh[v]:
                    blocked[u] -= 1
                selected.remove(v)
                freed = [
                    u
                    for u in neigh[v]
                    if blocked[u] == 0 and allowed[u]
                ]
                rng.shuffle(freed)
                take = []
                for u in freed:
                    if blocked[u] == 0:
                        take.append(u)
                        for w in neigh[u]:
                            blocked[w] += 1
                if len(take) > 1:
                    selected.update(take)
                    cur = list(selected)
                    improved = True
                    break
                # revert
                for u in take:
                    for w in neigh[u]:
                        blocked[w] -= 1
                selected.add(v)
                for u in neigh[v]:
                    blocked[u] += 1
        sz = len(selected)
        if sz > best:
            best = sz
            print(f"support {supp} sliced={len(sliced)} grown={sz} extra_free={added}", flush=True)
            lines.append(f"{supp} sliced={len(sliced)} grown={sz}")
        if sz >= 368 and first_conflict(list(selected)) is None:
            hit = sorted(selected)
            break

    # Free-fiber construction: letters {0,2,4} is impossible (shape 1).
    # {0,1,3,5}: fibers 3 and 5 unconstrained vs each other and vs {0,1}.
    supp = (0, 1, 3, 5)
    # greedy MIS in each C7^4 fiber, then repair the 0-1 pair
    fibers = {i: [] for i in supp}
    for v in range(NVERTS):
        c = decode(v)
        if c[0] in fibers:
            fibers[c[0]].append(v)
    packed = []
    for letter in (3, 5):
        # greedy in this fiber: vertices already 4-dim independent problem
        take = greedy_mis_fast(fibers[letter])
        packed.extend(take)
        print(f"fiber {letter} greedy {len(take)}", flush=True)
        lines.append(f"fiber {letter} {len(take)}")
    # 0-1 slice: remaining vertices with coord0 in {0,1} not blocked by packed
    blocked = [0] * NVERTS
    selected = set(packed)
    for v in packed:
        for u in neigh[v]:
            blocked[u] += 1
    cands = [v for v in fibers[0] + fibers[1] if blocked[v] == 0]
    extra = greedy_mis_fast(cands)
    selected.update(extra)
    print(f"01-slice extra {len(extra)} total {len(selected)}", flush=True)
    lines.append(f"01 extra {len(extra)} total {len(selected)}")
    if len(selected) > best:
        best = len(selected)
    if len(selected) >= 368 and first_conflict(list(selected)) is None:
        hit = sorted(selected)

    # random restarts on 4-support from empty
    for trial in range(40):
        supp = (0, 1, 3, 5)
        allow = {0, 1, 3, 5}
        verts = [v for v in range(NVERTS) if decode(v)[0] in allow]
        rng.shuffle(verts)
        take = greedy_mis_fast(verts)
        if len(take) > best:
            best = len(take)
            print(f"random 4-support trial {trial} size {len(take)}", flush=True)
            lines.append(f"random {trial} {len(take)}")
        if len(take) >= 368 and first_conflict(take) is None:
            hit = sorted(take)
            break

    lines.append(f"best {best}")
    lines.append(f"seconds {time.time()-t0:.1f}")
    if hit is not None:
        out = HERE / f"R{len(hit)}_4support.txt"
        out.write_text("\n".join(format_word(v) for v in hit) + "\n")
        print(f"WROTE {out}")
        lines.append(f"wrote {out}")
    else:
        print(f"no 368 in 4-support search best={best}")
        lines.append("no 368")
    (HERE / "four_support_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
