#!/usr/bin/env python3
"""Name the eight Δ=4 connected non-WKE graphs on 8 vertices."""

from itertools import combinations
from wke import parse_g6

GRAPHS = [
    "G?rFeW",
    "G?ouUW",
    "G?rLeW",
    "G?rLeS",
    "G?rNeW",
    "GEjbtg",
    "GEnfbW",
    "GEnbvG",
    "G?r@e[",  # the n_ge4=1 example
]


def decode(g6):
    n, edges = parse_g6(g6)
    E = {tuple(sorted(e)) for e in edges}
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    deg = [len(s) for s in adj]
    tris = []
    for a, b, c in combinations(range(n), 3):
        if (a, b) in E and (b, c) in E and (a, c) in E:
            tris.append((a, b, c))
    # bipartite?
    color = {}
    bip = True
    for s in range(n):
        if s in color:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in color:
                    color[w] = 1 - color[v]
                    stack.append(w)
                elif color[w] == color[v]:
                    bip = False
    return {
        "g6": g6,
        "deg": deg,
        "edges": sorted(E),
        "n_edges": len(E),
        "tris": tris,
        "bipartite": bip,
        "adj": [sorted(s) for s in adj],
    }


def is_4reg_complement_of(name, pred):
    pass


def main():
    for g6 in GRAPHS:
        d = decode(g6)
        print("=" * 60)
        print(g6, "deg", d["deg"], "e", d["n_edges"], "t", len(d["tris"]), "bip", d["bipartite"])
        print("adj", d["adj"])
        print("tris", d["tris"])


if __name__ == "__main__":
    main()
