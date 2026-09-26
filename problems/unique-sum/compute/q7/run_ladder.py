#!/usr/bin/env python3
"""Run the AP5 ceiling and both named-class families for one prime, one job at a time."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def run(cmd, what):
    print(f'# {what}', flush=True)
    print(' '.join(map(str, cmd)), flush=True)
    result = subprocess.run(cmd)
    if result.returncode not in (0, 3):
        raise SystemExit(f'{what} failed with {result.returncode}')
    return result.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('cover', type=Path)
    ap.add_argument('exact', type=Path)
    ap.add_argument('p', type=int)
    ap.add_argument('bound', type=int)
    ap.add_argument('--ap5-nodes', type=int, default=50000000)
    ap.add_argument('--ap5-seconds', type=float, default=10800)
    ap.add_argument('--class-nodes', type=int, default=20000000)
    ap.add_argument('--class-seconds', type=float, default=3600)
    ap.add_argument('--dual-seconds', type=float, default=4200)
    args = ap.parse_args()
    p, bound = args.p, args.bound
    cover, exact = args.cover.resolve(), args.exact.resolve()
    python = sys.executable
    ap5_c = HERE / f'p{p}_ap5_cover.json'
    ap5_r = HERE / f'p{p}_ap5_exact.json'
    ap4 = HERE / f'p{p}_ap4_not_ap5_classes.json'
    free = HERE / f'p{p}_ap4_free_classes.json'
    dual_ap4 = HERE / f'p{p}_dual_ap4_not_ap5.json'
    dual_free = HERE / f'p{p}_dual_ap4_free.json'

    def decide(path, what):
        payload = json.loads(path.read_text())
        status = payload.get('status')
        print(f"{what} status={status} nodes={payload.get('nodes')} seconds={payload.get('seconds')}", flush=True)
        if status == 'SAT':
            print(f'SAT_WITNESS {what} p={p} bound={bound}', flush=True)
            return 1
        if status != 'UNSAT':
            return 3
        return 0

    def skip_unsat(path, what):
        if not path.exists():
            return False
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            return False
        if payload.get('status') != 'UNSAT':
            return False
        print(f'# skip {what} (stored UNSAT)', flush=True)
        return True

    if not skip_unsat(ap5_c, f'p={p} AP5 C'):
        run([python, HERE/'run_cover.py', cover, str(p), str(bound),
             '--initial-ap', '5', '--forbid-ap', '0',
             '--nodes', str(args.ap5_nodes), '--seconds', str(args.ap5_seconds),
             '--output', ap5_c], f'p={p} AP5 C')
        rc = decide(ap5_c, f'p={p} AP5 C')
        if rc:
            return rc

    if not skip_unsat(ap5_r, f'p={p} AP5 Rust'):
        run([python, HERE/'run_exact.py', exact, str(p), str(bound),
             '--initial-ap', '5', '--forbid-ap', '0',
             '--nodes', str(args.ap5_nodes), '--seconds', str(args.ap5_seconds),
             '--source', HERE/'verify_exact.rs', '--output', ap5_r], f'p={p} AP5 Rust')
        rc = decide(ap5_r, f'p={p} AP5 Rust')
        if rc:
            return rc

    if not skip_unsat(ap4, f'p={p} AP4-not-AP5 C'):
        run([python, HERE/'midpoint_cases.py', cover, str(p), str(bound),
             '--initial-ap', '4', '--forbid-ap', '5', '--center', str(p-1),
             '--nodes', str(args.class_nodes), '--seconds-per-case', str(args.class_seconds),
             '--output', ap4], f'p={p} AP4-not-AP5 C')
        rc = decide(ap4, f'p={p} AP4-not-AP5 C')
        if rc:
            return rc

    if not skip_unsat(free, f'p={p} AP4-free C'):
        run([python, HERE/'midpoint_cases.py', cover, str(p), str(bound),
             '--initial-ap', '3', '--forbid-ap', '4', '--center', '1',
             '--nodes', str(args.class_nodes), '--seconds-per-case', str(args.class_seconds),
             '--output', free], f'p={p} AP4-free C')
        rc = decide(free, f'p={p} AP4-free C')
        if rc:
            return rc

    if not skip_unsat(dual_ap4, f'p={p} AP4-not-AP5 Rust dual'):
        run([python, HERE/'dual_classes.py', exact, ap4,
             '--nodes', str(args.class_nodes), '--seconds', str(args.dual_seconds),
             '--output', dual_ap4], f'p={p} AP4-not-AP5 Rust dual')
        rc = decide(dual_ap4, f'p={p} AP4-not-AP5 Rust dual')
        if rc:
            return rc

    if not skip_unsat(dual_free, f'p={p} AP4-free Rust dual'):
        run([python, HERE/'dual_classes.py', exact, free,
             '--nodes', str(args.class_nodes), '--seconds', str(args.dual_seconds),
             '--output', dual_free], f'p={p} AP4-free Rust dual')
        rc = decide(dual_free, f'p={p} AP4-free Rust dual')
        if rc:
            return rc

    print(f'LADDER_COMPLETE p={p} bound={bound}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
