#!/usr/bin/env python3
"""40-colour the 1480-point (1/4)Z^5 kissing graph.

D5 is a 40-clique, so χ ≥ 40.  A proper 40-colouring is a short
certificate that ω = 40, hence that this graph has no 41-clique.

Precolour the 40 D5 roots with distinct colours.  An extra is adjacent
to a root iff their integer inner product is ≤ 16, so its list is
exactly the missed-root set (the colours of the non-neighbours in D5).
The remaining constraints are that adjacent extras get different colours.

A greedy list-colouring is tried first; if it fails, Cadical and Glucose
solve the same list-colouring SAT.  An independent checker rebuilds the
graph and rejects any colouring that is not proper.
"""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from sphere import extras_and_groups, ip

HERE = Path(__file__).resolve().parent


def build():
    G = extras_and_groups(4)
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
    """DSATUR-style list colouring.  colour[v] in 0..39 or None."""
    colour = [None] * n
    used = [0] * n  # bitset of colours used by coloured neighbours
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
            key = (sat[v], -avail, -lists[v].__len__(), v)
            if best_key is None or key > best_key:
                best_key = key
                best = v
        return best

    while uncolored:
        v = pick()
        avail = [c for c in lists[v] if not ((used[v] >> c) & 1)]
        if not avail:
            return None
        # least-used among available
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


def sat_color(lists, adj, n, solver_name="cadical195"):
    from pysat.solvers import Cadical195, Glucose4

    # var id: extra v, colour c -> 1 + v*40 + c  (c in 0..39, unused c never appear)
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
    """Independent proper-colouring check.  Returns None if ok, else reason."""
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
        # extra is not adjacent to the D5 root of its colour
        if ip(extras[v], D[colour[v]]) <= thresh:
            return f"d5-conflict {v}"
    for i in range(n):
        nbr = adj[i]
        while nbr:
            j = (nbr & -nbr).bit_length() - 1
            nbr &= nbr - 1
            if j > i and colour[i] == colour[j]:
                return f"edge {i} {j}"
    # D5 is precoloured 0..39 and is a clique; extras using colour c
    # must not be adjacent to D[c], already checked.
    return None


def main() -> int:
    G, extras, lists, adj, edges = build()
    n = len(extras)
    list_sizes = Counter(len(L) for L in lists)
    print(f"extras={n} extra_edges={edges} list_hist={dict(sorted(list_sizes.items()))}",
          flush=True)

    report = {
        "d": 4,
        "n": len(G["pts"]),
        "n_d5": 40,
        "n_extras": n,
        "n_extra_edges": edges,
        "list_size_hist": {str(a): b for a, b in sorted(list_sizes.items())},
        "greedy": False,
        "sat": None,
        "colored": False,
        "omega_le": None,
        "no_41": False,
    }

    colour = greedy(lists, adj, n)
    method = None
    if colour is not None:
        reason = check_colouring(G, extras, lists, adj, colour)
        if reason is None:
            report["greedy"] = True
            method = "greedy"
            print("greedy 40-colouring ok", flush=True)
        else:
            print("greedy produced an invalid colouring:", reason, flush=True)
            colour = None

    if colour is None:
        for name in ("cadical195", "glucose4"):
            print(f"SAT list-colouring with {name} ...", flush=True)
            colour = sat_color(lists, adj, n, name)
            if colour is None:
                report["sat"] = {"solver": name, "sat": False}
                print(f"  {name} UNSAT", flush=True)
                continue
            reason = check_colouring(G, extras, lists, adj, colour)
            report["sat"] = {"solver": name, "sat": True, "check": reason}
            if reason is None:
                method = f"sat:{name}"
                print(f"  {name} 40-colouring ok", flush=True)
                break
            print(f"  {name} model failed check: {reason}", flush=True)
            colour = None

    if colour is not None:
        report["colored"] = True
        report["method"] = method
        report["omega_le"] = 40
        report["no_41"] = True
        report["colouring"] = colour
        report["comment"] = (
            "Proper 40-colouring of the 1480-point (1/4)Z^5 kissing graph. "
            "D5 is a 40-clique, so ω = 40.  No 41-clique in this graph."
        )
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "d4_40color.json").write_text(
            json.dumps({
                "n": 1480,
                "n_d5": 40,
                "n_extras": n,
                "method": method,
                "colouring_extras": colour,
                "omega": 40,
                "no_41": True,
            }, indent=2) + "\n"
        )
    else:
        report["comment"] = (
            "No 40-colouring found.  That does not produce a 41-clique. "
            "The n1<=32 slice remains a separate search."
        )

    (HERE / "color_d4.json").write_text(json.dumps({
        k: v for k, v in report.items() if k != "colouring"
    }, indent=2) + "\n")
    print("wrote color_d4.json colored=", report["colored"],
          "no_41=", report["no_41"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
