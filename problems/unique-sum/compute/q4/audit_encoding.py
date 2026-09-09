#!/usr/bin/env python3
"""Compare every small membership assignment with the definition, including symmetry."""
import json
from pathlib import Path
import sys
from pysat.solvers import Solver

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_sat import formula


def admissible(p, values):
    # Direct unordered pairs, independent of the producer's ordered counter.
    counts = [0] * p
    for i, a in enumerate(values):
        for b in values[i:]:
            counts[(a + b) % p] += 1
    return len(values) >= 2 and 1 not in counts


def leader(p, mask, depth):
    order = [0] + [x for a in range(1, (p + 1) // 2) for x in (a, p-a)]
    word = tuple((mask >> x) & 1 for x in order[:depth])
    return all(word >= tuple((mask >> ((a*x+b) % p)) & 1 for x in order[:depth])
               for a in range(1, p) for b in range(p))


def main():
    checked = instances = 0
    exact = {}
    for p in (3, 5, 7, 11):
        subsets = [[x for x in range(p) if mask >> x & 1] for mask in range(1 << p)]
        valid = [admissible(p, values) for values in subsets]
        exact[p] = min(len(a) for a, good in zip(subsets, valid) if good)
        # Full assignment checks test both directions of every auxiliary encoding.
        # At p=11 the two boundary cardinalities suffice; smaller primes use all.
        bounds = range(3, p+1) if p < 11 else (6, 7)
        for depth in sorted({0, min(4, p), p}):
            order = [0] + [x for a in range(1, (p+1)//2) for x in (a, p-a)]
            for initial_ap in (3,) if p == 3 else (3, 4):
                root = sum(1 << x for x in order[:initial_ap])
                allowed = [mask & root == root and leader(p, mask, depth)
                           for mask in range(1 << p)]
                has_ap = [any(all((start + i*step) % p in a for i in range(initial_ap))
                              for start in range(p) for step in range(1, p)) for a in subsets]
                for bound in bounds:
                    for atmost in (False, True):
                        for sumset_bound in (False, True):
                            cnf, selected = formula(p, bound, depth, atmost, initial_ap, sumset_bound)
                            instances += 1
                            with Solver(name='cadical195', bootstrap_with=cnf) as solver:
                                exists = False
                                for mask, values in enumerate(subsets):
                                    cardinality_ok = len(values) <= bound if atmost else len(values) == bound
                                    expected = valid[mask] and cardinality_ok and allowed[mask]
                                    result = solver.solve(assumptions=[v if mask >> x & 1 else -v
                                                                       for x, v in enumerate(selected)])
                                    assert result == expected, (p, bound, atmost, depth, initial_ap, sumset_bound, values, result, expected)
                                    exists |= expected
                                    checked += 1
                                # No valid orbit in the specified AP family is lost.
                                raw_exists = any(good and has_ap[m] and (len(a) <= bound if atmost else len(a) == bound)
                                                 for m, (a, good) in enumerate(zip(subsets, valid)))
                                assert exists == raw_exists, (p, bound, atmost, depth, initial_ap)
    # Regression for the unordered definition: {0,1,4} has unique sums at p=5.
    assert not admissible(5, [0, 1, 4])
    print(json.dumps(dict(status='VALID_ENCODING', assignments=checked,
                          formulas=instances, brute_force_minima=exact), sort_keys=True))


if __name__ == '__main__':
    main()
