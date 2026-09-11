#!/usr/bin/env python3
"""Check stored q6 artifacts against m(61)=15, without long searches."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE/name).read_text())


def family_unsat(name, expected_reps, initial_ap, forbid_ap, center):
    payload = load(name)
    assert payload['p'] == 61 and payload['bound'] == 14
    assert payload['initial_ap'] == initial_ap and payload['forbid_ap'] == forbid_ap
    assert payload['center'] == center and payload['status'] == 'UNSAT'
    reps = [row for i, row in enumerate(payload['cases']) if row.get('representative') == i]
    assert len(reps) == expected_reps
    for row in reps:
        result = row['result']
        assert result['status'] == 'UNSAT'
        assert result['p'] == 61 and result['bound'] == 14
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
    upper = load('p61_upper.json')
    assert upper['p'] == 61 and upper['cardinality'] == 15
    families = [
        family_unsat('ap4_not_ap5_classes.json', 28, 4, 5, 60),
        family_unsat('ap4_free_classes.json', 26, 3, 4, 1),
    ]
    duals = [
        dual_unsat('dual_ap4_not_ap5.json', 28, 'ap4_not_ap5_classes.json'),
        dual_unsat('dual_ap4_free.json', 26, 'ap4_free_classes.json'),
    ]
    ap5_rust = load('p61_ap5_exact.json')
    ap5_c = load('p61_ap5_cover.json')
    assert ap5_rust['status'] == 'UNSAT' and ap5_rust['p'] == 61 and ap5_rust['initial_ap'] == 5
    assert ap5_c['status'] == 'UNSAT' and ap5_c['p'] == 61 and ap5_c['initial_ap'] == 5
    print(json.dumps(dict(status='VALID_CLAIM_ARTIFACTS', families=families, duals=duals,
                          ap5={'rust_nodes': ap5_rust['nodes'], 'c_nodes': ap5_c['nodes']}),
                     sort_keys=True))


if __name__ == '__main__':
    main()
