#!/usr/bin/env python3
"""Independently re-check WKE on the n=8 connected non-WKE census hits.

Uses a second matching/cover enumeration (not the cached bitset tables)
and prints a human description of every Δ=4 example and every example
with fewer than three vertices of degree ≥4.
"""

from __future__ import annotations

import json
import subprocess
from itertools import combinations
from pathlib import Path

from wke import edges_to_mask, is_connected_mask, is_wke_mask, parse_g6

HERE = Path(__file__).resolve().parent
GENG = HERE / "bin" / "geng"
OUT = HERE / "certs"


def brute_wke(n, edges):
    """Second implementation: explicit matching list + vertex-cover scan."""
    E = {tuple(sorted(e)) for e in edges}
    pairs = list(combinations(range(n), 2))
    matchings = [[]]

    def rec(start, used, cur):
        for i in range(start, len(pairs)):
            a, b = pairs[i]
            e = (a, b)
            if e not in E:
                continue
            if a in used or b in used:
                continue
            nxt = cur + [e]
            matchings.append(nxt)
            rec(i + 1, used | {a, b}, nxt)

    rec(0, set(), [])
    for M in matchings:
        rem = E - set(M)
        k = len(M)
        ok = False
        for r in range(k + 1):
            for Q in combinations(range(n), r):
                s = set(Q)
                if all(a in s or b in s for a, b in rem):
                    ok = True
                    break
            if ok:
                break
        if ok:
            return True, M
    return False, None


def describe(n, edges):
    E = {tuple(sorted(e)) for e in edges}
    deg = [0] * n
    adj = [set() for _ in range(n)]
    for a, b in E:
        deg[a] += 1
        deg[b] += 1
        adj[a].add(b)
        adj[b].add(a)
    # triangles
    tris = 0
    for a, b, c in combinations(range(n), 3):
        if (a, b) in E and (b, c) in E and (a, c) in E:
            tris += 1
    return {
        "deg": deg,
        "n_edges": len(E),
        "n_tris": tris,
        "delta": max(deg),
        "n_ge4": sum(1 for d in deg if d >= 4),
        "n_ge5": sum(1 for d in deg if d >= 5),
        "adj": [sorted(s) for s in adj],
    }


def main():
    proc = subprocess.run(
        [str(GENG), "-q", "8"], capture_output=True, text=True, check=True
    )
    exceptions = []
    n_ge4_lt3 = []
    disagreements = []
    n_conn_nonwke = 0
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if not parsed:
            continue
        n, edges = parsed
        gmask = edges_to_mask(n, edges)
        if not is_connected_mask(n, gmask):
            continue
        bitset = is_wke_mask(n, gmask)
        if bitset:
            continue
        n_conn_nonwke += 1
        brute, wit = brute_wke(n, edges)
        if brute:
            disagreements.append({"g6": line.strip(), "witness_M": wit})
            continue
        info = describe(n, edges)
        rec = {"g6": line.strip(), **info}
        if info["delta"] <= 4:
            exceptions.append(rec)
        if info["n_ge4"] < 3:
            n_ge4_lt3.append(rec)

    out = {
        "connected_nonwke": n_conn_nonwke,
        "bitset_vs_brute_disagreements": disagreements,
        "delta_le_4": exceptions,
        "n_ge4_lt3": n_ge4_lt3,
    }
    print(json.dumps({
        "connected_nonwke": n_conn_nonwke,
        "disagreements": len(disagreements),
        "delta_le_4": len(exceptions),
        "n_ge4_lt3": len(n_ge4_lt3),
    }, indent=2), flush=True)
    for rec in exceptions:
        print("DELTA4", rec["g6"], "deg", rec["deg"], "e", rec["n_edges"], "t", rec["n_tris"], flush=True)
    for rec in n_ge4_lt3:
        print("FEW4", rec["g6"], "deg", rec["deg"], "e", rec["n_edges"], "t", rec["n_tris"], flush=True)
    if disagreements:
        print("DISAGREE", disagreements[:5], flush=True)
    (OUT / "n8_exceptions.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
