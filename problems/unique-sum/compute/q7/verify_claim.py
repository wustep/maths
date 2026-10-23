#!/usr/bin/env python3
"""Check stored q7 artifacts against m(67)=16, without long searches."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


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
    return dict(file=name, duals=len(payload['duals']),
                max_seconds=max(r['seconds'] for r in payload['duals']))


def main():
    upper = load('p67_upper.json')
    assert upper['p'] == 67 and upper['cardinality'] == 16
    families = [
        family_unsat('p67_ap4_not_ap5_classes.json', 31, 67, 15, 4, 5, 66),
        family_unsat('p67_ap4_free_classes.json', 29, 67, 15, 3, 4, 1),
    ]
    duals = [
        dual_unsat('p67_dual_ap4_not_ap5.json', 31, 'p67_ap4_not_ap5_classes.json'),
        dual_unsat('p67_dual_ap4_free.json', 29, 'p67_ap4_free_classes.json'),
    ]
    rust = load('p67_ap5_exact.json')
    cside = load('p67_ap5_cover.json')
    assert rust['status'] == 'UNSAT' and rust['p'] == 67 and rust['initial_ap'] == 5
    assert cside['status'] == 'UNSAT' and cside['p'] == 67 and cside['initial_ap'] == 5
    print(json.dumps(dict(status='VALID_CLAIM_ARTIFACTS', families=families, duals=duals,
                          ap5={'rust_nodes': rust.get('nodes'), 'c_nodes': cside.get('nodes')}),
                     sort_keys=True))


if __name__ == '__main__':
    main()
