#!/usr/bin/env python3
"""Forced-graph statistics and the certified 10-block partition.

Default: compute the unique-pair graph on the committed 50-set, then
load and verify result/data/partition_p10.json. The paper takes
p(H)=10 from that artifact.

The discovery run used greedy colouring plus Metropolis recolouring
and found partitions with 16, 12, 11, then 10 blocks. It did not find
9 or 8 blocks in that run. That is an incomplete search, not a lower
bound on p(H). This script does not write a new colouring.

Pass --search to rerun a short Metropolis walk. It will not overwrite
the certified file.
"""

from __future__ import annotations

import argparse
import random
from collections import Counter

from covering_seed_io import (
    PARTITION_PATH,
    cover_mult,
    pair_lists,
    read_matrix,
    read_partition,
)


def pair_needed_syndromes(columns, r):
    column_set = set(columns)
    return [s for s in range(1 << r) if s != 0 and s not in column_set]


def forced_edges(columns, r, lists, needed):
    edges = []
    degree = [0] * len(columns)
    hist = Counter()
    for s in needed:
        pairs = lists[s]
        hist[len(pairs)] += 1
        if len(pairs) == 1:
            i, j = pairs[0]
            edges.append((i, j))
            degree[i] += 1
            degree[j] += 1
    return edges, hist, degree


def partition_failures(block_of, lists, needed):
    failures = 0
    for s in needed:
        if not any(block_of[i] != block_of[j] for i, j in lists[s]):
            failures += 1
    return failures


def greedy_color(n, edges, n_colors):
    """Sequential greedy colouring of the forced graph."""
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    order = sorted(range(n), key=lambda v: len(adj[v]), reverse=True)
    color = [-1] * n
    for v in order:
        used = {color[u] for u in adj[v] if color[u] >= 0}
        for c in range(n_colors):
            if c not in used:
                color[v] = c
                break
        else:
            return None
    return color


def metropolis(block_of, lists, needed, n_colors, steps, rng):
    """Recolour vertices; energy is the number of unsplit pair-syndromes."""
    n = len(block_of)
    color = list(block_of)
    energy = partition_failures(color, lists, needed)
    best = energy
    for _ in range(steps):
        v = rng.randrange(n)
        old = color[v]
        new = rng.randrange(n_colors)
        if new == old:
            continue
        color[v] = new
        nxt = partition_failures(color, lists, needed)
        if nxt <= energy or rng.random() < 0.05:
            energy = nxt
            if energy < best:
                best = energy
        else:
            color[v] = old
        if best == 0:
            return color, 0
    return color, best


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--search",
        action="store_true",
        help="rerun a short Metropolis walk; do not write a colouring",
    )
    args = ap.parse_args(argv)

    r, n, columns = read_matrix()
    lists = pair_lists(columns, r)
    needed = pair_needed_syndromes(columns, r)
    edges, hist, degree = forced_edges(columns, r, lists, needed)
    expected_hist = {1: 821, 2: 123, 4: 19, 5: 8, 6: 2}
    assert len(needed) == 973, len(needed)
    assert dict(hist) == expected_hist, dict(hist)
    assert len(edges) == 821, len(edges)
    assert max(degree) == 42, max(degree)
    print("pair-needed syndromes: %d" % len(needed))
    print("pair-multiplicity: %s" % dict(sorted(hist.items())))
    print("unique-pair edges: %d" % len(edges))
    print("max forced-graph degree: %d" % max(degree))

    blob = read_partition()
    assert blob["columns"] == columns, "certified partition columns disagree"
    block_of = list(blob["block_of_column"])
    p = len(set(block_of))
    assert p == 10, p
    failures = partition_failures(block_of, lists, needed)
    assert failures == 0, "certified partition misses %d syndromes" % failures
    print("certified partition: %s" % PARTITION_PATH)
    print("p(H) = %d from the artifact (not from a later search)" % p)
    print(
        "discovery run: greedy+Metropolis found 16, 12, 11, then 10; "
        "did not find 9 or 8 in that run (incomplete search, not a lower bound)"
    )

    if args.search:
        rng = random.Random(0)
        found = []
        for n_colors in (16, 12, 11, 10, 9, 8):
            seed = greedy_color(n, edges, n_colors)
            if seed is None:
                print("search: greedy failed at %d colours" % n_colors)
                continue
            coloring, energy = metropolis(
                seed, lists, needed, n_colors, steps=2000, rng=rng
            )
            if energy == 0:
                found.append(n_colors)
                print("search: found a %d-block colouring (not written)" % n_colors)
            else:
                print(
                    "search: no %d-block colouring in this short walk (energy %d)"
                    % (n_colors, energy)
                )
        print("search found: %s (do not treat a miss as p(H) > 9)" % found)

    mult = cover_mult(columns, r)
    assert sum(mult) == 1 + n + n * (n - 1) // 2 == 1276
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
