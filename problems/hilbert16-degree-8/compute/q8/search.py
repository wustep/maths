#!/usr/bin/env python3
"""One process, bounded sign balls, atomic checkpoint after every flip.

Search all combinatorial flips, a superset of the regular flips. A discovery
is only a candidate; this driver never claims algebraic realizability.
"""
import argparse
from collections import Counter
import json
from math import comb
import subprocess
import time

from common import (HERE, PTS, atomic_json, baseline, code_scheme, digest,
                    plan, seeds, source_hashes, task_tris, unpack, write_task)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=str, default=str(HERE / 'certs/coverage.json'))
    ap.add_argument('--max-tasks', type=int, help='cap completed tasks, for a prefix')
    args = ap.parse_args()
    rows, seedlist = plan(), seeds()
    provenance = dict(radius=3, plan_sha256=digest(rows), seeds_sha256=digest(seedlist),
                      sources=source_hashes())
    path = HERE / args.output
    if path.exists():
        saved = json.loads(path.read_text())
        assert saved['provenance'] == provenance, 'checkpoint source/input mismatch'
        results = saved['tasks']
        assert len(results) <= len(rows)
    else:
        results = []
    work = HERE / 'work'
    work.mkdir(exist_ok=True)
    exe = work / 'ball'
    subprocess.run(['cc', '-O3', '-std=c11', '-Wall', '-Wextra',
                    str(HERE / 'ball.c'), '-o', str(exe)], check=True)
    expected = sum(comb(45, k) for k in range(4))
    known = baseline()
    start = time.monotonic()
    for idx in range(len(results), len(rows)):
        if args.max_tasks is not None and idx >= args.max_tasks:
            break
        row = rows[idx]
        tris = task_tris(row, seedlist[row['seed']])
        signs = unpack(seedlist[row['seed']])[2]
        task = work / 'task.txt'
        # The empty curve is not a new nonempty scheme.
        write_task(tris, signs, task, known=known | {'<>'})
        p = subprocess.run([str(exe), str(task), '3'], check=True,
                           capture_output=True, text=True)
        messages = [json.loads(line) for line in p.stdout.splitlines()]
        summaries = [m for m in messages if m['kind'] == 'summary']
        assert len(summaries) == 1
        summary = summaries[0]
        assert summary['complete'] and summary['evals'] == expected
        counts = {code_scheme(code): n for code, n in summary['counts']}
        assert len(counts) == len(summary['counts']) and sum(counts.values()) == expected
        candidates = [m for m in messages if m['kind'] == 'witness']
        novel = set(counts) - known - {'<>'}
        assert {code_scheme(m['code']) for m in candidates} == novel
        entry = dict(row, id=idx, complete=True, evals=expected, counts=counts,
                     candidates=candidates)
        results.append(entry)
        total = Counter()
        for r in results:
            total.update(r['counts'])
        saved = dict(provenance=provenance, planned_tasks=len(rows),
                     complete=len(results) == len(rows), tasks=results,
                     evaluations=sum(r['evals'] for r in results),
                     counts=dict(total), candidate_schemes=sorted(set(total)-known-{'<>'}))
        atomic_json(path, saved)
        if candidates or (idx + 1) % 25 == 0 or idx == 0 or idx + 1 == len(rows):
            print(f'{idx+1}/{len(rows)} tasks; {saved["evaluations"]} evaluations; '
                  f'{len(total)} schemes; {len(saved["candidate_schemes"])} candidates; '
                  f'{time.monotonic()-start:.1f}s this invocation', flush=True)
        if candidates:
            print('Candidate saved; pause for independent verification.', flush=True)
            return 3
    return 0 if len(results) == len(rows) else 2


if __name__ == '__main__':
    raise SystemExit(main())
