#!/usr/bin/env python3
"""Check midpoint case coverage and every affine identification independently."""
import hashlib
import itertools
import json
from pathlib import Path

from midpoint_cases import cases


def contains_ap(p, values, length):
    patterns = ({(a+i*d) % p for i in range(length)}
                for a in range(p) for d in range(1, p))
    return any(pattern <= values for pattern in patterns)


def verify_rows(p, initial_ap, forbidden, center):
    rows = cases(p, initial_ap, forbidden, center)
    expected_pairs = {(a, b) for a in range(p) for b in range(a+1, p) if (a+b-2*center)%p == 0}
    assert {tuple(row['pair']) for row in rows} == expected_pairs
    for i, row in enumerate(rows):
        values = set(row['root'])
        if row.get('forbidden_progression'):
            assert contains_ap(p, values, forbidden)
        else:
            assert not contains_ap(p, values, forbidden)
            rep = row['representative']
            assert rep <= i and rows[rep]['representative'] == rep
            target = set(rows[rep]['root'])
            assert any({(a*x+b) % p for x in values} == target
                       for a in range(1, p) for b in range(p))
    return rows


def main():
    checked = 0
    for p in (5, 7, 11, 13):
        for length in (3, 4):
            center = 1 if length == 3 else p-1
            root = {0, 1, p-1} | ({2} if length == 4 else set())
            for forbidden in sorted({length+1, p}):
                rows = verify_rows(p, length, forbidden, center)
                for size in range(len(root), p+1):
                    for combo in itertools.combinations(range(p), size):
                        values = set(combo)
                        if not root <= values or contains_ap(p, values, forbidden):
                            continue
                        supports_center = any(a != b and (a+b-2*center) % p == 0
                                              for a in values for b in values)
                        covered = any(not row.get('forbidden_progression') and set(row['root']) <= values
                                      for row in rows)
                        assert supports_center == covered
                        checked += 1
    summaries = []
    for length, forbidden, center in ((3, 4, 1), (4, 5, 58)):
        rows = verify_rows(59, length, forbidden, center)
        summaries.append(dict(p=59, initial_ap=length, forbid_ap=forbidden, center=center,
                              pairs=len(rows), forbidden_roots=sum(bool(r.get('forbidden_progression')) for r in rows),
                              representatives=sum(r.get('representative') == i for i, r in enumerate(rows))))
    source = Path(__file__).with_name('midpoint_cases.py')
    print(json.dumps(dict(status='VALID_PARTITION', small_sets_checked=checked,
                          partition_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), families=summaries)))


if __name__ == '__main__':
    main()
