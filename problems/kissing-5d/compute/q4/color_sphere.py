#!/usr/bin/env python3
"""40-colour (1/d)Z^5 kissing graphs for d in {3,5,6}.

D5 is a 40-clique, so a proper 40-colouring proves ω = 40 and empties
that sphere.  This is not the leftover d=4 graph.
"""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def build(d):
    G = extras_and_groups(d)
    extras = G["extras"]
    masks = G["masks"]
    thresh = G["thresh"]
    n = len(extras)
    lists = [[] for _ in range(n)]
    for i, m in enumerate(masks):
        x = m
        while x:
            b = (x & -x).bit_length() - 1
            lists[i].append(b)
            x &= x - 1
    adj = [0] * n
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ip(extras[i], extras[j]) <= thresh:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    return G, extras, lists, adj, edges


def greedy(lists, adj, n):
    """First-fit on smallest lists.  Linear in n + edges for 40 colours."""
    order = sorted(range(n), key=lambda v: (len(lists[v]), v))
    colour = [None] * n
    used = [0] * n
    for v in order:
        avail = [c for c in lists[v] if not ((used[v] >> c) & 1)]
        if not avail:
            return None
        c = avail[0]
        colour[v] = c
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            used[u] |= 1 << c
    return colour


def greedy_dsatur(lists, adj, n):
    """DSATUR-style; only for n of a few thousand."""
    colour = [None] * n
    used = [0] * n
    sat = [0] * n
    uncolored = set(range(n))

    def pick():
        best = None
        best_key = None
        for v in uncolored:
            avail = 0
            for c in lists[v]:
                if not ((used[v] >> c) & 1):
                    avail += 1
            key = (sat[v], -avail, -len(lists[v]), v)
            if best_key is None or key > best_key:
                best_key = key
                best = v
        return best

    while uncolored:
        v = pick()
        avail = [c for c in lists[v] if not ((used[v] >> c) & 1)]
        if not avail:
            return None
        hist = Counter(colour[u] for u in range(n) if colour[u] is not None)
        avail.sort(key=lambda c: (hist[c], c))
        c = avail[0]
        colour[v] = c
        uncolored.remove(v)
        nbr = adj[v]
        while nbr:
            u = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if colour[u] is None and not ((used[u] >> c) & 1):
                used[u] |= 1 << c
                sat[u] += 1
    return colour


def sat_color(lists, adj, n, solver_name="glucose4"):
    from pysat.solvers import Cadical195, Glucose4

    def vid(v, c):
        return 1 + v * 40 + c

    Solver = Cadical195 if solver_name == "cadical195" else Glucose4
    slv = Solver()
    for v in range(n):
        slv.add_clause([vid(v, c) for c in lists[v]])
        for a, b in combinations(lists[v], 2):
            slv.add_clause([-vid(v, a), -vid(v, b)])
    for i in range(n):
        nbr = adj[i]
        while nbr:
            j = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if j <= i:
                continue
            common = set(lists[i]).intersection(lists[j])
            for c in common:
                slv.add_clause([-vid(i, c), -vid(j, c)])
    sat = slv.solve()
    model = slv.get_model() if sat else None
    slv.delete()
    if not sat:
        return None
    colour = [None] * n
    true = set(x for x in model if x > 0)
    for v in range(n):
        hits = [c for c in lists[v] if vid(v, c) in true]
        if len(hits) != 1:
            return None
        colour[v] = hits[0]
    return colour


def check_colouring(G, extras, lists, adj, colour):
    n = len(extras)
    if colour is None or len(colour) != n:
        return "missing"
    D = G["D"]
    thresh = G["thresh"]
    if any(c is None or c < 0 or c > 39 for c in colour):
        return "range"
    for v in range(n):
        if colour[v] not in lists[v]:
            return f"list {v}"
        if ip(extras[v], D[colour[v]]) <= thresh:
            return f"d5-conflict {v}"
    for i in range(n):
        nbr = adj[i]
        while nbr:
            j = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if j > i and colour[i] == colour[j]:
                return f"edge {i} {j}"
    return None


def color_one(d, try_sat=True):
    G, extras, lists, adj, edges = build(d)
    n = len(extras)
    list_sizes = Counter(len(L) for L in lists)
    print(f"d={d} extras={n} extra_edges={edges} lists={dict(sorted(list_sizes.items()))}",
          flush=True)
    report = {
        "d": d,
        "n": len(G["pts"]),
        "n_extras": n,
        "n_extra_edges": edges,
        "list_size_hist": {str(a): b for a, b in sorted(list_sizes.items())},
        "greedy": False,
        "colored": False,
        "no_41": False,
    }
    colour = greedy(lists, adj, n)
    method = None
    if colour is not None:
        reason = check_colouring(G, extras, lists, adj, colour)
        if reason is None:
            report["greedy"] = True
            method = "greedy"
        else:
            colour = None
    if colour is None and n <= 1600:
        colour = greedy_dsatur(lists, adj, n)
        if colour is not None:
            reason = check_colouring(G, extras, lists, adj, colour)
            if reason is None:
                report["greedy"] = True
                method = "dsatur"
            else:
                colour = None
    if colour is None and try_sat and n <= 800:
        for name in ("glucose4", "cadical195"):
            try:
                colour = sat_color(lists, adj, n, name)
            except Exception as exc:
                report["sat_error"] = str(exc)
                colour = None
                break
            if colour is None:
                continue
            reason = check_colouring(G, extras, lists, adj, colour)
            if reason is None:
                method = f"sat:{name}"
                break
            colour = None
    if colour is not None:
        report["colored"] = True
        report["method"] = method
        report["no_41"] = True
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / f"d{d}_40color.json").write_text(json.dumps({
            "d": d,
            "n": report["n"],
            "n_extras": n,
            "method": method,
            "colouring_extras": colour,
            "omega": 40,
            "no_41": True,
        }, indent=2) + "\n")
    print(f"  colored={report['colored']}", flush=True)
    return report


def main():
    report = {}
    for d in (3, 5, 6):
        report[str(d)] = color_one(d, try_sat=(d == 3))
    report["found_41"] = False
    (HERE / "color_sphere.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
