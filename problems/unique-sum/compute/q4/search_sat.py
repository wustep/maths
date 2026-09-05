#!/usr/bin/env python3
"""Cardinality SAT with affine lexicographic symmetry breaking.

Uses the q2 pair-variable encoding. A lexicographically maximal membership
word in an affine orbit survives every added comparison. Ordering residues
as 0,1,-1,2,-2,... means that this representative contains 0,1,-1 whenever
the set contains a nontrivial progression. Comparisons may be truncated:
every full maximum still survives. No existence monotonicity is assumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
from time import monotonic

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from search_green_m_p import assert_admissible, build_exact_cnf


def formula(p: int, bound: int, depth: int, atmost: bool):
    cnf, selected, pool = build_exact_cnf(p, bound)
    if atmost:
        # Reuse precisely the predicate and root clauses from the producer.
        # Its cardinality encoding occupies the suffix before the three units.
        pair_clause_count = 3 * p * (p - 1) // 2 + p * (p + 1) // 2
        cnf.clauses = cnf.clauses[:pair_clause_count] + cnf.clauses[-3:]
        cnf.extend(CardEnc.atmost(selected, bound=bound, vpool=pool,
                                 encoding=EncType.seqcounter).clauses)
    order = [0]
    for value in range(1, (p + 1) // 2):
        order.extend([value, p - value])
    for multiplier in range(1, p):
        for translation in range(p):
            if multiplier == 1 and translation == 0:
                continue
            previous = None
            for residue in order[:depth]:
                left = selected[residue]
                right = selected[(multiplier * residue + translation) % p]
                if left == right:
                    continue
                guard = [] if previous is None else [-previous]
                cnf.append([*guard, left, -right])
                equal = pool.id()
                # Equal prefixes force the next guard; a strict advantage can
                # set it false and ends this comparison.
                cnf.append([*guard, -left, -right, equal])
                cnf.append([*guard, left, right, equal])
                previous = equal
    return cnf, selected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('p', type=int)
    ap.add_argument('bound', type=int)
    ap.add_argument('--depth', type=int, default=12)
    ap.add_argument('--atmost', action='store_true')
    ap.add_argument('--conflicts', type=int, default=1000000)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--dimacs', type=Path)
    args = ap.parse_args()
    if (args.p < 3 or args.p % 2 == 0 or any(args.p % n == 0 for n in range(2, int(args.p**0.5)+1))
            or not 0 <= args.depth <= args.p or args.conflicts < 1):
        ap.error('require an odd prime, 0 <= depth <= p, positive conflicts')
    # Hard per-process virtual-memory ceiling, comfortably below 2 GiB RSS.
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))
    start = monotonic()
    cnf, selected = formula(args.p, args.bound, args.depth, args.atmost)
    if args.dimacs:
        cnf.to_file(str(args.dimacs))
    digest = hashlib.sha256(cnf.to_dimacs().encode()).hexdigest()
    print(f'built variables={cnf.nv} clauses={len(cnf.clauses)} sha256={digest}', flush=True)
    with Solver(name=args.solver, bootstrap_with=cnf) as solver:
        solver.conf_budget(args.conflicts)
        result = solver.solve_limited()
        witness = None
        if result:
            positive = set(solver.get_model())
            witness = [i for i, variable in enumerate(selected) if variable in positive]
            assert_admissible(args.p, witness)
            assert len(witness) <= args.bound
            if not args.atmost:
                assert len(witness) == args.bound
        report = dict(p=args.p, bound=args.bound, atmost=args.atmost,
                      depth=args.depth, solver=args.solver,
                      conflict_budget=args.conflicts,
                      status='SAT' if result else 'UNKNOWN' if result is None else 'UNSAT',
                      witness=witness, statistics=solver.accum_stats(),
                      cnf_sha256=digest, variables=cnf.nv, clauses=len(cnf.clauses),
                      seconds=monotonic()-start,
                      max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)
    return 3 if result is None else 0


if __name__ == '__main__':
    raise SystemExit(main())
