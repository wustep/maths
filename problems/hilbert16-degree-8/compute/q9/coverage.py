#!/usr/bin/env python3
"""Audit the compact remaining-domain and extra-domain summaries."""
import json
from math import comb
from pathlib import Path

from common import (HERE, Q8_PLAN_SHA, Q8_SEEDS_SHA, REMAINING_START,
                    REMAINING_STOP, baseline, digest, extra_plan, plan, seeds)


def main():
    rows, seedlist = plan(), seeds()
    assert digest(rows) == Q8_PLAN_SHA and digest(seedlist) == Q8_SEEDS_SHA
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    saved = json.loads((HERE / 'certs/coverage_remaining.json').read_text())
    assert saved['complete'] and not saved['missing_ids'] and not saved['extra_ids']
    assert saved['planned_remaining'] == REMAINING_STOP - REMAINING_START == 1108
    assert len(saved['tasks']) == 1108
    assert saved['evaluations'] == 1108 * expected
    ids = [t['id'] for t in saved['tasks']]
    assert ids == list(range(REMAINING_START, REMAINING_STOP))
    novel = set()
    for i, t in enumerate(saved['tasks']):
        row = rows[t['id']]
        assert t['id'] == REMAINING_START + i
        assert t['seed'] == row['seed']
        assert t['complete'] and t['evals'] == expected
        assert t['n_schemes'] > 0
        for k in ('removed', 'added', 'triangulation_sha256'):
            assert digest(t[k]) == digest(row[k])
        assert set(t['novel']).isdisjoint(known) and '<>' not in t['novel']
        novel.update(t['novel'])
        assert {code_scheme_from_candidate(m) for m in t['candidates']} == set(t['novel'])
    assert sorted(novel) == saved['candidate_schemes']
    extra = json.loads((HERE / 'certs/coverage_extra.json').read_text())
    erows = extra_plan()
    assert extra['complete'] and extra['n_tasks'] == len(erows) == 21
    assert extra['evaluations'] == 21 * expected
    print(f'Coverage audit: remaining {saved["n_tasks"]}/1108, extra {extra["n_tasks"]}/21, '
          f'{saved["evaluations"] + extra["evaluations"]} evaluations, '
          f'{len(saved["candidate_schemes"])} candidate schemes', flush=True)
    return 0


def code_scheme_from_candidate(m):
    from common import code_scheme
    return code_scheme(m['code'])


if __name__ == '__main__':
    raise SystemExit(main())
