#!/usr/bin/env python3
"""Dual arithmetic check of the saved 16-sets at 67, 71, and 73."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
FILES = ('p67_upper.json', 'p71_upper.json', 'p73_upper.json')


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('rust_binary', type=Path)
    args = ap.parse_args()
    rows = []
    for name in FILES:
        upper = json.loads((HERE/name).read_text())
        p, values = upper['p'], upper['witness']
        assert values == sorted(set(values)) and len(values) == 16
        ordered = [0] * p
        unordered = [0] * p
        for i, a in enumerate(values):
            for j, b in enumerate(values):
                ordered[(a+b) % p] += 1
                if i <= j:
                    unordered[(a+b) % p] += 1
        unique = [s for s in range(p) if unordered[s] == 1]
        assert unique == [s for s in range(p) if ordered[s] in (1, 2)]
        assert not unique
        assert sum(n > 0 for n in ordered) == upper['sumset_size']
        result = subprocess.run([str(args.rust_binary)],
                                input=' '.join(map(str, [p, *values])),
                                text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        independent = json.loads(result.stdout)
        assert independent['unique_sums'] == []
        assert independent['p'] == p and independent['cardinality'] == 16
        rows.append(dict(p=p, cardinality=16, sumset_size=upper['sumset_size']))
    print(json.dumps(dict(status='VALID_UPPER', checks=rows)))


if __name__ == '__main__':
    main()
