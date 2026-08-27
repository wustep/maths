#!/usr/bin/env python3
"""Degeneracy and greedy 36-colouring of the 355-point T^5 remainder.

The four published 40-point codes give 35-cliques, so ω ≥ 35.  q4 found
no 35-colouring, so χ ≥ 36.  This file is graph analysis only: degrees,
core numbers, intersections of the published 35s, and a greedy
36-colouring attempt.  No SAT, no 36-clique branch-and-bound.

A proper 36-colouring does not prove ω = 35.  A proper 35-colouring
would, and is written to t5_35color.json as a list of 355 colours in
0..34.  Neither outcome moves the published range 40 ≤ τ₅ ≤ 44.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from t5_36 import build_pool, is_clique  # noqa: E402

PUB_NAMES = ("D5", "L5", "Q5", "R5")


def degrees(adj, n):
    return [adj[v].bit_count() for v in range(n)]


def core_numbers(adj, n):
    """Batagelj–Zaversnik core numbers.  Degeneracy is max(core)."""
    deg = [adj[v].bit_count() for v in range(n)]
    md = max(deg) if n else 0
    bins = [[] for _ in range(md + 1)]
    for v in range(n):
        bins[deg[v]].append(v)
    vert = []
    bin_start = [0] * (md + 2)
    for d in range(md + 1):
        bin_start[d] = len(vert)
        vert.extend(bins[d])
    bin_start[md + 1] = n
    pos = [0] * n
    for i, v in enumerate(vert):
        pos[v] = i
    core = [0] * n
    cur = deg[:]
    for i in range(n):
        v = vert[i]
        core[v] = cur[v]
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if pos[u] > i and cur[u] > cur[v]:
                du = cur[u]
                pu = pos[u]
                pw = bin_start[du]
                w = vert[pw]
                if u != w:
                    vert[pu], vert[pw] = w, u
                    pos[u], pos[w] = pw, pu
                bin_start[du] += 1
                cur[u] -= 1
    return core, vert


def degeneracy_elim(adj, n):
    """Smallest-degree-last order and the remaining degree at removal."""
    rem = [adj[v].bit_count() for v in range(n)]
    alive = [True] * n
    n_alive = n
    order = []
    elim_deg = []
    # bucket of current remaining degrees; n=355, scan is cheap
    for _ in range(n):
        v = None
        best = None
        for i in range(n):
            if not alive[i]:
                continue
            key = (rem[i], i)
            if best is None or key < best:
                best = key
                v = i
        order.append(v)
        elim_deg.append(rem[v])
        alive[v] = False
        n_alive -= 1
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if alive[u]:
                rem[u] -= 1
    return order, elim_deg


def check_cores(adj, n, core):
    """Each v with core k has at least k neighbours of core ≥ k."""
    for v in range(n):
        k = core[v]
        got = 0
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if core[u] >= k:
                got += 1
        if got < k:
            return False
    return True


def check_colouring(adj, n, colour, ncolors):
    if colour is None or len(colour) != n:
        return "missing"
    if any(c is None or c < 0 or c >= ncolors for c in colour):
        return "range"
    for i in range(n):
        for j in range(i + 1, n):
            if ((adj[i] >> j) & 1) and colour[i] == colour[j]:
                return f"edge {i} {j}"
    return None


def greedy_first_fit(adj, n, order, ncolors):
    colour = [None] * n
    used = [0] * n
    for v in order:
        mask = used[v]
        c = 0
        while c < ncolors and ((mask >> c) & 1):
            c += 1
        if c >= ncolors:
            return None
        colour[v] = c
        bit = 1 << c
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            used[u] |= bit
    return colour


def greedy_unlimited(adj, n, order):
    colour = [None] * n
    used = [0] * n
    maxc = 0
    for v in order:
        mask = used[v]
        c = 0
        while (mask >> c) & 1:
            c += 1
        colour[v] = c
        if c > maxc:
            maxc = c
        bit = 1 << c
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            used[u] |= bit
    return colour, maxc + 1


def dsatur(adj, n, ncolors, precolour=None, deg=None):
    """DSATUR list-colouring with at most ncolors colours."""
    if deg is None:
        deg = [adj[v].bit_count() for v in range(n)]
    colour = [None] * n
    used = [0] * n
    sat = [0] * n
    if precolour is not None:
        for v, c in enumerate(precolour):
            if c is None:
                continue
            if c < 0 or c >= ncolors:
                return None
            colour[v] = c
            bit = 1 << c
            nbr = adj[v]
            while nbr:
                u = (nbr & -nbr).bit_length() - 1
                nbr &= nbr - 1
                if colour[u] is None and not ((used[u] >> c) & 1):
                    used[u] |= bit
                    sat[u] += 1
    uncolored = [v for v in range(n) if colour[v] is None]
    un_set = set(uncolored)

    def pick():
        best = None
        best_key = None
        for v in uncolored:
            avail = ncolors - bin(used[v] & ((1 << ncolors) - 1)).count("1")
            key = (sat[v], deg[v], -avail, v)
            if best_key is None or key > best_key:
                best_key = key
                best = v
        return best

    while uncolored:
        v = pick()
        avail = [c for c in range(ncolors) if not ((used[v] >> c) & 1)]
        if not avail:
            return None
        hist = Counter(colour[u] for u in range(n) if colour[u] is not None)
        avail.sort(key=lambda c: (hist[c], c))
        c = avail[0]
        colour[v] = c
        un_set.remove(v)
        uncolored = [u for u in uncolored if u != v]
        bit = 1 << c
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if colour[u] is None and not ((used[u] >> c) & 1):
                used[u] |= bit
                sat[u] += 1
    return colour


def apply_precolour(n, mapping):
    pre = [None] * n
    for v, c in mapping.items():
        pre[v] = c
    return pre


def published_sets(published):
    sets = {}
    for name in PUB_NAMES:
        rec = published[name]
        sets[name] = set(rec["remainder_clique"])
    return sets


def intersection_report(sets):
    pairwise = {}
    for a, b in combinations(PUB_NAMES, 2):
        pairwise[f"{a}&{b}"] = len(sets[a] & sets[b])
    triple = {}
    for a, b, c in combinations(PUB_NAMES, 3):
        triple[f"{a}&{b}&{c}"] = len(sets[a] & sets[b] & sets[c])
    all4 = len(sets["D5"] & sets["L5"] & sets["Q5"] & sets["R5"])
    return {
        "pairwise": pairwise,
        "triple": triple,
        "D5&L5&Q5&R5": all4,
    }


def coverage_hist(sets, n):
    hist = [0] * 5
    for v in range(n):
        k = sum(1 for name in PUB_NAMES if v in sets[name])
        hist[k] += 1
    return {str(k): hist[k] for k in range(5)}


def try_colourings(adj, n, deg, elim_order, published):
    """Greedy / DSATUR attempts at 36 colours, then 35 if a 36 works."""
    attempts = []
    reverse_elim = list(reversed(elim_order))
    dec_deg = sorted(range(n), key=lambda v: (-deg[v], v))
    inc_deg = sorted(range(n), key=lambda v: (deg[v], v))

    # How many colours does unlimited smallest-last first-fit use?
    sl_colour, sl_used = greedy_unlimited(adj, n, reverse_elim)
    attempts.append({"method": "smallest_last_unlimited", "colors_used": sl_used})

    candidates = []

    def record(method, colour, ncolors):
        if colour is None:
            attempts.append({"method": method, "ok": False, "ncolors": ncolors})
            return
        reason = check_colouring(adj, n, colour, ncolors)
        if reason is not None:
            attempts.append({
                "method": method, "ok": False, "ncolors": ncolors,
                "reason": reason,
            })
            return
        used = max(colour) + 1
        attempts.append({
            "method": method, "ok": True, "ncolors": ncolors,
            "colors_used": used,
        })
        candidates.append((used, method, colour))

    record("smallest_last_36",
           greedy_first_fit(adj, n, reverse_elim, 36), 36)
    record("largest_degree_36",
           greedy_first_fit(adj, n, dec_deg, 36), 36)
    record("smallest_degree_36",
           greedy_first_fit(adj, n, inc_deg, 36), 36)
    record("natural_36",
           greedy_first_fit(adj, n, list(range(n)), 36), 36)
    record("dsatur_36", dsatur(adj, n, 36, deg=deg), 36)

    for name, rec in published.items():
        C = rec["remainder_clique"]
        if len(C) != 35 or not is_clique(adj, C):
            continue
        pre = apply_precolour(n, {v: i for i, v in enumerate(C)})
        record(f"precolour_{name}_dsatur_36",
               dsatur(adj, n, 36, precolour=pre, deg=deg), 36)
        # first-fit the rest in reverse-elim order
        rest = [v for v in reverse_elim if v not in set(C)]
        colour = pre[:]
        used = [0] * n
        for v, c in enumerate(pre):
            if c is None:
                continue
            bit = 1 << c
            nbr = adj[v]
            while nbr:
                u = (nbr & -nbr).bit_length() - 1
                nbr &= nbr - 1
                used[u] |= bit
        ok = True
        for v in rest:
            mask = used[v]
            c = 0
            while c < 36 and ((mask >> c) & 1):
                c += 1
            if c >= 36:
                ok = False
                break
            colour[v] = c
            bit = 1 << c
            nbr = adj[v]
            while nbr:
                u = (nbr & -nbr).bit_length() - 1
                nbr &= nbr - 1
                used[u] |= bit
        record(f"precolour_{name}_sl_36", colour if ok else None, 36)

    # If a 36-colouring exists, try the same methods at 35.
    # q4 SAT said none; this is a cheap independent check, not a SAT.
    if candidates:
        record("smallest_last_35",
               greedy_first_fit(adj, n, reverse_elim, 35), 35)
        record("dsatur_35", dsatur(adj, n, 35, deg=deg), 35)
        for name, rec in published.items():
            C = rec["remainder_clique"]
            if len(C) != 35 or not is_clique(adj, C):
                continue
            pre = apply_precolour(n, {v: i for i, v in enumerate(C)})
            record(f"precolour_{name}_dsatur_35",
                   dsatur(adj, n, 35, precolour=pre, deg=deg), 35)

    best = None
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1]))
        best = candidates[0]
    return best, sl_used, attempts


def main() -> int:
    G = build_pool()
    adj, n = G["adj"], G["n"]
    published = G["published"]
    deg = degrees(adj, n)
    m = sum(deg) // 2
    core, bz_order = core_numbers(adj, n)
    degeneracy = max(core) if core else 0
    elim_order, elim_deg = degeneracy_elim(adj, n)
    cores_ok = check_cores(adj, n, core)
    # B–Z order is itself a degeneracy ordering (low core first).
    # Prefer the explicit smallest-degree-last elim order for colouring.

    sets = published_sets(published)
    pub_ok = {}
    for name in PUB_NAMES:
        C = published[name]["remainder_clique"]
        pub_ok[name] = {
            "remainder_size": len(C),
            "is_35_clique": len(C) == 35 and is_clique(adj, C),
        }

    inter = intersection_report(sets)
    cover = coverage_hist(sets, n)

    best, sl_used, attempts = try_colourings(
        adj, n, deg, elim_order, published,
    )

    found_36 = bool(best and best[0] <= 36)
    found_35 = bool(best and best[0] <= 35)
    colour = best[2] if best else None
    method = best[1] if best else None
    colors_used = best[0] if best else None

    if found_35 and colour is not None:
        # User-facing witness: a raw list of 355 colours in 0..34.
        (HERE / "t5_35color.json").write_text(
            json.dumps(colour, indent=2) + "\n"
        )

    mean = (2 * m / n) if n else 0.0
    core_hist = {str(k): c for k, c in sorted(Counter(core).items())}
    deg_hist = {str(k): c for k, c in sorted(Counter(deg).items())}

    if found_35:
        comment = (
            "Proper 35-colouring of the 355-point T^5 remainder.  "
            "Published 35-cliques give ω = 35, so there is no 36-clique "
            "in this remainder.  That does not by itself prove τ₅ = 40."
        )
    elif found_36:
        comment = (
            "Greedy produced a proper 36-colouring of the 355-point T^5 "
            "remainder, so χ ≤ 36.  The four published 35-cliques give "
            "ω ≥ 35, and q4 found no 35-colouring (χ ≥ 36).  A "
            "36-colouring does not prove ω = 35 and does not move the "
            "published range 40 ≤ τ₅ ≤ 44."
        )
    else:
        comment = (
            "No 35- or 36-colouring from the greedy / DSATUR / "
            "degeneracy-order attempts.  Incomplete search, not a lower "
            "bound on χ.  A d-degenerate graph is (d+1)-colourable; "
            f"here d = {degeneracy}.  Did not claim τ₅ = 40."
        )

    report = {
        "n": n,
        "m": m,
        "degree": {
            "min": min(deg) if deg else 0,
            "max": max(deg) if deg else 0,
            "mean": mean,
            "mean_exact": f"{2 * m}/{n}",
            "histogram": deg_hist,
        },
        "degeneracy": degeneracy,
        "elim_degree_max": max(elim_deg) if elim_deg else 0,
        "core_check_ok": cores_ok,
        "core_histogram": core_hist,
        "core_numbers": core,
        "degeneracy_order": elim_order,
        "bz_order": bz_order,
        "published": pub_ok,
        "published_intersections": inter,
        "in_how_many_published_35": cover,
        "union_of_published_35": len(set().union(*sets.values())),
        "smallest_last_colors": sl_used,
        "colouring": {
            "ncolors_attempt": 36,
            "found_36": found_36,
            "found_35": found_35,
            "method": method,
            "colors_used": colors_used,
            "colouring": colour,
            "attempts": attempts,
        },
        "comment": comment,
    }
    (HERE / "t5_degeneracy.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    summary = {
        "n": n,
        "m": m,
        "degree_min": report["degree"]["min"],
        "degree_max": report["degree"]["max"],
        "degree_mean": mean,
        "degeneracy": degeneracy,
        "elim_degree_max": report["elim_degree_max"],
        "core_check_ok": cores_ok,
        "published_intersections": inter,
        "in_how_many_published_35": cover,
        "found_36": found_36,
        "found_35": found_35,
        "method": method,
        "colors_used": colors_used,
        "smallest_last_colors": sl_used,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
