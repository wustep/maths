#!/usr/bin/env python3
"""35-colour the 355-point T^5 remainder, or SAT-decide a 36-clique.

The five D5-basis vectors of the 360-point Szöllősi pool are universal.
A 41-point code in the pool exists iff this remainder has a 36-clique.
The four published 40-point codes give 35-cliques in the remainder, so
χ ≥ ω ≥ 35.  A proper 35-colouring is a short certificate that ω = 35.

If 35-colouring fails, Cadical and Glucose decide the exact-36 clique
CNF (non-edge forbids, Sinz cardinality).  A SAT model is a 36-clique
and lifts through the five basis vectors to a 41-code.  UNSAT without
a DRAT file is residue, not an emptiness proof.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "q1"))
sys.path.insert(0, str(ROOT / "q2"))
sys.path.insert(0, str(ROOT / "q3"))

from t5_36 import build_pool, is_clique  # noqa: E402

HERE.mkdir(parents=True, exist_ok=True)


def greedy_from_clique(adj, n, clique):
    """Precolour a 35-clique and try DSATUR list-colouring of the rest."""
    colour = [None] * n
    for i, v in enumerate(clique):
        colour[v] = i
    used = [0] * n
    for v in range(n):
        bits = 0
        for u in clique:
            if (adj[v] >> u) & 1:
                bits |= 1 << colour[u]
        used[v] = bits
    sat = [bin(used[v]).count("1") for v in range(n)]
    uncolored = [v for v in range(n) if colour[v] is None]

    def pick():
        best = None
        best_key = None
        for v in uncolored:
            avail = 35 - bin(used[v] & ((1 << 35) - 1)).count("1")
            key = (sat[v], -avail, v)
            if best_key is None or key > best_key:
                best_key = key
                best = v
        return best

    while uncolored:
        v = pick()
        avail = [c for c in range(35) if not ((used[v] >> c) & 1)]
        if not avail:
            return None
        hist = Counter(c for c in colour if c is not None)
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


def sat_color(adj, n, clique, solver_name="cadical195"):
    from pysat.solvers import Cadical195, Glucose4

    def vid(v, c):
        return 1 + v * 35 + c

    Solver = Cadical195 if solver_name == "cadical195" else Glucose4
    slv = Solver()
    # precolour the clique
    for i, v in enumerate(clique):
        slv.add_clause([vid(v, i)])
    for v in range(n):
        slv.add_clause([vid(v, c) for c in range(35)])
        for a, b in combinations(range(35), 2):
            slv.add_clause([-vid(v, a), -vid(v, b)])
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                for c in range(35):
                    slv.add_clause([-vid(i, c), -vid(j, c)])
    sat = slv.solve()
    model = slv.get_model() if sat else None
    slv.delete()
    if not sat:
        return None
    true = set(x for x in model if x > 0)
    colour = [None] * n
    for v in range(n):
        hits = [c for c in range(35) if vid(v, c) in true]
        if len(hits) != 1:
            return None
        colour[v] = hits[0]
    return colour


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


def clique_sat(adj, n, target=36, solver_name="cadical195"):
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF
    from pysat.solvers import Cadical195, Glucose4

    cnf = CNF()
    for i in range(n):
        for j in range(i + 1, n):
            if not ((adj[i] >> j) & 1):
                cnf.append([-(i + 1), -(j + 1)])
    card = CardEnc.equals(lits=list(range(1, n + 1)), bound=target,
                          encoding=EncType.seqcounter)
    cnf.extend(card.clauses)
    Solver = Cadical195 if solver_name == "cadical195" else Glucose4
    slv = Solver(bootstrap_with=cnf)
    sat = slv.solve()
    model = slv.get_model() if sat else None
    slv.delete()
    if not sat:
        return None, {"solver": solver_name, "sat": False,
                      "n_clauses": len(cnf.clauses)}
    true = set(x for x in model if 1 <= x <= n)
    clique = sorted(v - 1 for v in true)
    return clique, {"solver": solver_name, "sat": True,
                    "n_clauses": len(cnf.clauses), "size": len(clique)}


def main() -> int:
    G = build_pool()
    adj = G["adj"]
    n = G["n"]
    published = G["published"]
    print(f"remainder n={n} published={ {k: v['remainder_size'] for k, v in published.items()} }",
          flush=True)

    report = {
        "n_remainder": n,
        "published": {k: v["remainder_size"] for k, v in published.items()},
        "colored": False,
        "found_36": False,
        "found_41": False,
        "complete": False,
    }

    colour = None
    method = None
    for name, rec in published.items():
        C = rec["remainder_clique"]
        if len(C) != 35 or not is_clique(adj, C):
            continue
        g = greedy_from_clique(adj, n, C)
        if g is not None and check_colouring(adj, n, g, 35) is None:
            colour = g
            method = f"greedy:{name}"
            print(f"greedy 35-colouring from {name}", flush=True)
            break
        print(f"greedy from {name} failed", flush=True)

    if colour is None:
        # SAT colouring from D5 remainder if present
        C = None
        for name, rec in published.items():
            if rec["remainder_size"] == 35 and is_clique(adj, rec["remainder_clique"]):
                C = rec["remainder_clique"]
                break
        if C is not None:
            for sname in ("cadical195", "glucose4"):
                print(f"SAT 35-colouring {sname} ...", flush=True)
                colour = sat_color(adj, n, C, sname)
                if colour is None:
                    print(f"  {sname} UNSAT for 35-colouring", flush=True)
                    continue
                reason = check_colouring(adj, n, colour, 35)
                if reason is None:
                    method = f"sat:{sname}"
                    print(f"  {sname} 35-colouring ok", flush=True)
                    break
                print(f"  {sname} bad model {reason}", flush=True)
                colour = None

    if colour is not None:
        report["colored"] = True
        report["method"] = method
        report["complete"] = True
        report["omega"] = 35
        report["comment"] = (
            "Proper 35-colouring of the 355-point T^5 remainder. "
            "Published 35-cliques give ω = 35, so there is no 36-clique "
            "and the Szöllősi pool has no 41-point code."
        )
        (HERE / "certs").mkdir(exist_ok=True)
        (HERE / "certs" / "t5_35color.json").write_text(
            json.dumps({
                "n": n,
                "method": method,
                "colouring": colour,
                "omega": 35,
                "found_36": False,
                "found_41": False,
            }, indent=2) + "\n"
        )
    else:
        print("no 35-colouring; SAT 36-clique ...", flush=True)
        clique, rec = clique_sat(adj, n, 36, "cadical195")
        report["clique_sat"] = rec
        if clique is not None and len(clique) == 36 and is_clique(adj, clique):
            report["found_36"] = True
            report["found_41"] = True
            report["complete"] = True
            report["clique36"] = clique
            # lift through the five universal basis vectors
            univ = G["univ"]
            keep = G["keep"]
            pool = G["pool"]
            idx = [keep[i] for i in clique] + list(univ)
            pts = [list(map(str, pool[i])) for i in idx]
            (HERE / "certs").mkdir(exist_ok=True)
            (HERE / "certs" / "code41.json").write_text(
                json.dumps({
                    "n": 41,
                    "source": "T5 remainder 36-clique plus 5 universal basis vectors",
                    "remainder_clique": clique,
                    "points": pts,
                }, indent=2) + "\n"
            )
            report["comment"] = (
                "36-clique in the T^5 remainder.  Together with the five "
                "universal basis vectors this is a 41-point exact kissing code."
            )
        else:
            # second solver
            clique2, rec2 = clique_sat(adj, n, 36, "glucose4")
            report["clique_sat_glucose"] = rec2
            if clique2 is not None and is_clique(adj, clique2):
                report["found_36"] = True
                report["found_41"] = True
                report["complete"] = True
            else:
                report["complete"] = False
                report["comment"] = (
                    "No 35-colouring and SAT 36-clique returned no model. "
                    "UNSAT without a DRAT file is residue, not an exclusion."
                )

    (HERE / "t5_omega.json").write_text(json.dumps(
        {k: v for k, v in report.items() if k != "clique36"}, indent=2
    ) + "\n")
    print("wrote t5_omega.json colored=", report["colored"],
          "found_36=", report["found_36"], "complete=", report["complete"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
