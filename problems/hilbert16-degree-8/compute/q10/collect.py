#!/usr/bin/env python3
"""Merge shard manifests and write a compact leftover-domain summary."""
from collections import Counter
import json
from math import comb
from pathlib import Path

from common import (HERE, LEFTOVER_PLAN_SHA, LEFTOVER_SEEDS_SHA, atomic_json,
                    baseline, digest, leftover_plan, leftover_seeds)


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
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    shards = load_shards('work/shard[0-9].json')
    by_id = {}
    total = Counter()
    for path, saved in shards:
        assert saved['provenance']['plan_sha256'] == LEFTOVER_PLAN_SHA
        assert saved['provenance']['seeds_sha256'] == LEFTOVER_SEEDS_SHA
        assert saved['provenance']['domain'] == 'q9-followup-leftover'
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


def merge_followup():
    known = baseline()
    path = HERE / 'work/followup.json'
    if not path.exists():
        return dict(complete=False, n_tasks=0, candidate_schemes=[])
    saved = json.loads(path.read_text())
    expected = sum(comb(45, k) for k in range(4))
    assert saved['provenance']['domain'] == 'q10-certificate-flips'
    assert saved['complete']
    total = Counter()
    for t in saved['tasks']:
        assert t['complete'] and t['evals'] == expected
        total.update(t['counts'])
    extra_known = set(saved['provenance'].get('extra_schemes', []))
    novel = sorted(set(total) - known - extra_known - {'<>'})
    summary = dict(planned=len(saved['tasks']), complete=True, n_tasks=len(saved['tasks']),
                   evaluations=saved['evaluations'], n_schemes=len(total),
                   candidate_schemes=novel)
    compact = dict(summary, tasks=[compact_task(t) for t in saved['tasks']])
    atomic_json(HERE / 'certs/coverage_followup.json', compact)
    return summary


def main():
    leftover, novel = merge_leftover()
    followup = merge_followup()
    out = dict(leftover=leftover, followup=followup,
               q9_claim='../q9/CLAIM.md',
               baseline=2394,
               candidate_schemes=sorted(set(novel) | set(followup.get('candidate_schemes', []))))
    atomic_json(HERE / 'certs/summary.json', out)
    print(json.dumps(out, indent=2, sort_keys=True))
    if leftover['complete'] and not out['candidate_schemes']:
        print('RESIDUE: leftover domain finished with no scheme outside the 2,394.')
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
