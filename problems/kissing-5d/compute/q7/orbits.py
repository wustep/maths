#!/usr/bin/env python3
"""Aut(D5) orbits of 5-star leftover hosts.

The hyperoctahedral group of signed coordinate permutations has order
5! * 2^5 = 3840 and preserves D5 roots, extras, and the kissing graph.
It acts on the ten coordinate-stars.  The 252 five-star combinations
split into three orbits, one per axis type (n_full, n_half):

    (2, 1)  k=32, 60 pools, 528 extras
    (1, 3)  k=31, 160 pools, 596 extras
    (0, 5)  k=30, 32 pools, 625 extras

A leftover-tight emptiness proof on one representative, plus this
orbit check, empties the type.  Restricted finite-graph fact.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "q4"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from cnfutil import load_graph, pool_for_stars, star_type  # noqa: E402
from sphere import ip  # noqa: E402

REPS = {
    "k32_n2_1": (0, 1, 2, 3, 4),
    "k31_n1_3": (0, 1, 2, 4, 6),
    "k30_n0_5": (0, 2, 4, 6, 8),
}

Q6_CUTOFF = (
    (0, 1, 2, 3, 4),
    (0, 1, 2, 3, 5),
    (0, 1, 2, 3, 6),
    (0, 1, 2, 3, 7),
)


def map_star(star_idx, perm, signs):
    axis = star_idx // 2
    sign = -1 if star_idx % 2 == 0 else 1
    new_axis = perm[axis]
    new_sign = signs[axis] * sign
    return 2 * new_axis + (0 if new_sign < 0 else 1)


def apply_to_vec(v, perm, signs):
    out = [0] * 5
    for i in range(5):
        out[perm[i]] = signs[i] * v[i]
    return tuple(out)


def orbit_of(comb):
    seen = set()
    for perm in permutations(range(5)):
        for signs in product((-1, 1), repeat=5):
            image = tuple(sorted(map_star(s, perm, signs) for s in comb))
            seen.add(image)
    return seen


def main() -> int:
    G = load_graph()
    extras = G["extras"]
    D = G["D"]
    thresh = G["thresh"]
    all_combs = list(combinations(range(10), 5))
    by_type = {}
    pool_stats = {}
    for comb in all_combs:
        typ = star_type(comb)
        by_type.setdefault(typ, []).append(comb)
        U, local, _, _ = pool_for_stars(G, comb)
        pool_stats[comb] = {
            "k": U.bit_count(),
            "n_extras": len(local),
            "type": list(typ),
        }

    # Aut preserves inner products on extras (spot check + one full perm).
    perm0 = (1, 2, 3, 4, 0)
    signs0 = (1, -1, 1, -1, 1)
    idx = {p: i for i, p in enumerate(extras)}
    n_check = 0
    ok_graph = True
    for a in range(0, len(extras), 17):
        ga = apply_to_vec(extras[a], perm0, signs0)
        if ga not in idx:
            ok_graph = False
            break
        for b in range(a + 1, len(extras), 29):
            gb = apply_to_vec(extras[b], perm0, signs0)
            if gb not in idx:
                ok_graph = False
                break
            if (ip(extras[a], extras[b]) <= thresh) != (ip(ga, gb) <= thresh):
                ok_graph = False
                break
            n_check += 1
        if not ok_graph:
            break

    # D5 is preserved
    Dset = set(D)
    d5_ok = True
    for r in D:
        if apply_to_vec(r, perm0, signs0) not in Dset:
            d5_ok = False
            break

    orbits = {}
    transitive = True
    for name, rep in REPS.items():
        orb = orbit_of(rep)
        typ = star_type(rep)
        expected = set(by_type[typ])
        if orb != expected:
            transitive = False
        rec = pool_stats[rep]
        orbits[name] = {
            "rep": list(rep),
            "type": list(typ),
            "k": rec["k"],
            "n_extras": rec["n_extras"],
            "orbit_size": len(orb),
            "type_size": len(expected),
            "transitive": orb == expected,
        }

    q6_types = [star_type(c) for c in Q6_CUTOFF]
    report = {
        "aut_order": 3840,
        "n_five_star": 252,
        "type_counts": {f"{a}_{b}": len(v) for (a, b), v in sorted(by_type.items())},
        "orbits": orbits,
        "transitive": transitive and all(o["transitive"] for o in orbits.values()),
        "graph_spot_ok": ok_graph,
        "n_adj_checks": n_check,
        "d5_preserved_spot": d5_ok,
        "q6_cutoff_all_type_2_1": all(t == (2, 1) for t in q6_types),
        "found_41": False,
        "comment": (
            "Signed permutations act transitively on each 5-star type.  "
            "A leftover-tight certificate on one representative empties "
            "that type.  Restricted; not an unrestricted bound."
        ),
    }
    (HERE / "orbits.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "transitive": report["transitive"],
        "orbits": {k: {kk: v[kk] for kk in ("rep", "k", "n_extras", "orbit_size", "transitive")}
                   for k, v in orbits.items()},
        "graph_spot_ok": ok_graph,
        "d5_preserved_spot": d5_ok,
    }, indent=2))
    return 0 if report["transitive"] and ok_graph and d5_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
