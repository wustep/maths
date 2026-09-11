#!/usr/bin/env python3
"""Independent Rust replay of every stored named-class representative."""
import argparse
import json
from pathlib import Path
import subprocess
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    ap.add_argument('family', type=Path)
    ap.add_argument('--nodes', type=int, default=10000000)
    ap.add_argument('--seconds', type=float, default=240)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    family = json.loads(args.family.read_text())
    payload = dict(p=family['p'], bound=family['bound'], initial_ap=family['initial_ap'],
                   forbid_ap=family['forbid_ap'], center=family['center'],
                   source=args.family.name, status='UNKNOWN', duals=[])
    args.output.write_text(json.dumps(payload, indent=2)+'\n')
    for i, row in enumerate(family['cases']):
        if row.get('representative') != i:
            continue
        command = [str(args.binary.resolve()), str(family['p']), str(family['bound']),
                   str(args.nodes), str(family['initial_ap']), str(family['forbid_ap']),
                   row['root_mask']]
        start = time.monotonic()
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=args.seconds)
            timeout = False
        except subprocess.TimeoutExpired:
            timeout = True
            result = None
        status = 'UNKNOWN'
        stdout = ''
        if not timeout and result.returncode == 0:
            stdout = result.stdout
            line = [ln for ln in stdout.splitlines() if ln.startswith('p=')][0]
            status = dict(part.split('=', 1) for part in line.split())['status']
        elif not timeout and result.returncode == 3:
            stdout = result.stdout
            status = 'UNKNOWN'
        elif not timeout:
            raise RuntimeError(f'rust dual failed: {result.stderr}')
        entry = dict(case=i, pair=row['pair'], root_mask=row['root_mask'],
                     status=status, timed_out=timeout, seconds=time.monotonic()-start,
                     stdout=stdout)
        payload['duals'].append(entry)
        statuses = [d['status'] for d in payload['duals']]
        payload['status'] = 'SAT' if 'SAT' in statuses else 'UNSAT' if all(s == 'UNSAT' for s in statuses) and len(statuses) == sum(r.get('representative')==j for j,r in enumerate(family['cases'])) else 'UNKNOWN'
        args.output.write_text(json.dumps(payload, indent=2)+'\n')
        print(f"dual case={i} pair={row['pair']} status={status} seconds={entry['seconds']:.3f}", flush=True)
        if status == 'SAT':
            break
    print(f"dual_status={payload['status']} n={len(payload['duals'])}", flush=True)
    return 3 if payload['status'] == 'UNKNOWN' else 0


if __name__ == '__main__':
    raise SystemExit(main())
