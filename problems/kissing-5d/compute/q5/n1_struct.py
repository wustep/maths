#!/usr/bin/env python3
"""ω(pool(U)) versus |U| on the 1480-point (1/4)Z^5 leftover.

Integer model: a in Z^5, a·a = 32, edge iff a·b <= 16.
D5 is the 40 vectors of type (4,4,0,0,0).  An extra's missed-set is the
set of D5 roots it does not kiss.  Groups (seeds) are extras with a
common missed-set; they are 4-sets or 6-sets.

pool(U) is the extras whose missed-set sits inside U.  A clique E in
pool(U) plus D5 \\ U is a 41-set iff |E| >= |U| + 1.  This file tests
whether ω(pool(U)) <= |U| on concrete U (stars, random seed-unions,
single seeds) and looks for a short exact reason that would make the
inequality hold for every U.

A missed-root colouring of extras would prove the inequality: colour
each extra by a D5 root it misses.  If that were a proper colouring,
then pool(U) would be |U|-colourable, hence ω <= |U|.  The script
checks this and records why it fails if it fails.  It does not claim
τ5 = 40, and it does not claim a proof it has not checked.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q4 = HERE.parent / "q4"
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(HERE.parent))

from cliqueutil import clique_search  # noqa: E402
from sphere import extras_and_groups, ip  # noqa: E402

NODE_LIMIT = 200_000
RNG_SEED = 20260827
TYPE_A = (2, 2, 2, 2, 4)
TYPE_B = (1, 1, 1, 2, 5)
TYPE_C = (1, 2, 3, 3, 3)


def type_key(v):
    return tuple(sorted(abs(x) for x in v))


def extra_graph(extras, thresh):
    n = len(extras)
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(extras[i], extras[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    return adj, edges


def induce(adj, pool):
    n = len(pool)
    local = [0] * n
    edges = 0
    for a in range(n):
        ia = pool[a]
        bits = adj[ia]
        for b in range(a + 1, n):
            if (bits >> pool[b]) & 1:
                local[a] |= 1 << b
                local[b] |= 1 << a
                edges += 1
    return local, edges


def pool_of(masks, U):
    return [i for i, m in enumerate(masks) if m & ~U == 0]


def stars_of(D):
    stars = []
    names = []
    for i in range(5):
        for s in (-1, 1):
            bits = 0
            for j, r in enumerate(D):
                if r[i] == s * 4:
                    bits |= 1 << j
            assert bits.bit_count() == 8
            stars.append(bits)
            names.append(f"e{i}{'+' if s > 0 else '-'}")
    return stars, names


def rank_mod2(rows):
    """Row rank of 0-1 vectors given as ints, over GF(2)."""
    basis = []
    for v in rows:
        x = v
        for b in basis:
            # cancel the lowest bit of b if present
            lo = b & -b
            if x & lo:
                x ^= b
        if x:
            basis.append(x)
    return len(basis)


def rank_Q(rows, ncols):
    """Exact row rank over Q of 0-1 rows given as ints."""
    mat = []
    for v in rows:
        mat.append([Fraction(1 if (v >> j) & 1 else 0) for j in range(ncols)])
    rank = 0
    used = set()
    for col in range(ncols):
        pivot = None
        for i, row in enumerate(mat):
            if i in used:
                continue
            if row[col] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        used.add(pivot)
        pv = mat[pivot][col]
        for j in range(ncols):
            mat[pivot][j] /= pv
        for i, row in enumerate(mat):
            if i == pivot or row[col] == 0:
                continue
            fac = row[col]
            for j in range(ncols):
                row[j] -= fac * mat[pivot][j]
        rank += 1
    return rank


def principal_root(p, D, thresh):
    """Missed D5 root of largest inner product; None if not unique."""
    best_ip = thresh
    hits = []
    for j, r in enumerate(D):
        s = ip(p, r)
        if s > thresh:
            if s > best_ip:
                best_ip = s
                hits = [j]
            elif s == best_ip:
                hits.append(j)
    if len(hits) != 1:
        return None
    return hits[0]


def search_pool(adj, pool, U, node_limit=NODE_LIMIT):
    k = U.bit_count()
    n = len(pool)
    if n == 0:
        return {
            "n_pool": 0,
            "k": k,
            "best": 0,
            "target": k + 1,
            "nodes": 0,
            "complete": True,
            "hit": None,
        }
    local, _ = induce(adj, pool)
    hit, best, nodes, complete = clique_search(
        local, n, target=k + 1, node_limit=node_limit, seed_best=0
    )
    return {
        "n_pool": n,
        "k": k,
        "best": best,
        "target": k + 1,
        "nodes": nodes,
        "complete": complete,
        "hit": None if hit is None else [pool[i] for i in hit],
    }


def classify(rec):
    if rec["best"] > rec["k"]:
        return "gt"
    if not rec["complete"]:
        return "incomplete"
    if rec["best"] == rec["k"]:
        return "eq"
    return "lt"


def tally(rows):
    c = Counter(classify(r) for r in rows)
    return {
        "n": len(rows),
        "omega_eq_U": c["eq"],
        "omega_lt_U": c["lt"],
        "omega_gt_U": c["gt"],
        "incomplete": c["incomplete"],
        "all_complete": c["incomplete"] == 0 and c["gt"] == 0,
    }


def main() -> int:
    G = extras_and_groups(4)
    extras = G["extras"]
    D = G["D"]
    groups = G["groups"]
    masks = G["masks"]
    thresh = G["thresh"]
    assert len(D) == 40
    assert len(extras) == 1440
    assert len(groups) == 240
    assert len(masks) == 1440

    four = [m for m in groups if m.bit_count() == 4]
    six = [m for m in groups if m.bit_count() == 6]
    other = [m for m in groups if m.bit_count() not in (4, 6)]
    assert len(four) == 160 and len(six) == 80 and not other

    type_A = [p for p in extras if type_key(p) == TYPE_A]
    type_B = [p for p in extras if type_key(p) == TYPE_B]
    type_C = [p for p in extras if type_key(p) == TYPE_C]
    assert len(type_A) == 160
    assert len(type_B) == 640
    assert len(type_C) == 640

    four_sizes = [len(groups[m]) for m in four]
    six_sizes = [len(groups[m]) for m in six]
    assert all(s == 5 for s in four_sizes)
    assert all(s == 8 for s in six_sizes)

    four_splits = []
    for m in four:
        keys = Counter(type_key(p) for p in groups[m])
        four_splits.append({str(k): v for k, v in keys.items()})
    six_splits = []
    for m in six:
        keys = Counter(type_key(p) for p in groups[m])
        six_splits.append({str(k): v for k, v in keys.items()})
    four_split_u = sorted({json.dumps(s, sort_keys=True) for s in four_splits})
    six_split_u = sorted({json.dumps(s, sort_keys=True) for s in six_splits})

    # Expected: each four-seed is 1 A + 4 B; each six-seed is 8 C.
    expect_four = {str(TYPE_A): 1, str(TYPE_B): 4}
    expect_six = {str(TYPE_C): 8}
    assert all(s == expect_four for s in four_splits)
    assert all(s == expect_six for s in six_splits)

    # A 4-seed sitting inside a 6-seed would enlarge pool(six-seed).
    four_in_six = 0
    for s in six:
        four_in_six += sum(1 for f in four if f & ~s == 0)

    print("type split ok; four-seeds inside a six-seed:", four_in_six,
          flush=True)

    adj, n_edges = extra_graph(extras, thresh)
    print(f"extras graph n=1440 edges={n_edges}", flush=True)

    # Same-missed extras are edgeless.
    intra = 0
    for m, pts in groups.items():
        idx = [i for i, mm in enumerate(masks) if mm == m]
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                if (adj[idx[a]] >> idx[b]) & 1:
                    intra += 1
    assert intra == 0

    # Colouring extras by a missed root: colour class r = extras that
    # miss r.  Proper iff those extras never kiss.
    shared_root_edges = 0
    example_pair = None
    per_root = []
    for r in range(40):
        bit = 1 << r
        idx = [i for i, m in enumerate(masks) if m & bit]
        e = 0
        sample = None
        for a in range(len(idx)):
            bits = adj[idx[a]]
            for b in range(a + 1, len(idx)):
                if (bits >> idx[b]) & 1:
                    e += 1
                    if sample is None:
                        sample = (idx[a], idx[b])
        shared_root_edges += e
        per_root.append({"root": r, "n_extras": len(idx), "edges": e})
        if example_pair is None and sample is not None:
            i, j = sample
            common = masks[i] & masks[j]
            roots = []
            x = common
            while x:
                b = (x & -x).bit_length() - 1
                roots.append(b)
                x &= ~(1 << b)
            example_pair = {
                "extra_i": list(extras[i]),
                "extra_j": list(extras[j]),
                "inner": ip(extras[i], extras[j]),
                "thresh": thresh,
                "missed_i": masks[i].bit_count(),
                "missed_j": masks[j].bit_count(),
                "n_shared_roots": common.bit_count(),
                "shared_root_indices": roots,
            }

    # Principal-root colouring (unique max inner product among missed
    # roots).  A proper colouring of this form would prove ω <= |U|
    # for every U, because the colour of an extra in pool(U) lies in U.
    prin = [principal_root(p, D, thresh) for p in extras]
    n_unique_principal = sum(1 for c in prin if c is not None)
    prin_conflicts = 0
    prin_example = None
    for i in range(len(extras)):
        ci = prin[i]
        if ci is None:
            continue
        bits = adj[i]
        j = 0
        x = bits
        while x:
            j = (x & -x).bit_length() - 1
            x &= ~(1 << j)
            if prin[j] == ci:
                prin_conflicts += 1
                if prin_example is None:
                    prin_example = {
                        "extra_i": list(extras[i]),
                        "extra_j": list(extras[j]),
                        "inner": ip(extras[i], extras[j]),
                        "principal_root": ci,
                    }
    # each edge counted twice
    prin_conflicts //= 2

    colouring_ok = shared_root_edges == 0
    print(
        f"shared-root kissing edges={shared_root_edges} "
        f"unique_principal={n_unique_principal} "
        f"principal_conflicts={prin_conflicts}",
        flush=True,
    )

    stars, star_names = stars_of(D)
    seeds = list(groups)

    star_rows = []
    star_hits = []
    for t, S in enumerate(stars):
        pool = pool_of(masks, S)
        rec = search_pool(adj, pool, S)
        rec["name"] = star_names[t]
        rec["n_seeds_in_U"] = sum(1 for m in seeds if m & ~S == 0)
        star_rows.append(rec)
        print(
            f"star {star_names[t]} n={rec['n_pool']} k=8 "
            f"best={rec['best']} complete={rec['complete']} "
            f"nodes={rec['nodes']}",
            flush=True,
        )
        if rec["hit"] is not None:
            star_hits.append(rec)

    # Linear algebra on a star clique, if we found |E| = 8 (tight).
    la = {
        "checked": False,
        "comment": (
            "No tight star clique was returned as a target hit; "
            "stars are expected to have ω = 8 = |U|, found by "
            "raising best rather than by the target-|U|+1 exit."
        ),
    }
    tight = [r for r in star_rows if r["best"] == 8 and r["complete"]]
    # Recover an 8-clique on the first tight star by a second search
    # whose target is 8, so clique_search returns the clique.
    if tight:
        S = stars[star_names.index(tight[0]["name"])]
        pool = pool_of(masks, S)
        local, _ = induce(adj, pool)
        hit8, best8, nodes8, complete8 = clique_search(
            local, len(pool), target=8, node_limit=NODE_LIMIT, seed_best=7
        )
        if hit8 is not None and len(hit8) == 8:
            E = [pool[i] for i in hit8]
            rows = [masks[i] for i in E]
            la = {
                "checked": True,
                "star": tight[0]["name"],
                "clique_size": 8,
                "rank_Q": rank_Q(rows, 40),
                "rank_GF2": rank_mod2(rows),
                "nodes": nodes8,
                "complete": complete8,
                "best": best8,
            }
            # Four-seeds of a star lie in a 4-flat (one root from each
            # opposite pair).  Characteristic vectors then span at most 5
            # over Q, so they cannot be independent at size 8.
            print(
                f"LA star clique rank_Q={la['rank_Q']} "
                f"rank_GF2={la['rank_GF2']}",
                flush=True,
            )

    seed_rows = []
    for m in seeds:
        pool = pool_of(masks, m)
        rec = search_pool(adj, pool, m)
        rec["seed_k"] = m.bit_count()
        rec["n_seeds_in_U"] = sum(1 for s in seeds if s & ~m == 0)
        seed_rows.append(rec)

    rng = random.Random(RNG_SEED)
    random_rows = []
    seen = set()
    attempts = 0
    while len(random_rows) < 200 and attempts < 5000:
        attempts += 1
        t = rng.randint(3, 6)
        chosen = tuple(sorted(rng.sample(range(len(seeds)), t)))
        if chosen in seen:
            continue
        seen.add(chosen)
        U = 0
        for i in chosen:
            U |= seeds[i]
        pool = pool_of(masks, U)
        rec = search_pool(adj, pool, U)
        rec["n_seeds_chosen"] = t
        rec["n_seeds_in_U"] = sum(1 for s in seeds if s & ~U == 0)
        random_rows.append(rec)
        if len(random_rows) % 50 == 0:
            print(f"random {len(random_rows)}/200", flush=True)

    leads = []
    for family, rows in (
        ("star", star_rows),
        ("single_seed", seed_rows),
        ("random", random_rows),
    ):
        for rec in rows:
            if rec["best"] <= rec["k"]:
                continue
            Ubits = None
            if family == "star":
                Ubits = stars[star_names.index(rec["name"])]
            elif family == "single_seed":
                Ubits = seeds[seed_rows.index(rec)]
            # random: reconstruct from pool misses
            if rec["hit"] is not None:
                U_actual = 0
                for i in rec["hit"]:
                    U_actual |= masks[i]
                leads.append({
                    "family": family,
                    "k_ambient": rec["k"],
                    "k_clique_union": U_actual.bit_count(),
                    "extras_clique": [list(extras[i]) for i in rec["hit"]],
                    "U_root_indices": [
                        j for j in range(40) if (U_actual >> j) & 1
                    ],
                    "U_roots": [
                        list(D[j]) for j in range(40)
                        if (U_actual >> j) & 1
                    ],
                    "n_extras": len(rec["hit"]),
                    "complete": rec["complete"],
                })

    star_stats = tally(star_rows)
    seed_stats = tally(seed_rows)
    rand_stats = tally(random_rows)
    all_rows = star_rows + seed_rows + random_rows
    all_stats = tally(all_rows)

    # Decide the proof field from checks actually run.
    proved = False
    if colouring_ok:
        proved = True
        argument = (
            "Colour each extra by any D5 root it misses.  Extras that "
            "miss a common root never kiss, so this is a proper "
            "colouring.  On pool(U) the colours used all lie in U, "
            "hence ω(pool(U)) <= |U| for every U.  A 41-set in the "
            "1480-graph would need a clique E with |E| >= |U| + 1, "
            "which cannot occur.  This empties the leftover graph; it "
            "does not by itself prove τ5 = 40."
        )
    else:
        argument = (
            "A missed-root colouring of extras does not prove "
            "ω(pool(U)) <= |U|.  Two extras that miss the same D5 root "
            "can still kiss: the extras-graph has "
            f"{shared_root_edges} such edges.  An explicit pair is "
            "recorded under coloring.example_pair (inner product "
            f"{example_pair['inner'] if example_pair else 'n/a'} <= "
            f"{thresh}).  Same-missed extras — those with the same "
            "full seed — are edgeless, but sharing a single root is "
            "weaker and is not a stable set.  "
            "A principal-root colouring (the unique missed root of "
            "largest inner product, when it exists) also fails: "
            f"{n_unique_principal} extras have a unique principal "
            f"root, and {prin_conflicts} kissing pairs share it.  "
            "Linear independence of missed-set characteristic vectors "
            "on a tight star clique also fails as a proof: those "
            "vectors live in an affine 4-flat (one root from each "
            "opposite pair in the star) and are dependent at size 8.  "
            "Hall matching of a clique into U is equivalent to the "
            "inequality itself, not a separate reason.  The tests "
            "below found no U with ω > |U|, but that is a finite "
            "sample (plus the ten stars and every single seed), not a "
            "proof for every U.  Leftover |U| >= 19 of the 1480-graph "
            "remains open.  This does not claim τ5 = 40."
        )

    report = {
        "n": 1480,
        "n_d5": 40,
        "n_extras": 1440,
        "n_groups": 240,
        "n_extra_edges": n_edges,
        "n_intra_group_edges": intra,
        "groups_edgeless": intra == 0,
        "type_split": {
            "n_four_seeds": 160,
            "n_six_seeds": 80,
            "four_seed_group_size": 5,
            "six_seed_group_size": 8,
            "type_A": {"abs": [4, 2, 2, 2, 2], "n": 160},
            "type_B": {"abs": [5, 2, 1, 1, 1], "n": 640},
            "type_C": {"abs": [3, 3, 3, 2, 1], "n": 640},
            "four_seed_type_split_unique": four_split_u,
            "six_seed_type_split_unique": six_split_u,
            "four_seeds_inside_a_six_seed": four_in_six,
            "comment": (
                "Each four-seed is 1 type-A (4,2,2,2,2) plus 4 type-B "
                "(5,2,1,1,1).  Each six-seed is 8 type-C (3,3,3,2,1)."
            ),
        },
        "proved": proved,
        "argument": argument,
        "counterexample": leads[0] if leads else None,
        "n_leads": len(leads),
        "leads": leads,
        "coloring": {
            "same_missed_edgeless": intra == 0,
            "shared_root_kissing_edges": shared_root_edges,
            "shared_root_is_stable": colouring_ok,
            "example_pair": example_pair,
            "per_root_edge_min": min(p["edges"] for p in per_root),
            "per_root_edge_max": max(p["edges"] for p in per_root),
            "n_unique_principal": n_unique_principal,
            "principal_conflicts": prin_conflicts,
            "principal_example": prin_example,
        },
        "linear_algebra": la,
        "tests": {
            "node_limit": NODE_LIMIT,
            "rng_seed": RNG_SEED,
            "stars": {
                **star_stats,
                "rows": [
                    {
                        "name": r["name"],
                        "n_pool": r["n_pool"],
                        "k": r["k"],
                        "best": r["best"],
                        "nodes": r["nodes"],
                        "complete": r["complete"],
                        "n_seeds_in_U": r["n_seeds_in_U"],
                        "cmp": classify(r),
                    }
                    for r in star_rows
                ],
            },
            "single_seeds": {
                **seed_stats,
                "four_seed_best_unique": sorted({
                    r["best"] for r in seed_rows if r["seed_k"] == 4
                }),
                "six_seed_best_unique": sorted({
                    r["best"] for r in seed_rows if r["seed_k"] == 6
                }),
                "four_seed_n_pool_unique": sorted({
                    r["n_pool"] for r in seed_rows if r["seed_k"] == 4
                }),
                "six_seed_n_pool_unique": sorted({
                    r["n_pool"] for r in seed_rows if r["seed_k"] == 6
                }),
            },
            "random_unions": {
                **rand_stats,
                "n_chosen_hist": dict(sorted(
                    Counter(r["n_seeds_chosen"] for r in random_rows).items()
                )),
                "k_hist": dict(sorted(
                    Counter(r["k"] for r in random_rows).items()
                )),
                "best_minus_k_hist": dict(sorted(
                    Counter(r["best"] - r["k"] for r in random_rows).items()
                )),
                "sample": [
                    {
                        "n_pool": r["n_pool"],
                        "k": r["k"],
                        "best": r["best"],
                        "complete": r["complete"],
                        "n_seeds_chosen": r["n_seeds_chosen"],
                        "n_seeds_in_U": r["n_seeds_in_U"],
                        "cmp": classify(r),
                    }
                    for r in random_rows[:12]
                ],
            },
        },
        "stats": all_stats,
        "comment": (
            "q4 emptied every seed-union with |U| <= 18; leftover is "
            "|U| >= 19.  A 41-set needs |E| >= |U| + 1.  This file "
            "asks whether ω(pool(U)) <= |U| always.  A yes with a "
            "proof would empty the 1480-graph.  A single U with "
            "ω > |U| is a 41-lead.  Tests used cliqueutil.clique_search "
            f"with node_limit={NODE_LIMIT}.  No claim that τ5 = 40."
        ),
    }

    out = HERE / "n1_struct.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    summary = {
        "proved": proved,
        "n_leads": len(leads),
        "stats": all_stats,
        "stars": star_stats,
        "single_seeds": seed_stats,
        "random": rand_stats,
        "shared_root_edges": shared_root_edges,
        "la": {k: la[k] for k in la if k != "comment"},
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
