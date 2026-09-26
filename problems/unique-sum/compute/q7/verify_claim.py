#!/usr/bin/env python3
"""Check stored q7 artifacts. Exit 0 only when the three published
equalities are fully dual-certified; otherwise exit 3 (partial)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIMES = (
    dict(p=67, bound=15, ap4_not_ap5=31, ap4_free=29, center_ap4=66),
    dict(p=71, bound=15, ap4_not_ap5=33, ap4_free=31, center_ap4=70),
    dict(p=73, bound=15, ap4_not_ap5=34, ap4_free=32, center_ap4=72),
)


def load(name):
    path = HERE / name
    if not path.exists():
        return None
    return json.loads(path.read_text())


def family_unsat(name, expected_reps, p, bound, initial_ap, forbid_ap, center):
    payload = load(name)
    if payload is None:
        return None
    assert payload['p'] == p and payload['bound'] == bound
    assert payload['initial_ap'] == initial_ap and payload['forbid_ap'] == forbid_ap
    assert payload['center'] == center
    reps = [row for i, row in enumerate(payload['cases']) if row.get('representative') == i]
    assert len(reps) == expected_reps
    if payload.get('status') != 'UNSAT':
        return dict(file=name, status=payload.get('status'), representatives=len(reps), complete=False)
    for row in reps:
        result = row.get('result')
        assert result is not None
        assert result['status'] == 'UNSAT'
        assert result['p'] == p and result['bound'] == bound
        assert result['forbid_ap'] == forbid_ap
        assert result['root_mask'] == row['root_mask']
        assert int(result.get('nodes', 0)) > 0
    return dict(file=name, status='UNSAT', representatives=len(reps), complete=True,
                max_seconds=max(r['result']['seconds'] for r in reps),
                max_nodes=max(r['result']['nodes'] for r in reps))


def dual_unsat(name, expected, family_name):
    payload = load(name)
    family = load(family_name)
    if payload is None or family is None:
        return None
    roots = {row['root_mask'] for i, row in enumerate(family['cases']) if row.get('representative') == i}
    dual_roots = {row['root_mask'] for row in payload.get('duals', [])}
    complete = (payload.get('status') == 'UNSAT'
                and len(payload.get('duals', [])) == expected
                and roots == dual_roots
                and all(row['status'] == 'UNSAT' for row in payload['duals']))
    return dict(file=name, status=payload.get('status'), duals=len(payload.get('duals', [])),
                complete=complete)


def main():
    families = []
    duals = []
    ap5 = []
    missing = []
    complete_primes = []
    for spec in PRIMES:
        p = spec['p']
        upper = load(f'p{p}_upper.json')
        assert upper is not None
        assert upper['p'] == p and upper['cardinality'] == 16
        fam_ap4 = family_unsat(f'p{p}_ap4_not_ap5_classes.json', spec['ap4_not_ap5'],
                               p, spec['bound'], 4, 5, spec['center_ap4'])
        fam_free = family_unsat(f'p{p}_ap4_free_classes.json', spec['ap4_free'],
                                p, spec['bound'], 3, 4, 1)
        dual_ap4 = dual_unsat(f'p{p}_dual_ap4_not_ap5.json', spec['ap4_not_ap5'],
                              f'p{p}_ap4_not_ap5_classes.json')
        dual_free = dual_unsat(f'p{p}_dual_ap4_free.json', spec['ap4_free'],
                               f'p{p}_ap4_free_classes.json')
        rust = load(f'p{p}_ap5_exact.json')
        cside = load(f'p{p}_ap5_cover.json')
        for label, obj in ((f'p{p}_ap4_not_ap5', fam_ap4), (f'p{p}_ap4_free', fam_free),
                           (f'p{p}_dual_ap4', dual_ap4), (f'p{p}_dual_free', dual_free)):
            if obj is None:
                missing.append(label)
            elif obj.get('complete'):
                if 'representatives' in obj:
                    families.append(obj)
                else:
                    duals.append(obj)
            else:
                missing.append(label)
        ap5_ok = True
        if rust is None or cside is None:
            missing.append(f'p{p}_ap5')
            ap5_ok = False
        else:
            assert rust['p'] == p and rust['initial_ap'] == 5
            assert cside['p'] == p and cside['initial_ap'] == 5
            if rust.get('status') != 'UNSAT' or cside.get('status') != 'UNSAT':
                missing.append(f'p{p}_ap5')
                ap5_ok = False
            else:
                ap5.append(dict(p=p, rust_nodes=rust.get('nodes'), c_nodes=cside.get('nodes')))
        if (ap5_ok and fam_ap4 and fam_ap4.get('complete') and fam_free and fam_free.get('complete')
                and dual_ap4 and dual_ap4.get('complete') and dual_free and dual_free.get('complete')):
            complete_primes.append(p)
    status = 'VALID_CLAIM_ARTIFACTS' if complete_primes == [67, 71, 73] else 'PARTIAL'
    print(json.dumps(dict(status=status, complete_primes=complete_primes, missing=missing,
                          families=families, duals=duals, ap5=ap5), sort_keys=True))
    return 0 if status == 'VALID_CLAIM_ARTIFACTS' else 3


if __name__ == '__main__':
    sys.exit(main())
