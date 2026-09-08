#!/usr/bin/env python3
"""Audit the saved finite-domain manifest; optional fresh exhaustive replay.

This checks search coverage, not q8/CLAIM.md. With --replay, no saved
histogram is trusted: the entire domain is regenerated and recomputed.
"""
import argparse
from collections import Counter
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile

from common import (HERE, baseline, canon, code_scheme, digest, plan, seeds,
                    source_hashes, task_tris, unpack)
from tcurve import TCurve, validate_triangulation


def audit(path):
    saved = json.loads(Path(path).read_text())
    rows, seedlist = plan(), seeds()
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
        assert saved['complete'], 'full replay requires a completed manifest'
        with tempfile.TemporaryDirectory(prefix='h16-q8-replay-') as tmp:
            path = Path(tmp) / 'coverage.json'
            subprocess.run([sys.executable, str(HERE/'search.py'), '--output', str(path)],check=True)
            assert json.loads(path.read_text()) == saved, 'fresh exhaustive replay differs'
        print('PASS: fresh exhaustive replay matches every saved frequency')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
