#!/usr/bin/env python3
"""5-vertex flag algebra for triangle-free oriented graphs.

Builds:
  - 317 unlabeled C3-free types on 5 vertices
  - the F4-marginal π: ℝ^{317} → ℝ^{32}
  - the 14×14 λ-flag Cauchy–Schwarz slices AC5[p][q][t]

Used by sdp_f5.py to search for a threshold below the F4 number.
"""

from __future__ import annotations

import itertools
import json
import pickle
from pathlib import Path

from flags4 import (
    H_CANON,
    L_flag,
    canon_key,
    enumerate_labeled,
    has_c3,
    induced,
    type_of,
)

OUT = Path(__file__).resolve().parent / "certs"
CACHE = Path(__file__).resolve().parent / "certs" / "flags5.pkl"


def enumerate_labeled_n(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for choices in itertools.product((0, 1, 2), repeat=len(pairs)):
        arcs = []
        for ch, (i, j) in zip(choices, pairs):
            if ch == 1:
                arcs.append((i, j))
            elif ch == 2:
                arcs.append((j, i))
        fa = frozenset(arcs)
        if has_c3(fa, n):
            continue
        yield fa


def build_types():
    """Return (canon_list, labeled_by_type, type_of_5)."""
    canons = {}
    labeled = []
    for arcs in enumerate_labeled_n(5):
        key = canon_key(arcs, 5)
        if key not in canons:
            canons[key] = len(canons)
        labeled.append((arcs, canons[key]))
    # stable list of keys by type index
    inv = [None] * len(canons)
    for k, i in canons.items():
        inv[i] = k
    return inv, labeled, canons


def f4_marginal(labeled, n_types: int):
    """π[t][i] = average number of 4-subsets of type Hi, divided by 5,
    i.e. the probability a random 4-subset of a type-t graph is Hi.
    """
    n_lab = [0] * n_types
    acc = [[0] * 32 for _ in range(n_types)]
    for arcs, t in labeled:
        n_lab[t] += 1
        for drop in range(5):
            verts = tuple(v for v in range(5) if v != drop)
            sub = induced(arcs, verts)
            acc[t][type_of(sub)] += 1
    pi = [[0.0] * 32 for _ in range(n_types)]
    for t in range(n_types):
        for i in range(32):
            # 5 subsets, so / (5 * n_lab)
            pi[t][i] = acc[t][i] / (5.0 * n_lab[t])
    return pi, n_lab


def ac5_slices(labeled, n_types: int):
    """AC5[p][q][t] = average over labeled type-t graphs of the number of
    (root, pairA, pairB) with L(root,pairA)=p and L(root,pairB)=q.

    pairA, pairB are ordered (so AC is not forced symmetric in the count
    of unordered partitions) and extras within a pair are unordered
    (we try both orders when identifying L).
    """
    n_lab = [0] * n_types
    acc = [[[0] * n_types for _ in range(14)] for _ in range(14)]
    missed = 0
    for arcs, t in labeled:
        n_lab[t] += 1
        verts = (0, 1, 2, 3, 4)
        for root in verts:
            others = [v for v in verts if v != root]
            # ordered assignment of two disjoint unordered pairs
            for i, j in itertools.combinations(others, 2):
                rest = [v for v in others if v != i and v != j]
                a, b = rest
                Lp = L_flag(induced(arcs, (root, i, j)))
                Lq = L_flag(induced(arcs, (root, a, b)))
                if Lp is None or Lq is None:
                    missed += 1
                    continue
                acc[Lp][Lq][t] += 1
    AC = [[[0.0] * n_types for _ in range(14)] for _ in range(14)]
    for p in range(14):
        for q in range(14):
            for t in range(n_types):
                if n_lab[t]:
                    AC[p][q][t] = acc[p][q][t] / n_lab[t]
    return AC, n_lab, missed


def main():
    print("enumerating 5-vertex types ...", flush=True)
    keys, labeled, cmap = build_types()
    n_types = len(keys)
    print(f"types={n_types} labeled={len(labeled)}", flush=True)
    print("F4-marginal ...", flush=True)
    pi, n_lab = f4_marginal(labeled, n_types)
    # sanity: each row of π sums to 1
    row_sums = [sum(pi[t]) for t in range(n_types)]
    print("π row-sum min/max", min(row_sums), max(row_sums))
    print("AC5 ...", flush=True)
    AC, n_lab2, missed = ac5_slices(labeled, n_types)
    print("missed L-flags", missed, "n_lab match", n_lab == n_lab2)
    # how many AC entries nonzero
    nnz = sum(
        1
        for p in range(14)
        for q in range(14)
        for t in range(n_types)
        if abs(AC[p][q][t]) > 1e-12
    )
    print("AC5 nnz", nnz, "of", 14 * 14 * n_types)

    blob = {
        "n_types": n_types,
        "n_labeled": n_lab,
        "pi": pi,  # 317 × 32
        "AC5": AC,  # 14 × 14 × 317
    }
    CACHE.write_bytes(pickle.dumps(blob, protocol=4))
    meta = {
        "n_types": n_types,
        "labeled_total": len(labeled),
        "pi_row_sum_minmax": [min(row_sums), max(row_sums)],
        "AC5_nnz": nnz,
        "missed_L": missed,
    }
    (OUT / "flags5_meta.json").write_text(json.dumps(meta, indent=2))
    print("wrote", CACHE, "and flags5_meta.json")


if __name__ == "__main__":
    main()
