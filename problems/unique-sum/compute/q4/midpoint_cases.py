#!/usr/bin/env python3
"""Partition an AP-avoiding completion problem by a named midpoint witness.

Every selected center c needs distinct selected endpoints u,v with u+v=2c.
List ALL these pairs. Roots already containing a forbidden AP are impossible
in this conditional family. Affine-equivalent remaining roots share one run.
No assumption that every solution avoids an AP is made by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path

from audit_cover import has_ap, mask, root
from run_cover import run


def canonical(p, values):
    return min(tuple(sorted((a*(x-b)) % p for x in values))
               for a in range(1, p) for b in values)


def cases(p, initial_ap, forbid_ap, center):
    selected = root(p, initial_ap)
    assert selected >> center & 1, 'center must be selected in the root'
    rows, classes = [], {}
    for a in range(p):
        b = (2*center-a) % p
        if a >= b:
            continue
        combined = selected | (1 << a) | (1 << b)
        values = {x for x in range(p) if combined >> x & 1}
        row = dict(pair=[a, b], root=sorted(values), root_mask=hex(combined))
        if has_ap(p, values, forbid_ap):
            row['forbidden_progression'] = True
        else:
            key = canonical(p, values)
            if key not in classes:
                classes[key] = len(rows)
            row['representative'] = classes[key]
        rows.append(row)
    assert len(rows) == (p-1)//2
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    ap.add_argument('p', type=int)
    ap.add_argument('bound', type=int)
    ap.add_argument('--initial-ap', type=int, default=3)
    ap.add_argument('--forbid-ap', type=int, default=4)
    ap.add_argument('--center', type=int, default=1)
    ap.add_argument('--nodes', type=int, default=10000000)
    ap.add_argument('--seconds-per-case', type=float, default=60)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if not 3 <= args.p < 64 or any(args.p % d == 0 for d in range(2, args.p)):
        ap.error('odd prime below 64 required')
    if not (2 <= args.bound <= args.p and 3 <= args.initial_ap <= args.p
            and 3 <= args.forbid_ap <= args.p and 0 <= args.center < args.p
            and args.nodes > 0 and args.seconds_per_case > 0):
        ap.error('invalid bounds, progression, center or limits')
    source = Path(__file__).with_name('cover_search.c')
    payload = dict(p=args.p, bound=args.bound, initial_ap=args.initial_ap,
                   forbid_ap=args.forbid_ap, center=args.center,
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   binary_sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                   partition_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   status='UNKNOWN', conditional=True,
                   cases=cases(args.p, args.initial_ap, args.forbid_ap, args.center))

    def save():
        # A terminated campaign leaves a valid manifest of completed cases.
        temporary = args.output.with_suffix('.tmp')
        temporary.write_text(json.dumps(payload, indent=2)+'\n')
        temporary.replace(args.output)

    save()
    for i, row in enumerate(payload['cases']):
        if row.get('representative') != i:
            continue
        row['result'] = run(args.binary, args.p, args.bound, args.nodes, args.initial_ap,
                            args.forbid_ap, int(row['root_mask'], 16), args.seconds_per_case)
        save()
        print(f"case={i} center={args.center} pair={row['pair']} status={row['result']['status']}", flush=True)
        if row['result']['status'] == 'SAT':
            break
    results = [row.get('result', {}).get('status') for i, row in enumerate(payload['cases'])
               if row.get('representative') == i]
    payload['status'] = 'SAT' if 'SAT' in results else 'UNSAT' if all(s == 'UNSAT' for s in results) else 'UNKNOWN'
    save()
    print(f"conditional_status={payload['status']} representatives={len(results)}", flush=True)
    return 3 if payload['status'] == 'UNKNOWN' else 0


if __name__ == '__main__':
    raise SystemExit(main())
