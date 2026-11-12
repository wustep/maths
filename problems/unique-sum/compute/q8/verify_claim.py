#!/usr/bin/env python3
"""Check stored q8 artifacts against m(67)=m(71)=m(73)=16, without long searches."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIMES = (
    dict(p=67, bound=15, ap4_not_ap5=31, ap4_free=29, center_ap4=66),
    dict(p=71, bound=15, ap4_not_ap5=33, ap4_free=31, center_ap4=70),
    dict(p=73, bound=15, ap4_not_ap5=34, ap4_free=32, center_ap4=72),
)


def load(name):
    return json.loads((HERE/name).read_text())


def family_unsat(name, expected_reps, p, bound, initial_ap, forbid_ap, center):
    payload = load(name)
    assert payload['p'] == p and payload['bound'] == bound
    assert payload['initial_ap'] == initial_ap and payload['forbid_ap'] == forbid_ap
    assert payload['center'] == center and payload['status'] == 'UNSAT'
    reps = [row for i, row in enumerate(payload['cases']) if row.get('representative') == i]
    assert len(reps) == expected_reps
    for row in reps:
        result = row['result']
        assert result['status'] == 'UNSAT'
        assert result['p'] == p and result['bound'] == bound
        assert result['forbid_ap'] == forbid_ap
        assert result['root_mask'] == row['root_mask']
        assert int(result.get('nodes', 0)) > 0
    return dict(file=name, representatives=len(reps),
                max_seconds=max(r['result']['seconds'] for r in reps),
                max_nodes=max(r['result']['nodes'] for r in reps))


def dual_unsat(name, expected, family_name):
    payload = load(name)
    family = load(family_name)
    assert payload['status'] == 'UNSAT' and len(payload['duals']) == expected
    roots = {row['root_mask'] for i, row in enumerate(family['cases']) if row.get('representative') == i}
    dual_roots = {row['root_mask'] for row in payload['duals']}
    assert roots == dual_roots
    assert all(row['status'] == 'UNSAT' for row in payload['duals'])
    return dict(file=name, duals=len(payload['duals']))


def main():
    families = []
    duals = []
    ap5 = []
    for spec in PRIMES:
        p = spec['p']
        upper = load(f'p{p}_upper.json')
        assert upper['p'] == p and upper['cardinality'] == 16
        families.append(family_unsat(f'p{p}_ap4_not_ap5_classes.json', spec['ap4_not_ap5'],
                                     p, spec['bound'], 4, 5, spec['center_ap4']))
        families.append(family_unsat(f'p{p}_ap4_free_classes.json', spec['ap4_free'],
                                     p, spec['bound'], 3, 4, 1))
        duals.append(dual_unsat(f'p{p}_dual_ap4_not_ap5.json', spec['ap4_not_ap5'],
                                f'p{p}_ap4_not_ap5_classes.json'))
        duals.append(dual_unsat(f'p{p}_dual_ap4_free.json', spec['ap4_free'],
                                f'p{p}_ap4_free_classes.json'))
        rust = load(f'p{p}_ap5_exact.json')
        cside = load(f'p{p}_ap5_cover.json')
        assert rust['status'] == 'UNSAT' and rust['p'] == p and rust['initial_ap'] == 5
        assert cside['status'] == 'UNSAT' and cside['p'] == p and cside['initial_ap'] == 5
        ap5.append(dict(p=p, rust_nodes=rust.get('nodes'), c_nodes=cside.get('nodes')))
    print(json.dumps(dict(status='VALID_CLAIM_ARTIFACTS', families=families, duals=duals, ap5=ap5),
                     sort_keys=True))


if __name__ == '__main__':
    main()
