#!/usr/bin/env python3
"""Find a lifting for a recorded candidate; exact checks decide acceptance.

This optional discovery step uses NumPy/SciPy. Replaying the committed
certificate needs neither package. LP failure is not algebraic exclusion.
"""
import argparse
from fractions import Fraction
import json
from math import lcm

from common import HERE, PTS, atomic_json, code_scheme, seeds, task_tris
from haas import convexity_rows
from verify import build_rust, verify_new


def main():
    from scipy.optimize import linprog
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--task', type=int, default=81)
    ap.add_argument('--output', default=str(HERE / 'work/lifted_candidate.json'))
    args = ap.parse_args()
    saved = json.loads((HERE / 'certs/coverage.json').read_text())
    row = saved['tasks'][args.task]
    assert row['id'] == args.task
    seed = seeds()[row['seed']]
    tris = task_tris(row, seed)
    rows = convexity_rows(tris)
    sol = linprog([0]*45, A_ub=[[-v for v in r] for r in rows],
                  b_ub=[-1]*len(rows), method='highs',
                  bounds=[(0,0) if p in ((0,0),(8,0),(0,8)) else (None,None)
                          for p in PTS])
    if not sol.success:
        print('No lifting obtained: ' + sol.message)
        return 2
    h = [Fraction(float(v)).limit_denominator(10**6) for v in sol.x]
    scale = lcm(*(v.denominator for v in h))
    heights = {f'{x},{y}': int(v*scale) for (x,y),v in zip(PTS,h)}
    exe = build_rust()
    certs = []
    for m in row['candidates']:
        c = dict(degree=8, scheme=code_scheme(m['code']), triangles=tris,
                 heights=heights,
                 signs={f'{x},{y}': (-1 if m['bits']>>i&1 else 1)
                        for i,(x,y) in enumerate(PTS)},
                 source=dict(seed=seed['source'], task=row['id'],
                             removed=row['removed'], added=row['added']))
        print('Exact independent checks:', verify_new(c, exe))
        certs.append(c)
    assert certs, 'task has no candidate witnesses'
    atomic_json(args.output, certs)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
