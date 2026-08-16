#!/usr/bin/env python3
"""Exhaustive 3-out search from the 367-set.

Polak-Schrijver reported no 3-out/4-in. Re-check: after deleting 3 vertices,
can the newly freed neighbourhood supply 4 or more pairwise non-adjacent points?
"""

from __future__ import annotations

import time
from pathlib import Path

from c7_common import NVERTS, closed_neighbors, format_word
from search_local import add_vertex, blocked_from, build_neigh, rem_vertex, residual_mis, newly_free
from verify_set import first_conflict, load_set

HERE = Path(__file__).resolve().parent


def main() -> None:
    t0 = time.time()
    words = load_set(HERE / "R367.txt")
    selected = set(words)
    cur = list(words)
    n = len(cur)
    print("building neighborhoods...", flush=True)
    neigh = build_neigh()
    blocked = blocked_from(selected, neigh)
    trials = 0
    best_gain = -99
    hit = None
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                rem = [cur[i], cur[j], cur[k]]
                for v in rem:
                    rem_vertex(v, selected, blocked, neigh)
                freed = newly_free(rem, blocked, neigh)
                add = residual_mis(freed, neigh)
                gain = len(add) - 3
                if gain > best_gain:
                    best_gain = gain
                    print(f"best_gain={best_gain} add={len(add)} trial={trials}", flush=True)
                if gain >= 1:
                    hit = sorted(selected | set(add))
                    print(f"HIT size={len(hit)}", flush=True)
                    for v in rem:
                        add_vertex(v, selected, blocked, neigh)
                    break
                for v in rem:
                    add_vertex(v, selected, blocked, neigh)
                trials += 1
            if hit is not None:
                break
        if hit is not None:
            break
        if i % 5 == 0:
            print(f"i={i}/{n} trials={trials} best_gain={best_gain} t={time.time()-t0:.1f}s", flush=True)
    (HERE / "three_out_log.txt").write_text(
        f"trials {trials}\nbest_gain {best_gain}\nhit {hit is not None}\nseconds {time.time()-t0:.1f}\n"
    )
    if hit is not None:
        if first_conflict(hit) is not None:
            raise SystemExit("adjacent 3-out set")
        out = HERE / f"R{len(hit)}_3out.txt"
        out.write_text("\n".join(format_word(v) for v in hit) + "\n")
        print(f"wrote {out}")
    else:
        print(f"no 3-out improvement trials={trials} best_gain={best_gain}")


if __name__ == "__main__":
    main()
