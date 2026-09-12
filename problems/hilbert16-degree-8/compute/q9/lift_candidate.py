#!/usr/bin/env python3
"""Find a lifting for a recorded candidate; exact checks decide acceptance.

Discovery may use SciPy. Replaying a committed certificate needs no
numerical package. LP failure is not algebraic exclusion.
"""
import argparse
from fractions import Fraction
import json
from math import lcm
from pathlib import Path
import sys

from common import (HERE, PTS, atomic_json, baseline, canon, cert_plan,
                    cert_seeds, code_scheme, extra_plan, extra_seeds, plan,
                    seeds, task_tris)
from haas import convexity_rows, regularize
from verify import build_rust, verify_new


def heights_from_vector(h):
    return {f'{x},{y}': int(v) for (x, y), v in zip(PTS, h)}


def try_regularize(tris, nseed=40):
    for seed in range(nseed):
        got = regularize(tris, iters=200000, seed=seed)
        if got is not None:
            return {f'{x},{y}': int(h) for (x, y), h in got.items()}
    return None


def try_linprog(tris):
    try:
        from scipy.optimize import linprog
    except ImportError:
        return None
    rows = convexity_rows(tris)
    sol = linprog([0] * 45, A_ub=[[-v for v in r] for r in rows],
                  b_ub=[-1] * len(rows), method='highs',
                  bounds=[(0, 0) if p in ((0, 0), (8, 0), (0, 8)) else (None, None)
                          for p in PTS])
    if not sol.success:
        print('No lifting obtained: ' + sol.message, flush=True)
        return None
    h = [Fraction(float(v)).limit_denominator(10 ** 6) for v in sol.x]
    scale = lcm(*(v.denominator for v in h))
    return {f'{x},{y}': int(v * scale) for (x, y), v in zip(PTS, h)}


def load_row(task, extra, certs=None):
    if certs:
        rows, seedlist = cert_plan(certs, source_prefix='q9 addition: '), cert_seeds(certs, source_prefix='q9 addition: ')
    elif extra:
        rows, seedlist = extra_plan(), extra_seeds()
    else:
        rows, seedlist = plan(), seeds()
    row = rows[task]
    seed = seedlist[row['seed']]
    tris = task_tris(row, seed)
    return row, seed, tris


def certificate(tris, heights, bits, scheme, source):
    return dict(
        degree=8, scheme=scheme, triangles=tris, heights=heights,
        signs={f'{x},{y}': (-1 if bits >> i & 1 else 1)
               for i, (x, y) in enumerate(PTS)},
        source=source,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--task', type=int, required=True)
    ap.add_argument('--extra', action='store_true')
    ap.add_argument('--certs', type=str)
    ap.add_argument('--shard', type=str, help='shard JSON containing the task')
    ap.add_argument('--output', default=str(HERE / 'work/lifted_candidate.json'))
    args = ap.parse_args()
    cpath = None
    if args.certs:
        cpath = Path(args.certs)
        if not cpath.is_absolute():
            cpath = HERE / cpath
    row, seed, tris = load_row(args.task, args.extra, certs=cpath)
    candidates = None
    if args.shard:
        saved = json.loads(Path(args.shard).read_text())
        match = [t for t in saved['tasks'] if t['id'] == args.task]
        assert len(match) == 1
        candidates = match[0]['candidates']
    else:
        path = HERE / 'certs/candidates.jsonl'
        recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        want = 'q9-certificate-flips' if args.certs else (
            'q8-certificate-flips' if args.extra else 'q8-remaining')
        match = [r for r in recs if r['id'] == args.task and r.get('domain') == want]
        assert match, 'no candidate record for this task'
        candidates = match[-1]['candidates']
    heights = try_linprog(tris)
    method = 'scipy-highs'
    if heights is None:
        heights = try_regularize(tris)
        method = 'agmon-motzkin'
    if heights is None:
        print('No lifting obtained by LP or projection.', flush=True)
        return 2
    exe = build_rust()
    certs = []
    known = baseline()
    for m in candidates:
        scheme = code_scheme(m['code'])
        if scheme in known or scheme == '<>':
            continue
        c = certificate(tris, heights, m['bits'], scheme, dict(
            seed=seed.get('source', seed.get('scheme')), task=args.task,
            removed=row['removed'], added=row['added'], lifting=method,
            extra=bool(args.extra)))
        print('Exact independent checks:', verify_new(c, exe), flush=True)
        certs.append(c)
    assert certs, 'task has no new nonempty witnesses after lifting'
    atomic_json(args.output, certs)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
