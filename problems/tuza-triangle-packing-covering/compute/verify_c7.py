#!/usr/bin/env python3
"""Independent check of 8-regular codegree-7 Puleo certificates.

Does not import the searcher.  Rebuilds (S,X) from a stored rim set R
via the hub-only template, or reads an explicit ILP certificate, and
checks the three Puleo conditions by edge incidence on the 9-vertex
local graph.

Vertex labels: C = {0,...,6}, u = 7, v = 8.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "certs" / "reduce_c7_8reg.json"


def require(cond, msg):
    if not cond:
        raise SystemExit(f"FAIL {msg}")


def parse_g6(line):
    s = line.strip()
    n = ord(s[0]) - 63
    bits = []
    for c in s[1:]:
        val = ord(c) - 63
        for b in range(5, -1, -1):
            bits.append((val >> b) & 1)
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges


def t_edges(t):
    a, b, c = t
    return {tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))}


def local_through_triangles(hedges):
    nC, u, v = 7, 7, 8
    H = {tuple(sorted(e)) for e in hedges}
    tris = []
    for x in range(nC):
        tris.append((u, v, x))
    for a, b in H:
        tris.append((u, a, b))
        tris.append((v, a, b))
    return tris


def all_local_triangles(hedges):
    nC, u, v = 7, 7, 8
    H = {tuple(sorted(e)) for e in hedges}
    tris = local_through_triangles(hedges)
    for a, b, c in combinations(range(nC), 3):
        if (
            tuple(sorted((a, b))) in H
            and tuple(sorted((b, c))) in H
            and tuple(sorted((a, c))) in H
        ):
            tris.append((a, b, c))
    return tris, u, v


def min_cover(n, edges):
    E = [tuple(sorted(e)) for e in edges]
    for r in range(n + 1):
        for Q in combinations(range(n), r):
            s = set(Q)
            if all(a in s or b in s for a, b in E):
                return r, list(Q)
    return n, list(range(n))


def matchings_of(edges):
    el = [tuple(sorted(e)) for e in edges]
    out = [[]]

    def rec(start, used, cur):
        for i in range(start, len(el)):
            a, b = el[i]
            if a in used or b in used:
                continue
            nxt = cur + [el[i]]
            out.append(nxt)
            rec(i + 1, used | {a, b}, nxt)

    rec(0, set(), [])
    return out


def best_two_matchings(edges):
    ms = matchings_of(edges)
    best = 0
    pair = ([], [])
    sets = [(m, set(m)) for m in ms]
    for m1, s1 in sets:
        for m2, s2 in sets:
            if s1.isdisjoint(s2):
                val = len(m1) + len(m2)
                if val > best:
                    best = val
                    pair = (m1, m2)
    return best, pair


def template_SX(hedges, R):
    """Build (S,X) from a rim set as in Gupta's hub-only template, t=1."""
    nC, u, v = 7, 7, 8
    H = {tuple(sorted(e)) for e in hedges}
    R = [tuple(sorted(e)) for e in R]
    Rset = set(R)
    rem = [e for e in H if e not in Rset]
    q, Q = min_cover(nC, rem)
    bR, (M1, M2) = best_two_matchings(R)
    # packing without uvx
    S0 = [(u, a, b) for a, b in M1] + [(v, a, b) for a, b in M2]
    p0 = len(S0)
    # packing with one uvx
    best_with = None
    p1 = -1
    for x in range(nC):
        Rx = [e for e in R if x not in e]
        bx, (N1, N2) = best_two_matchings(Rx)
        cand = [(u, v, x)] + [(u, a, b) for a, b in N1] + [(v, a, b) for a, b in N2]
        if len(cand) > p1:
            p1 = len(cand)
            best_with = cand
    if p0 >= p1:
        S = S0
    else:
        S = best_with
    X = {(u, v)}
    X.update(Rset)
    for x in Q:
        X.add(tuple(sorted((u, x))))
        X.add(tuple(sorted((v, x))))
    return S, sorted(X), {"q": q, "Q": Q, "p": len(S), "lhs": 1 + len(R) + 2 * q, "rhs": 2 * len(S)}


def check_puleo(hedges, S, X):
    tris, u, v = all_local_triangles(hedges)
    through = [t for t in tris if u in t or v in t]
    Xset = {tuple(sorted(e)) for e in X}
    used = []
    for t in S:
        te = t_edges(t)
        for prev in used:
            if te & prev:
                return False, "S not edge-disjoint"
        used.append(te)
    if len(Xset) > 2 * len(S):
        return False, f"|X|={len(Xset)} > 2|S|={2*len(S)}"
    for t in through:
        if not (t_edges(t) & Xset):
            return False, f"unhit through-triangle {t}"
    for t in S:
        for e in t_edges(t):
            if u not in e and v not in e and e not in Xset:
                return False, f"S-edge {e} off hubs not in X"
    return True, "ok"


def main():
    data = json.loads(SRC.read_text())
    results = data["results"]
    n_ok = 0
    n_template = 0
    n_ilp = 0
    certs = []
    for rec in results:
        n, hedges = parse_g6(rec["g6"])
        require(n == 7, f"core order {n}")
        if rec["how"] == "template":
            R = rec["template_info"]["R"]
            S, X, meta = template_SX(hedges, R)
            ok, why = check_puleo(hedges, S, X)
            require(ok, f"template {rec['g6']}: {why} meta={meta}")
            require(meta["lhs"] <= meta["rhs"], f"template arithmetic {rec['g6']} {meta}")
            n_template += 1
            certs.append({"g6": rec["g6"], "how": "template", "S": S, "X": X, **meta})
        elif rec["how"] == "ilp":
            S = [tuple(t) for t in rec["cert"]["S"]]
            X = [tuple(e) for e in rec["cert"]["X"]]
            ok, why = check_puleo(hedges, S, X)
            require(ok, f"ilp {rec['g6']}: {why}")
            n_ilp += 1
            certs.append({"g6": rec["g6"], "how": "ilp", "S": S, "X": X, "ns": len(S), "nx": len(X)})
        else:
            raise SystemExit(f"FAIL uncertified core {rec['g6']}")
        n_ok += 1
    print(f"PASS all {n_ok} cores (template={n_template} ilp={n_ilp})", flush=True)
    out = {
        "n_cores": n_ok,
        "n_template": n_template,
        "n_ilp": n_ilp,
        "certificates": certs,
    }
    dest = HERE / "certs" / "c7_8reg_verified.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
