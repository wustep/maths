#!/usr/bin/env python3
"""Run the Rust exact search with explicit wall, node and address-space caps."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    ap.add_argument('p', type=int)
    ap.add_argument('bound', type=int)
    ap.add_argument('--initial-ap', type=int, default=3)
    ap.add_argument('--forbid-ap', type=int, default=0)
    ap.add_argument('--root', default='')
    ap.add_argument('--nodes', type=int, default=3000000)
    ap.add_argument('--seconds', type=float, default=300)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.nodes <= 0 or args.seconds <= 0:
        ap.error('positive node and wall limits required')
    command = [str(args.binary.resolve()), str(args.p), str(args.bound), str(args.nodes),
               str(args.initial_ap), str(args.forbid_ap)]
    if args.root:
        command.append(args.root)
    def cap_memory():
        resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024**2, 1536 * 1024**2))
    source_digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    binary_digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    start = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, preexec_fn=cap_memory)
    timeout = False
    try:
        stdout, stderr = proc.communicate(timeout=args.seconds)
    except subprocess.TimeoutExpired:
        timeout = True
        proc.kill()
        stdout, stderr = proc.communicate()
    status = 'UNKNOWN'
    if not timeout and proc.returncode == 0:
        lines = [line for line in stdout.splitlines() if line.startswith(f'p={args.p} limit={args.bound} status=')]
        if len(lines) != 1:
            raise RuntimeError('missing/unexpected search summary')
        status = dict(part.split('=', 1) for part in lines[0].split())['status']
        if status not in ('SAT', 'UNSAT'):
            raise RuntimeError('successful exit without a completed decision')
    elif not timeout and proc.returncode != 3:
        raise RuntimeError(f'search failed ({proc.returncode}): {stderr}')
    report = dict(p=args.p, bound=args.bound, initial_ap=args.initial_ap, forbid_ap=args.forbid_ap,
                  root_mask=args.root or None, status=status,
                  source=args.source.name, source_sha256=source_digest, binary_sha256=binary_digest,
                  node_limit=args.nodes, wall_limit_seconds=args.seconds,
                  address_space_limit_mib=1536, timed_out=timeout,
                  exit_code=proc.returncode, stdout=stdout, stderr=stderr,
                  seconds=time.monotonic()-start,
                  max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)
    return 3 if status == 'UNKNOWN' else 0


if __name__ == '__main__':
    raise SystemExit(main())
