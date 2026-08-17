#!/usr/bin/env python3
"""8-regular codegree-6 hub-only template + ILP fallback.

Local graph: C={0..5}, u=6, v=7, a=8, b=9.
Template (Gupta §6 with t=3): X = {uv, ua, vb} ∪ R ∪ {ux,vx : x in Q}.
Inequality: 3 + |R| + 2q(R) <= 2p(R).
Through-triangles uax are hit by ua regardless of N(a)∩C; likewise vbx.
An ambient ab edge is not in L.

If the template fails, a 10-vertex ILP may use triangles inside C.
"""

from __future__ import annotations

import json
import subprocess
from itertools import combinations
from pathlib import Path

from wke import parse_g6

HERE = Path(__file__).resolve().parent
GENG = HERE / "bin" / "geng"
OUT = HERE / "certs"

try:
    import pulp

    HAS_PULP = True
except ImportError:
    HAS_PULP = False


def geng6():
    proc = subprocess.run([str(GENG), "-q", "6"], capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if parsed:
            yield parsed[1], line.strip()


def beta(n, edges):
    E = list(edges)
    for r in range(n + 1):
        for Q in combinations(range(n), r):
            s = set(Q)
            if all(a in s or b in s for a, b in E):
                return r, list(Q)
    return n, list(range(n))


def two_matching_number(edges):
    elist = list(edges)
    m = len(elist)
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
    best = 0
    pair = ([], [])
    for m1 in matchings:
        s1 = set(m1)
        for m2 in matchings:
            if s1.isdisjoint(m2):
                val = len(m1) + len(m2)
                if val > best:
                    best = val
                    pair = ([elist[i] for i in m1], [elist[i] for i in m2])
    return best, pair


def p_of(R, nC=6):
    bR, pair = two_matching_number(R)
    p = bR
    best_x = None
    for x in range(nC):
        Rx = [e for e in R if x not in e]
        bx, _ = two_matching_number(Rx)
        if 1 + bx > p:
            p = 1 + bx
            best_x = x
    return p, pair, best_x


def template_search(hedges):
    E = list(hedges)
    if len(E) <= 12:
        cands = range(1 << len(E))
    else:
        cands = [0, (1 << len(E)) - 1]
        for k in range(1, min(5, len(E) + 1)):
            for comb in combinations(range(len(E)), k):
                m = 0
                for i in comb:
                    m |= 1 << i
                cands.append(m)
                cands.append(((1 << len(E)) - 1) ^ m)
    best = None
    for rmask in cands:
        R = [E[i] for i in range(len(E)) if (rmask >> i) & 1]
        rem = [e for i, e in enumerate(E) if not ((rmask >> i) & 1)]
        q, Q = beta(6, rem)
        p, pair, best_x = p_of(R)
        lhs, rhs = 3 + len(R) + 2 * q, 2 * p
        info = {"R": R, "q": q, "Q": Q, "p": p, "lhs": lhs, "rhs": rhs, "pair": pair, "best_x": best_x}
        if best is None or rhs - lhs > best["rhs"] - best["lhs"]:
            best = info
        if lhs <= rhs:
            return True, info
    return False, best


def t_edges(t):
    a, b, c = t
    return {tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))}


def local_tris(hedges, Na=None, Nb=None):
    """Triangles of L. Na, Nb subsets of C = neighbourhoods of a,b into C."""
    C = range(6)
    u, v, a, b = 6, 7, 8, 9
    if Na is None:
        Na = set(C)
    if Nb is None:
        Nb = set(C)
    H = {tuple(sorted(e)) for e in hedges}
    tris = []
    for x in C:
        tris.append((u, v, x))
    for x, y in H:
        tris.append((u, x, y))
        tris.append((v, x, y))
    for x in Na:
        tris.append((u, a, x))
    for x in Nb:
        tris.append((v, b, x))
    # triangles inside C
    for x, y, z in combinations(C, 3):
        if tuple(sorted((x, y))) in H and tuple(sorted((y, z))) in H and tuple(sorted((x, z))) in H:
            tris.append((x, y, z))
    # a with two core verts if they are neighbours of a and adjacent
    for x, y in combinations(Na, 2):
        if tuple(sorted((x, y))) in H:
            tris.append((a, x, y))
    for x, y in combinations(Nb, 2):
        if tuple(sorted((x, y))) in H:
            tris.append((b, x, y))
    return tris, u, v


def ilp_cert(hedges):
    """Transferable certificate: S lives in {u,v}∪C; ua,vb,uv forced into X.

    Then every uax / vbx is hit independently of N(a)∩C and N(b)∩C.
    """
    if not HAS_PULP:
        return None
    # triangles that exist for every side-neighbourhood
    tris, u, v = local_tris(hedges, set(), set())
    a, b = 8, 9
    E = set()
    for t in tris:
        E |= t_edges(t)
    E.add((u, a))
    E.add((v, b))
    E.add((u, v))
    E = sorted(E)
    through = [t for t in tris if u in t or v in t]
    # also the possible uax, vbx — hit uniformly by ua, vb
    prob = pulp.LpProblem("c6", pulp.LpMinimize)
    Svar = [pulp.LpVariable(f"s{i}", cat="Binary") for i in range(len(tris))]
    Xvar = {e: pulp.LpVariable(f"x{i}", cat="Binary") for i, e in enumerate(E)}
    # force the three template spokes
    for e0 in ((u, v), (u, a), (v, b)):
        e0 = tuple(sorted(e0))
        prob += Xvar[e0] == 1
    prob += pulp.lpSum(Xvar[e] for e in E) - 2 * pulp.lpSum(Svar)
    for e in E:
        inc = [Svar[i] for i, t in enumerate(tris) if e in t_edges(t)]
        if inc:
            prob += pulp.lpSum(inc) <= 1
    for t in through:
        tes = t_edges(t)
        prob += pulp.lpSum(Xvar[e] for e in tes if e in Xvar) >= 1
    for i, t in enumerate(tris):
        for e in t_edges(t):
            if u not in e and v not in e:
                prob += Xvar[e] >= Svar[i]
    prob += pulp.lpSum(Xvar[e] for e in E) <= 2 * pulp.lpSum(Svar)
    st = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=8))
    if pulp.LpStatus[st] != "Optimal":
        return None
    S = [tris[i] for i, sv in enumerate(Svar) if pulp.value(sv) > 0.5]
    X = [e for e in E if pulp.value(Xvar[e]) > 0.5]
    if len(X) <= 2 * len(S):
        return {"S": S, "X": X, "ns": len(S), "nx": len(X)}
    return None


def check(hedges, S, X, Na=None, Nb=None):
    tris, u, v = local_tris(hedges, Na, Nb)
    Xset = {tuple(sorted(e)) for e in X}
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
    print("pulp", HAS_PULP, flush=True)
    n_t = n_ilp = n_fail = 0
    fails = []
    recs = []
    for edges, g6 in geng6():
        ok, info = template_search(edges)
        rec = {"g6": g6, "n_edges": len(edges), "template": ok}
        if ok:
            n_t += 1
            rec["how"] = "template"
            rec["info"] = {k: info[k] for k in ("R", "q", "Q", "p", "lhs", "rhs")}
        else:
            cert = ilp_cert(edges)
            # verify against complete and empty side neighbourhoods
            sides = [(set(), set()), (set(range(6)), set(range(6))), (set(range(6)), set()), (set(), set(range(6)))]
            good = False
            if cert:
                good = all(check(edges, cert["S"], cert["X"], Na, Nb) for Na, Nb in sides)
            if good:
                n_ilp += 1
                rec["how"] = "ilp"
                rec["cert"] = cert
            else:
                n_fail += 1
                rec["how"] = "fail"
                rec["best"] = {k: info[k] for k in ("R", "q", "p", "lhs", "rhs")} if info else None
                fails.append(g6)
                print("FAIL", g6, "e", len(edges), flush=True)
        recs.append(rec)
    summary = {"n_cores": len(recs), "template": n_t, "ilp": n_ilp, "fail": n_fail, "fails": fails}
    print(json.dumps(summary, indent=2), flush=True)
    (OUT / "reduce_c6_8reg.json").write_text(json.dumps({"summary": summary, "results": recs}, indent=2) + "\n")


if __name__ == "__main__":
    main()
