#!/usr/bin/env python3
"""Exact Hamming-ball repair SAT around a near (5,5,43)-graph.

With at most k edge flips, a 5-set having more than k nonedges cannot become a
clique, and one having more than k edges cannot become independent.  Omitting
those impossible clauses gives an exact, much smaller encoding of the radius-k
ball rather than a heuristic filter.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import fingerprint, is_ramsey, parse_graph6, to_graph6
from orbit_sat import Enc


def build(nbr: list[int], radius: int) -> tuple[Enc, dict[tuple[int, int], int], dict]:
    n = len(nbr)
    enc = Enc()
    edge_vars = {
        (u, v): enc.var("flip", u, v)
        for u, v in itertools.combinations(range(n), 2)
    }
    n_clique = n_independent = 0
    hist = {str(i): 0 for i in range(11)}
    for vertices in itertools.combinations(range(n), 5):
        pairs = list(itertools.combinations(vertices, 2))
        original = [bool((nbr[u] >> v) & 1) for u, v in pairs]
        edges = sum(original)
        hist[str(edges)] += 1
        if 10 - edges <= radius:
            # At least one final nonedge.
            enc.add(
                [edge_vars[pair] if old else -edge_vars[pair]
                 for pair, old in zip(pairs, original)]
            )
            n_clique += 1
        if edges <= radius:
            # At least one final edge.
            enc.add(
                [-edge_vars[pair] if old else edge_vars[pair]
                 for pair, old in zip(pairs, original)]
            )
            n_independent += 1
    enc.card_between(list(edge_vars.values()), 0, radius)
    stats = {
        "relevant_clique_clauses": n_clique,
        "relevant_independent_clauses": n_independent,
        "five_set_edge_histogram": hist,
    }
    return enc, edge_vars, stats


def write_dimacs(enc: Enc, path: Path, n: int, radius: int) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"c exact radius-{radius} repair of near R(5,5,{n}) graph\n")
        f.write(f"p cnf {enc.next_var - 1} {len(enc.clauses)}\n")
        for clause in enc.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def objective(nbr: list[int]) -> tuple[int, list[int]]:
    bad = []
    for vertices in itertools.combinations(range(len(nbr)), 5):
        edges = sum((nbr[u] >> v) & 1 for u, v in itertools.combinations(vertices, 2))
        if edges in (0, 10):
            bad.append(sum(1 << v for v in vertices))
    return len(bad), bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("graph6", type=Path)
    ap.add_argument("radius", type=int)
    ap.add_argument("--cnf", type=Path)
    ap.add_argument("--cert", type=Path)
    ap.add_argument("--no-solve", action="store_true")
    args = ap.parse_args()
    line = args.graph6.read_text().strip().splitlines()[0]
    n, nbr = parse_graph6(line)
    before, bad = objective(nbr)
    t0 = time.time()
    enc, edge_vars, stats = build(nbr, args.radius)
    build_sec = time.time() - t0
    cnf_hash = write_dimacs(enc, args.cnf, n, args.radius) if args.cnf else None
    sat = None
    model = None
    solve_sec = None
    if not args.no_solve:
        from pysat.solvers import Cadical195

        t1 = time.time()
        with Cadical195(bootstrap_with=enc.clauses) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else None
        solve_sec = round(time.time() - t1, 3)
    rec: dict[str, object] = {
        "n": n,
        "radius": args.radius,
        "source_graph6_sha256": hashlib.sha256((line + "\n").encode()).hexdigest(),
        "source_objective": before,
        "source_bad_masks": [hex(x) for x in bad],
        "nvars": enc.next_var - 1,
        "nclauses": len(enc.clauses),
        "build_sec": round(build_sec, 3),
        **stats,
    }
    if sat is not None:
        rec["solve_sec"] = solve_sec
        rec["status"] = "SAT" if sat else "UNSAT"
        rec["solver"] = "PySAT Cadical195"
    if cnf_hash:
        rec["cnf_sha256"] = cnf_hash
    if model:
        positive = {v for v in model if v > 0}
        flips = [pair for pair, var in edge_vars.items() if var in positive]
        candidate = nbr.copy()
        for u, v in flips:
            candidate[u] ^= 1 << v
            candidate[v] ^= 1 << u
        rec["flips"] = flips
        rec["verified_55"] = is_ramsey(candidate)
        rec["graph6"] = to_graph6(candidate)
        rec["fingerprint"] = fingerprint(candidate)
    if args.cert:
        args.cert.parent.mkdir(parents=True, exist_ok=True)
        args.cert.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True), flush=True)
    return 2 if sat and not rec.get("verified_55") else 0


if __name__ == "__main__":
    raise SystemExit(main())
