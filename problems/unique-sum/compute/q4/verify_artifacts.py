#!/usr/bin/env python3
"""Dual arithmetic replay of saved witnesses and honest near-miss annotations."""
import argparse
import csv
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent


def check(binary, p, values, expected_unique=0, expected_support=None):
    assert values == sorted(set(values)) and len(values) >= 2
    assert all(type(x) is int and 0 <= x < p for x in values)
    ordered = [0] * p
    unordered = [0] * p
    for i, a in enumerate(values):
        for j, b in enumerate(values):
            ordered[(a+b) % p] += 1
            if i <= j:
                unordered[(a+b) % p] += 1
    unique = [s for s in range(p) if unordered[s] == 1]
    assert unique == [s for s in range(p) if ordered[s] in (1, 2)]
    assert len(unique) == expected_unique, (p, values, unique, expected_unique)
    if expected_support is not None:
        assert sum(x > 0 for x in ordered) == expected_support
    result = subprocess.run([str(binary)], input=' '.join(map(str, [p, *values])),
                            text=True, capture_output=True)
    assert result.returncode == (1 if unique else 0), result.stderr
    independent = json.loads(result.stdout)
    assert independent['ordered_counts'] == ordered
    assert independent['unique_sums'] == unique
    assert independent['p'] == p and independent['cardinality'] == len(values)
    return dict(p=p, cardinality=len(values), unique_sums=unique,
                ordered_pairs=len(values)**2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rust_binary', type=Path)
    args = ap.parse_args()
    rows = []
    for row in csv.DictReader((HERE.parent/'green_m_p.csv').open()):
        values = json.loads(row['witness'])
        assert len(values) == int(row['m'])
        rows.append(check(args.rust_binary, int(row['p']), values))
    upper = json.loads((HERE.parent/'q3/p59_upper.json').read_text())
    assert upper['p'] == 59 and upper['cardinality'] == 15
    rows.append(check(args.rust_binary, 59, upper['witness'], expected_support=upper['sumset_size']))
    rows.append(check(args.rust_binary, 59,
                      [0,1,3,4,5,9,13,15,16,21,29,33,45,58], expected_unique=1))
    source = json.loads((HERE/'published_oeis.json').read_text())
    data = list(map(int, source['data'].split(',')))
    assert data == [3,4,5,7,7,8,9,10,11,11,12,13,13,13,14,15,15,16,16,16]
    primes = [p for p in range(3, 74) if all(p % d for d in range(2, p))]
    for example in source['example']:
        match = re.fullmatch(r'a\((\d+)\) = (\d+): \{([0-9, ]+)\}\.', example)
        if not match:
            continue
        index, size = int(match[1])-1, int(match[2])
        values = list(map(int, match[3].split(',')))
        assert len(values) == size == data[index]
        rows.append(check(args.rust_binary, primes[index], values))
    for name in ('anneal_p79_k16.json', 'anneal_p79_k17.json', 'square_p79_cap19.json'):
        payload = json.loads((HERE/name).read_text())
        expected_unique = payload.get('best_unique', 0)
        assert payload['status'] == ('UNKNOWN' if expected_unique else 'SAT')
        rows.append(check(args.rust_binary, payload['p'], payload['witness'],
                          expected_unique, payload.get('sumset_size')))
    # Failure behavior: a diagonal and an off-diagonal unique sum must reject.
    check(args.rust_binary, 5, [0, 1], expected_unique=3)
    print(json.dumps(dict(status='VALID_ARTIFACTS', checks=rows,
                          exact_table_extended=False), sort_keys=True))


if __name__ == '__main__':
    main()
