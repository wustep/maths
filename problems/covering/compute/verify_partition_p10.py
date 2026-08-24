#!/usr/bin/env python3
"""Verify a (2,0)-partition of the committed 50-set.

Every pair-needed syndrome must have a representing pair whose two
columns lie in different blocks. Columns are re-read from the matrix
text; the partition file supplies block labels only.
"""

from covering_seed_io import (
    PARTITION_PATH,
    pair_lists,
    read_matrix,
    read_partition,
)


def main():
    r, n, columns = read_matrix()
    blob = read_partition()
    if list(blob["columns"]) != list(columns):
        raise SystemExit("partition JSON columns disagree with the matrix text")
    block_of = blob["block_of_column"]
    if len(block_of) != n:
        raise SystemExit("partition length does not match the matrix")
    blocks = sorted(set(block_of))
    if blocks != list(range(len(blocks))):
        raise SystemExit("block labels are not 0..p-1")
    if any(block_of.count(b) == 0 for b in blocks):
        raise SystemExit("an empty block")

    column_set = set(columns)
    needed = [s for s in range(1 << r) if s != 0 and s not in column_set]
    lists = pair_lists(columns, r)
    failures = []
    for s in needed:
        if not any(block_of[i] != block_of[j] for i, j in lists[s]):
            failures.append(s)
    print("pair-needed syndromes: %d" % len(needed))
    print("blocks: %d" % len(blocks))
    print("cross-block failures: %d" % len(failures))
    print("partition file: %s" % PARTITION_PATH)
    if failures:
        raise SystemExit("first unsplit syndrome: %d" % failures[0])
    print("every pair-needed syndrome has a two-block representing pair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
