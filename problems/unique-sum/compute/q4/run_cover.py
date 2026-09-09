#!/usr/bin/env python3
"""Run one C cover case with a wall limit; interruption is always UNKNOWN."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time


def run(binary, p, bound, nodes, initial_ap, forbid_ap, root, seconds):
    command = [str(binary.resolve()), str(p), str(bound), str(nodes), str(initial_ap), str(forbid_ap)]
    if root is not None:
        command.append(hex(root))
    start = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=seconds)
    except subprocess.TimeoutExpired:
        return dict(p=p, bound=bound, initial_ap=initial_ap, forbid_ap=forbid_ap,
                    root_mask=None if root is None else hex(root), status='UNKNOWN',
                    timed_out=True, wall_limit_seconds=seconds, node_limit=nodes,
                    seconds=time.monotonic()-start)
    if result.returncode not in (0, 3):
        raise RuntimeError(f'cover search failed ({result.returncode}): {result.stderr}')
    payload = json.loads(result.stdout)
    assert payload['status'] in ('SAT', 'UNSAT', 'UNKNOWN')
    assert (result.returncode == 3) == (payload['status'] == 'UNKNOWN')
    if payload['status'] == 'SAT':
        values = payload['witness']
        assert values == sorted(set(values)) and 2 <= len(values) <= bound
        assert all(0 <= x < p for x in values)
        counts = [0] * p
        for a in values:
            for b in values:
                counts[(a+b) % p] += 1
        assert all(n not in (1, 2) for n in counts)
        selected = sum(1 << x for x in values)
        assert selected & int(payload['root_mask'], 16) == int(payload['root_mask'], 16)
        assert not forbid_ap or not any(all((a+i*d) % p in values for i in range(forbid_ap))
                                       for a in range(p) for d in range(1, p))
    return dict(**payload, timed_out=False, wall_limit_seconds=seconds)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    ap.add_argument('p', type=int)
    ap.add_argument('bound', type=int)
    ap.add_argument('--initial-ap', type=int, default=3)
    ap.add_argument('--forbid-ap', type=int, default=0)
    ap.add_argument('--root', type=lambda s: int(s, 0))
    ap.add_argument('--nodes', type=int, default=10000000)
    ap.add_argument('--seconds', type=float, default=180)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.seconds <= 0 or args.nodes <= 0:
        ap.error('positive limits required')
    source = Path(__file__).with_name('cover_search.c')
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    binary_digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    payload = run(args.binary, args.p, args.bound, args.nodes, args.initial_ap,
                  args.forbid_ap, args.root, args.seconds)
    payload.update(source=source.name, source_sha256=source_digest, binary_sha256=binary_digest)
    args.output.write_text(json.dumps(payload, indent=2)+'\n')
    print(json.dumps(payload), flush=True)
    return 3 if payload['status'] == 'UNKNOWN' else 0


if __name__ == '__main__':
    raise SystemExit(main())
