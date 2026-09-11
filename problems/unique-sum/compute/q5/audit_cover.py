#!/usr/bin/env python3
"""Compare the C completion search with enumeration of every small subset."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess


def mask(values):
    return sum(1 << x for x in values)


def root(p, length):
    return mask(([0] + [x for i in range(1, (p+1)//2) for x in (i, p-i)])[:length])


def good(p, values):
    counts = [0] * p
    for a in values:
        for b in values:
            counts[(a+b) % p] += 1
    return len(values) >= 2 and all(n not in (1, 2) for n in counts)


def has_ap(p, values, length):
    return bool(length) and any(all((a+i*d) % p in values for i in range(length))
                               for a in range(p) for d in range(1, p))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('binary', type=Path)
    args = ap.parse_args()
    checks = []
    subsets = 0
    for p in (3, 5, 7, 11, 13):
        valid = []
        for size in range(2, p+1):
            for a in itertools.combinations(range(p), size):
                subsets += 1
                if good(p, a):
                    valid.append((mask(a), size, set(a)))
        for initial_ap in range(3, min(p, 6)+1):
            roots = {root(p, initial_ap)}
            if initial_ap == 3:
                roots.update(root(p, 3) | (1 << a) | (1 << b)
                             for a in range(p) for b in range(a+1, p) if (a+b)%p == 2)
            for forbidden in (0, min(p, initial_ap+1)):
                for selected in sorted(roots):
                    sizes = [k for m, k, a in valid
                             if m & selected == selected and not has_ap(p, a, forbidden)]
                    minimum = min(sizes) if sizes else p+1
                    for bound in sorted({max(2, minimum-1), min(p, minimum)}):
                        result = subprocess.run([str(args.binary), str(p), str(bound), '1000000',
                                                 str(initial_ap), str(forbidden), hex(selected)],
                                                capture_output=True, text=True, timeout=10)
                        assert result.returncode == 0, result
                        payload = json.loads(result.stdout)
                        expected = 'SAT' if minimum <= bound else 'UNSAT'
                        assert payload['status'] == expected, (p, bound, selected, forbidden, payload)
                        if expected == 'SAT':
                            a = payload['witness']
                            assert len(set(a)) == len(a) <= bound and good(p, a)
                            assert mask(a) & selected == selected and not has_ap(p, set(a), forbidden)
                        checks.append(dict(p=p, bound=bound, initial_ap=initial_ap,
                                           forbid_ap=forbidden, root_mask=hex(selected), status=expected))
    limited = subprocess.run([str(args.binary), '59', '14', '1', '3', '0'],
                             capture_output=True, text=True)
    assert limited.returncode == 3 and json.loads(limited.stdout)['status'] == 'UNKNOWN'
    source = Path(__file__).with_name('cover_search.c')
    print(json.dumps(dict(status='VALID_COVER_CONTROLS', subsets=subsets, checks=checks,
                          source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), limit_exit=3)))


if __name__ == '__main__':
    main()
