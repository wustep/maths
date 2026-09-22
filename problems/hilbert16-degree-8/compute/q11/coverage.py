#!/usr/bin/env python3
"""Audit the compact leftover-domain summary against the recorded plan."""
import json
from math import comb

from common import (HERE, LEFTOVER_PLAN_SHA, LEFTOVER_SEEDS_SHA, N_LEFTOVER,
                    baseline, digest, leftover_plan, leftover_seeds)


def main():
    rows, seedlist = leftover_plan(), leftover_seeds()
    assert digest(rows) == LEFTOVER_PLAN_SHA and digest(seedlist) == LEFTOVER_SEEDS_SHA
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    saved = json.loads((HERE / 'certs/coverage_leftover.json').read_text())
    assert saved['complete'] and not saved['missing_ids'] and not saved['extra_ids']
    assert saved['planned'] == len(rows) == N_LEFTOVER
    assert len(saved['tasks']) == N_LEFTOVER
    assert saved['evaluations'] == N_LEFTOVER * expected
    ids = [t['id'] for t in saved['tasks']]
    assert ids == list(range(N_LEFTOVER))
    novel = set()
    for i, t in enumerate(saved['tasks']):
        row = rows[t['id']]
        assert t['id'] == i
        assert t['seed'] == row['seed']
        assert t['complete'] and t['evals'] == expected
        assert t['n_schemes'] > 0
        for k in ('removed', 'added', 'triangulation_sha256'):
            assert digest(t[k]) == digest(row[k])
        assert set(t['novel']).isdisjoint(known) and '<>' not in t['novel']
        novel.update(t['novel'])
        assert {code_scheme_from_candidate(m) for m in t['candidates']} == set(t['novel'])
    assert sorted(novel) == saved['candidate_schemes']
    print(f'Coverage audit: leftover {saved["n_tasks"]}/{N_LEFTOVER}, '
          f'{saved["evaluations"]} evaluations, '
          f'{len(saved["candidate_schemes"])} candidate schemes', flush=True)
    followup_path = HERE / 'certs/coverage_followup.json'
    if followup_path.exists():
        extra = json.loads(followup_path.read_text())
        assert extra['complete']
        print(f'Followup audit: {extra["n_tasks"]} tasks, {extra["evaluations"]} evaluations, '
              f'{len(extra.get("candidate_schemes", []))} candidate schemes', flush=True)
    return 0


def code_scheme_from_candidate(m):
    from common import code_scheme
    return code_scheme(m['code'])


if __name__ == '__main__':
    raise SystemExit(main())
