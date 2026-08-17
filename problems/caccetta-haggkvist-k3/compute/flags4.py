#!/usr/bin/env python3
"""From-scratch 4-vertex flag counts for triangle-free oriented graphs.

Rebuilds HKN's types H0..H31, the 8 β-flags K0..K7, the 14 λ-flags L0..L13,
and the matrices AC, AR, BR by enumerating labeled graphs.  Compares AC
against the published Table 1.

A labeled oriented graph is a set of arcs, no loops, no 2-cycles.
"""

from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent / "certs"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# HKN type representatives on {a,b,c,d} = {0,1,2,3}
# ---------------------------------------------------------------------------
# edge names: ab=01, ac=02, ad=03, bc=12, bd=13, cd=23, and reverses.
def E(*names: str) -> frozenset[tuple[int, int]]:
    mp = {"a": 0, "b": 1, "c": 2, "d": 3}
    arcs = []
    for nm in names:
        arcs.append((mp[nm[0]], mp[nm[1]]))
    return frozenset(arcs)


H_EDGES = [
    E(),  # H0
    E("cd"),  # H1
    E("bd", "cd"),  # H2
    E("bd", "dc"),  # H3
    E("db", "dc"),  # H4
    E("ad", "bd", "cd"),  # H5
    E("ad", "bd", "dc"),  # H6
    E("ad", "db", "dc"),  # H7
    E("da", "db", "dc"),  # H8
    E("bc", "bd", "cd"),  # H9
    E("ad", "bc"),  # H10
    E("ad", "bc", "cd"),  # H11
    E("ad", "bc", "bd"),  # H12
    E("ad", "bc", "bd", "cd"),  # H13
    E("ad", "bc", "bd", "dc"),  # H14
    E("ad", "bc", "db"),  # H15
    E("ad", "bc", "db", "dc"),  # H16
    E("da", "bc", "bd"),  # H17
    E("da", "bc", "bd", "cd"),  # H18
    E("da", "bc", "bd", "dc"),  # H19
    E("da", "bc", "db", "dc"),  # H20
    E("ac", "ad", "bc", "bd"),  # H21
    E("ac", "ad", "bc", "bd", "cd"),  # H22
    E("ac", "ad", "bc", "db"),  # H23
    E("ac", "ad", "bc", "db", "dc"),  # H24
    E("ac", "da", "bc", "db"),  # H25
    E("ac", "da", "bc", "db", "dc"),  # H26
    E("ac", "ad", "cb", "db", "cd"),  # H27
    E("ac", "da", "cb", "bd"),  # H28
    E("ac", "da", "cb", "db", "dc"),  # H29
    E("ca", "da", "cb", "db", "cd"),  # H30
    E("ab", "ac", "ad", "bc", "bd", "cd"),  # H31 cyclic
]


def has_2cycle(arcs: frozenset[tuple[int, int]]) -> bool:
    return any((j, i) in arcs for i, j in arcs)


def has_c3(arcs: frozenset[tuple[int, int]], n: int = 4) -> bool:
    for i, j, k in itertools.combinations(range(n), 3):
        if ((i, j) in arcs and (j, k) in arcs and (k, i) in arcs) or (
            (i, k) in arcs and (k, j) in arcs and (j, i) in arcs
        ):
            return True
    return False


def relabel(arcs: frozenset[tuple[int, int]], perm: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    return frozenset((perm[i], perm[j]) for i, j in arcs)


def canon_key(arcs: frozenset[tuple[int, int]], n: int = 4) -> tuple:
    """Canonical representative: min tuple of sorted arcs over S_n."""
    best = None
    for perm in itertools.permutations(range(n)):
        r = relabel(arcs, perm)
        key = tuple(sorted(r))
        if best is None or key < best:
            best = key
    return best


# Precompute canonical key -> H-index
H_CANON = {canon_key(e): i for i, e in enumerate(H_EDGES)}
assert len(H_CANON) == 32, f"H types collide: {len(H_CANON)}"


def type_of(arcs: frozenset[tuple[int, int]]) -> int:
    return H_CANON[canon_key(arcs)]


# ---------------------------------------------------------------------------
# β-flags K0..K7 on {1,2,a} = roots 0,1 extra 2, with 0→1
# ---------------------------------------------------------------------------
def K_flag(arcs3: frozenset[tuple[int, int]]) -> int | None:
    """Identify which K_i the β-flag on vertices (0,1,2) is. Need 0→1."""
    if (0, 1) not in arcs3:
        return None
    extra = []
    for u, v in arcs3:
        if (u, v) == (0, 1):
            continue
        extra.append((u, v))
    extra_set = frozenset(extra)
    table = {
        frozenset(): 0,  # K0 {12}
        frozenset([(1, 2)]): 1,  # K1 {12, 2a}  2→a means vertex2 → extra = 1→2
        frozenset([(2, 1)]): 2,  # K2 {12, a2}
        frozenset([(0, 2)]): 3,  # K3 {12, 1a}
        frozenset([(0, 2), (1, 2)]): 4,  # K4 {12, 1a, 2a}
        frozenset([(0, 2), (2, 1)]): 5,  # K5 {12, 1a, a2}
        frozenset([(2, 0)]): 6,  # K6 {12, a1}
        frozenset([(2, 0), (2, 1)]): 7,  # K7 {12, a1, a2}
    }
    return table.get(extra_set)


def induced(arcs: frozenset[tuple[int, int]], verts: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    idx = {v: i for i, v in enumerate(verts)}
    out = []
    s = set(verts)
    for i, j in arcs:
        if i in s and j in s:
            out.append((idx[i], idx[j]))
    return frozenset(out)


# ---------------------------------------------------------------------------
# λ-flags L0..L13 on {1,a,b} = root 0, extras 1,2
# ---------------------------------------------------------------------------
def E_L(*names: str) -> frozenset[tuple[int, int]]:
    # 1=0 (root), a=1, b=2
    mp = {"1": 0, "a": 1, "b": 2}
    return frozenset((mp[nm[0]], mp[nm[1]]) for nm in names)


L_EDGES = [
    E_L(),  # L0
    E_L("ab"),  # L1
    E_L("1b"),  # L2
    E_L("1b", "ab"),  # L3
    E_L("1b", "ba"),  # L4
    E_L("b1"),  # L5
    E_L("b1", "ab"),  # L6
    E_L("b1", "ba"),  # L7
    E_L("1a", "1b"),  # L8
    E_L("1a", "1b", "ab"),  # L9
    E_L("1a", "b1"),  # L10
    E_L("1a", "b1", "ba"),  # L11
    E_L("a1", "b1"),  # L12
    E_L("a1", "b1", "ab"),  # L13
]


def swap_ab(arcs: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
    # swap extras 1 and 2
    tr = {0: 0, 1: 2, 2: 1}
    return frozenset((tr[i], tr[j]) for i, j in arcs)


L_INDEX: dict[frozenset[tuple[int, int]], int] = {}
for i, e in enumerate(L_EDGES):
    L_INDEX[e] = i
    L_INDEX[swap_ab(e)] = i  # identify swap of non-roots


def L_flag(arcs3: frozenset[tuple[int, int]]) -> int | None:
    return L_INDEX.get(arcs3)


def alpha_flag(arcs2: frozenset[tuple[int, int]]) -> bool:
    """α: λ-flag root → extra, on vertices (0,1)."""
    return arcs2 == frozenset([(0, 1)])


def enumerate_labeled(n: int = 4):
    pairs = list(itertools.combinations(range(n), 2))
    # each pair: 0 none, 1 i→j, 2 j→i
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


def compute_AC():
    """AC_ij coefficient of Ψ_t = average over labeled type-t graphs of
    the number of vertex permutations (x,y,z,w) with x→y, flag(x,y,z)=Ki,
    flag(x,y,w)=Kj.

    This is HKN's 24 [[Ki·Kj]]_β if the 24 is 4! and densities are unlabeled
    type densities (each type weighted equally as a random 4-set's iso type).
    """
    n_type = [0] * 32
    acc = [[[0] * 32 for _ in range(8)] for _ in range(8)]  # acc[i][j][t]
    unknown_k = 0
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        # all 4! assignments (x,y,z,w)
        for perm in itertools.permutations(range(4)):
            x, y, z, w = perm
            if (x, y) not in arcs:
                continue
            ki = K_flag(induced(arcs, (x, y, z)))
            kj = K_flag(induced(arcs, (x, y, w)))
            if ki is None or kj is None:
                unknown_k += 1
                continue
            acc[ki][kj][t] += 1
    # average per labeled copy of the type
    AC = [[defaultdict(int) for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            for t in range(32):
                if n_type[t] == 0:
                    continue
                # total configs / n_type = average per labeled graph
                # HKN Table 1 looks like small integers (2,4,1,…), so we want
                # acc[i][j][t] / n_type[t]
                val = acc[i][j][t] / n_type[t]
                if abs(val) > 1e-12:
                    AC[i][j][t] = val
    return AC, n_type, unknown_k


# Published Table 1, for comparison.
PUB_AC = {
    (0, 0): {1: 2, 10: 4},
    (0, 1): {3: 1, 11: 1, 15: 1},
    (0, 2): {2: 2, 11: 1, 12: 1},
    (0, 3): {4: 2, 12: 1, 17: 1},
    (0, 4): {9: 1, 13: 1, 18: 1},
    (0, 5): {9: 1, 14: 1, 19: 1},
    (0, 6): {3: 1, 15: 1, 17: 1},
    (0, 7): {9: 1, 16: 1, 20: 1},
    (1, 1): {7: 2, 16: 2},
    (1, 2): {6: 2, 14: 1},
    (1, 3): {17: 1, 23: 1, 25: 2},
    (1, 4): {19: 1, 24: 1, 27: 1},
    (1, 5): {18: 1, 27: 1},
    (1, 6): {15: 1, 23: 1, 28: 4},
    (1, 7): {18: 1, 29: 1},
    (2, 2): {5: 6, 13: 2},
    (2, 3): {12: 1, 21: 4, 23: 1},
    (2, 4): {14: 1, 22: 2},
    (2, 5): {13: 1, 22: 2, 24: 1},
    (2, 6): {11: 1, 23: 1, 25: 2},
    (2, 7): {13: 1, 24: 1, 26: 2},
    (3, 3): {8: 6, 20: 2},
    (3, 4): {20: 1, 26: 2, 29: 1},
    (3, 5): {20: 1, 29: 1, 30: 2},
    (3, 6): {7: 2, 19: 1},
    (3, 7): {19: 1, 30: 2},
    (4, 4): {30: 2, 31: 2},
    (4, 5): {29: 1, 31: 1},
    (4, 6): {16: 1, 24: 1},
    (4, 7): {27: 1, 31: 1},
    (5, 5): {26: 2, 31: 2},
    (5, 6): {16: 1, 27: 1},
    (5, 7): {24: 1, 31: 1},
    (6, 6): {6: 2, 18: 2},
    (6, 7): {14: 1, 27: 1, 29: 1},
    (7, 7): {22: 2, 31: 2},
}


def ac_to_dict(AC):
    d = {}
    for i in range(8):
        for j in range(i, 8):
            terms = {}
            for t in range(32):
                val = AC[i][j][t] if isinstance(AC[i][j], dict) else AC[i][j][t]
                if abs(val) > 1e-9:
                    terms[t] = val
            if terms:
                d[(i, j)] = terms
    return d


def compute_lambda_products():
    """For each L_p and the α flag, count expansions into H_t.

    L · α is a 4-vertex λ-flag (root + 2 from L + 1 from α).
    L · 1 expands L into 4-vertex graphs by adding a free vertex (the
    'c0 AR' term).

    We count, for each labeled 4-graph of type t:
      BR-style: # of (root, a, b, extra_alpha) with
          λ-flag(root,a,b)=L_p and λ-flag(root, extra_alpha)=α
      AR-style: # of (root, a, b, dummy) with λ-flag(root,a,b)=L_p
          (dummy unrestricted except the 4-set is the graph)
    """
    n_type = [0] * 32
    # br[p][t], ar[p][t]
    br = [[0] * 32 for _ in range(14)]
    ar = [[0] * 32 for _ in range(14)]
    missed_L = 0
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for root, a, b, extra in itertools.permutations(range(4)):
            Lf = L_flag(induced(arcs, (root, a, b)))
            if Lf is None:
                missed_L += 1
                continue
            ar[Lf][t] += 1
            if (root, extra) in arcs:
                # α: only the outgoing edge, no incoming extra→root
                # α as listed is the flag "directed edge from root", which
                # is just that one edge on 2 vertices (no other pair).
                br[Lf][t] += 1
    # average
    AR = [[0.0] * 32 for _ in range(14)]
    BR = [[0.0] * 32 for _ in range(14)]
    for p in range(14):
        for t in range(32):
            if n_type[t]:
                AR[p][t] = ar[p][t] / n_type[t]
                BR[p][t] = br[p][t] / n_type[t]
    return AR, BR, n_type, missed_L


def main():
    # sanity: all H representatives are C3-free and pairwise non-isomorphic
    for i, e in enumerate(H_EDGES):
        assert not has_2cycle(e), i
        assert not has_c3(e), (i, e)
    print("32 H-types, pairwise non-isomorphic:", len(H_CANON) == 32)

    AC, n_type, unk = compute_AC()
    print("labeled C3-free oriented graphs on 4 verts:", sum(n_type))
    print("per type:", n_type)
    print("unknown K flags on a β-edge:", unk)

    got = ac_to_dict(AC)
    print("\n=== AC vs Table 1 ===")
    mismatches = 0
    all_keys = set(got) | set(PUB_AC)
    for key in sorted(all_keys):
        g = {k: float(v) for k, v in got.get(key, {}).items()}
        p = {k: float(v) for k, v in PUB_AC.get(key, {}).items()}
        # scale? find a global scale later
        if g != p:
            mismatches += 1
            print(f"  AC{key}")
            print(f"    computed {g}")
            print(f"    published {p}")
    print("entry mismatches (raw, before scale):", mismatches)

    # try a global scale: published (0,0) is 2 Ψ1 + 4 Ψ10
    # computed average for (0,0)
    print("\ncomputed AC[0][0]:", dict(got.get((0, 0), {})))

    AR, BR, n2, missL = compute_lambda_products()
    print("\nmissed L flags:", missL)
    print("AR row0:", AR[0])
    print("BR row0:", BR[0])

    payload = {
        "n_labeled_by_type": n_type,
        "AC_computed": {f"{i},{j}": {str(t): v for t, v in terms.items()} for (i, j), terms in got.items()},
        "AR_computed": AR,
        "BR_computed": BR,
    }
    path = OUT / "flags4.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
