#!/usr/bin/env python3
"""Audit the saved finite-domain manifest; optional fresh exhaustive replay.

This checks search coverage, not q8/CLAIM.md. With --replay, no saved
histogram is trusted: the entire domain is regenerated and recomputed.
"""
import argparse
from collections import Counter
from itertools import combinations
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile

from common import (HERE, baseline, canon, code_scheme, digest, plan, seeds,
                    source_hashes, task_tris, unpack)
from tcurve import TCurve, validate_triangulation


def check_flip_domain(rows, seedlist):
    """Separate pair-of-triangles enumeration using crossing determinants."""
    def det(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    actual = set()
    for i, seed in enumerate(seedlist):
        tris = unpack(seed)[0]
        for t,u in combinations(tris,2):
            shared = set(t)&set(u)
            if len(shared) != 2:
                continue
            a,b = sorted(shared)
            c, = set(t)-shared
            d, = set(u)-shared
            if det(a,b,c)*det(a,b,d)<0 and det(c,d,a)*det(c,d,b)<0:
                assert abs(det(a,c,d)) == abs(det(b,c,d)) == 1
                actual.add((i, (a,b), tuple(sorted((c,d)))))
    planned = {(r['seed'], tuple(map(tuple,r['removed'])), tuple(map(tuple,r['added'])))
               for r in rows}
    assert len(planned)==len(rows) and planned==actual, 'flip domain mismatch'


def audit(path):
    saved = json.loads(Path(path).read_text())
    rows, seedlist = plan(), seeds()
    check_flip_domain(rows, seedlist)
    assert saved['provenance'] == dict(radius=3, plan_sha256=digest(rows),
                                      seeds_sha256=digest(seedlist), sources=source_hashes())
    assert saved['planned_tasks'] == len(rows)
    assert len(saved['tasks']) <= len(rows)
    assert saved['complete'] == (len(saved['tasks'])==len(rows))
    expected = sum(comb(45,k) for k in range(4))
    total = Counter()
    for i, result in enumerate(saved['tasks']):
        row = rows[i]
        assert result['id'] == i
        for k, value in row.items():
            assert digest(result[k]) == digest(value)
        assert result['complete'] and result['evals'] == expected
        assert sum(result['counts'].values()) == expected
        assert all(type(n) is int and n>0 for n in result['counts'].values())
        assert all(canon(s)==s for s in result['counts'])
        tris = task_tris(row, seedlist[row['seed']])
        assert not validate_triangulation(8,tris)
        signs = unpack(seedlist[row['seed']])[2]
        assert TCurve(8,tris,signs).scheme() in result['counts']
        novel = set(result['counts']) - baseline() - {'<>'}
        assert {code_scheme(m['code']) for m in result['candidates']} == novel
        total.update(result['counts'])
    assert dict(total) == saved['counts']
    assert sum(total.values()) == saved['evaluations'] == len(saved['tasks'])*expected
    assert sorted(set(total)-baseline()-{'<>'}) == saved['candidate_schemes']
    print(f'Coverage audit: {len(saved["tasks"])}/{len(rows)} balls, '
          f'{saved["evaluations"]} evaluations, {len(total)} schemes, '
          f'{len(saved["candidate_schemes"])} candidate schemes',flush=True)
    return saved


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--replay', action='store_true')
    ap.add_argument('--manifest', default=str(HERE / 'certs/coverage.json'))
    args = ap.parse_args()
    saved = audit(args.manifest)
    if args.replay:
        with tempfile.TemporaryDirectory(prefix='h16-q8-replay-') as tmp:
            path = Path(tmp) / 'coverage.json'
            p = subprocess.run([sys.executable, str(HERE/'search.py'), '--output', str(path),
                                '--max-tasks', str(len(saved['tasks']))])
            assert p.returncode in (0,2,3), 'search replay failed'
            assert json.loads(path.read_text()) == saved, 'fresh exhaustive replay differs'
        print('PASS: fresh replay of the recorded domain matches every saved frequency')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
