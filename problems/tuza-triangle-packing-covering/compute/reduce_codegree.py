#!/usr/bin/env python3
"""Search Puleo reducible-pair certificates at an 8-regular codegree-c edge.

Local model (Gupta §5, rewritten for degree 8):
  C = common neighbours, |C|=c
  A = exclusive neighbours of u, |A|=7-c
  B = exclusive neighbours of v, |B|=7-c
  L keeps every edge of G[W] except A--B.

A certificate is a set S of edge-disjoint triangles of L and a set X of
edges of L with |X|<=2|S|, every triangle of L through u or v meeting X,
and every S-edge with both ends outside {u,v} lying in X.

For c=7 this is a 9-vertex local graph determined by an arbitrary 7-vertex
core H.  We try the hub-only packing/cover template first, then a CBC ILP
that may use triangles inside C.

This is a *new* finite check: Gupta's catalogues are for 7-regular graphs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

from wke import parse_g6

HERE = Path(__file__).resolve().parent
GENG = Path(__file__).resolve().parent / "bin" / "geng"
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)

# try pulp
try:
    import pulp

    HAS_PULP = True
except ImportError:
    HAS_PULP = False


def geng(n, connected=False):
    args = [str(GENG), "-q"]
    if connected:
        args.append("-c")
    args.append(str(n))
    proc = subprocess.run(args, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if parsed:
            yield parsed[0], parsed[1], line.strip()


def beta(n, edges):
    """Vertex-cover number of an n-vertex graph."""
    E = [e for e in edges]
    best = n
    for r in range(n + 1):
        for Q in combinations(range(n), r):
            s = set(Q)
            if all(a in s or b in s for a, b in E):
                return r
    return best


def two_matching_number(edges):
    """Largest |F| for F subset edges that is a union of two matchings."""
    # enumerate pairs of disjoint matchings
    elist = list(edges)
    m = len(elist)
    best = 0
    # all matchings as index-sets
    matchings = []

    def rec(start, used, cur):
        matchings.append(list(cur))
        for i in range(start, m):
            a, b = elist[i]
            if a in used or b in used:
                continue
            cur.append(i)
            rec(i + 1, used | {a, b}, cur)
            cur.pop()

    rec(0, set(), [])
    for m1 in matchings:
        s1 = set(m1)
        for m2 in matchings:
            if s1.isdisjoint(m2):
                best = max(best, len(m1) + len(m2))
    return best


def template_ok(nC, hedges):
    """Hub-only template for 8-regular codegree 7 (A=B=empty, t=1).

    Search some Rsubseteq E(H).  For nC=7 this is 2^{|E|} which can be
    large; we try R in a useful family plus a short systematic scan.
    """
    E = list(hedges)
    # try: empty; all; each matching-like subset via bit scan if small
    if len(E) <= 12:
        cands = range(1 << len(E))
    else:
        # empty, full, and single/double/triple edge subsets + all-but-k
        cands = [0, (1 << len(E)) - 1]
        for k in range(1, min(5, len(E) + 1)):
            for comb in combinations(range(len(E)), k):
                m = 0
                for i in comb:
                    m |= 1 << i
                cands.append(m)
                cands.append(((1 << len(E)) - 1) ^ m)

    def eval_R(rmask):
        R = [E[i] for i in range(len(E)) if (rmask >> i) & 1]
        rem = [e for i, e in enumerate(E) if not ((rmask >> i) & 1)]
        q = beta(nC, rem)
        bR = two_matching_number(R)
        p = bR
        verts = set(range(nC))
        for x in verts:
            Rx = [e for e in R if x not in e]
            p = max(p, 1 + two_matching_number(Rx))
        return 1 + len(R) + 2 * q <= 2 * p, {
            "R": R,
            "q": q,
            "p": p,
            "b": bR,
            "lhs": 1 + len(R) + 2 * q,
            "rhs": 2 * p,
        }

    best = None
    for rmask in cands:
        ok, info = eval_R(rmask)
        if best is None or info["rhs"] - info["lhs"] > best["rhs"] - best["lhs"]:
            best = info
        if ok:
            return True, info
    return False, best


def local_triangles_c7(hedges):
    """Triangles of L at codegree 7. u=nC, v=nC+1, C=0..nC-1."""
    nC = 7
    u, v = nC, nC + 1
    tris = []
    # uvx
    for x in range(nC):
        tris.append((u, v, x))
    H = set(tuple(sorted(e)) for e in hedges)
    # uxy, vxy for xy in H
    for a, b in H:
        tris.append((u, a, b))
        tris.append((v, a, b))
    # triangles inside C
    for a, b, c in combinations(range(nC), 3):
        if (
            tuple(sorted((a, b))) in H
            and tuple(sorted((b, c))) in H
            and tuple(sorted((a, c))) in H
        ):
            tris.append((a, b, c))
    return tris, u, v


def ilp_certificate(hedges):
    if not HAS_PULP:
        return None
    tris, u, v = local_triangles_c7(hedges)
    # all edges that appear
    E = set()
    for t in tris:
        a, b, c = t
        E.add(tuple(sorted((a, b))))
        E.add(tuple(sorted((b, c))))
        E.add(tuple(sorted((a, c))))
    E = sorted(E)
    through = []
    for t in tris:
        if u in t or v in t:
            through.append(t)

    def t_edges(t):
        a, b, c = t
        return [tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))]

    # We search for any feasible S,X.  Minimise 2|S|-|X| slack? Just feasibility.
    # S_i binary, X_e binary.
    # To keep CBC fast: cap |S| at 12 and try decreasing slack.
    prob = pulp.LpProblem("reduce", pulp.LpMinimize)
    Svar = [pulp.LpVariable(f"s{i}", cat="Binary") for i in range(len(tris))]
    Xvar = {e: pulp.LpVariable(f"x{i}", cat="Binary") for i, e in enumerate(E)}
    # dummy objective: minimise |X| - 2|S| (want <= 0)
    prob += pulp.lpSum(Xvar[e] for e in E) - 2 * pulp.lpSum(Svar)
    # edge-disjoint S
    for e in E:
        inc = [Svar[i] for i, t in enumerate(tris) if e in t_edges(t)]
        if inc:
            prob += pulp.lpSum(inc) <= 1
    # X hits every through-triangle
    for t in through:
        tes = t_edges(t)
        prob += pulp.lpSum(Xvar[e] for e in tes) >= 1
    # S-edges off {u,v} lie in X
    for i, t in enumerate(tris):
        for e in t_edges(t):
            if u not in e and v not in e:
                # if S_i then X_e
                prob += Xvar[e] >= Svar[i]
    # |X| <= 2|S|
    prob += pulp.lpSum(Xvar[e] for e in E) <= 2 * pulp.lpSum(Svar)
    # S nonempty not required (empty only works if no through triangles)
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=5))
    if pulp.LpStatus[status] != "Optimal":
        return None
    S = [tris[i] for i, sv in enumerate(Svar) if pulp.value(sv) > 0.5]
    X = [e for e in E if pulp.value(Xvar[e]) > 0.5]
    if len(X) <= 2 * len(S):
        return {"S": S, "X": X, "ns": len(S), "nx": len(X)}
    return None


def verify_cert(hedges, S, X):
    tris, u, v = local_triangles_c7(hedges)
    Xset = set(tuple(sorted(e)) for e in X)

    def t_edges(t):
        a, b, c = t
        return {tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))}

    used = []
    for t in S:
        te = t_edges(t)
        for prev in used:
            if te & prev:
                return False
        used.append(te)
    if len(Xset) > 2 * len(S):
        return False
    for t in tris:
        if u in t or v in t:
            if not (t_edges(t) & Xset):
                return False
    for t in S:
        for e in t_edges(t):
            if u not in e and v not in e and e not in Xset:
                return False
    return True


def main():
    print(f"pulp={HAS_PULP}", flush=True)
    results = []
    n_template = 0
    n_ilp = 0
    n_fail = 0
    fails = []
    for n, edges, g6 in geng(7, connected=False):
        ok_t, info_t = template_ok(7, edges)
        rec = {"g6": g6, "n_edges": len(edges), "template": ok_t}
        if ok_t:
            n_template += 1
            rec["how"] = "template"
            rec["template_info"] = {
                "p": info_t["p"],
                "q": info_t["q"],
                "lhs": info_t["lhs"],
                "rhs": info_t["rhs"],
                "R": info_t["R"],
            }
        else:
            cert = ilp_certificate(edges) if HAS_PULP else None
            if cert and verify_cert(edges, cert["S"], cert["X"]):
                n_ilp += 1
                rec["how"] = "ilp"
                rec["cert"] = cert
            else:
                n_fail += 1
                rec["how"] = "fail"
                rec["template_best"] = info_t
                fails.append(g6)
        results.append(rec)
        if len(results) % 100 == 0:
            print(
                f"progress {len(results)} template={n_template} ilp={n_ilp} fail={n_fail}",
                flush=True,
            )

    summary = {
        "n_cores": len(results),
        "template": n_template,
        "ilp": n_ilp,
        "fail": n_fail,
        "fails": fails,
    }
    print(json.dumps(summary, indent=2), flush=True)
    (OUT / "reduce_c7_8reg.json").write_text(
        json.dumps({"summary": summary, "results": results}, indent=2) + "\n"
    )
    # store only failures + a few successes as a compact cert file
    compact = {
        "summary": summary,
        "failures": [r for r in results if r["how"] == "fail"],
        "ilp_certs": [r for r in results if r["how"] == "ilp"],
    }
    (OUT / "reduce_c7_8reg_compact.json").write_text(json.dumps(compact, indent=2) + "\n")


if __name__ == "__main__":
    main()
