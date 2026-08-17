#!/usr/bin/env python3
"""How many C3-free oriented graphs on 5 vertices (labeled / unlabeled)?"""

import itertools
from collections import Counter


def has_c3(arcs, n):
    s = set(arcs)
    for i, j, k in itertools.combinations(range(n), 3):
        if ((i, j) in s and (j, k) in s and (k, i) in s) or (
            (i, k) in s and (k, j) in s and (j, i) in s
        ):
            return True
    return False


def canon(arcs, n):
    best = None
    for perm in itertools.permutations(range(n)):
        r = tuple(sorted((perm[i], perm[j]) for i, j in arcs))
        if best is None or r < best:
            best = r
    return best


def main():
    n = 5
    pairs = list(itertools.combinations(range(n), 2))
    labeled = 0
    keys = Counter()
    for ch in itertools.product((0, 1, 2), repeat=len(pairs)):
        arcs = []
        for c, (i, j) in zip(ch, pairs):
            if c == 1:
                arcs.append((i, j))
            elif c == 2:
                arcs.append((j, i))
        if has_c3(arcs, n):
            continue
        labeled += 1
        keys[canon(arcs, n)] += 1
    print("labeled C3-free", labeled)
    print("unlabeled types", len(keys))
    print("largest class", max(keys.values()) if keys else 0)
    print("class size histogram", Counter(keys.values()).most_common(10))


if __name__ == "__main__":
    main()
