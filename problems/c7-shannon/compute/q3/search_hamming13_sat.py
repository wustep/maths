#!/usr/bin/env python3
"""Hamming-13 residue: 6-out / 7-in using only ≤4-blocker vertices.

Cases that add a 5- or 6-blocker vertex are finished in
search_hamming13.c. This SAT instance is the leftover: remove 6 seed
vertices and add ≥7 vertices each blocked by at most 4 seed points.
"""

from __future__ import annotations

import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
import sys

sys.path.insert(0, str(ROOT))

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Cadical195

from c7_common import NVERTS, adjacent, closed_neighbors, format_word
from verify_set import first_conflict, load_set

ENC = EncType.kmtotalizer


def atmost(lits, bound, top_id):
    if bound < 0:
        return [[1], [-1]], top_id
    if not lits or bound >= len(lits):
        return [], top_id
    if bound == 0:
        return [[-x] for x in lits], top_id
    cnf = CardEnc.atmost(lits=lits, bound=bound, top_id=top_id, encoding=ENC)
    return list(cnf.clauses), cnf.nv


def exactly(lits, k, top_id):
    if k < 0 or k > len(lits):
        return [[1], [-1]], top_id
    clauses, top_id = atmost(lits, k, top_id)
    more, top_id = atmost([-x for x in lits], len(lits) - k, top_id)
    clauses.extend(more)
    return clauses, top_id


def atleast(lits, k, top_id):
    return atmost([-x for x in lits], len(lits) - k, top_id)


def main() -> None:
    t0 = time.time()
    seed = load_set(ROOT / "R367.txt")
    index = {s: i for i, s in enumerate(seed)}
    seed_set = set(seed)
    blockers = [[] for _ in range(NVERTS)]
    for i, s in enumerate(seed):
        for u in closed_neighbors(s):
            if u in index:
                continue
            blockers[u].append(i)
    cands = [
        v
        for v in range(NVERTS)
        if v not in seed_set and 1 <= len(blockers[v]) <= 4
    ]
    print(f"cands_le4={len(cands)}", flush=True)
    rem = list(range(1, len(seed) + 1))
    add_map = {}
    vid = len(seed)
    for v in cands:
        vid += 1
        add_map[v] = vid
    add_lits = list(add_map.values())
    top_id = vid
    cnf = CNF()
    for v, lit in add_map.items():
        for i in blockers[v]:
            cnf.append([-lit, rem[i]])
    add_verts = list(add_map)
    for i, u in enumerate(add_verts):
        for v in add_verts[i + 1 :]:
            if adjacent(u, v):
                cnf.append([-add_map[u], -add_map[v]])
    extra, top_id = exactly(rem, 6, top_id)
    cnf.extend(extra)
    extra, top_id = atleast(add_lits, 7, top_id)
    cnf.extend(extra)
    print(f"clauses={len(cnf.clauses)} vars={top_id}", flush=True)
    solver = Cadical195(bootstrap_with=cnf.clauses)
    sat = solver.solve()
    sec = time.time() - t0
    lines = [
        f"cands_le4 {len(cands)}",
        f"clauses {len(cnf.clauses)} vars {top_id}",
        f"sat {sat} seconds {sec:.2f}",
    ]
    if sat:
        model = set(solver.get_model())
        kept = [seed[i] for i, lit in enumerate(rem) if lit not in model]
        added = [v for v, lit in add_map.items() if lit in model]
        T = sorted(set(kept) | set(added))
        print(f"SAT size={len(T)} added={len(added)}", flush=True)
        if first_conflict(T) is not None:
            raise SystemExit("SAT model adjacent")
        out = HERE / f"R{len(T)}_hamming13.txt"
        out.write_text("\n".join(format_word(v) for v in T) + "\n")
        lines.append(f"wrote {out} size {len(T)}")
    else:
        print(f"UNSAT or unknown sat={sat} t={sec:.2f}s", flush=True)
        lines.append("no 368 in <=4-blocker Hamming-13")
    (HERE / "hamming13_sat_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
