#!/usr/bin/env python3
"""Few-flip SAT around the published 367-set.

Stolen from the W(2,7) sibling: Cadical on a small Hamming ball around a
published seed, with pysat.card.CardEnc.atmost (no homemade counters).

A 368-set T at Hamming distance d=2r+1 from the seed removes r vertices and
adds r+1. Candidates to add are vertices adjacent to at most r seed points.
"""

from __future__ import annotations

import argparse
import time
from collections import Counter
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Cadical195

from c7_common import NVERTS, adjacent, closed_neighbors, format_word
from verify_set import first_conflict, load_set

HERE = Path(__file__).resolve().parent
ENC = EncType.kmtotalizer


def atmost(lits: list[int], bound: int, top_id: int) -> tuple[list[list[int]], int]:
    """Library at-most-k. Empty/trivial cases avoid CardEnc edge bugs."""
    if bound < 0:
        return [[1], [-1]], top_id  # UNSAT
    if not lits or bound >= len(lits):
        return [], top_id
    if bound == 0:
        return [[-x] for x in lits], top_id
    cnf = CardEnc.atmost(lits=lits, bound=bound, top_id=top_id, encoding=ENC)
    return list(cnf.clauses), cnf.nv


def exactly(lits: list[int], k: int, top_id: int) -> tuple[list[list[int]], int]:
    """Exactly-k via two at-most constraints (no one-way atleast gadget)."""
    if k < 0 or k > len(lits):
        return [[1], [-1]], top_id
    clauses, top_id = atmost(lits, k, top_id)
    more, top_id = atmost([-x for x in lits], len(lits) - k, top_id)
    clauses.extend(more)
    return clauses, top_id


def atleast(lits: list[int], k: int, top_id: int) -> tuple[list[list[int]], int]:
    """At-least-k as at-most on the negated literals."""
    return atmost([-x for x in lits], len(lits) - k, top_id)


def seed_blockers(seed: list[int]) -> list[list[int]]:
    """blockers[v] = indices of seed vertices whose closed neighbourhood contains v."""
    index = {s: i for i, s in enumerate(seed)}
    blockers: list[list[int]] = [[] for _ in range(NVERTS)]
    for i, s in enumerate(seed):
        for u in closed_neighbors(s):
            if u in index:
                continue
            blockers[u].append(i)
    return blockers


def solve_r(
    seed: list[int],
    blockers: list[list[int]],
    r: int,
    k: int,
    time_limit: int,
) -> tuple[str, list[int] | None, dict]:
    seed_set = set(seed)
    cands = [v for v in range(NVERTS) if v not in seed_set and 0 < len(blockers[v]) <= r]
    free = [v for v in range(NVERTS) if v not in seed_set and len(blockers[v]) == 0]
    stats = {"r": r, "k": k, "cands": len(cands), "free": len(free)}
    if r == 0:
        if not free:
            return "UNSAT", None, stats
        cands = free
    if r + 1 > len(cands) + len(free):
        return "UNSAT", None, stats

    rem = list(range(1, len(seed) + 1))
    add_map = {}
    vid = len(seed)
    pool = cands if r > 0 else free
    if r > 0:
        pool = cands
    for v in pool:
        vid += 1
        add_map[v] = vid
    add_lits = list(add_map.values())
    top_id = vid
    cnf = CNF()

    # Independence: adding v requires deleting every seed neighbour.
    for v, lit in add_map.items():
        for i in blockers[v]:
            cnf.append([-lit, rem[i]])

    # Independence among added vertices.
    add_verts = list(add_map)
    for i, u in enumerate(add_verts):
        for v in add_verts[i + 1 :]:
            if adjacent(u, v):
                cnf.append([-add_map[u], -add_map[v]])

    # |removed| = r, |added| >= r+1, |added| <= k-r. All via CardEnc.atmost.
    extra, top_id = exactly(rem, r, top_id)
    cnf.extend(extra)
    extra, top_id = atleast(add_lits, r + 1, top_id)
    cnf.extend(extra)
    extra, top_id = atmost(add_lits, k - r, top_id)
    cnf.extend(extra)

    stats["clauses"] = len(cnf.clauses)
    stats["vars"] = top_id
    solver = Cadical195(bootstrap_with=cnf.clauses)
    t0 = time.time()
    sat = solver.solve()
    if time.time() - t0 > time_limit and sat is None:
        sat = None
    stats["seconds"] = time.time() - t0
    if sat is None:
        return "UNKNOWN", None, stats
    if not sat:
        return "UNSAT", None, stats
    model = set(solver.get_model())
    kept = [seed[i] for i, lit in enumerate(rem) if -lit in model or lit not in model]
    # rem lit true means removed
    kept = [seed[i] for i, lit in enumerate(rem) if lit not in model]
    added = [v for v, lit in add_map.items() if lit in model]
    T = sorted(set(kept) | set(added))
    return "SAT", T, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-set", type=Path, default=HERE / "R367.txt")
    ap.add_argument("--k-max", type=int, default=11)
    ap.add_argument("--time-limit", type=int, default=90)
    args = ap.parse_args()
    seed = load_set(args.seed_set)
    assert len(seed) == len(set(seed)) == 367
    print(f"seed {args.seed_set} size={len(seed)}", flush=True)
    blockers = seed_blockers(seed)
    hist = Counter(len(blockers[v]) for v in range(NVERTS) if v not in set(seed))
    print("blocker_histogram", dict(sorted(hist.items())[:20]), flush=True)
    print(f"free_vertices={hist.get(0, 0)}", flush=True)

    lines = [
        f"seed {args.seed_set} size {len(seed)}",
        f"free {hist.get(0, 0)}",
        f"encoding CardEnc.atmost kmtotalizer (atleast via negated atmost)",
    ]
    found = None
    # odd Hamming distances 1,3,...,k_max
    for k in range(1, args.k_max + 1, 2):
        rmax = (k - 1) // 2
        print(f"=== Hamming <= {k} (r <= {rmax}) ===", flush=True)
        k_status = "UNSAT"
        for r in range(0, rmax + 1):
            status, T, stats = solve_r(seed, blockers, r, k, args.time_limit)
            msg = (
                f"k={k} r={r} {status} cands={stats['cands']} free={stats['free']} "
                f"clauses={stats.get('clauses', 0)} vars={stats.get('vars', 0)} "
                f"sec={stats.get('seconds', 0):.2f}"
            )
            print(msg, flush=True)
            lines.append(msg)
            if status == "SAT" and T is not None:
                if first_conflict(T) is not None:
                    raise SystemExit("SAT model is adjacent")
                found = T
                k_status = f"SAT size={len(T)}"
                out = HERE / f"R{len(T)}_fewflip.txt"
                out.write_text("\n".join(format_word(v) for v in T) + "\n")
                print(f"WROTE {out}", flush=True)
                lines.append(f"wrote {out}")
                break
            if status == "UNKNOWN":
                k_status = "UNKNOWN"
        lines.append(f"k={k} summary {k_status}")
        if found is not None:
            break
        if k_status == "UNKNOWN":
            break

    if found is None:
        lines.append("no 368-set in completed few-flip balls")
        print("no 368-set in completed few-flip balls")
    (HERE / "fewflip_sat_log.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
