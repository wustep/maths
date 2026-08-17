#!/usr/bin/env python3
"""Unlabelled split-graph census of (nu, tau) via geng -S.

Looks for tau > 2 nu (would refute the conjecture on split graphs) and for
tight examples tau == 2 nu that are not a single K4 or K5 plus pendant K2
blocks (Tuza's classical family, restricted to split graphs).
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from tuza import nu_tau_ilp, triangles_of
from wke import parse_g6

HERE = Path(__file__).resolve().parent
GENG = Path(__file__).resolve().parent / "bin" / "geng"
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)


def geng_split(n):
    proc = subprocess.run(
        [str(GENG), "-q", "-S", str(n)], capture_output=True, text=True, check=True
    )
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if parsed:
            yield parsed[0], parsed[1], line.strip()


def components_of_blocks(n, edges):
    """Very small 2-connected-component / block heuristic for classification.

    We only need a cheap recogniser for 'one K4 or K5 plus trees'.
    """
    E = set(tuple(sorted(e)) for e in edges)
    # clique number
    omega = 1
    for k in range(n, 1, -1):
        found = False
        for S in combinations(range(n), k):
            if all(tuple(sorted((a, b))) in E for a, b in combinations(S, 2)):
                omega = k
                found = True
                break
        if found:
            break
    return omega


def is_tuza_split_family(n, edges):
    """True if the graph is K_t (t<=3), or one K4/K5 with only pending tree edges
    attached at single vertices (no extra triangles).

    Split + Tuza-tight typically means at most one of {K4, K5} as a block
    and all other blocks K2 (otherwise induced 2K2 from two clique-blocks).
    """
    tris = triangles_of(edges, list(range(n)))
    if not tris:
        return True  # forest, tau=nu=0
    # vertices used in some triangle
    used = set()
    for a, b, c in tris:
        used.update((a, b, c))
    H = [e for e in edges if e[0] in used and e[1] in used]
    # induced on triangle-vertices should be K4 or K5
    m = len(used)
    eH = len(H)
    if m == 3 and eH == 3:
        return True  # one triangle, tau=nu=1
    if m == 4 and eH == 6:
        return True  # K4 plus pendants outside
    if m == 5 and eH == 10:
        return True  # K5 plus pendants outside
    return False


def main():
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 6, 7, 8, 9]
    all_out = {}
    for n in ns:
        print(f"=== split n={n} ===", flush=True)
        tight = []
        slack = Counter()
        n_graphs = 0
        n_counter = 0
        n_tight = 0
        n_tight_new = 0
        new_examples = []
        for nv, edges, g6 in geng_split(n):
            n_graphs += 1
            nu, tau = nu_tau_ilp(edges, list(range(nv)))
            if tau > 2 * nu:
                n_counter += 1
                print(f"COUNTEREXAMPLE {g6} nu={nu} tau={tau}", flush=True)
            if nu == 0:
                slack[None] += 1
                continue
            if tau == 2 * nu:
                n_tight += 1
                fam = is_tuza_split_family(nv, edges)
                rec = {
                    "g6": g6,
                    "nu": nu,
                    "tau": tau,
                    "classical": fam,
                    "n_edges": len(edges),
                    "omega": components_of_blocks(nv, edges),
                }
                tight.append(rec)
                if not fam:
                    n_tight_new += 1
                    new_examples.append(rec)
                    print(f"NEW TIGHT? {g6} nu={nu} tau={tau} omega={rec['omega']}", flush=True)
            else:
                slack[round(tau / nu, 4)] += 1
        summary = {
            "n": n,
            "graphs": n_graphs,
            "counterexamples": n_counter,
            "tight": n_tight,
            "tight_nonclassical": n_tight_new,
            "new_examples": new_examples,
            "tight_all": tight,
        }
        all_out[str(n)] = summary
        print(
            f"n={n} graphs={n_graphs} tight={n_tight} new={n_tight_new} cex={n_counter}",
            flush=True,
        )
    (OUT / "split_census.json").write_text(json.dumps(all_out, indent=2) + "\n")


if __name__ == "__main__":
    main()
