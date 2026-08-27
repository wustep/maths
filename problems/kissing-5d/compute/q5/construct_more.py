#!/usr/bin/env python3
"""Algebraic 41-point hunts outside the leftover (1/4)Z^5 and T^5 graphs.

Pools, all exact (integer or Q(√3) models):

- (1/7)Z^5: count and type census.  Full 41-clique B&B is skipped
  (n=13480).  Type-restrict: same-missed and mixed-U slices on the
  high D5-degree extras, plus one support-4 axis slice of size 192.
- Signed-permutation orbit of (√3, 1, 0, 0, 0)/√2, alone and with D5.
  q4 construct41 did Q(√2) and Q(√5), not Q(√3).
- Cube vertices + axes + a weight-3 hole type, mixed-norm kissing
  test 4(u·v)^2 <= |u|^2|v|^2 (exact integers).

A hit is written to certs/code41.json as 41 points of squared norm 2
with pairwise inner product <= 1.  Incomplete clique search is
residue, not a lower bound.  Does not claim tau_5 = 40.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q4 = ROOT / "q4"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Q4))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))

from cliqueutil import clique_search  # noqa: E402
from sphere import d5_pts, enumerate_sphere, ip  # noqa: E402

F = Fraction


def strip_clique(rec):
    return {k: v for k, v in rec.items() if k != "clique"}


def clique_from_adj(adj, n, target=41, node_limit=2_000_000, seed_best=0):
    if n > 200:
        return {
            "n": n,
            "skipped": True,
            "reason": "n>200; cliqueutil cap",
            "best": None,
            "found_41": False,
            "complete": False,
        }
    hit, best, nodes, complete = clique_search(
        adj, n, target=target, node_limit=node_limit, seed_best=seed_best
    )
    return {
        "n": n,
        "best": best,
        "found_41": bool(hit),
        "nodes": nodes,
        "complete": complete,
        "clique": hit,
    }


def clique_on_pts(pts, thresh, target=41, node_limit=2_000_000, seed_best=0):
    n = len(pts)
    if n > 200:
        return {
            "n": n,
            "skipped": True,
            "reason": "n>200; cliqueutil cap",
            "best": None,
            "found_41": False,
            "complete": False,
        }
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if ip(pts[i], pts[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    rec = clique_from_adj(adj, n, target, node_limit, seed_best)
    rec["thresh"] = thresh
    return rec


def signed_orbit_int(v):
    out = []
    seen = set()
    for p in set(permutations(v)):
        nz = [i for i, x in enumerate(p) if x]
        for signs in product((-1, 1), repeat=len(nz)):
            w = [0] * 5
            for s, i in zip(signs, nz):
                w[i] = s * p[i]
            t = tuple(w)
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def signed_orbit_pairs(seed):
    """seed is a 5-tuple of (a, b) meaning a + b√3."""
    out = []
    seen = set()
    for perm in permutations(seed):
        nz = [i for i, x in enumerate(perm) if x != (0, 0)]
        for signs in product((-1, 1), repeat=len(nz)):
            v = list(perm)
            for s, i in zip(signs, nz):
                a, b = v[i]
                v[i] = (s * a, s * b)
            t = tuple(v)
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def ip_sqrt3(u, v):
    p = q = 0
    for (a, b), (c, d) in zip(u, v):
        p += a * c + 3 * b * d
        q += a * d + b * c
    return p, q


def le_sqrt3(p, q, bound_p, bound_q=0):
    """p + q√3 <= bound_p + bound_q √3."""
    r = p - bound_p
    s = q - bound_q
    if s == 0:
        return r <= 0
    if s > 0:
        return r < 0 and r * r >= 3 * s * s
    if r <= 0:
        return True
    return r * r <= 3 * s * s


def kiss_mixed_int(u, nu, v, nv):
    """Same-sphere kissing for integer vectors of (possibly different) norms.

    Need 2 u·v <= sqrt(nu nv), i.e. u·v <= 0 or 4 (u·v)^2 <= nu nv.
    """
    uv = u[0] * v[0] + u[1] * v[1] + u[2] * v[2] + u[3] * v[3] + u[4] * v[4]
    if uv <= 0:
        return True
    return 4 * uv * uv <= nu * nv


def write_code41_rational(points, source):
    """points are 5-tuples of Fraction with |x|^2 = 2 and ip <= 1."""
    (HERE / "certs").mkdir(exist_ok=True)
    assert len(points) >= 41
    pts = [tuple(F(x) for x in p) for p in points[:41]]
    for a in range(41):
        if sum(x * x for x in pts[a]) != F(2):
            raise ValueError("norm")
        for b in range(a + 1, 41):
            if sum(x * y for x, y in zip(pts[a], pts[b])) > F(1):
                raise ValueError("pair")
    payload = {
        "n": 41,
        "source": source,
        "points": [[str(x) for x in p] for p in pts],
    }
    (HERE / "certs" / "code41.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )


def hunt_d7():
    pts = enumerate_sphere(7)
    D = d5_pts(7)
    Dset = set(D)
    thresh = 49
    types = Counter(tuple(sorted(abs(x) for x in p)) for p in pts)
    supp = Counter()
    for key, n in types.items():
        supp[sum(1 for x in key if x)] += n
    rec = {
        "n": len(pts),
        "thresh": thresh,
        "n_types": len(types),
        "types": {str(k): v for k, v in sorted(types.items())},
        "support": {str(k): v for k, v in sorted(supp.items())},
        "comment": (
            "n=13480 > 400; no full 41-clique B&B.  "
            "Type-restrict below."
        ),
    }
    extras = []
    deg_hist = Counter()
    for p in pts:
        if p in Dset:
            continue
        miss = 0
        deg = 0
        for i, r in enumerate(D):
            if ip(p, r) <= thresh:
                deg += 1
            else:
                miss |= 1 << i
        deg_hist[deg] += 1
        extras.append((p, miss, deg))
    rec["n_extras"] = len(extras)
    rec["d5_deg_hist"] = {str(k): v for k, v in sorted(deg_hist.items())}

    # Same-missed on high D5-degree extras (deg >= 35): groups are tiny.
    high_by = defaultdict(list)
    for p, miss, deg in extras:
        if deg >= 35:
            high_by[miss].append(p)
    same = []
    best_same_total = 0
    hit = None
    for M, pool in high_by.items():
        k = M.bit_count()
        n1 = 40 - k
        target = k + 1
        n = len(pool)
        if n < 2:
            omega = n
            complete = True
            nodes = 0
        else:
            adj = [0] * n
            for i in range(n):
                for j in range(i + 1, n):
                    if ip(pool[i], pool[j]) <= thresh:
                        adj[i] |= 1 << j
                        adj[j] |= 1 << i
            found, omega, nodes, complete = clique_search(
                adj, n, target=target, node_limit=200_000
            )
            if found is not None and n1 + len(found) >= 41:
                extra = [pool[i] for i in found]
                common = [r for r in D if all(ip(p, r) <= thresh for p in extra)]
                hit = extra + common
        best_same_total = max(best_same_total, n1 + omega)
        same.append({
            "missed": k, "n": n, "best": omega, "target": target,
            "complete": complete, "nodes": nodes,
        })
    rec["same_missed_highdeg"] = {
        "n_groups": len(high_by),
        "group_size_hist": dict(sorted(Counter(len(v) for v in high_by.values()).items())),
        "best_total": best_same_total,
        "max_group_omega": max((s["best"] for s in same), default=0),
        "any_incomplete": any(not s["complete"] for s in same),
        "found_41": hit is not None,
        "comment": "same-missed extras are edgeless (omega=1) on these types",
    }
    if hit is not None:
        rec["hit_int"] = hit
        return rec

    # Mixed-U slices k=3,4,5 on high-deg extras.  Each U-pool is n<=200.
    def pool_for(U):
        pool = []
        sub = U
        while True:
            if sub in high_by:
                pool.extend(high_by[sub])
            if sub == 0:
                break
            sub = (sub - 1) & U
        return pool

    mixed = {}
    for k in (3, 4, 5):
        target = k + 1
        n1 = 40 - k
        seeds = [m for m in high_by if m.bit_count() <= k]
        seen = set()
        tried = 0
        n_U = 0
        best_ex = 0
        complete = True
        found_hit = None
        for M in seeds:
            popM = M.bit_count()
            rest = [i for i in range(40) if not ((M >> i) & 1)]
            need = k - popM
            for extra_idx in combinations(rest, need):
                U = M
                for i in extra_idx:
                    U |= 1 << i
                if U in seen:
                    continue
                seen.add(U)
                n_U += 1
                pool = pool_for(U)
                if len(pool) < target:
                    continue
                tried += 1
                n = len(pool)
                if n > 200:
                    complete = False
                    continue
                adj = [0] * n
                for i in range(n):
                    for j in range(i + 1, n):
                        if ip(pool[i], pool[j]) <= thresh:
                            adj[i] |= 1 << j
                            adj[j] |= 1 << i
                found, best, nodes, comp = clique_search(
                    adj, n, target, node_limit=200_000
                )
                complete = complete and comp
                if best > best_ex:
                    best_ex = best
                if found is not None:
                    extra = [pool[i] for i in found]
                    common = [r for r in D
                              if all(ip(p, r) <= thresh for p in extra)]
                    found_hit = extra + common
                    break
            if found_hit is not None:
                break
        mixed[str(k)] = {
            "k": k,
            "n1": n1,
            "n_U": n_U,
            "tried": tried,
            "best_extras": best_ex,
            "best_total": best_ex + n1,
            "found_41": found_hit is not None,
            "complete": complete and found_hit is None,
        }
        if found_hit is not None:
            rec["hit_int"] = found_hit
            rec["mixed_highdeg"] = mixed
            return rec
    rec["mixed_highdeg"] = mixed

    # Type (0,1,5,6,6): 960 points, one zero.  Axis slice n=192 <= 200.
    t = (0, 1, 5, 6, 6)
    slice0 = [p for p in pts if tuple(sorted(abs(x) for x in p)) == t and p[0] == 0]
    rec["type_01566_axis"] = clique_on_pts(slice0, thresh, seed_best=0)
    rec["type_01566_axis"]["type"] = str(t)
    rec["type_01566_axis"]["comment"] = (
        "zero fixed in coordinate 0; 192 of the 960 type-(0,1,5,6,6) extras"
    )
    return rec


def hunt_qsqrt3():
    """Orbit of (√3, 1, 0, 0, 0)/√2.  Unscaled |x|^2 = 4, scale 1/√2.

    Unscaled coords (a,b) = a + b√3.  Kissing: unscaled ip <= 2.
    D5 is already |x|^2 = 2; cross ip p+q√3 <= √2.
    """
    seed = ((0, 1), (1, 0), (0, 0), (0, 0), (0, 0))
    orbit = signed_orbit_pairs(seed)
    n = len(orbit)
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            p, q = ip_sqrt3(orbit[i], orbit[j])
            if le_sqrt3(p, q, 2, 0):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    alone = clique_from_adj(adj, n, seed_best=0)
    alone["seed"] = "(sqrt(3), 1, 0, 0, 0)/sqrt(2)"
    alone["field"] = "Q(sqrt(3))"

    d5 = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [(0, 0)] * 5
            v[i] = (si, 0)
            v[j] = (sj, 0)
            d5.append(tuple(v))
    pool = d5 + orbit
    kinds = ["d5"] * len(d5) + ["o"] * len(orbit)
    m = len(pool)
    adj2 = [0] * m
    for i in range(m):
        for j in range(i + 1, m):
            p, q = ip_sqrt3(pool[i], pool[j])
            ki, kj = kinds[i], kinds[j]
            if ki == "d5" and kj == "d5":
                ok = le_sqrt3(p, q, 1, 0)
            elif ki == "o" and kj == "o":
                ok = le_sqrt3(p, q, 2, 0)
            else:
                # p + q√3 <= √2
                if le_sqrt3(p, q, 0, 0):
                    ok = True
                else:
                    ok = le_sqrt3(p * p + 3 * q * q, 2 * p * q, 2, 0)
            if ok:
                adj2[i] |= 1 << j
                adj2[j] |= 1 << i
    mixed = clique_from_adj(adj2, m, seed_best=40)
    mixed["seed"] = "D5 union (sqrt(3), 1, 0, 0, 0)/sqrt(2)"
    mixed["field"] = "Q(sqrt(3))"
    mixed["n_d5"] = 40
    mixed["n_orbit"] = n

    # Larger Q(√3) orbit of (√3, 1, 1, 1, 0)/√3, n=320: count only.
    seed2 = ((3, 0), (0, 1), (0, 1), (0, 1), (0, 0))
    orbit2 = signed_orbit_pairs(seed2)
    big = {
        "seed": "(sqrt(3), 1, 1, 1, 0)/sqrt(3)",
        "field": "Q(sqrt(3))",
        "n": len(orbit2),
        "skipped": True,
        "reason": "n=320 > 200; no 41-clique B&B",
        "best": None,
        "found_41": False,
        "complete": False,
    }
    # Axis slice n=64 + D5 = 104, searchable.
    sl = [p for p in orbit2 if p[0] == (0, 0)]
    d5b = []
    for i, j in combinations(range(5), 2):
        for si, sj in product((-1, 1), repeat=2):
            v = [(0, 0)] * 5
            v[i] = (3 * si, 0)
            v[j] = (3 * sj, 0)
            d5b.append(tuple(v))
    pool3 = d5b + sl
    adj3 = [0] * len(pool3)
    for i in range(len(pool3)):
        for j in range(i + 1, len(pool3)):
            p, q = ip_sqrt3(pool3[i], pool3[j])
            if le_sqrt3(p, q, 9, 0):
                adj3[i] |= 1 << j
                adj3[j] |= 1 << i
    slrec = clique_from_adj(adj3, len(pool3), seed_best=40)
    slrec["seed"] = "D5 union (sqrt(3),1,1,1,0)/sqrt(3) with first coord 0"
    slrec["n_orbit_slice"] = len(sl)

    return {
        "orbit": strip_clique(alone),
        "d5_union": strip_clique(mixed),
        "orbit_1110": big,
        "d5_union_1110_axis": strip_clique(slrec),
        "found_41": bool(alone.get("found_41") or mixed.get("found_41")
                         or slrec.get("found_41")),
        "best": max(x.get("best") or 0 for x in (alone, mixed, slrec)),
        "complete": all(x.get("complete") for x in (alone, mixed, slrec)),
    }


def hunt_cube_axes_holes():
    """Cube (±1)^5, axes (±2,0,..), weight-3 holes (±1,±1,±1,0,0).

    Mixed integer norms 5, 4, 3.  Kissing via 4(u·v)^2 <= nu nv.
    Weight-3 is not the D5 hole used in the early cube+axes+D5 mix.
    """
    axes = []
    for k in range(5):
        for s in (-1, 1):
            v = [0] * 5
            v[k] = 2 * s
            axes.append((tuple(v), 4))
    cube = [(c, 5) for c in product((-1, 1), repeat=5)]
    w3 = []
    for idxs in combinations(range(5), 3):
        for signs in product((-1, 1), repeat=3):
            v = [0] * 5
            for t, ix in enumerate(idxs):
                v[ix] = signs[t]
            w3.append((tuple(v), 3))
    w4 = []
    for z in range(5):
        for signs in product((-1, 1), repeat=4):
            v = [0] * 5
            t = 0
            for i in range(5):
                if i == z:
                    continue
                v[i] = signs[t]
                t += 1
            w4.append((tuple(v), 4))

    def run(pts, seed_best, node_limit=2_000_000):
        n = len(pts)
        adj = [0] * n
        for i in range(n):
            for j in range(i + 1, n):
                if kiss_mixed_int(pts[i][0], pts[i][1], pts[j][0], pts[j][1]):
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        return clique_from_adj(
            adj, n, seed_best=seed_best, node_limit=node_limit
        )

    w3rec = run(axes + cube + w3, seed_best=0)
    w3rec["parts"] = {"axes": 10, "cube": 32, "weight3": 80}
    w3rec["hole"] = "(pm1,pm1,pm1,0,0)"
    # Weight-4: a short lower-bound search, then a 41-decision with
    # seed_best=40 so colouring prunes anything that cannot beat 40.
    w4_lb = run(axes + cube + w4, seed_best=0, node_limit=200_000)
    w4_dec = run(axes + cube + w4, seed_best=40)
    w4rec = {
        "n": 122,
        "parts": {"axes": 10, "cube": 32, "weight4": 80},
        "hole": "(pm1,pm1,pm1,pm1,0)",
        "best": w4_lb.get("best"),
        "best_lb_nodes": w4_lb.get("nodes"),
        "best_lb_complete": w4_lb.get("complete"),
        "found_41": bool(w4_dec.get("found_41")),
        "complete": bool(w4_dec.get("complete")),
        "nodes": w4_dec.get("nodes"),
        "comment": (
            "best is a lower bound from a seed_best=0 search; "
            "complete is the 41-decision with seed_best=40"
        ),
    }
    return {
        "weight3": strip_clique(w3rec),
        "weight4": w4rec,
        "found_41": bool(w3rec.get("found_41") or w4rec.get("found_41")),
        "best": max(w3rec.get("best") or 0, w4rec.get("best") or 0),
        "complete": bool(w3rec.get("complete") and w4rec.get("complete")),
    }


def main() -> int:
    (HERE / "certs").mkdir(exist_ok=True)
    parts = {}

    print("---- d7 ----", flush=True)
    d7 = hunt_d7()
    hit7 = d7.pop("hit_int", None)
    # Do not dump clique index lists from the axis slice.
    if "type_01566_axis" in d7:
        d7["type_01566_axis"] = strip_clique(d7["type_01566_axis"])
    parts["d7"] = d7
    print("d7 n", d7["n"], "same_best", d7["same_missed_highdeg"]["best_total"],
          "mixed", {k: v.get("best_total") for k, v in d7["mixed_highdeg"].items()},
          flush=True)

    # Leftover-graph type restrictions: record size only, do not search.
    typeB = [p for p in enumerate_sphere(4)
             if tuple(sorted(abs(x) for x in p)) == (1, 1, 1, 2, 5)]
    parts["d5_plus_typeB"] = {
        "n": 40 + len(typeB),
        "skipped": True,
        "reason": "subgraph of leftover 1480; other workers own that graph",
        "best": None,
        "found_41": False,
        "complete": False,
    }
    orbit_c = signed_orbit_int((3, 3, 3, 2, 1))
    parts["C_orbit"] = {
        "n": len(orbit_c),
        "skipped": True,
        "reason": "type-C extras of leftover (1/4)Z^5; not re-searched",
        "best": None,
        "found_41": False,
        "complete": False,
    }

    print("---- Q(sqrt(3)) ----", flush=True)
    parts["Qsqrt3"] = hunt_qsqrt3()
    print("Qsqrt3", {k: parts["Qsqrt3"][k]
                     for k in ("best", "found_41", "complete")}, flush=True)

    print("---- cube+axes+holes ----", flush=True)
    parts["cube_axes_holes"] = hunt_cube_axes_holes()
    print("holes", {k: parts["cube_axes_holes"][k]
                    for k in ("best", "found_41", "complete")}, flush=True)

    found = False
    if hit7 is not None and len(hit7) >= 41:
        write_code41_rational(
            [tuple(F(x, 7) for x in p) for p in hit7[:41]],
            "construct_more.py d=7 mixed/same-missed",
        )
        found = True
    for name, rec in parts.items():
        if isinstance(rec, dict) and rec.get("found_41"):
            found = True

    bests = []
    for rec in parts.values():
        if not isinstance(rec, dict):
            continue
        if isinstance(rec.get("best"), int):
            bests.append(rec["best"])
        sm = rec.get("same_missed_highdeg", {})
        if isinstance(sm.get("best_total"), int):
            bests.append(sm["best_total"])
        for sl in rec.get("mixed_highdeg", {}).values():
            if isinstance(sl.get("best_total"), int):
                bests.append(sl["best_total"])
        ax = rec.get("type_01566_axis", {})
        if isinstance(ax.get("best"), int):
            bests.append(ax["best"])
        for sub in rec.values():
            if isinstance(sub, dict) and isinstance(sub.get("best"), int):
                bests.append(sub["best"])

    report = {
        "parts": parts,
        "found_41": found,
        "best": max(bests) if bests else 0,
        "comment": (
            "No exact 41-point spherical code in the pools that finished.  "
            "d7 n=13480 is count-plus-type-restrict only; a skipped or "
            "incomplete search is residue, not a lower bound.  "
            "Did not re-search the leftover 1480-point (1/4)Z^5 graph "
            "or the 355-point T^5 remainder.  Did not claim tau_5=40."
        ),
    }
    if found:
        report["comment"] = (
            "A 41-point spherical code was written to certs/code41.json. "
            "Replay: python3 verify.py."
        )
    (HERE / "construct_more.json").write_text(json.dumps(report, indent=2) + "\n")

    summary = {
        "pools": {
            "d7": {
                "n": d7["n"],
                "support": d7["support"],
                "same_missed_best_total": d7["same_missed_highdeg"]["best_total"],
                "mixed_best_totals": {
                    k: v["best_total"] for k, v in d7["mixed_highdeg"].items()
                },
                "type_01566_axis": {
                    k: d7["type_01566_axis"].get(k)
                    for k in ("n", "best", "found_41", "complete")
                },
            },
            "d5_plus_typeB": {"n": parts["d5_plus_typeB"]["n"], "skipped": True},
            "C_orbit": {"n": parts["C_orbit"]["n"], "skipped": True},
            "Qsqrt3_orbit": parts["Qsqrt3"]["orbit"],
            "Qsqrt3_plus_D5": parts["Qsqrt3"]["d5_union"],
            "Qsqrt3_1110": parts["Qsqrt3"]["orbit_1110"],
            "Qsqrt3_1110_axis": parts["Qsqrt3"]["d5_union_1110_axis"],
            "cube_axes_w3": parts["cube_axes_holes"]["weight3"],
            "cube_axes_w4": parts["cube_axes_holes"]["weight4"],
        },
        "best": report["best"],
        "found_41": found,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
