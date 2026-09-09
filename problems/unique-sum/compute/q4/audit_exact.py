#!/usr/bin/env python3
"""Check the exact brancher's progression-restricted minima by full enumeration."""
import argparse
import itertools
import json
from pathlib import Path
import subprocess


def minimum(p, length):
    patterns = {sum(1 << ((a+i*d) % p) for i in range(length))
                for a in range(p) for d in range(1, p)}
    for size in range(2, p+1):
        for values in itertools.combinations(range(p), size):
            mask = sum(1 << x for x in values)
            if not any(mask & pattern == pattern for pattern in patterns):
                continue
            counts = [0] * p
            for a in values:
                for b in values:
                    counts[(a+b) % p] += 1
            if all(n not in (1, 2) for n in counts):
                return size
    raise AssertionError('whole group must work')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    args = ap.parse_args()
    checks = []
    for p in (3, 5, 7, 11):
        for length in range(3, min(p, 6)+1):
            size = minimum(p, length)
            for limit in (size-1, size):
                result = subprocess.run([str(args.binary), str(p), str(limit), '1000000', str(length)],
                                        capture_output=True, text=True, timeout=10)
                expected = 'SAT' if limit == size else 'UNSAT'
                assert result.returncode == 0 and f' status={expected} ' in result.stdout, result
                if expected == 'SAT':
                    witness = json.loads(result.stdout.split('witness=')[1])
                    assert len(witness) <= limit
                    counts = [0] * p
                    for a in witness:
                        for b in witness:
                            counts[(a+b) % p] += 1
                    assert all(n not in (1,2) for n in counts)
                    assert any(all((a+i*d) % p in witness for i in range(length))
                               for a in range(p) for d in range(1,p))
                checks.append(dict(p=p, initial_ap=length, limit=limit, status=expected))
    # A budget of one must produce UNKNOWN and exit 3, never UNSAT.
    limited = subprocess.run([str(args.binary), '59', '14', '1', '3'], capture_output=True, text=True)
    assert limited.returncode == 3 and 'status=UNKNOWN' in limited.stdout
    print(json.dumps(dict(status='VALID_EXACT_CONTROLS', checks=checks, limit_exit=3), sort_keys=True))


if __name__ == '__main__':
    main()
