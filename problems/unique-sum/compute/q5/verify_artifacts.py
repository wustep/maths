#!/usr/bin/env python3
"""Dual arithmetic replay of saved witnesses and honest near-miss annotations."""
import json
from pathlib import Path
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
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rust_binary', type=Path)
    args = ap.parse_args()
    rows = []
    upper = json.loads((HERE.parent/'q3/p59_upper.json').read_text())
    rows.append(check(args.rust_binary, 59, upper['witness'], expected_support=upper['sumset_size']))
    rows.append(check(args.rust_binary, 59,
                      [0,1,3,4,5,9,13,15,16,21,29,33,45,58], expected_unique=1))
    oeis = [0,1,2,3,4,5,9,10,16,25,27,32,42,44,48]
    rows.append(check(args.rust_binary, 59, oeis))
    check(args.rust_binary, 5, [0, 1], expected_unique=3)
    print(json.dumps(dict(status='VALID_ARTIFACTS', checks=rows), sort_keys=True))


if __name__ == '__main__':
    main()
