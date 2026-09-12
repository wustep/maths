#!/usr/bin/env python3
"""Bounded sign balls on a recorded range of the q8 flip plan.

Does not stop on a candidate: every assigned ball is finished. A discovery
is only a candidate; this driver never claims algebraic realizability.
"""
import argparse
from collections import Counter
import fcntl
import json
from math import comb
from pathlib import Path
import subprocess
import time

from common import (HERE, Q8_PLAN_SHA, Q8_SEEDS_SHA, atomic_json,
                    baseline, canon, cert_plan, cert_seeds, code_scheme,
                    digest, extra_plan, extra_seeds, plan, seeds,
                    source_hashes, task_tris, unpack, write_task)


def append_jsonl(path, rec):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(rec, sort_keys=True) + '\n'
    with open(path, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)
        f.flush()


def parse_ids(args, nplan):
    if args.ids:
        text = Path(args.ids).read_text() if Path(args.ids).exists() and not args.ids[0].isdigit() else args.ids
        ids = []
        for part in text.replace(',', ' ').split():
            if '-' in part:
                a, b = map(int, part.split('-', 1))
                ids.extend(range(a, b + 1))
            else:
                ids.append(int(part))
        return ids
    start = args.start
    stop = args.stop
    assert 0 <= start < stop <= nplan
    return list(range(start, stop))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=str, required=True)
    ap.add_argument('--start', type=int, default=82)
    ap.add_argument('--stop', type=int, default=1190)
    ap.add_argument('--ids', type=str, help='comma/space IDs or a file of IDs')
    ap.add_argument('--extra', action='store_true',
                    help='search one-flip balls of the q8 certificate')
    ap.add_argument('--certs', type=str,
                    help='search one-flip balls of certificates in this JSON')
    ap.add_argument('--radius', type=int, default=3)
    args = ap.parse_args()
    assert args.radius == 3, 'this campaign records radius 3 only'
    extra_known = set()
    if args.certs:
        cpath = Path(args.certs)
        if not cpath.is_absolute():
            cpath = HERE / cpath
        rows, seedlist = cert_plan(cpath, source_prefix='q9 addition: '), cert_seeds(cpath, source_prefix='q9 addition: ')
        domain = 'q9-certificate-flips'
        extra_known = {canon(c['scheme']) for c in seedlist}
    elif args.extra:
        rows, seedlist = extra_plan(), extra_seeds()
        domain = 'q8-certificate-flips'
    else:
        rows, seedlist = plan(), seeds()
        domain = 'q8-remaining'
        assert digest(rows) == Q8_PLAN_SHA
        assert digest(seedlist) == Q8_SEEDS_SHA
    provenance = dict(radius=args.radius, domain=domain,
                      plan_sha256=digest(rows), seeds_sha256=digest(seedlist),
                      sources=source_hashes())
    path = Path(args.output)
    if not path.is_absolute():
        path = HERE / path
    if args.start > len(rows):
        args.start = len(rows)
    if args.stop > len(rows):
        args.stop = len(rows)
    ids = parse_ids(args, len(rows))
    for i in ids:
        assert 0 <= i < len(rows)
    if path.exists():
        saved = json.loads(path.read_text())
        assert saved['provenance'] == provenance, 'checkpoint source/input mismatch'
        results = saved['tasks']
        done = {r['id'] for r in results}
        assert done <= set(ids)
    else:
        results, done = [], set()
    work = HERE / 'work'
    work.mkdir(exist_ok=True)
    exe = work / 'ball'
    if not exe.exists():
        subprocess.run(['cc', '-O3', '-std=c11', '-Wall', '-Wextra',
                        str(HERE / 'ball.c'), '-o', str(exe)], check=True)
    expected = sum(comb(45, k) for k in range(4))
    known = baseline() | extra_known
    start = time.monotonic()
    cand_path = HERE / 'certs/candidates.jsonl'
    for idx in ids:
        if idx in done:
            continue
        row = rows[idx]
        tris = task_tris(row, seedlist[row['seed']])
        signs = unpack(seedlist[row['seed']])[2]
        task = work / f'task-{path.stem}-{idx}.txt'
        write_task(tris, signs, task, known=known | {'<>'})
        p = subprocess.run([str(exe), str(task), str(args.radius)], check=True,
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
        compact = [{k: m[k] for k in ('code', 'bits')} for m in candidates]
        entry = dict(row, id=idx, complete=True, evals=expected, counts=counts,
                     candidates=compact, novel=sorted(novel))
        results.append(entry)
        results.sort(key=lambda r: r['id'])
        total = Counter()
        for r in results:
            total.update(r['counts'])
        saved = dict(provenance=provenance, planned_ids=ids,
                     complete=len(results) == len(ids), tasks=results,
                     evaluations=sum(r['evals'] for r in results),
                     counts=dict(total),
                     candidate_schemes=sorted(set(total) - known - {'<>'}))
        atomic_json(path, saved)
        task.unlink(missing_ok=True)
        if novel:
            rec = dict(id=idx, domain=domain, seed=row['seed'],
                       removed=row['removed'], added=row['added'],
                       triangulation_sha256=row['triangulation_sha256'],
                       schemes=sorted(novel), candidates=compact)
            append_jsonl(cand_path, rec)
            print(f'CANDIDATE task {idx} schemes {sorted(novel)}', flush=True)
        if novel or (len(results) % 10 == 0) or len(results) == 1 or len(results) == len(ids):
            print(f'{len(results)}/{len(ids)} this shard; {saved["evaluations"]} evaluations; '
                  f'{len(total)} schemes; {len(saved["candidate_schemes"])} candidates; '
                  f'{time.monotonic()-start:.1f}s', flush=True)
    return 0 if len(results) == len(ids) else 2


if __name__ == '__main__':
    raise SystemExit(main())
