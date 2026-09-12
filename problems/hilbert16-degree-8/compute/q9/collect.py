#!/usr/bin/env python3
"""Merge shard manifests and write a compact remaining-domain summary."""
from collections import Counter
import json
from math import comb
from pathlib import Path

from common import (HERE, Q8_PLAN_SHA, Q8_SEEDS_SHA, REMAINING_START,
                    REMAINING_STOP, atomic_json, baseline, digest, extra_plan,
                    plan, seeds)


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


def merge_remaining():
    rows = plan()
    assert digest(rows) == Q8_PLAN_SHA
    assert digest(seeds()) == Q8_SEEDS_SHA
    expected_ids = list(range(REMAINING_START, REMAINING_STOP))
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    shards = load_shards('work/shard[0-9].json')
    by_id = {}
    total = Counter()
    for path, saved in shards:
        assert saved['provenance']['plan_sha256'] == Q8_PLAN_SHA
        assert saved['provenance']['seeds_sha256'] == Q8_SEEDS_SHA
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
        planned_remaining=len(expected_ids),
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
    atomic_json(HERE / 'certs/coverage_remaining.json', compact)
    return summary, novel, by_id


def merge_extra():
    rows = extra_plan()
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    path = HERE / 'work/shardE.json'
    if not path.exists():
        return dict(complete=False, n_tasks=0)
    saved = json.loads(path.read_text())
    assert saved['provenance']['domain'] == 'q8-certificate-flips'
    assert saved['complete']
    assert len(saved['tasks']) == len(rows)
    total = Counter()
    for t in saved['tasks']:
        assert t['complete'] and t['evals'] == expected
        total.update(t['counts'])
    novel = sorted(set(total) - known - {'<>'})
    summary = dict(planned=len(rows), complete=True, n_tasks=len(saved['tasks']),
                   evaluations=saved['evaluations'], n_schemes=len(total),
                   candidate_schemes=novel)
    compact = dict(summary, tasks=[compact_task(t) for t in saved['tasks']])
    atomic_json(HERE / 'certs/coverage_extra.json', compact)
    return summary


def main():
    remaining, novel, _ = merge_remaining()
    extra = merge_extra()
    out = dict(remaining=remaining, extra=extra,
               q8_claim='../q8/CLAIM.md',
               baseline=2385,
               candidate_schemes=sorted(set(novel) | set(extra.get('candidate_schemes', []))))
    atomic_json(HERE / 'certs/summary.json', out)
    print(json.dumps(out, indent=2, sort_keys=True))
    if remaining['complete'] and extra.get('complete') and not out['candidate_schemes']:
        print('RESIDUE: both recorded domains finished with no scheme outside the 2,385.')
        return 2
    if out['candidate_schemes']:
        print('Candidates:', out['candidate_schemes'])
        cert = HERE / 'certs/new_schemes.json'
        if not cert.exists():
            print('Candidates recorded; lift and write certs/new_schemes.json before run_all.sh')
            return 3
    return 0 if remaining['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
