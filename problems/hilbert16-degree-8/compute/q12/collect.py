#!/usr/bin/env python3
"""Merge shard manifests and write a compact leftover-domain summary."""
from collections import Counter
import json
from math import comb
from pathlib import Path

from common import (HERE, LEFTOVER_PLAN_SHA, LEFTOVER_SEEDS_SHA, N_LEFTOVER,
                    atomic_json, baseline, canon, digest, leftover_plan,
                    leftover_seeds)


def load_shards(pattern):
    files = sorted(HERE.glob(pattern))
    out = []
    for path in files:
        saved = json.loads(path.read_text())
        out.append((path, saved))
    return out


def compact_task(t):
    return dict(id=t['id'], seed=t['seed'], removed=t['removed'], added=t['added'],
                triangulation_sha256=t['triangulation_sha256'], complete=t['complete'],
                evals=t['evals'], n_schemes=len(t['counts']),
                novel=t.get('novel', []), candidates=t.get('candidates', []))


def merge_leftover():
    rows = leftover_plan()
    seedlist = leftover_seeds()
    assert digest(rows) == LEFTOVER_PLAN_SHA
    assert digest(seedlist) == LEFTOVER_SEEDS_SHA
    expected_ids = list(range(len(rows)))
    assert len(expected_ids) == N_LEFTOVER
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    shards = load_shards('work/shard[0-9].json')
    by_id = {}
    total = Counter()
    for path, saved in shards:
        assert saved['provenance']['plan_sha256'] == LEFTOVER_PLAN_SHA
        assert saved['provenance']['seeds_sha256'] == LEFTOVER_SEEDS_SHA
        assert saved['provenance']['domain'] == 'q11-followup-leftover'
        assert saved['complete']
        for t in saved['tasks']:
            assert t['id'] not in by_id, f'duplicate task {t["id"]}'
            assert t['complete'] and t['evals'] == expected
            by_id[t['id']] = t
            total.update(t['counts'])
    missing = [i for i in expected_ids if i not in by_id]
    extra = sorted(set(by_id) - set(expected_ids))
    novel = sorted(set(total) - known - {'<>'})
    summary = dict(
        planned=len(expected_ids),
        complete=not missing and not extra,
        n_tasks=len(by_id),
        missing_ids=missing,
        extra_ids=extra,
        evaluations=sum(t['evals'] for t in by_id.values()),
        n_schemes=len(total),
        candidate_schemes=novel,
        shards=[str(p.relative_to(HERE)) for p, _ in shards],
    )
    compact = dict(summary, tasks=[compact_task(by_id[i]) for i in sorted(by_id)])
    atomic_json(HERE / 'certs/coverage_leftover.json', compact)
    return summary, novel


def merge_followup(exclude=()):
    known = baseline() | set(exclude)
    shards = load_shards('work/followup[0-9].json')
    if not shards:
        return dict(complete=False, n_tasks=0, candidate_schemes=[])
    expected = sum(comb(45, k) for k in range(4))
    by_id = {}
    total = Counter()
    extra_known = set()
    plan_sha = seeds_sha = None
    for path, saved in shards:
        assert saved['provenance']['domain'] == 'q12-certificate-flips'
        assert saved['complete']
        if plan_sha is None:
            plan_sha = saved['provenance']['plan_sha256']
            seeds_sha = saved['provenance']['seeds_sha256']
        else:
            assert saved['provenance']['plan_sha256'] == plan_sha
            assert saved['provenance']['seeds_sha256'] == seeds_sha
        extra_known |= set(saved['provenance'].get('extra_schemes', []))
        for t in saved['tasks']:
            assert t['id'] not in by_id, f'duplicate followup task {t["id"]}'
            assert t['complete'] and t['evals'] == expected
            by_id[t['id']] = t
            total.update(t['counts'])
    novel = sorted(set(total) - known - extra_known - {'<>'})
    summary = dict(planned=len(by_id), complete=True, n_tasks=len(by_id),
                   evaluations=sum(t['evals'] for t in by_id.values()),
                   n_schemes=len(total), candidate_schemes=novel,
                   shards=[str(p.relative_to(HERE)) for p, _ in shards])
    compact = dict(summary, tasks=[compact_task(by_id[i]) for i in sorted(by_id)])
    atomic_json(HERE / 'certs/coverage_followup.json', compact)
    return summary


def main():
    leftover, novel = merge_leftover()
    followup = merge_followup(exclude=novel)
    cert_path = HERE / 'certs/new_schemes.json'
    schemes = []
    if cert_path.exists():
        schemes = [canon(c['scheme']) for c in json.loads(cert_path.read_text())]
        assert set(schemes) == set(novel) | set(followup.get('candidate_schemes', []))
    out = dict(leftover=leftover, followup=followup,
               q11_claim='../q11/CLAIM.md',
               baseline=2415,
               n_new=len(schemes),
               bound=2415 + len(schemes),
               schemes=schemes,
               candidate_schemes=sorted(set(novel) | set(followup.get('candidate_schemes', []))))
    atomic_json(HERE / 'certs/summary.json', out)
    print(json.dumps(out, indent=2, sort_keys=True))
    if leftover['complete'] and not out['candidate_schemes']:
        print('RESIDUE: leftover domain finished with no scheme outside the 2,415.')
        return 2
    if out['candidate_schemes']:
        print('Candidates:', out['candidate_schemes'])
        cert = HERE / 'certs/new_schemes.json'
        if not cert.exists():
            print('Candidates recorded; lift and write certs/new_schemes.json before run_all.sh')
            return 3
    return 0 if leftover['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
